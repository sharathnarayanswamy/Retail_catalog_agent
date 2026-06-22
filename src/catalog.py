"""
In-memory catalog store and deterministic filter functions.
The agent never sees the raw catalog — only results returned by these functions.
"""

import json
from pathlib import Path


def load_catalog(path: str = "data/catalog.json") -> list[dict]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(
            f"{p} not found. Run `python data/prepare_catalog.py` first."
        )
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def _slim(product: dict) -> dict:
    return {k: product[k] for k in ("id", "title", "price", "type", "colour", "season", "usage", "gender")}


def search_catalog(
    catalog: list[dict],
    category: str | None = None,
    keywords: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    attributes: dict | None = None,
    exclude: list[dict] | None = None,
) -> list[dict]:
    """Filter catalog and return up to 10 slim product records."""
    results = catalog

    if category:
        cat_lower = category.lower()
        results = [
            p for p in results
            if (p["category"].lower() == cat_lower
                or p["subcategory"].lower() == cat_lower
                or p["type"].lower() == cat_lower)
        ]

    if keywords:
        words = keywords.lower().split()
        results = [
            p for p in results
            if all(w in (p["title"] + " " + p["type"]).lower() for w in words)
        ]

    if min_price is not None:
        results = [p for p in results if p["price"] >= min_price]

    if max_price is not None:
        results = [p for p in results if p["price"] <= max_price]

    if attributes:
        for key, value in attributes.items():
            val_lower = str(value).lower()
            results = [p for p in results if p.get(key, "").lower() == val_lower]

    if exclude:
        for ex in exclude:
            field = ex.get("field", "")
            val_lower = ex.get("value", "").lower()
            if field:
                results = [p for p in results if p.get(field, "").lower() != val_lower]

    return [_slim(p) for p in results[:10]]


def get_product_details(catalog: list[dict], product_id: str) -> dict | None:
    for p in catalog:
        if p["id"] == product_id:
            return p
    return None


def list_categories(catalog: list[dict]) -> dict:
    return {
        "categories": sorted({p["category"] for p in catalog}),
        "subcategories": sorted({p["subcategory"] for p in catalog}),
        "types": sorted({p["type"] for p in catalog}),
        "colours": sorted({p["colour"] for p in catalog}),
        "seasons": sorted({p["season"] for p in catalog}),
        "usages": sorted({p["usage"] for p in catalog}),
        "genders": sorted({p["gender"] for p in catalog}),
        "price_range": {
            "min": min(p["price"] for p in catalog),
            "max": max(p["price"] for p in catalog),
        },
    }
