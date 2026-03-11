"""Entry point — parse CLI args and run the agent."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv

# Load .env from the project root (two levels up from this file)
_ROOT = Path(__file__).parent.parent.parent
load_dotenv(_ROOT / ".env")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="litellm-agent",
        description="Ask questions about LiteLLM usage and spend via a Claude AI agent.",
    )
    parser.add_argument(
        "prompt",
        nargs="?",
        help="Question or request for the agent. If omitted, reads from stdin.",
    )
    args = parser.parse_args()

    if args.prompt:
        prompt = args.prompt
    elif not sys.stdin.isatty():
        prompt = sys.stdin.read().strip()
    else:
        parser.print_help()
        sys.exit(1)

    # Import here so dotenv loads before any env-dependent imports
    from agent.agent import run

    run(prompt)


if __name__ == "__main__":
    main()
