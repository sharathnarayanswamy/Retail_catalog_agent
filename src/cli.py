"""
Terminal chat interface. Run from the project root:
    python src/cli.py

Commands:
    reset   — start a new conversation
    quit    — exit
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.catalog import load_catalog
from src.agent import Agent


def main() -> None:
    print("Loading catalog...", flush=True)
    try:
        catalog = load_catalog()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)

    agent = Agent(catalog)
    print(
        f"Ready — {len(catalog)} products loaded.\n"
        "Type 'reset' to start a new conversation, 'quit' to exit.\n"
    )

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit"):
            print("Goodbye!")
            break
        if user_input.lower() == "reset":
            agent.reset()
            print("Conversation reset.\n")
            continue

        response = agent.chat(user_input)
        print(f"\nAssistant: {response}\n")


if __name__ == "__main__":
    main()
