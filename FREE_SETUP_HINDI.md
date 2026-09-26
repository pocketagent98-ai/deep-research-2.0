# 🔬 Deep Research 2.0 — FREE Setup Guide (Hindi)

Ye repo **GPT Researcher** ka fork hai — open-source ka sabse popular deep research agent (29,000+ ⭐), jiska latest release hi **"Deep Research 2.0"** update hai. Is setup me **ek bhi rupaya kharch nahi hoga** — sirf free LLM APIs use honge.

- 🤖 **Research agent team**: planner + parallel researchers + reviewer + reviser + writer + publisher
- 🕷️ **12 parallel web scraping agents** (configurable)
- 🔍 **SearxNG meta-search** (optional): 70+ search engines, bina API key
- 🧠 **Qdrant vector memory** (optional): purani research yaad rehti hai
- ✅ **Fact-checking** (optional): Ragas + Prometheus-style judge
- ⏱️ **Kai ghante tak** autonomous deep research
- 🧾 Final report: Markdown / PDF / DOCX, real citations ke saath

---

## 1. Free LLM ka jugaad — do providers

| Provider | Base URL | Free models | Kitna free |
|---|---|---|---|
| **z.ai** (default) | `https://api.z.ai/api/paas/v4/` | `glm-4.5-flash`, `glm-4.7-flash` | Poore din, rate-limit ~1 request/sec |
| **NaraRouter** | `https://router.bynara.id/v1` | `auto/bynara` (free tier models, dashboard me "Free" wale models dekho) | Free tokens **har roz reset** hote hain |

**Jugaad ka idea:** dono keys rakho. z.ai ka free quota khatam ya slow ho jaye to `.env` me bas `OPENAI_BASE_URL` + `OPENAI_API_KEY` badal kar NaraRouter par switch kar do (2 line ka kaam). Dono OpenAI-compatible hain, code me kuch nahi badalna padta. Isse practically unlimited, multi-hour research chalti hai — bina paisa diye.

> Doosra free z.ai model jo aapko yaad nahi aa raha tha: wo **`glm-4.7-flash`** hai (naya version). `glm-4.5-flash` aur `glm-4.7-flash` — dono 100% free hain.

## 2. Setup (5 minute)

```bash
# 1. Repo clone karo
git clone https://github.com/pocketagent98-ai/deep-research-2.0.git
cd deep-research-2.0

# 2. Dependencies install karo
pip install -r requirements.txt

# 3. Free local embeddings ke liye (ek baar)
pip install sentence-transformers langchain-huggingface

# 4. Env file banao aur apni keys daalo
cp .env.free.example .env
```

Ab `.env` file kholo aur:
- `OPENAI_API_KEY=YOUR_ZAI_API_KEY_HERE` ki jagah **apni z.ai key** paste karo
- (Optional) NaraRouter use karna ho to file me Option B wale lines dekho

> ⚠️ **Security — ye zaroor padho:** Ye repo **public** hai. `.env` file `.gitignore` me already hai, to wo kabhi upload nahi hogi — **lekin apni keys kabhi bhi kisi code file, commit ya chat me paste karke commit mat karna**. Agar kabhi galti se key commit ho jaye to turant us provider ke dashboard me jaakar **key delete/regenerate** kar do.

## 3. Deep Research chalana

### Mode A — Deep Research (recursive, sabse gehra)

```bash
bash scripts/deep-research-free.sh "aapka research topic"
```

ya seedha:

```bash
python cli.py "aapka research topic" --report_type deep --tone objective
```

Ye **depth-3, breadth-8** ke saath chalta hai: har topic se 8 sub-queries banti hain, har sub-query phir se 8 aur queries banati hai, aur aisa 3 level deep. 12 scrapers parallel me websites kholkar padhte hain. **30 minute se kai ghante tak** lag sakte hain — jitna gehra, utna detailed report.

Report `output/` folder me ban jayegi.

### Mode B — Multi-Agent Team (STORM style, 12+ agents)

`multi_agents/task.json` kholo aur `query` badlo:

```json
{
  "query": "aapka research topic",
  "max_sections": 5,
  ...
}
```

Phhr:

```bash
cd multi_agents
pip install -r requirements.txt
python main.py
```

Isme poora agent team kaam karta hai: Chief Editor → Researcher (har section par parallel) → Reviewer → Reviser → Writer → Publisher. Final report `multi_agents/output/` me Markdown/PDF/DOCX me milti hai.

## 4. Research ko aur LAMBA aur GEHRA karna (tuning)

Sab kuch `.env` me hai:

| Variable | Default (is setup me) | Kya karta hai |
|---|---|---|
| `DEEP_RESEARCH_BREADTH` | 8 | Har level par kitni sub-queries — badhao to aur zyada angles cover honge |
| `DEEP_RESEARCH_DEPTH` | 3 | Kitne level deep jaana hai — 4 karo to double time double gehrai |
| `DEEP_RESEARCH_CONCURRENCY` | 8 | Kitni sub-queries ek saath chalti hain |
| `MAX_SCRAPER_WORKERS` | 12 | Kitne scraping agents parallel me websites padhte hain |
| `SCRAPER_RATE_LIMIT_DELAY` | 1.0 | Har scraper ke becha kitne second ka gap (429 errors se bachne ke liye) |

Ghanton tak research ke liye shuruat me hi set karo:
```env
DEEP_RESEARCH_BREADTH=10
DEEP_RESEARCH_DEPTH=4
DEEP_RESEARCH_CONCURRENCY=10
MAX_SCRAPER_WORKERS=12
```

## 5. 🔍 Power-up: SearxNG — 70+ search engines, ZERO limit

DuckDuckGo theek hai, lekin **SearxNG** Google, Bing, DuckDuckGo, Wikipedia jaise 70+ engines se ek saath results laata hai — **bina kisi API key ke, bina kisi limit ke**. Ye aapke hi computer par Docker me chalta hai:

```bash
# SearxNG (search) + Qdrant (memory) dono chalao
docker compose -f docker-compose.free-stack.yml up -d

# .env me ye 2 lines uncomment karo:
#   RETRIEVER=searx
#   SEARX_URL=http://localhost:8888
```

Bas — ab research agent 70+ engines se search karega. Browser me `http://localhost:8888` kholkar khud bhi try kar sakte ho.

## 6. 🕷️ Power-up: Trafilatura — clean text scraping

Websites par ads, menus, footer ki faltu cheezein research me noise laati hain. **Trafilatura** sirf asli article text nikaal deta hai — better quality + kam tokens (free tier par zyada kaam ho jata hai):

```bash
pip install -r requirements-free.txt

# .env me:
#   SCRAPER=trafilatura
```

Kaam kaise karta hai quick test (Wikipedia se 71KB clean text nikala tha):
```bash
python -c "
import requests, importlib.util
spec = importlib.util.spec_from_file_location('t', 'gpt_researcher/scraper/trafilatura_scraper/trafilatura_scraper.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
s = requests.Session(); s.headers.update({'User-Agent': 'Mozilla/5.0'})
print(len(m.TrafilaturaScraper('https://en.wikipedia.org/wiki/Guitar', session=s).scrape()[0]), 'chars of clean text')
"
```

## 7. 🧠 Power-up: Qdrant — research memory (vector database)

Kai ghanton ki research me hazaron pages ka data hota hai, aur purani reports ka fayda tabhi hai jab unhe yaad rakha ja sake. **Qdrant** ek open-source vector database hai jo milliseconds me purane facts dhoondh deta hai:

```bash
# Qdrant chalao (docker-compose.free-stack.yml me included)
docker compose -f docker-compose.free-stack.yml up -d qdrant
pip install -r requirements-free.txt

# Apni reports/notes/PDFs memory me daalo:
python scripts/memory-qdrant.py index output/

# Baad me search karo — purani research se:
python scripts/memory-qdrant.py search "guitar ki history kisne banai"

# Kya stored hai dekho:
python scripts/memory-qdrant.py list
```

Embeddings **local** hain (sentence-transformers) — koi API key nahi, zero cost.

## 8. ✅ Power-up: Fact-checking — Ragas + Prometheus-style judge

99% accuracy ka goal yahin se aata hai. Report ban jaane ke baad usko uske sources ke against **audit** karo:

```bash
pip install -r requirements-free.txt

# Report ko sources ke against check karo:
python scripts/fact-check.py output/aapki-report.md --sources-dir output/sources/
```

Do checks chalte hain, dono aapke FREE LLM (z.ai/NaraRouter) par:

1. **RAGAS Faithfulness** — report ke kitne % claims source text se supported hain (score bar me dikhta hai). Ye pakadta hai ki AI ne kuch "apni taraf se" to nahi joda.
2. **Prometheus-style LLM Judge** — ek critic model jo rubric dekar **specific** unsupported claims, contradictions aur missing points list karta hai.

> Honest note: ye tools accuracy *measure* karte hain, guarantee nahi karte. Score 90%+ aaye tabhi report par bharosa karo, waraa revise karwao.

## 9. Troubleshooting

- **`429 / rate limit` errors** → `SCRAPER_RATE_LIMIT_DELAY` ko `2.0`–`3.0` kar do, ya `DEEP_RESEARCH_CONCURRENCY` thoda kam karo (free tier ~1 request/sec deta hai)
- **Search results kam aa rahe hain** → SearxNG on karo (section 5), ya Tavily free plan (1000 credits/month)
- **Report Hindi me chahiye** → `.env` me `LANGUAGE=hindi` kar do
- **z.ai slow lag raha hai** → `.env` me NaraRouter (Option B) par switch karo
- **SearxNG search kamp nahi kar raha** → `curl "http://localhost:8888/search?q=test&format=json"` chala kar dekho — JSON aana chahiye
- **Qdrant error** → `docker ps` se check karo container chal raha hai, phir `QDRANT_URL` sahi hai

## 10. Original project ka credit

Ye [assafelovic/gpt-researcher](https://github.com/Assafelovic/gpt-researcher) (Apache-2.0) ka fork hai. Original project ko ⭐ dena mat bhoolna!
