# What Conversational Product Discovery Actually Requires

*A teardown of Project 1 — a single Claude agent that turns natural-language shopping intent into grounded product recommendations from a real catalog.*

---

I built a conversational product discovery agent in three weeks. One model, three tools, a 1,200-product apparel catalog, no embeddings, no vector database. It passes 15/15 eval queries including hard cases like "something for a rainy festival weekend" and "I want to look put-together without trying too hard."

Here's what turned out harder than expected — and what it taught me about where the real work in agentic commerce actually lives.

---

## 1. The system prompt is the product

I spent more time on 40 lines of system prompt than on the search and filtering code combined. That wasn't the plan.

The code is simple: load a JSON file, filter by field values, cap at 10 results, return slim records. The agent loop is about 30 lines. What took iteration was getting the model to reliably translate fuzzy human language into those filter fields.

The first version of the prompt said *"translate fuzzy language into catalog fields"* and listed a few examples. The agent did it about 60% of the time. The version that works says:

> *"warm", "cosy", "cold weather", "winter" → attributes.season = "Winter" or "Fall"; lean toward Sweaters, Sweatshirts, Jackets, Coats as the type*

Concrete. Directional. Named the target fields. Listed the item types to lean toward.

The lesson: with a tool-calling agent, your prompt is specifying an intent-parsing layer, not just setting a tone. Vague instructions produce vague mappings. You have to be as precise as a type system.

---

## 2. Over-clarification is the main failure mode — and it's subtle

My first eval run had a query that failed in a way I didn't predict: *"something warm and cosy, under £100, not black"* triggered a clarifying question. The agent asked "what type of item are you looking for?" instead of searching.

That query has a price constraint, a colour exclusion, and a season signal. It has enough to search. But the agent decided it wasn't ready.

The pattern kept appearing: any time a query didn't specify gender or exact item type, the agent withheld a search and asked. On the surface it looked polite and careful. In practice it was useless — customers don't want to be interrogated before seeing results.

The fix wasn't "be less cautious." It required explicit rules:

> *Never withhold a search because you don't know gender. Search all genders and present the results.*
>
> *If you can infer ANY of season, usage, or type from the query, search immediately.*

The interesting thing: the clarifying question behaviour is the right behaviour for truly ambiguous queries ("a gift", "something nice"). The problem is that models default to caution more broadly than you want. You have to draw a hard line between "you literally have nothing to filter on" and "you have partial signal — use it."

---

## 3. Two catalog fields do more work than the entire search algorithm

The catalog has nine fields: id, title, gender, category, subcategory, type, colour, season, usage, price.

`season` and `usage` are not in the source dataset the way I needed them. The original Kaggle data has them, but the mapping work — and more importantly, realising *these fields carry all the fuzzy intent* — was where the actual design insight lives.

Consider:

- *"something for a city break"* → `usage=Casual`
- *"for a job interview"* → `usage=Formal`
- *"warm and cosy"* → `season=Winter` or `season=Fall`
- *"festival weekend"* → `usage=Casual`, type=Jackets

Without `season` and `usage` as first-class filter fields, none of these queries work with keyword search. You'd need semantic search (embeddings, vector retrieval) to handle "warm" matching "Winter" and "Formal" matching "job interview." With these fields, a deterministic string filter works every time.

This is the most transferable finding: before you reach for embeddings, ask whether your catalog schema is doing enough work. A well-designed field can replace retrieval sophistication. In this project, two fields replaced a vector database.

---

## What this means for the next project

Project 2 will add semantic search — embeddings over product titles and descriptions. The interesting question is not "does it work better?" It's "for which queries does it change anything?" My prediction: queries where the exact season and usage are unclear (e.g. "cosy festival outerwear" vs. "warm festival gear"), semantic search will outperform the filter approach. For queries where the mapping is clear ("blue jacket under £100"), it won't matter.

The eval set from this project becomes the baseline. Any query that currently passes via keyword + attribute filtering should still pass. The new layer should only improve the ones that relied on the agent to do the mapping in the prompt.

---

*Project 1 source: [github link] | Built with Claude claude-sonnet-4-6, Python, Streamlit*
