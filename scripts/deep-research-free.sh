#!/usr/bin/env bash
# =============================================================================
#  FREE Deep Research 2.0 launcher  (z.ai / NaraRouter par free)
#
#  Use:
#     bash scripts/deep-research-free.sh "aapka research topic"
# =============================================================================
set -euo pipefail
cd "$(dirname "$0")/.."

if [ ! -f .env ]; then
  echo ">> .env nahi mili. Pehle ye karo:"
  echo "      cp .env.free.example .env"
  echo "   phir .env kholkar OPENAI_API_KEY me apni z.ai ya NaraRouter key paste karo."
  exit 1
fi

QUERY="${1:-}"
if [ -z "$QUERY" ]; then
  read -r -p "Research topic likho: " QUERY
fi

echo ">> Deep Research shuru: $QUERY"
echo ">> 12 parallel scrapers | depth=3 | breadth=8 | concurrency=8"
echo ">> (30 minute se KAI GHANTE tak chal sakta hai — terminal band mat karna)"
echo ""
exec python cli.py "$QUERY" --report_type deep --tone objective
