"""Unit tests for the tool dispatcher, using a mocked LiteLLMClient."""
import json
from unittest.mock import MagicMock

from agent.tools import dispatch_tool


def make_client(**method_returns: object) -> MagicMock:
    client = MagicMock()
    for method, return_value in method_returns.items():
        getattr(client, method).return_value = return_value
    return client


def test_get_global_spend():
    client = make_client(get_global_spend={"total_cost": 1.23, "total_tokens": 5000})
    result = json.loads(dispatch_tool("get_global_spend", {}, client))
    assert result["total_cost"] == 1.23


def test_get_spend_logs_passes_filters():
    client = make_client(get_spend_logs=[{"id": "abc"}])
    dispatch_tool(
        "get_spend_logs",
        {"start_date": "2024-01-01", "end_date": "2024-01-31", "limit": 50},
        client,
    )
    client.get_spend_logs.assert_called_once_with(
        start_date="2024-01-01",
        end_date="2024-01-31",
        api_key=None,
        user_id=None,
        limit=50,
    )


def test_dispatch_unknown_tool_returns_error():
    client = MagicMock()
    result = json.loads(dispatch_tool("nonexistent_tool", {}, client))
    assert "error" in result
