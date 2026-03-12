# DSIT LiteLLM Reporting Agent

A Claude-powered CLI agent that answers natural-language questions about [LiteLLM](https://github.com/BerriAI/litellm) proxy usage. Ask questions in plain English and get spend reports, usage breakdowns, and metrics — sourced directly from your LiteLLM proxy.

## How It Works

```
User question → Claude (with thinking) → Tool dispatcher → LiteLLM REST API → Answer
```

The agent runs a streaming agentic loop: Claude reads your question, decides which LiteLLM API endpoints to call, retrieves the data, and synthesises a response. It can call multiple tools in sequence and save reports to disk.

## Requirements

- Python 3.11+
- [`uv`](https://docs.astral.sh/uv/) package manager
- A running LiteLLM proxy instance
- An Anthropic API key

## Installation

```bash
git clone <repo-url>
cd dsit-litellm-reporting-agent
uv sync
```

## Configuration

Copy `.env.example` to `.env` and fill in the required values:

```bash
cp .env.example .env
```

| Variable | Required | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | Yes | Anthropic API key |
| `LITELLM_BASE_URL` | Yes | LiteLLM proxy URL, e.g. `http://localhost:4000` |
| `LITELLM_API_KEY` | Yes | LiteLLM API key with spend-read permissions |
| `ANTHROPIC_BASE_URL` | No | Proxy URL for Anthropic (if using an intermediary) |
| `ANTHROPIC_MODEL` | No | Model ID (default: `eu.anthropic.claude-sonnet-4-6`) |
| `REPORT_FORMAT` | No | Output format: `table`, `json`, or `markdown` |
| `OUTPUT_DIR` | No | Directory for saved reports (default: `./output`) |

## Usage

Pass your question as a positional argument:

```bash
uv run litellm-agent "What is the total spend this month?"
```

Or pipe it from stdin:

```bash
echo "Show me spend by user for the last 7 days" | uv run litellm-agent
```

### Example Prompts

```bash
uv run litellm-agent "What is the global spend so far this month?"
uv run litellm-agent "Which users have spent the most in March 2026?"
uv run litellm-agent "Show me daily activity for user alice@example.com"
uv run litellm-agent "What models are configured on the proxy?"
uv run litellm-agent "Are there any errors showing in the Prometheus metrics?"
uv run litellm-agent "Save a CSV of spend by team for Q1 2026"
```

## Available Tools

The agent has access to the following LiteLLM API tools:

| Tool | Description |
|---|---|
| `get_global_spend` | Total spend and tokens for the current period |
| `get_global_spend_report` | Aggregate breakdown by model, user, and key |
| `get_spend_logs` | Raw filterable spend log entries |
| `get_spend_by_user` | Spend totals grouped by user |
| `get_spend_by_key` | Spend totals grouped by API key |
| `get_spend_by_tag` | Spend totals grouped by tag |
| `get_spend_by_team` | Spend totals grouped by team |
| `get_model_list` | Models configured on the proxy |
| `get_user_info` | Per-user spend, budget, and keys |
| `get_user_daily_activity` | Daily usage breakdown by model/provider/key |
| `get_key_info` | Per-key spend, expiry, and budget |
| `get_team_info` | Team budget and member details |
| `get_customer_info` | External end-user tracking data |
| `get_prometheus_metrics` | Latency, errors, health, and in-flight requests |
| `write_file` | Save a report as CSV or JSON to `./output/` |

## Project Structure

```
.
├── src/agent/
│   ├── main.py             # CLI entry point
│   ├── agent.py            # Streaming agentic loop
│   ├── tools.py            # Tool schemas and dispatcher
│   └── litellm_client.py   # httpx wrapper for LiteLLM API
├── tests/
│   └── test_tools.py       # Unit tests (mocked client)
├── output/                 # Generated report files
├── .env.example            # Environment variable template
├── pyproject.toml          # Project metadata and dependencies
└── SKILL.md                # Developer reference and architecture guide
```

## Running Tests

```bash
uv run pytest
```

## Extending the Agent

To add support for a new LiteLLM endpoint:

1. Add a method to `LiteLLMClient` in `src/agent/litellm_client.py`
2. Add a tool schema entry to `TOOLS` in `src/agent/tools.py`
3. Add a dispatch branch in `_execute()` in `src/agent/tools.py`
4. Add a test in `tests/test_tools.py`

See `SKILL.md` for a full developer reference.

## Dependencies

- [`anthropic`](https://pypi.org/project/anthropic/) — Anthropic SDK for Claude
- [`httpx`](https://www.python-httpx.org/) — Async-capable HTTP client
- [`python-dotenv`](https://pypi.org/project/python-dotenv/) — `.env` file loading
- [`rich`](https://rich.readthedocs.io/) — Console output formatting
