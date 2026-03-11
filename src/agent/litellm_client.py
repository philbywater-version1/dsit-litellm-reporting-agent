"""
HTTP client for the LiteLLM proxy REST API.

Wraps the spend/usage endpoints. All methods return parsed dicts or lists
ready to be handed back to Claude as tool results.
"""
from __future__ import annotations

import os
from typing import Any

import httpx


class LiteLLMClient:
    def __init__(self, base_url: str | None = None, api_key: str | None = None):
        self.base_url = (base_url or os.environ["LITELLM_BASE_URL"]).rstrip("/")
        self.api_key = api_key or os.environ["LITELLM_API_KEY"]
        self._client = httpx.Client(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )

    def _get(self, path: str, params: dict | None = None) -> Any:
        response = self._client.get(path, params=params)
        response.raise_for_status()
        return response.json()

    # ------------------------------------------------------------------ #
    # Spend / usage endpoints                                              #
    # ------------------------------------------------------------------ #

    def get_spend_logs(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
        api_key: str | None = None,
        user_id: str | None = None,
        limit: int = 100,
    ) -> list[dict]:
        """Return raw spend log entries, optionally filtered."""
        params: dict = {"limit": limit}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        if api_key:
            params["api_key"] = api_key
        if user_id:
            params["user_id"] = user_id
        return self._get("/spend/logs", params=params)

    def get_spend_by_user(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> list[dict]:
        """Return spend totals grouped by user."""
        params: dict = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        return self._get("/spend/users", params=params)

    def get_spend_by_key(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> list[dict]:
        """Return spend totals grouped by API key."""
        params: dict = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        return self._get("/spend/keys", params=params)

    def get_spend_by_tag(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> list[dict]:
        """Return spend totals grouped by request tag."""
        params: dict = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        return self._get("/spend/tags", params=params)

    def get_global_spend(self) -> dict:
        """Return the global spend summary for the current period."""
        return self._get("/global/spend")

    def get_global_spend_report(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> dict:
        """Return an aggregate spend report (top models, users, keys)."""
        params: dict = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        return self._get("/global/spend/report", params=params)

    def get_spend_by_team(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> list[dict]:
        """Return spend totals grouped by team."""
        params: dict = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        return self._get("/global/spend/teams", params=params)

    def get_model_list(self) -> list[dict]:
        """Return the list of models configured on the proxy."""
        return self._get("/models")

    # ------------------------------------------------------------------ #
    # User / key / team detail endpoints                                   #
    # ------------------------------------------------------------------ #

    def get_user_info(self, user_id: str) -> dict:
        """Return detailed info for a user: spend, keys, rate limits, budget."""
        return self._get("/user/info", params={"user_id": user_id})

    def get_user_daily_activity(
        self,
        user_id: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> dict:
        """Return daily usage broken down by model, provider, and API key."""
        params: dict = {}
        if user_id:
            params["user_id"] = user_id
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        return self._get("/user/daily/activity", params=params)

    def get_key_info(self, key: str) -> dict:
        """Return spend, expiry, assigned models, and remaining budget for a key."""
        return self._get("/key/info", params={"key": key})

    def get_team_info(self, team_id: str) -> dict:
        """Return team spend, budget cap, remaining budget, and members."""
        return self._get("/team/info", params={"team_id": team_id})

    def get_customer_info(self, customer_id: str) -> dict:
        """Return spend and budget info for an external end-user/customer."""
        return self._get("/customer/info", params={"end_user_id": customer_id})

    # ------------------------------------------------------------------ #
    # Prometheus metrics                                                   #
    # ------------------------------------------------------------------ #

    def get_prometheus_metrics(self) -> dict:
        """Return parsed Prometheus metrics (latency, errors, budgets, health)."""
        response = self._client.get("/metrics")
        response.raise_for_status()
        return {"raw": response.text}

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "LiteLLMClient":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
