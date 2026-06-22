# BRIEF.md — Conversational Product Discovery Agent

*Project 1 of the Agentic Commerce Build Plan. Spec first: this defines the what and why. PLAN.md defines the how.*

---

## Goal

Build an agent that turns natural-language shopping intent into relevant products from a real catalog, conversationally. A shopper says *"something warm for a winter city break, under £100, not black"* and the agent finds it, asks a clarifying question if it needs to, and explains its picks — grounded entirely in real catalog data.

## Why this project, why first

It's the discovery layer of an AI Hub at its simplest, and it's the foundation every later project builds on. The point is not a chatbot demo. The point is to prove one thing publicly: **I can ship a working agent against real commerce data, not a toy.** That claim is the entry ticket to everything else in the plan.

It also establishes the build discipline the scarce-skill positioning depends on — grounding (no invented products), a small eval set from day one, and a README written as a product spec.

## Scope

**In:**
- A single agent (one Claude model) using tool/function calling.
- A real product catalog of 500–2,000 SKUs in one vertical (apparel, electronics, or home — pick one I know well).
- Structured tools the agent calls: search the catalog, get product details, list categories.
- Multi-turn conversation with memory of the session (follow-ups like "cheaper" or "in blue" work).
- Clarifying questions when intent is ambiguous.
- A small evaluation set (~15 queries) run from the start.
- A CLI for building, a thin web UI for the demo.

**Out (deliberately — these are later projects):**
- Embeddings / semantic search → Project 2.
- Formal guardrails and eval framework → Project 3.
- Multiple coordinating agents → Project 4.
- MCP server / external exposure → Project 5.
- Cart, checkout, payments, auth, user accounts, a database. Catalog lives in memory.

If a feature isn't on the **In** list, it doesn't go in Project 1. Scope creep here is the main risk.

## The hard problem (where the actual work is)

Keyword search is trivial. The real work is the agent reliably translating fuzzy human intent into structured catalog queries:
- *"warm"* → category/attribute mapping (coats, knitwear; material = wool/fleece)
- *"under £100"* → a price filter
- *"not black"* → an exclusion
- *"for a city break"* → soft styling intent the agent should reason about, not filter on literally
- And knowing when the request is too vague and it should ask one good question instead of guessing.

Plus grounding discipline: the agent must never present a product that isn't in the catalog, or invent attributes. This is the lightweight ancestor of the guardrail work in Project 3, so build the habit now.

## Success criteria (how I know it's done)

1. Handles at least 12 of 15 eval queries correctly (right products, right filters, sensible response).
2. Multi-turn works: a follow-up refines the previous result without restating everything.
3. Asks a clarifying question on genuinely ambiguous queries instead of guessing.
4. Zero invented products across the eval set — every product shown exists in the catalog.
5. A stranger can clone the repo, read the README, and run it in under five minutes.

## Deliverables

- Public GitHub repo, README written as a product spec (architecture, decisions, how to run).
- A 60–90 second demo (recorded screen of the web UI).
- A short teardown post: *What conversational product discovery actually requires* — the three things that turned out harder than expected.

## Constraints

- ~3 weeks, part-time.
- Built spec-first (this file → PLAN.md → code), with CLAUDE.md as persistent project memory.
- Real catalog data, not hand-typed examples.
- Keep the dependency list short; this should run anywhere.
