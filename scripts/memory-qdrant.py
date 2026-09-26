#!/usr/bin/env python
"""
Qdrant Memory — purani research yaad rakhna (The Memory)
=========================================================
Apni purani research reports / PDF-notes / articles ko Qdrant vector DB me
index karo, aur baad me milliseconds me unhe search karo. Deep research me
jab hazaron pages ka data hota hai, tab yahi memory kaam aati hai.

Setup:
    1. Qdrant chalao:  docker compose -f docker-compose.free-stack.yml up -d qdrant
    2. pip install -r requirements-free.txt
    3. .env me (optional):  QDRANT_URL=http://localhost:6333

Use:
    # Reports folder ki saari files memory me daalo:
    python scripts/memory-qdrant.py index output/

    # Memory se poocho:
    python scripts/memory-qdrant.py search "guitar ki history kisne banai"

    # Kya-kya stored hai dekho:
    python scripts/memory-qdrant.py list

Embeddings FREE hain — local sentence-transformers model, koi API key nahi.
"""

import argparse
import glob
import hashlib
import os
import sys

from dotenv import load_dotenv

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(ROOT, ".env"))

QDRANT_URL = os.environ.get("QDRANT_URL", "http://localhost:6333")
COLLECTION = "deep_research_memory"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"   # 384 dims, local & free
CHUNK_SIZE = 1000        # characters per chunk
CHUNK_OVERLAP = 150

_vector_size = None


def get_embedder():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(MODEL_NAME)


def get_client():
    from qdrant_client import QdrantClient
    return QdrantClient(url=QDRANT_URL, timeout=10)


def ensure_collection(client, vector_size):
    from qdrant_client.models import Distance, VectorParams
    if not client.collection_exists(COLLECTION):
        client.create_collection(
            collection_name=COLLECTION,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )
        print(f"Created collection: {COLLECTION} (dim={vector_size})")


def chunk_text(text):
    text = text.strip()
    if len(text) <= CHUNK_SIZE:
        return [text]
    chunks, start = [], 0
    while start < len(text):
        end = min(start + CHUNK_SIZE, len(text))
        # sentence boundary par kaatne ki koshish
        if end < len(text):
            window = text[start:end]
            cut = max(window.rfind(". "), window.rfind("\n"), window.rfind("। "))
            if cut > CHUNK_SIZE // 2:
                end = start + cut + 1
        chunks.append(text[start:end])
        start = end - CHUNK_OVERLAP
        if start < 0:
            start = 0
    return [c for c in chunks if c.strip()]


def collect_files(path):
    if os.path.isfile(path):
        return [path]
    exts = (".md", ".txt", ".pdf")
    files = []
    for ext in exts:
        files.extend(glob.glob(os.path.join(path, f"**/*{ext}"), recursive=True))
    return sorted(set(files))


def read_file(path):
    if path.lower().endswith(".pdf"):
        try:
            import fitz  # pymupdf
            with fitz.open(path) as doc:
                return "\n".join(page.get_text() for page in doc)
        except ImportError:
            print(f"  !! PDF padhne ke liye 'pip install pymupdf' karo — skip: {path}")
            return ""
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def cmd_index(paths):
    files = []
    for p in paths:
        files.extend(collect_files(p))
    if not files:
        print("!! Koi .md/.txt/.pdf file nahi mili.")
        sys.exit(1)

    from qdrant_client.models import PointStruct

    embedder = get_embedder()
    dim = embedder.get_sentence_embedding_dimension()
    client = get_client()
    ensure_collection(client, dim)

    total_points = 0
    for path in files:
        text = read_file(path)
        if not text.strip():
            continue
        chunks = chunk_text(text)
        if not chunks:
            continue
        vectors = embedder.encode(chunks, show_progress_bar=False).tolist()
        base = hashlib.md5(os.path.abspath(path).encode()).hexdigest()[:12]
        points = [
            PointStruct(
                id=int(hashlib.md5(f"{base}-{i}".encode()).hexdigest()[:15], 16),
                vector=vectors[i],
                payload={
                    "file": os.path.basename(path),
                    "path": os.path.abspath(path),
                    "chunk": i,
                    "text": chunks[i],
                },
            )
            for i in range(len(chunks))
        ]
        client.upsert(collection_name=COLLECTION, points=points)
        total_points += len(points)
        print(f"  + {os.path.basename(path)}  ({len(chunks)} chunks)")

    print(f"\nDone — {total_points} chunks memory me save ho gaye. Ab search karo:")
    print(f"  python scripts/memory-qdrant.py search \"aapka sawaal\"")


def cmd_search(query, top):
    from qdrant_client.models import SearchFilter
    embedder = get_embedder()
    client = get_client()
    if not client.collection_exists(COLLECTION):
        print("!! Memory khali hai. Pehle index karo: python scripts/memory-qdrant.py index output/")
        sys.exit(1)

    vector = embedder.encode([query], show_progress_bar=False)[0].tolist()
    hits = client.query_points(
        collection_name=COLLECTION, query=vector, limit=top
    ).points

    if not hits:
        print("Kuch nahi mila.")
        return
    for i, hit in enumerate(hits, 1):
        p = hit.payload
        print(f"\n[{i}] score={hit.score:.3f}  ({p.get('file')} | chunk {p.get('chunk')})")
        snippet = (p.get("text") or "")[:400]
        print(f"    {snippet}...")


def cmd_list():
    client = get_client()
    if not client.collection_exists(COLLECTION):
        print("Memory khali hai (collection exist nahi karti).")
        return
    info = client.get_collection(COLLECTION)
    points, _ = client.scroll(collection_name=COLLECTION, limit=250, with_payload=True)
    files = {}
    for p in points:
        f = p.payload.get("file", "?")
        files[f] = files.get(f, 0) + 1
    print(f"Collection: {COLLECTION} | total points: {info.points_count}")
    for f, n in sorted(files.items()):
        print(f"  - {f}  ({n} chunks)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Qdrant research memory: index / search / list")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_index = sub.add_parser("index", help="files/folder ko memory me daalo")
    p_index.add_argument("paths", nargs="+", help="file ya folder (output/ etc.)")

    p_search = sub.add_parser("search", help="memory me search karo")
    p_search.add_argument("query")
    p_search.add_argument("--top", type=int, default=5)

    sub.add_parser("list", help="stored files dikhaao")

    args = parser.parse_args()
    if args.cmd == "index":
        cmd_index(args.paths)
    elif args.cmd == "search":
        cmd_search(args.query, args.top)
    elif args.cmd == "list":
        cmd_list()
