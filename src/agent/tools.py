"""
Tool definitions and dispatcher for the Claude agent.

Each tool wraps one or more LiteLLMClient methods and returns a plain-text
or JSON string that Claude can reason over.
"""
from __future__ import annotations

import json
from typing import Any

from agent.litellm_client import LiteLLMClient

# ------------------------------------------------------------------ #
# Tool schema definitions (passed to Claude's API)                    #
# ------------------------------------------------------------------ #

TOOLS: list[dict] = [
    {
        "name": "get_global_spend",
        "description": (
            "Fetch the global spend summary for the current billing period. "
            "Returns total cost, total tokens, and request count."
        ),
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_global_spend_report",
        "description": (
            "Fetch an aggregate spend report showing top models, users, and keys. "
            "Optionally filter by date range (YYYY-MM-DD)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "start_date": {
                    "type": "string",
                    "description": "Start date in YYYY-MM-DD format (inclusive).",
                },
                "end_date": {
                    "type": "string",
                    "description": "End date in YYYY-MM-DD format (inclusive).",
                },
            },
            "required": [],
        },
    },
    {
        "name": "get_spend_logs",
        "description": (
            "Fetch raw spend log entries. Optionally filter by date range, "
            "user ID, or API key. Returns a list of log records."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "start_date": {"type": "string", "description": "YYYY-MM-DD"},
                "end_date": {"type": "string", "description": "YYYY-MM-DD"},
                "user_id": {"type": "string", "description": "Filter by user ID."},
                "api_key": {"type": "string", "description": "Filter by API key."},
                "limit": {
                    "type": "integer",
                    "description": "Max records to return (default 100).",
                    "default": 100,
                },
            },
            "required": [],
        },
    },
    {
        "name": "get_spend_by_user",
        "description": "Fetch spend totals grouped by user. Optionally filter by date range.",
        "input_schema": {
            "type": "object",
            "properties": {
                "start_date": {"type": "string", "description": "YYYY-MM-DD"},
                "end_date": {"type": "string", "description": "YYYY-MM-DD"},
            },
            "required": [],
        },
    },
    {
        "name": "get_spend_by_key",
        "description": "Fetch spend totals grouped by API key. Optionally filter by date range.",
        "input_schema": {
            "type": "object",
            "properties": {
                "start_date": {"type": "string", "description": "YYYY-MM-DD"},
                "end_date": {"type": "string", "description": "YYYY-MM-DD"},
            },
            "required": [],
        },
    },
    {
        "name": "get_spend_by_tag",
        "description": "Fetch spend totals grouped by request tag. Optionally filter by date range.",
        "input_schema": {
            "type": "object",
            "properties": {
                "start_date": {"type": "string", "description": "YYYY-MM-DD"},
                "end_date": {"type": "string", "description": "YYYY-MM-DD"},
            },
            "required": [],
        },
    },
    {
        "name": "get_spend_by_team",
        "description": "Fetch spend totals grouped by team. Optionally filter by date range.",
        "input_schema": {
            "type": "object",
            "properties": {
                "start_date": {"type": "string", "description": "YYYY-MM-DD"},
                "end_date": {"type": "string", "description": "YYYY-MM-DD"},
            },
            "required": [],
        },
    },
    {
        "name": "get_model_list",
        "description": "List all models currently configured on the LiteLLM proxy.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
]


# ------------------------------------------------------------------ #
# Tool dispatcher                                                     #
# ------------------------------------------------------------------ #

def dispatch_tool(name: str, tool_input: dict[str, Any], client: LiteLLMClient) -> str:
    """Execute a tool call and return the result as a JSON string."""
    try:
        result = _execute(name, tool_input, client)
        return json.dumps(result, indent=2, default=str)
    except Exception as exc:
        return json.dumps({"error": str(exc)})


def _execute(name: str, inp: dict[str, Any], client: LiteLLMClient) -> Any:
    if name == "get_global_spend":
        return client.get_global_spend()

    if name == "get_global_spend_report":
        return client.get_global_spend_report(
            start_date=inp.get("start_date"),
            end_date=inp.get("end_date"),
        )

    if name == "get_spend_logs":
        return client.get_spend_logs(
            start_date=inp.get("start_date"),
            end_date=inp.get("end_date"),
            api_key=inp.get("api_key"),
            user_id=inp.get("user_id"),
            limit=inp.get("limit", 100),
        )

    if name == "get_spend_by_user":
        return client.get_spend_by_user(
            start_date=inp.get("start_date"),
            end_date=inp.get("end_date"),
        )

    if name == "get_spend_by_key":
        return client.get_spend_by_key(
            start_date=inp.get("start_date"),
            end_date=inp.get("end_date"),
        )

    if name == "get_spend_by_tag":
        return client.get_spend_by_tag(
            start_date=inp.get("start_date"),
            end_date=inp.get("end_date"),
        )

    if name == "get_spend_by_team":
        return client.get_spend_by_team(
            start_date=inp.get("start_date"),
            end_date=inp.get("end_date"),
        )

    if name == "get_model_list":
        return client.get_model_list()

    raise ValueError(f"Unknown tool: {name}")
