"""
Tool definitions (Anthropic API format) and executors.
The agent calls these; they run against the in-memory catalog.
"""

import json
from src.catalog import search_catalog, get_product_details, list_categories

TOOL_DEFINITIONS: list[dict] = [
    {
        "name": "search_catalog",
        "description": (
            "Search the apparel and footwear catalog. Returns up to 10 matching products. "
            "Use attributes.season for warmth/weather intent and attributes.usage for occasion intent."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": (
                        "Filter by category, subcategory, or article type. "
                        "Examples: 'Apparel', 'Footwear', 'Topwear', 'Bottomwear', "
                        "'Shirts', 'Jeans', 'Jackets', 'Casual Shoes'."
                    ),
                },
                "keywords": {
                    "type": "string",
                    "description": "Free-text search over product title and type. Use for style or name keywords.",
                },
                "min_price": {
                    "type": "number",
                    "description": "Minimum price in GBP (£).",
                },
                "max_price": {
                    "type": "number",
                    "description": "Maximum price in GBP (£).",
                },
                "attributes": {
                    "type": "object",
                    "description": "Structured attribute filters.",
                    "properties": {
                        "colour": {
                            "type": "string",
                            "description": "Product colour, e.g. 'Blue', 'Black', 'Navy Blue', 'White'.",
                        },
                        "season": {
                            "type": "string",
                            "description": (
                                "Season the product is suited for: Summer, Winter, Fall, or Spring. "
                                "Map 'warm'/'cosy'/'winter' → Winter or Fall. "
                                "Map 'light'/'summer'/'hot' → Summer or Spring."
                            ),
                        },
                        "usage": {
                            "type": "string",
                            "description": (
                                "Occasion/usage type: Casual, Formal, Sports, or Ethnic. "
                                "Map 'city break'/'everyday'/'relaxed' → Casual. "
                                "Map 'work'/'office'/'smart' → Formal. "
                                "Map 'gym'/'running'/'active' → Sports."
                            ),
                        },
                        "gender": {
                            "type": "string",
                            "description": "Gender: Men, Women, Boys, Girls, or Unisex.",
                        },
                        "type": {
                            "type": "string",
                            "description": "Exact article type, e.g. 'Shirts', 'Jeans', 'Jackets', 'Boots'.",
                        },
                    },
                },
                "exclude": {
                    "type": "array",
                    "description": "List of field/value pairs to exclude from results.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "field": {
                                "type": "string",
                                "description": "Field to filter on: colour, season, usage, gender, or type.",
                            },
                            "value": {
                                "type": "string",
                                "description": "Value to exclude, e.g. 'Black'.",
                            },
                        },
                        "required": ["field", "value"],
                    },
                },
            },
        },
    },
    {
        "name": "get_product_details",
        "description": "Get the full record for a specific product by its ID.",
        "input_schema": {
            "type": "object",
            "properties": {
                "product_id": {
                    "type": "string",
                    "description": "Product ID returned from search_catalog.",
                },
            },
            "required": ["product_id"],
        },
    },
    {
        "name": "list_categories",
        "description": (
            "Return all available filter values in the catalog: categories, subcategories, "
            "article types, colours, seasons, usages, and genders. "
            "Call this when unsure which values exist before filtering."
        ),
        "input_schema": {
            "type": "object",
            "properties": {},
        },
    },
]


def execute_tool(catalog: list[dict], name: str, inputs: dict) -> object:
    if name == "search_catalog":
        return search_catalog(catalog, **inputs)
    if name == "get_product_details":
        return get_product_details(catalog, inputs["product_id"])
    if name == "list_categories":
        return list_categories(catalog)
    return {"error": f"Unknown tool: {name}"}
