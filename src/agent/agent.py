"""
Claude agentic loop for LiteLLM usage reporting.

Runs a manual tool-use loop so we have full control over streaming,
logging, and error handling.
"""
from __future__ import annotations

import os
from datetime import date
from typing import Iterator

import anthropic
from rich.console import Console

from agent.litellm_client import LiteLLMClient
from agent.tools import TOOLS, dispatch_tool

_SYSTEM_PROMPT_TEMPLATE = """\
You are a LiteLLM usage and spend analyst. You have access to tools that \
query a LiteLLM proxy's REST API to retrieve application usage data, spend \
logs, and cost breakdowns.

Today's date is {today}. When the user refers to "this month", "current month", \
or similar, use the first day of the current calendar month as start_date and \
today's date as end_date.

When the user asks a question, use the available tools to fetch the relevant \
data, then summarise the findings clearly. Always present numbers with \
appropriate units (tokens, USD, requests). When showing tabular data, use \
Markdown tables. If a date range is not specified, retrieve the current \
period's data.

Be concise but thorough. If the data suggests anomalies or notable trends, \
highlight them.
"""


def _build_system_prompt() -> str:
    return _SYSTEM_PROMPT_TEMPLATE.format(today=date.today().isoformat())

MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-opus-4-6")

console = Console()


def run(prompt: str) -> None:
    """Run the agent loop for a single user prompt, streaming output to stdout."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError("ANTHROPIC_API_KEY is not set.")

    base_url = os.environ.get("ANTHROPIC_BASE_URL")
    client = anthropic.Anthropic(api_key=api_key, base_url=base_url) if base_url else anthropic.Anthropic(api_key=api_key)
    litellm = LiteLLMClient()

    messages: list[dict] = [{"role": "user", "content": prompt}]

    with litellm:
        while True:
            # Stream the response so we get text in real time
            with client.messages.stream(
                model=MODEL,
                max_tokens=4096,
                system=_build_system_prompt(),
                tools=TOOLS,  # type: ignore[arg-type]
                messages=messages,  # type: ignore[arg-type]
                thinking={"type": "adaptive"},
            ) as stream:
                for text in stream.text_stream:
                    console.print(text, end="", markup=False, highlight=False)

                response = stream.get_final_message()

            # Append assistant response to history.
            # Explicitly convert SDK objects to plain dicts so LiteLLM's
            # message validation doesn't choke on internal SDK fields (e.g. `caller`).
            content: list[dict] = []
            for block in response.content:
                if block.type == "thinking":
                    content.append(
                        {"type": "thinking", "thinking": block.thinking, "signature": block.signature}
                    )
                elif block.type == "text":
                    content.append({"type": "text", "text": block.text})
                elif block.type == "tool_use":
                    content.append(
                        {"type": "tool_use", "id": block.id, "name": block.name, "input": block.input}
                    )
            messages.append({"role": "assistant", "content": content})

            if response.stop_reason == "end_turn":
                console.print()  # trailing newline
                break

            if response.stop_reason != "tool_use":
                # Unexpected stop — surface it and exit
                console.print(f"\n[yellow]Stopped: {response.stop_reason}[/yellow]")
                break

            # Execute tool calls and collect results
            tool_results = []
            for block in response.content:
                if block.type != "tool_use":
                    continue

                console.print(
                    f"\n[dim]→ calling tool: {block.name}({block.input})[/dim]"
                )

                result_str = dispatch_tool(block.name, block.input, litellm)
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result_str,
                    }
                )

            messages.append({"role": "user", "content": tool_results})
