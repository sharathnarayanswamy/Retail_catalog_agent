"""
Runs all queries from queries.jsonl through a fresh agent instance and prints
the conversation for eyeballing. No automated scoring — that's Project 3.

Usage:
    python evals/run_evals.py [--band easy|medium|hard|ambiguous]
"""

import sys
import json
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.catalog import load_catalog
from src.agent import Agent

QUERIES_PATH = Path(__file__).parent / "queries.jsonl"
DIVIDER = "=" * 70
SEPARATOR = "-" * 70


def load_queries(band: str | None = None) -> list[dict]:
    with open(QUERIES_PATH, encoding="utf-8") as f:
        queries = [json.loads(line) for line in f if line.strip()]
    if band:
        queries = [q for q in queries if q.get("band") == band]
    return queries


def run(queries: list[dict], catalog: list[dict]) -> None:
    total = len(queries)
    print(f"\nRunning {total} eval quer{'y' if total == 1 else 'ies'}...\n")
    print(DIVIDER)

    for i, item in enumerate(queries, 1):
        band = item.get("band", "?")
        query = item["query"]
        expected = item.get("expected", "")

        agent = Agent(catalog)
        response = agent.chat(query)

        print(f"[{i}/{total}] [{band.upper()}]  {query}")
        print(f"Expected: {expected}")
        print(f"\nResponse:\n{response}")
        print(SEPARATOR)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run product discovery evals.")
    parser.add_argument(
        "--band",
        choices=["easy", "medium", "hard", "ambiguous"],
        default=None,
        help="Run only queries in this difficulty band.",
    )
    args = parser.parse_args()

    print("Loading catalog...", flush=True)
    try:
        catalog = load_catalog()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)

    queries = load_queries(args.band)
    if not queries:
        print("No queries matched.")
        sys.exit(0)

    run(queries, catalog)


if __name__ == "__main__":
    main()
