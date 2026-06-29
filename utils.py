"""
utils.py – CatchUp AI Helper Functions
"""

import json
import os
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path


MOCK_DATA_PATH = Path(__file__).parent / "mock_data.json"


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_mock_data() -> dict:
    """Reads and returns the contents of mock_data.json."""
    if not MOCK_DATA_PATH.exists():
        raise FileNotFoundError(
            f"mock_data.json not found at {MOCK_DATA_PATH}. "
            "Please create it in the project root."
        )
    with open(MOCK_DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Time filtering
# ---------------------------------------------------------------------------

_RELATIVE_TIME_PATTERN = re.compile(
    r"(\d+)\s*(second|minute|hour|day|week)s?\s*ago", re.IGNORECASE
)

def parse_relative_time(time_range: str) -> datetime:
    """
    Convert a relative time string like '2 hours ago' into an absolute
    UTC datetime representing the cutoff point.
    """
    now = datetime.now(tz=timezone.utc)
    match = _RELATIVE_TIME_PATTERN.match(time_range.strip())
    if match:
        amount = int(match.group(1))
        unit = match.group(2).lower()
        deltas = {
            "second": timedelta(seconds=amount),
            "minute": timedelta(minutes=amount),
            "hour":   timedelta(hours=amount),
            "day":    timedelta(days=amount),
            "week":   timedelta(weeks=amount),
        }
        return now - deltas.get(unit, timedelta(hours=2))

    # Keyword shortcuts
    lower = time_range.lower().strip()
    if lower == "yesterday":
        return now - timedelta(days=1)
    if lower in ("today", "this morning"):
        return now.replace(hour=0, minute=0, second=0, microsecond=0)

    # Fallback: 2 hours
    return now - timedelta(hours=2)


def filter_by_time(data: dict, time_range: str) -> dict:
    """
    Filter all collections in *data* so only items after the cutoff remain.
    Expects the mock data structure with 'slack_messages', 'emails', and
    'documents' keys. Each item must have a timestamp / received_date field.
    Returns a filtered copy.
    """
    cutoff = parse_relative_time(time_range)

    def _parse_ts(ts_str: str) -> datetime:
        try:
            dt = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except (ValueError, TypeError):
            return datetime.min.replace(tzinfo=timezone.utc)

    filtered: dict = {}

    # Slack messages
    messages = data.get("slack_messages", [])
    filtered["slack_messages"] = [
        m for m in messages if _parse_ts(m.get("timestamp", "")) >= cutoff
    ]

    # Emails
    emails = data.get("emails", [])
    filtered["emails"] = [
        e for e in emails if _parse_ts(e.get("received_date", "")) >= cutoff
    ]

    # Documents (use last_modified)
    docs = data.get("documents", [])
    filtered["documents"] = [
        d for d in docs if _parse_ts(d.get("last_modified", "")) >= cutoff
    ]

    return filtered


# ---------------------------------------------------------------------------
# Filename generation
# ---------------------------------------------------------------------------

def generate_report_filename(prefix: str = "catchup_brief", ext: str = "pdf") -> str:
    """
    Generate a unique filename for PDF exports.
    Example: catchup_brief_20260622_204500.pdf
    """
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{ts}.{ext}"


# ---------------------------------------------------------------------------
# Quick smoke-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    data = load_mock_data()
    print(f"Loaded mock data: {len(data.get('slack_messages', []))} Slack messages, "
          f"{len(data.get('emails', []))} emails, "
          f"{len(data.get('documents', []))} documents")

    filtered = filter_by_time(data, "8 hours ago")
    print(f"After filtering (8h): {len(filtered['slack_messages'])} msgs, "
          f"{len(filtered['emails'])} emails, "
          f"{len(filtered['documents'])} docs")

    print("Report filename:", generate_report_filename())
