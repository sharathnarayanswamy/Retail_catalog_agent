"""
Converts styles.csv (Kaggle: paramaggarwal/fashion-product-images-small)
into data/catalog.json (~1,200 clean SKUs).

Usage:
    python data/prepare_catalog.py

Place styles.csv in the same directory (data/) before running.
"""

import csv
import json
import random
from pathlib import Path

PRICE_RANGES: dict[str, tuple[int, int]] = {
    "Tshirts": (12, 30),
    "Shirts": (25, 55),
    "Sweaters": (30, 70),
    "Sweatshirts": (30, 70),
    "Jackets": (60, 160),
    "Windcheater": (40, 90),
    "Coats": (60, 160),
    "Jeans": (40, 90),
    "Trousers": (30, 75),
    "Track Pants": (25, 60),
    "Shorts": (15, 40),
    "Skirts": (20, 55),
    "Dresses": (35, 90),
    "Tops": (15, 45),
    "Kurtas": (25, 65),
    "Leggings": (15, 40),
    "Casual Shoes": (45, 130),
    "Sports Shoes": (45, 130),
    "Formal Shoes": (55, 130),
    "Sandals": (25, 80),
    "Flats": (25, 70),
    "Heels": (35, 100),
    "Flip Flops": (10, 30),
    "Boots": (60, 150),
    "Loafers": (40, 100),
    "Sneakers": (40, 120),
}
DEFAULT_PRICE = (20, 60)

KEEP_CATEGORIES = {"Apparel", "Footwear"}
REQUIRED_FIELDS = {"baseColour", "season", "usage", "articleType", "productDisplayName"}
TARGET_SIZE = 1200


def assign_price(article_type: str, rng: random.Random) -> int:
    lo, hi = PRICE_RANGES.get(article_type, DEFAULT_PRICE)
    return round(rng.uniform(lo, hi))


def main() -> None:
    rng = random.Random(42)
    src = Path(__file__).parent / "styles.csv"
    dst = Path(__file__).parent / "catalog.json"

    if not src.exists():
        raise FileNotFoundError(
            f"{src} not found.\n"
            "Download styles.csv from:\n"
            "  https://www.kaggle.com/datasets/paramaggarwal/fashion-product-images-small\n"
            "and place it in the data/ directory."
        )

    records: list[dict] = []
    with open(src, encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("masterCategory") not in KEEP_CATEGORIES:
                continue
            if any(not (row.get(field) or "").strip() for field in REQUIRED_FIELDS):
                continue
            records.append(row)

    rng.shuffle(records)
    records = records[:TARGET_SIZE]

    catalog: list[dict] = []
    for row in records:
        article_type = row["articleType"].strip()
        catalog.append({
            "id": row["id"].strip(),
            "title": row["productDisplayName"].strip(),
            "gender": row["gender"].strip(),
            "category": row["masterCategory"].strip(),
            "subcategory": row["subCategory"].strip(),
            "type": article_type,
            "colour": row["baseColour"].strip(),
            "season": row["season"].strip(),
            "usage": row["usage"].strip(),
            "price": assign_price(article_type, rng),
        })

    with open(dst, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)

    type_counts = {}
    for p in catalog:
        type_counts[p["type"]] = type_counts.get(p["type"], 0) + 1

    print(f"Written {len(catalog)} records to {dst}")
    print(f"\nTop article types:")
    for t, n in sorted(type_counts.items(), key=lambda x: -x[1])[:10]:
        print(f"  {t}: {n}")


if __name__ == "__main__":
    main()
