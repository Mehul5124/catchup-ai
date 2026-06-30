"""
mcp_server.py – CatchUp AI MCP Server

Exposes three tools:
  - get_unread_slack   : Fetch Slack messages from mock data
  - get_unread_emails  : Fetch unread emails from mock data
  - get_recent_docs    : Fetch recent documents with comments
"""

import json
import sys
import io
from pathlib import Path

# Force UTF-8 output on Windows so emoji/unicode characters don't crash
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if sys.stderr.encoding and sys.stderr.encoding.lower() != "utf-8":
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# MCP Python SDK
from mcp.server.fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Mock data loader
# ---------------------------------------------------------------------------

class MockDataLoader:
    """Loads and caches mock_data.json from the project root."""

    _cache: dict | None = None
    _data_path = Path(__file__).parent / "mock_data.json"

    @classmethod
    def load(cls) -> dict:
        if cls._cache is None:
            if not cls._data_path.exists():
                raise FileNotFoundError(
                    f"mock_data.json not found at {cls._data_path}. "
                    "Please create it before running the MCP server."
                )
            with open(cls._data_path, "r", encoding="utf-8") as f:
                cls._cache = json.load(f)
        return cls._cache

    @classmethod
    def invalidate_cache(cls):
        """Force re-read on next load (useful for testing)."""
        cls._cache = None


# ---------------------------------------------------------------------------
# MCP Server definition
# ---------------------------------------------------------------------------

mcp = FastMCP(
    name="catchup-ai-server",
    instructions=(
        "You are a CatchUp AI data server. Use these tools to retrieve "
        "unread communications and recent documents for a user's briefing."
    ),
)


@mcp.tool()
def get_unread_slack() -> dict:
    """
    Retrieve all unread Slack messages from all channels.

    Returns a dict with:
      - count: total number of messages
      - messages: list of message objects (channel, user, message, timestamp, reactions)
    """
    print("[MCP] Called get_unread_slack", file=sys.stderr, flush=True)
    data = MockDataLoader.load()
    messages = data.get("slack_messages", [])
    return {
        "status": "success",
        "count": len(messages),
        "messages": messages,
    }


@mcp.tool()
def get_unread_emails() -> dict:
    """
    Retrieve all unread emails from the inbox.

    Returns a dict with:
      - count: total number of unread emails
      - emails: list of email objects (subject, sender, snippet, received_date, importance)
    """
    print("[MCP] Called get_unread_emails", file=sys.stderr, flush=True)
    data = MockDataLoader.load()
    all_emails = data.get("emails", [])
    # Return ALL emails (unread flag respected by caller if needed)
    return {
        "status": "success",
        "count": len(all_emails),
        "emails": all_emails,
    }


@mcp.tool()
def get_recent_docs() -> dict:
    """
    Retrieve recently modified documents that have comments/activity.

    Returns a dict with:
      - count: total number of documents
      - documents: list of document objects (name, owner, last_modified, folder, comments, version)
    """
    print("[MCP] Called get_recent_docs", file=sys.stderr, flush=True)
    data = MockDataLoader.load()
    docs = data.get("documents", [])
    # Only return docs that have comments (activity)
    active_docs = [d for d in docs if d.get("comments")]
    return {
        "status": "success",
        "count": len(active_docs),
        "documents": active_docs,
    }


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("[MCP] Starting CatchUp AI MCP Server (stdio mode)…", file=sys.stderr)
    mcp.run(transport="stdio")
