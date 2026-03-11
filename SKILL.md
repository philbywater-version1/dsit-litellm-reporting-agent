# DSIT LiteLLM Reporting Agent — Skill Orchestration

This file defines the tasks, prompts, and development workflow for the
LiteLLM reporting agent. Use it as the canonical reference when extending
or maintaining the project.

---

## Project Overview

A Claude Opus-powered agentic loop that answers natural-language questions
about LiteLLM proxy usage by calling the LiteLLM REST API.

```
User question
     │
     ▼
 Claude (claude-opus-4-6)
     │  ← tool schemas from tools.py
     ▼
 Tool dispatcher (tools.py)
     │  ← HTTP calls
     ▼
 LiteLLMClient (litellm_client.py)
     │  ← REST API
     ▼
 LiteLLM proxy (LITELLM_BASE_URL)
```

---

## Quick Start

```bash
# 1. Install dependencies (uv recommended)
uv venv && uv pip install -e ".[dev]"

# 2. Copy and fill in env vars
cp .env.example .env

# 3. Run the agent
uv run litellm-agent "What is the total spend so far this month?"

# Or pipe a prompt
echo "Show me spend by user for the last 7 days" | uv run litellm-agent
```

---

## Key Files

| File | Purpose |
|------|---------|
| `src/agent/main.py` | CLI entry point; loads `.env`, dispatches to `agent.run()` |
| `src/agent/agent.py` | Claude agentic loop (streaming, tool-use, message history) |
| `src/agent/tools.py` | Tool schemas (for Claude) + dispatcher (calls `LiteLLMClient`) |
| `src/agent/litellm_client.py` | `httpx`-based HTTP client wrapping LiteLLM spend endpoints |
| `tests/test_tools.py` | Unit tests for the tool dispatcher |
| `.env.example` | Required environment variables |

---

## Development Tasks

### Task: Add a new LiteLLM endpoint

1. Add a method to `LiteLLMClient` in `litellm_client.py`
2. Add a tool schema entry to `TOOLS` in `tools.py`
3. Add a dispatch branch in `_execute()` in `tools.py`
4. Add a test in `tests/test_tools.py`

### Task: Change the Claude model or system prompt

Edit `MODEL` and `SYSTEM_PROMPT` at the top of `src/agent/agent.py`.

### Task: Run tests

```bash
uv run pytest
```

### Task: Add structured report output

Extend `agent.py` to write the final assistant message to a file. Pass
`--output report.md` as a CLI flag, parsed in `main.py`.

---

## Available Tools (what Claude can call)

| Tool | Description |
|------|-------------|
| `get_global_spend` | Total spend/tokens for the current period |
| `get_global_spend_report` | Aggregate breakdown by model, user, key |
| `get_spend_logs` | Raw spend log entries (filterable by date, user, key) |
| `get_spend_by_user` | Spend totals grouped by user |
| `get_spend_by_key` | Spend totals grouped by API key |
| `get_spend_by_tag` | Spend totals grouped by request tag |
| `get_spend_by_team` | Spend totals grouped by team |
| `get_model_list` | List configured models on the proxy |
| `get_user_info` | Per-user spend, budget cap, remaining budget, assigned keys |
| `get_user_daily_activity` |  Day-by-day usage by model/provider — enables trend queries |
| `get_key_info` | Per-key spend, assigned user, recent activity |  
| `get_team_info` | Team budget cap, spend, remaining, member list |
| `get_customer_info` | External end-user/customer spend tracking | 
| `get_prometheus_metrics` | Latency, error rates, deployment health, in-flight requests |
    


---

## Example Prompts

```
# Summary
"Give me a spend summary for this month."

# Top spenders
"Which users have spent the most in the last 30 days?"

# Model breakdown
"Show me a breakdown of token usage by model."

# Anomaly detection
"Are there any unusual spikes in spend in the last week?"

# Key audit
"List all API keys and their total spend."
```

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | Yes | Anthropic API key |
| `LITELLM_BASE_URL` | Yes | LiteLLM proxy URL, e.g. `http://localhost:4000` |
| `LITELLM_API_KEY` | Yes | LiteLLM key with spend-read permissions |
| `REPORT_FORMAT` | No | `table` \| `json` \| `markdown` (default: `table`) |
