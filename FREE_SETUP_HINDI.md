# 🔬 Deep Research 2.0 — FREE Setup Guide (Hindi)

Ye repo **GPT Researcher** ka fork hai — open-source ka sabse popular deep research agent (29,000+ ⭐), jiska latest release hi **"Deep Research 2.0"** update hai. Is setup me **ek bhi rupaya kharch nahi hoga** — sirf free LLM APIs use honge.

- 🤖 **Research agent team**: planner + parallel researchers + reviewer + reviser + writer + publisher
- 🕷️ **12 parallel web scraping agents** (configurable)
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

Phir:

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

## 5. Troubleshooting

- **`429 / rate limit` errors** → `SCRAPER_RATE_LIMIT_DELAY` ko `2.0`–`3.0` kar do, ya `DEEP_RESEARCH_CONCURRENCY` thoda kam karo (free tier ~1 request/sec deta hai)
- **Search results kam aa rahe hain** → Tavily free plan le lo (1000 credits/month, card nahi lagta), `.env` me `RETRIEVER=tavily` + key daalo
- **Report Hindi me chahiye** → `.env` me `LANGUAGE=hindi` kar do
- **z.ai slow lag raha hai** → `.env` me NaraRouter (Option B) par switch karo

## 6. Original project ka credit

Ye [assafelovic/gpt-researcher](https://github.com/Assafelovic/gpt-researcher) (Apache-2.0) ka fork hai. Original project ko ⭐ dena mat bhoolna!
