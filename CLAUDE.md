# CLAUDE.md — Conversational Product Discovery Agent (Project 1)

Persistent project memory. Read this before touching any code. Update it when decisions change.

---

## Project in one line

A single Claude agent that turns natural-language shopping intent into grounded product recommendations from a real apparel catalog, via tool/function calling.

## Domain: Apparel

Vertical chosen: **Apparel** (clothing + footwear). This shapes the catalog schema, tool filter fields, and system prompt intent-mapping logic.

---

## Catalog: Fashion Product Images (apparel)

Source: Kaggle `paramaggarwal/fashion-product-images-small` → `styles.csv`
Images: NOT used (placeholder tiles in UI). Text fields only.

### Prep → `data/catalog.json` (~1,200 clean SKUs)

1. Load `styles.csv`
2. Keep `masterCategory` in `{Apparel, Footwear}`
3. Drop rows missing `baseColour` / `season` / `usage` / `articleType`
4. (Optional) narrow to 1–2 genders for coherence
5. Sample ~1,000–1,500 rows
6. Enrich `price` (no native price): assign realistic GBP by `articleType`, then jitter per row

| articleType | GBP range |
|---|---|
| Tshirts | 12–30 |
| Shirts | 25–55 |
| Sweaters / Sweatshirts | 30–70 |
| Jackets / Coats | 60–160 |
| Jeans | 40–90 |
| Trousers | 30–75 |
| Shoes | 45–130 |

### Record schema

```json
{
  "id": "15970",
  "title": "Turtle Check Men Navy Blue Shirt",
  "gender": "Men",
  "category": "Apparel",
  "subcategory": "Topwear",
  "type": "Shirts",
  "colour": "Navy Blue",
  "season": "Fall",
  "usage": "Casual",
  "price": 42
}
```

Fields map directly from `styles.csv`:
- `id` ← `id`
- `title` ← `productDisplayName`
- `gender` ← `gender`
- `category` ← `masterCategory`
- `subcategory` ← `subCategory`
- `type` ← `articleType`
- `colour` ← `baseColour`
- `season` ← `season`
- `usage` ← `usage`
- `price` ← enriched (not in source)

---

## Tool contracts

Three tools. The agent's only way to touch the catalog. Tools are dumb and deterministic — intelligence lives in how Claude maps language to tool arguments.

### `search_catalog`

```
inputs:
  category     (optional str)   — "Apparel" or "Footwear"
  keywords     (optional str)   — free-text over title + type
  min_price    (optional float)
  max_price    (optional float)
  attributes   (optional obj)   — { colour, season, usage, gender, type }
  exclude      (optional list)  — [{ "field": "colour", "value": "Black" }]

returns: list of ≤10 products (id, title, price, key attributes)
```

### `get_product_details`

```
inputs:  product_id (str)
returns: full record for one product
```

### `list_categories`

```
inputs:  none
returns: catalog categories + available values per filter field
         (types, colours, seasons, usages, genders)
```

---

## `search_catalog` filter → field mapping

| Agent filter | Catalog field |
|---|---|
| `gender` | `gender` (exact match) |
| `keywords` | free-text over `title` + `type` |
| `category` / `type` | `subcategory` or `type` (agent picks granularity) |
| `min_price` / `max_price` | `price` |
| `attributes.colour` | `colour` |
| `attributes.season` | `season` — "warm"/"winter" resolves HERE |
| `attributes.usage` | `usage` — "city break"/"formal" resolves HERE |
| `exclude` | drop rows matching `{field: value}` |

---

## Grounding + intent rules (seed for system prompt)

- **Only recommend products returned by a tool. Never invent.**
- `season` and `usage` carry the fuzzy-intent load — lean on them.
  - "warm" / "winter city break" → `season=Winter` or `season=Fall`
  - "city break" / "smart casual" → `usage=Casual` or `usage=Formal`
- Call `list_categories` when unsure which `articleType` / `usage` values exist in the catalog.
- Ask **one** clarifying question when intent is too vague to filter. Don't guess.
- Multi-turn: follow-ups like "cheaper" or "in blue" refine the prior search — carry session context.

---

## Scope (what is and is not in Project 1)

**In:** single agent, tool calling, in-memory catalog, multi-turn conversation, clarifying questions, 15-query eval set, CLI + Streamlit UI.

**Out (later projects):** embeddings / semantic search, formal eval framework, multiple coordinating agents, MCP server, cart / checkout / auth / database.

If a feature isn't in the **In** list, it doesn't go in this project.

---

## File structure

```
P1/
  BRIEF.md       project spec
  PLAN.md        build plan
  CLAUDE.md      this file
  README.md      product-spec style (write last)
  requirements.txt
  data/
    catalog.json       ~1,200 SKUs
    prepare_catalog.py script to build catalog.json from styles.csv
  src/
    catalog.py    load + deterministic filtering
    tools.py      three tool definitions + executors
    agent.py      conversation loop
    cli.py        terminal chat
  evals/
    queries.jsonl  15 queries
    run_evals.py   runs each through agent, prints output
  app.py         Streamlit UI (demo only)
```

---

## Key decisions log

| Decision | Choice | Reason |
|---|---|---|
| Vertical | Apparel | Rich fuzzy attributes (season, usage); matches brief examples |
| Catalog source | Kaggle fashion-product-images-small | Real data; ~44k SKUs, clean fields |
| Price | Synthetic GBP by articleType | Source has no price; type-based ranges stay realistic |
| Images | Not used | Out of scope for Project 1 |
| Search | Deterministic filter (no embeddings) | Embeddings are Project 2 |
| UI | Streamlit | Minimal dependency; demo-ready fast |