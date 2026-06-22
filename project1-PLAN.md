# PLAN.md — Conversational Product Discovery Agent

*The how. Derived from BRIEF.md. Build in the phase order below; each phase ends with something that runs.*

---

## Architecture in one picture

```
User (CLI / web UI)
      │
      ▼
  Agent loop  ──►  Claude (with tools)
      ▲                   │  decides: respond, or call a tool
      │                   ▼
      │            tool_use: search_catalog / get_product_details / list_categories
      │                   │
      └──── tool_result ◄─┘  (executed against in-memory catalog)
```

One agent, one conversation loop. Claude reasons over the message history and decides whether to answer or call a tool. Tools run deterministic queries against the catalog in memory and return structured results. No embeddings, no second model.

## Tools (the agent's only way to touch the catalog)

Define three tools with strict input schemas. The agent must use these — it never sees the raw catalog, which is what forces grounding.

1. **`search_catalog`** — the core tool.
   Inputs: `category` (optional), `keywords` (optional), `min_price` / `max_price` (optional), `attributes` (optional key/value map, e.g. colour, material), `exclude` (optional list). Returns: a list of matching products (id, title, price, key attributes), capped at ~10.

2. **`get_product_details`** — inputs: `product_id`. Returns: full record for one product. Used when the shopper drills into a specific item.

3. **`list_categories`** — no inputs. Returns the catalog's categories and the attribute keys available per category. The agent calls this to ground itself before guessing filter values.

Design rule: the tools are dumb and deterministic; the intelligence lives in how Claude maps language to tool arguments. That separation is the whole lesson of Project 1.

## The agent loop (pseudocode)

```
messages = [system_prompt]
loop:
    append user input to messages
    response = claude(messages, tools=[search_catalog, get_product_details, list_categories])
    while response.stop_reason == "tool_use":
        for each tool_use block:
            result = execute_tool(name, input)         # runs against catalog
            append tool_result to messages
        response = claude(messages, tools=...)
    print response text
```

System prompt should: state the agent is a shopping assistant for [vertical]; instruct it to call `list_categories` when unsure of valid filters; require that it only recommends products returned by tools; and tell it to ask one clarifying question when intent is too vague to filter.

## Catalog data

- Pick one vertical you know (recommend apparel or electronics — rich, intuitive attributes).
- Source: use a real open product dataset if one fits; otherwise generate a realistic synthetic catalog of ~1,000 SKUs (have Claude generate structured records with consistent categories, price ranges, and 4–6 attributes each). Real-feeling data matters for the "not a toy" claim.
- Store as `data/catalog.json`. Load into memory at startup. `catalog.py` holds the load + filter functions that the tools wrap.

## Eval seed (light, but from day one)

Create `evals/queries.jsonl`, ~15 queries across difficulty bands:
- **Easy (4):** direct ("show me running shoes", "blue jacket").
- **Medium (5):** multi-constraint ("waterproof boots under £80, size 9").
- **Hard (4):** fuzzy intent ("something for a rainy festival weekend").
- **Ambiguous (2):** should trigger a clarifying question ("a gift for my dad").

Each row: the query + a one-line note on what good behaviour looks like. `run_evals.py` runs each through the agent and prints the conversation for eyeballing. No scoring framework yet — that's Project 3. The goal now is just a repeatable way to see regressions.

## File structure

```
agentic-discovery/
  README.md            # product-spec style: what, why, architecture, how to run
  BRIEF.md  PLAN.md  CLAUDE.md
  requirements.txt
  data/catalog.json
  src/
    catalog.py         # load + deterministic filtering
    tools.py           # the three tool definitions + executors
    agent.py           # the conversation loop
    cli.py             # terminal chat
  evals/
    queries.jsonl
    run_evals.py
  app.py               # thin Streamlit UI for the demo only
```

## Three-week schedule

**Week 1 — it searches.**
Catalog loaded; `catalog.py` filtering working; the three tools defined and executing; single-turn agent loop returns grounded results from a typed query. End state: type a query in the CLI, get real products back.

**Week 2 — it converses.**
Multi-turn session memory; follow-ups refine prior results; clarifying-question behaviour; system prompt tuned; response quality polished (explains *why* it picked items). End state: a natural back-and-forth that feels like a good shop assistant.

**Week 3 — it ships.**
Write the 15 eval queries and `run_evals.py`; fix what they expose; build the Streamlit UI; write the README as a product spec; record the demo; draft the teardown post. End state: a stranger clones, reads, runs in five minutes.

## Definition of done

All five BRIEF success criteria met, repo public, demo recorded, teardown drafted. Then — and only then — Project 2 (grounding the same agent with semantic search) begins on top of this codebase.

## Notes for CLAUDE.md (persistent project memory)

Seed CLAUDE.md with: the vertical chosen, the catalog schema, the three tool contracts, the grounding rule (never recommend a product not returned by a tool), and the scope-out list so the build doesn't drift into Project 2–6 territory.
