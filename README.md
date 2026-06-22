# Conversational Product Discovery Agent

A single Claude agent that turns natural-language shopping intent into grounded product recommendations from a real apparel catalog — via tool/function calling, no embeddings, no vector database.

> *"Something warm for a winter city break, under £100, not black"* → real products, explained picks, follow-ups that work.

---

## What this is

A demonstration that intent-to-catalog mapping is the hard problem in conversational commerce — not the chat interface. The agent handles:

- **Fuzzy intent** — "warm" and "cosy" map to `season=Winter/Fall`; "city break" maps to `usage=Casual`; "smart" maps to `usage=Formal`
- **Multi-constraint queries** — price range, colour exclusion, gender, and occasion in a single turn
- **Multi-turn refinement** — "cheaper" or "in blue" refine the previous result without restating anything
- **Clarifying questions** — when intent is genuinely too vague to filter, one focused question instead of a guess
- **Grounding** — every product shown exists in the catalog; nothing is invented

What it is **not**: a keyword search with a chat wrapper. The work is in the mapping layer — the system prompt that teaches the model how `season` and `usage` carry the fuzzy-intent load, and the tool contracts that force grounding.

---

## Architecture

```
User (CLI / Streamlit)
        │
        ▼
   Agent loop  ──►  Claude claude-sonnet-4-6 (with tools)
        ▲                   │  decides: respond, or call a tool
        │                   ▼
        │        search_catalog / get_product_details / list_categories
        │                   │
        └──── tool_result ◄─┘  (executed against in-memory catalog)
```

One agent, one conversation loop. Claude reasons over the full message history and either responds or calls a tool. Tools run deterministic filter queries against a JSON catalog loaded into memory at startup. The agent never sees the raw catalog — only what the tools return.

**Key design rule:** tools are dumb and deterministic; all intelligence lives in how Claude maps natural language to tool arguments. This separation is the whole lesson of this project.

---

## Catalog

**Source:** [Kaggle — Fashion Product Images (Small)](https://www.kaggle.com/datasets/paramaggarwal/fashion-product-images-small) (`styles.csv`)

**Size:** ~1,200 SKUs (Apparel + Footwear, filtered and sampled)

**Schema:**

| Field | Source column | Notes |
|---|---|---|
| `id` | `id` | |
| `title` | `productDisplayName` | |
| `gender` | `gender` | Men / Women / Boys / Girls / Unisex |
| `category` | `masterCategory` | Apparel / Footwear |
| `subcategory` | `subCategory` | Topwear / Bottomwear / etc. |
| `type` | `articleType` | Shirts / Jeans / Jackets / etc. |
| `colour` | `baseColour` | |
| `season` | `season` | Summer / Winter / Fall / Spring |
| `usage` | `usage` | Casual / Formal / Sports / Ethnic |
| `price` | — | Synthetic GBP, assigned by article type |

Price is not in the source dataset. Realistic GBP ranges are assigned per article type (Tshirts £12–30, Jackets £60–160, etc.) with per-row jitter.

**Images** are not used. The catalog is text-only.

---

## Tools

The agent has exactly three tools. It cannot touch the catalog any other way.

### `search_catalog`

Filters the catalog and returns up to 10 matching products (slim view: id, title, price, type, colour, season, usage, gender).

```
category     (optional) — "Apparel", "Footwear", "Shirts", "Jeans", …
keywords     (optional) — free-text over title + type
min_price    (optional) — GBP
max_price    (optional) — GBP
attributes   (optional) — { colour, season, usage, gender, type }
exclude      (optional) — [{ "field": "colour", "value": "Black" }]
```

### `get_product_details`

Returns the full record for one product by ID.

### `list_categories`

Returns all distinct values for every filter field (types, colours, seasons, usages, genders) and the catalog price range. The agent calls this when it needs to check what values actually exist before filtering.

---

## How to run

**Prerequisites:** Python 3.10+, an [Anthropic API key](https://console.anthropic.com/)

```bash
# 1. Clone and install
git clone <repo-url>
cd agentic-discovery
pip install -r requirements.txt

# 2. Add your API key
cp .env.example .env
# edit .env and set ANTHROPIC_API_KEY=...

# 3. Build the catalog
# Download styles.csv from https://www.kaggle.com/datasets/paramaggarwal/fashion-product-images-small
# Place it in data/styles.csv, then:
python data/prepare_catalog.py

# 4. Run
python src/cli.py          # terminal chat
streamlit run app.py       # web UI
```

**Run the eval set:**
```bash
python evals/run_evals.py              # all 15 queries
python evals/run_evals.py --band hard  # just the hard ones
```

---

## Eval results

15 queries across four difficulty bands. Pass = right products, right filters, sensible response.

| Band | Queries | Pass |
|---|---|---|
| Easy | 4 | 4/4 |
| Medium | 5 | 5/5 |
| Hard | 4 | 4/4 |
| Ambiguous | 2 | 2/2 |
| **Total** | **15** | **15/15** |

Q4 ("black jeans under £60") has no results in the catalog — the sampled dataset has few black jeans under that price point — but the agent handled it correctly: reported no results and offered three concrete alternatives without inventing any products. Grounding held in every case.

---

## Key decisions

**Why keyword search instead of embeddings?**
Semantic search (embeddings + vector DB) is Project 2. This project proves the hard part is intent-to-filter mapping, not retrieval sophistication. With a well-designed system prompt and the right catalog fields (`season`, `usage`), keyword + attribute filtering handles most real queries.

**Why `season` and `usage` as first-class fields?**
They carry all the fuzzy-intent load. "Warm" → `season=Winter`. "City break" → `usage=Casual`. "Job interview" → `usage=Formal`. Without these fields, you'd need embeddings to handle this class of query. With them, deterministic filtering works.

**Why synthetic prices?**
The source dataset has no prices. Type-based GBP ranges with per-row jitter produce realistic spread without distorting the catalog's category distribution.

**Why Streamlit for the UI?**
Minimal dependency, no build step, ships in one file. The point of this project is the agent, not the UI framework.

---

## File structure

```
.
├── README.md
├── BRIEF.md            project spec
├── PLAN.md             build plan
├── CLAUDE.md           persistent project memory (for Claude Code)
├── requirements.txt
├── app.py              Streamlit web UI
├── data/
│   ├── prepare_catalog.py   styles.csv → catalog.json
│   └── catalog.json         ~1,200 SKUs (generated)
├── src/
│   ├── catalog.py      load + deterministic filtering
│   ├── tools.py        tool definitions + executors
│   ├── agent.py        conversation loop + system prompt
│   └── cli.py          terminal chat
└── evals/
    ├── queries.jsonl   15 eval queries
    └── run_evals.py    runs evals, prints for eyeballing
```

---

## What's next (Project 2)

This project uses keyword + attribute filtering. The natural next step is grounding the same agent with **semantic search** — embeddings over product titles and descriptions, so "something festival-appropriate" finds the right items even without an exact `usage` match. Same agent, same tools, better retrieval. [Project 2 →](#)
