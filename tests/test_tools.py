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


def test_get_user_info():
    client = make_client(get_user_info={"user_id": "alice", "spend": 2.50, "max_budget": 10.0})
    result = json.loads(dispatch_tool("get_user_info", {"user_id": "alice"}, client))
    assert result["user_id"] == "alice"
    client.get_user_info.assert_called_once_with(user_id="alice")


def test_get_user_daily_activity_passes_filters():
    client = make_client(get_user_daily_activity={"data": []})
    dispatch_tool(
        "get_user_daily_activity",
        {"user_id": "alice", "start_date": "2024-01-01", "end_date": "2024-01-31"},
        client,
    )
    client.get_user_daily_activity.assert_called_once_with(
        user_id="alice",
        start_date="2024-01-01",
        end_date="2024-01-31",
    )


def test_get_user_daily_activity_no_filters():
    client = make_client(get_user_daily_activity={"data": []})
    dispatch_tool("get_user_daily_activity", {}, client)
    client.get_user_daily_activity.assert_called_once_with(
        user_id=None,
        start_date=None,
        end_date=None,
    )


def test_get_key_info():
    client = make_client(get_key_info={"key": "sk-abc", "spend": 0.75, "expires": "2025-12-31"})
    result = json.loads(dispatch_tool("get_key_info", {"key": "sk-abc"}, client))
    assert result["key"] == "sk-abc"
    client.get_key_info.assert_called_once_with(key="sk-abc")


def test_get_team_info():
    client = make_client(get_team_info={"team_id": "eng", "spend": 5.0, "max_budget": 50.0})
    result = json.loads(dispatch_tool("get_team_info", {"team_id": "eng"}, client))
    assert result["team_id"] == "eng"
    client.get_team_info.assert_called_once_with(team_id="eng")


def test_get_customer_info():
    client = make_client(get_customer_info={"end_user_id": "cust-1", "spend": 1.10})
    result = json.loads(dispatch_tool("get_customer_info", {"customer_id": "cust-1"}, client))
    assert result["end_user_id"] == "cust-1"
    client.get_customer_info.assert_called_once_with(customer_id="cust-1")


def test_get_prometheus_metrics():
    client = make_client(get_prometheus_metrics={"raw": "# HELP litellm_spend_metric\n..."})
    result = json.loads(dispatch_tool("get_prometheus_metrics", {}, client))
    assert "raw" in result
    client.get_prometheus_metrics.assert_called_once()


def test_dispatch_unknown_tool_returns_error():
    client = MagicMock()
    result = json.loads(dispatch_tool("nonexistent_tool", {}, client))
    assert "error" in result
