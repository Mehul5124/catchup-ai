"""
agents.py – CatchUp AI Multi-Agent System (Google ADK)

Four agents:
  1. collector_agent    – fetches Slack, email, docs via direct tool calls
  2. classifier_agent   – groups data by topic using Gemini (with fallback)
  3. action_miner_agent – extracts action items using Gemini
  4. narrator_agent     – writes a polished markdown brief
  5. orchestrator       – SequentialAgent that drives the pipeline
"""

from __future__ import annotations

import json
import logging
import os
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

load_dotenv()

# ── Google ADK ───────────────────────────────────────────────────────────────
from google.adk.agents import Agent, SequentialAgent
from google.adk.runners import InMemoryRunner
from google.genai import types as genai_types

# ── Project helpers ──────────────────────────────────────────────────────────
from security import mask_for_role, redact_pii
from utils import filter_by_time, load_mock_data

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("catchup-ai")


# ===========================================================================
# 1. DATA COLLECTION TOOLS  (called by collector_agent)
# ===========================================================================

def fetch_slack_messages(time_range: str = "2 hours ago") -> dict:
    """
    Fetch unread Slack messages filtered by time range.

    Args:
        time_range: Relative time such as '2 hours ago' or 'yesterday'.

    Returns:
        dict with 'count' and 'messages' list.
    """
    logger.info("[Collector] Fetching Slack messages for range: %s", time_range)
    try:
        data = load_mock_data()
        filtered = filter_by_time(data, time_range)
        msgs = filtered.get("slack_messages", [])
        logger.info("[Collector] Found %d Slack messages", len(msgs))
        return {"status": "success", "count": len(msgs), "messages": msgs}
    except Exception as exc:
        logger.error("[Collector] Slack fetch failed: %s", exc)
        return {"status": "error", "error": str(exc), "messages": []}


def fetch_emails(time_range: str = "2 hours ago") -> dict:
    """
    Fetch unread emails filtered by time range.

    Args:
        time_range: Relative time such as '2 hours ago' or 'yesterday'.

    Returns:
        dict with 'count' and 'emails' list.
    """
    logger.info("[Collector] Fetching emails for range: %s", time_range)
    try:
        data = load_mock_data()
        filtered = filter_by_time(data, time_range)
        emails = filtered.get("emails", [])
        logger.info("[Collector] Found %d emails", len(emails))
        return {"status": "success", "count": len(emails), "emails": emails}
    except Exception as exc:
        logger.error("[Collector] Email fetch failed: %s", exc)
        return {"status": "error", "error": str(exc), "emails": []}


def fetch_documents(time_range: str = "2 hours ago") -> dict:
    """
    Fetch recently modified documents with comments filtered by time range.

    Args:
        time_range: Relative time such as '2 hours ago' or 'yesterday'.

    Returns:
        dict with 'count' and 'documents' list.
    """
    logger.info("[Collector] Fetching documents for range: %s", time_range)
    try:
        data = load_mock_data()
        filtered = filter_by_time(data, time_range)
        docs = [d for d in filtered.get("documents", []) if d.get("comments")]
        logger.info("[Collector] Found %d documents", len(docs))
        return {"status": "success", "count": len(docs), "documents": docs}
    except Exception as exc:
        logger.error("[Collector] Document fetch failed: %s", exc)
        return {"status": "error", "error": str(exc), "documents": []}


# ===========================================================================
# 2. AGENT DEFINITIONS
# ===========================================================================

MODEL = "gemini-2.0-flash"   # standard ADK default model


def _build_orchestrator(time_range: str, role: str) -> SequentialAgent:
    """
    Build a fresh SequentialAgent with role and time_range baked into the
    narrator prompt. This avoids the {role}/{time_range} placeholder bug
    where ADK does not auto-substitute session-state values into instructions.
    """

    # -- Collector ------------------------------------------------------------
    collector_agent = Agent(
        name="collector_agent",
        model=MODEL,
        description="Fetches all unread communications: Slack messages, emails, and recent documents.",
        instruction=f"""
You are the Collector Agent for CatchUp AI.

Your ONLY job is to fetch all available data using your tools.
Call ALL THREE tools in sequence:
  1. fetch_slack_messages with time_range="{time_range}"
  2. fetch_emails with time_range="{time_range}"
  3. fetch_documents with time_range="{time_range}"

After calling all three tools, combine the results into a single JSON string and
save it as your response. The JSON must have the exact structure:
{{
  "slack": <result from fetch_slack_messages>,
  "emails": <result from fetch_emails>,
  "documents": <result from fetch_documents>
}}

Always call all three tools. Do not skip any.
""",
        tools=[fetch_slack_messages, fetch_emails, fetch_documents],
        output_key="raw_data",
        generate_content_config=genai_types.GenerateContentConfig(temperature=0.1),
    )

    # -- Classifier -----------------------------------------------------------
    classifier_agent = Agent(
        name="classifier_agent",
        model=MODEL,
        description="Groups raw communications by topic/category.",
        instruction="""
You are the Classifier Agent for CatchUp AI.

You will receive raw data from the Collector Agent in the session state key 'raw_data'.

Your job: Read the raw data (Slack messages, emails, documents) and group them by TOPIC.

Common topics include (but are not limited to):
- "Funding & Finance" – fundraising, budgets, revenue, billing
- "Engineering & DevOps" – deployments, PRs, bugs, security
- "Sales & Customers" – deals, customer issues, contracts
- "Product & Design" – roadmap, mobile app, UI/UX
- "HR & People" – hiring, onboarding, team events
- "Leadership & OKRs" – strategy, OKRs, leadership decisions
- "General" – social, miscellaneous

Output a JSON object with this EXACT structure and save it in your response:
{
  "classified": {
    "<Topic Name>": {
      "slack_messages": [<list of relevant slack messages>],
      "emails": [<list of relevant emails>],
      "documents": [<list of relevant documents>]
    }
  },
  "topic_count": <integer>
}

Be thorough. Every item should be placed in exactly one topic.
""",
        output_key="classified_data",
        generate_content_config=genai_types.GenerateContentConfig(temperature=0.2),
    )

    # -- Action Miner ---------------------------------------------------------
    action_miner_agent = Agent(
        name="action_miner_agent",
        model=MODEL,
        description="Extracts action items and tasks requiring user attention.",
        instruction=f"""
You are the Action Miner Agent for CatchUp AI.

Look at the raw data in session state key 'raw_data'.

Find ALL action items — things that require someone to DO something. Look for:
- "@user" mentions or "@" callouts
- Keywords: "please", "review", "approve", "task", "need", "required", "urgent",
  "ASAP", "deadline", "by EOD", "by Friday", "sign", "submit", "check", "fix"
- Emails with importance=high
- Questions directed at specific people

This brief is for a {role.upper()}. Prioritise items relevant to that role.

For each action item determine its PRIORITY:
- URGENT: Critical outages, security issues, imminent deadlines (today)
- TODAY: Due today, high importance, blocking others
- FYI: Good to know, not time-sensitive

Output a JSON object with this EXACT structure:
{{
  "action_items": [
    {{
      "priority": "URGENT" | "TODAY" | "FYI",
      "action": "<what needs to be done>",
      "context": "<brief context>",
      "source": "slack" | "email" | "document",
      "from": "<who sent it>"
    }}
  ],
  "urgent_count": <int>,
  "today_count": <int>,
  "fyi_count": <int>
}}

Sort by priority: URGENT first, then TODAY, then FYI.
""",
        output_key="action_items",
        generate_content_config=genai_types.GenerateContentConfig(temperature=0.2),
    )

    # -- Narrator -------------------------------------------------------------
    narrator_agent = Agent(
        name="narrator_agent",
        model=MODEL,
        description="Writes a beautiful, structured markdown CatchUp brief.",
        instruction=f"""
You are the Narrator Agent for CatchUp AI — a skilled business writer.

You have access to:
- 'classified_data' in session state: topics with their messages
- 'action_items' in session state: extracted action items
- 'raw_data' in session state: all original communications

This brief is for: **{role.upper()}**
Time range covered: **{time_range}**

Write a COMPLETE, BEAUTIFUL markdown CatchUp brief with these EXACT sections:

---
# ☕ CatchUp AI Brief
_Generated for: {role} | Time range: {time_range}_

---

## 📰 Headlines
> The 3 most important things that happened while you were away.

1. **<Headline 1>** — <One sentence summary>
2. **<Headline 2>** — <One sentence summary>
3. **<Headline 3>** — <One sentence summary>

---

## ✅ Action Items

### 🔴 URGENT
- [ ] <action> _(from: source)_

### 🟡 TODAY
- [ ] <action> _(from: source)_

### 🔵 FYI
- [ ] <action> _(from: source)_

---

## 📋 Full Context by Topic

### 🏷️ <Topic Name>
**Slack** (N messages):
- `<channel>` **<user>**: <message summary>

**Emails** (N emails):
- 📧 **<subject>** from <sender> — <snippet>

**Documents** (N docs):
- 📄 **<doc name>** — <latest comment>

[repeat for each topic]

---
_Brief generated by CatchUp AI • Powered by Google Gemini_

---

Make it genuinely useful, scannable, and professional. Use emojis tastefully.
Output ONLY the markdown — no code blocks, no JSON.
""",
        output_key="full_summary",
        generate_content_config=genai_types.GenerateContentConfig(
            temperature=0.7, max_output_tokens=4096
        ),
    )

    return SequentialAgent(
        name="catchup_orchestrator",
        description="Orchestrates the full CatchUp AI pipeline: collect → classify → mine → narrate.",
        sub_agents=[
            collector_agent,
            classifier_agent,
            action_miner_agent,
            narrator_agent,
        ],
    )


# ===========================================================================
# 3. PUBLIC RUNNER API
# ===========================================================================

def _safe_parse_json(text: str | None, fallback: Any = None) -> Any:
    """Try to parse JSON from agent output; return fallback on failure."""
    if not text:
        return fallback
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(lines[1:-1]) if len(lines) > 2 else text
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        import re
        m = re.search(r"\{.*\}", text, re.DOTALL)
        if m:
            try:
                return json.loads(m.group())
            except json.JSONDecodeError:
                pass
    return fallback


async def run_catchup(time_range: str = "2 hours ago", role: str = "manager") -> dict:
    """
    Run the full CatchUp AI pipeline asynchronously.

    Args:
        time_range: e.g. '2 hours ago', '4 hours ago', 'yesterday'
        role: 'manager' or 'employee'

    Returns:
        dict with keys: headlines, action_items, full_summary, raw_data
    """
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        logger.error("GEMINI_API_KEY not set — cannot run agents")
        return _fallback_result(time_range, role)

    os.environ["GOOGLE_API_KEY"] = api_key
    os.environ["GEMINI_API_KEY"] = api_key

    logger.info("=== CatchUp AI Pipeline START | range=%s role=%s ===", time_range, role)

    try:
        # Load and mask raw data for security BEFORE sending to Gemini
        raw_data = load_mock_data()
        raw_data = filter_by_time(raw_data, time_range)
        masked_data = mask_for_role(raw_data, role)

        # Build a fresh orchestrator with role/time_range baked into prompts
        orchestrator = _build_orchestrator(time_range, role)

        runner = InMemoryRunner(agent=orchestrator, app_name="catchup_ai")

        session = await runner.session_service.create_session(
            app_name="catchup_ai",
            user_id="user",
            state={
                "time_range": time_range,
                "role": role,
                "masked_raw": json.dumps(masked_data, ensure_ascii=False),
            },
        )

        logger.info("Session created: %s", session.id)

        from google.genai import types as gtypes
        user_message = gtypes.Content(
            role="user",
            parts=[gtypes.Part(text=(
                f"Generate a CatchUp brief for a {role} covering the last {time_range}. "
                "Slack messages, emails, and documents are available via your tools. "
                "The time_range and role are in session state."
            ))],
        )

        final_response = ""
        async for event in runner.run_async(
            user_id="user",
            session_id=session.id,
            new_message=user_message,
        ):
            if event.is_final_response() and event.content:
                for part in event.content.parts:
                    if hasattr(part, "text") and part.text:
                        final_response += part.text

        updated_session = await runner.session_service.get_session(
            app_name="catchup_ai", user_id="user", session_id=session.id
        )
        state = updated_session.state if updated_session else {}

        full_summary = (
            state.get("full_summary")
            or final_response
            or _fallback_summary(time_range, role)
        )
        action_items_raw = _safe_parse_json(state.get("action_items"), {})
        raw_out = _safe_parse_json(state.get("raw_data"), masked_data)

        action_list = (
            action_items_raw.get("action_items", [])
            if isinstance(action_items_raw, dict)
            else []
        )
        headlines = _extract_headlines(full_summary)

        logger.info("=== CatchUp AI Pipeline COMPLETE ===")
        return {
            "headlines": headlines,
            "action_items": action_list,
            "full_summary": full_summary,
            "raw_data": raw_out if raw_out else masked_data,
        }

    except Exception as exc:
        logger.exception("Pipeline error: %s", exc)
        return _fallback_result(time_range, role, error=str(exc))


def run_catchup_sync(time_range: str = "2 hours ago", role: str = "manager") -> dict:
    """
    Synchronous wrapper around run_catchup().
    Safe to call from Streamlit (uses a new thread to avoid event-loop conflicts).
    """
    import asyncio
    import concurrent.futures

    def _run_in_thread():
        # Each thread gets its own clean event loop — avoids Streamlit loop conflicts
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(run_catchup(time_range, role))
        finally:
            loop.close()

    try:
        # Always run in a fresh thread so we never touch the caller's event loop
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(_run_in_thread)
            return future.result(timeout=120)
    except Exception as exc:
        logger.exception("Sync runner error: %s", exc)
        return _fallback_result(time_range, role, error=str(exc))


# ===========================================================================
# 4. FALLBACK HELPERS (when Gemini is unavailable)
# ===========================================================================

def _extract_headlines(markdown: str) -> list[str]:
    """Pull numbered headlines from the markdown brief."""
    import re
    lines = markdown.splitlines()
    headlines = []
    for line in lines:
        m = re.match(r"^\d+\.\s+\*\*(.+?)\*\*", line.strip())
        if m:
            headlines.append(m.group(1))
    return headlines[:3] if headlines else ["No headlines extracted"]


def _filter_data_by_role(data: dict, role: str) -> dict:
    """Filter data based on role (Manager = full access, Employee = team-only)."""
    if role == "manager":
        return data
    
    filtered = {"slack_messages": [], "emails": [], "documents": []}
    
    employee_channels = ["#engineering", "#product", "#random", "#customer_support", "#sales"]
    for msg in data.get("slack_messages", []):
        if msg.get("channel", "") in employee_channels:
            filtered["slack_messages"].append(msg)
    
    for email in data.get("emails", []):
        category = email.get("category", "")
        importance = email.get("importance", "low")
        if category not in ["Leadership", "Finance"] or importance == "high":
            filtered["emails"].append(email)
    
    for doc in data.get("documents", []):
        folder = doc.get("folder", "").lower()
        if "leadership" not in folder and "finance" not in folder:
            filtered["documents"].append(doc)
    
    return filtered


def _fallback_summary(time_range: str, role: str) -> str:
    """Generate a basic summary from mock data without Gemini."""
    try:
        data = load_mock_data()
        filtered = filter_by_time(data, time_range)
        masked = mask_for_role(filtered, role)
        
        # ✅ Apply ROLE-BASED filtering (removes entire items)
        role_filtered = _filter_data_by_role(masked, role)

        msgs = role_filtered.get("slack_messages", [])
        emails = role_filtered.get("emails", [])
        docs = role_filtered.get("documents", [])

        urgent_emails = [e for e in emails if e.get("importance") == "high"]
        mentions = [m for m in msgs if "@" in m.get("message", "")]
        actionable_docs = [d for d in docs if d.get("comments")]

        lines = [
            "# ☕ CatchUp AI Brief (Offline Mode)",
            f"_Generated for: {role} | Time range: {time_range}_",
            "",
            "---",
            "",
            "## 📰 Headlines",
            "",
            "1. **Company Activity** — Multiple updates across Slack and email",
            f"2. **{len(urgent_emails)} Urgent Emails** — Require your immediate attention",
            f"3. **{len(mentions)} @mentions** — Direct callouts requiring a response",
            "",
            "---",
            "",
            "## ✅ Action Items",
            "",
            "### 🔴 URGENT",
        ]

        for e in urgent_emails[:3]:
            lines.append(f"- [ ] Review: **{e['subject']}** _(from {e['sender']})_")

        lines += ["", "### 🟡 TODAY", ""]
        for m in mentions[:3]:
            lines.append(f"- [ ] Respond to @{m.get('user', '?')} in {m.get('channel', '#general')}")

        lines += ["", "### 🔵 FYI", ""]
        for e in emails[:3]:
            lines.append(f"- [ ] Note: **{e['subject']}**")

        lines += [
            "",
            "---",
            "",
            "## 📋 Actionable Context (Role-Masked & Filtered)",
            "",
            "*(Only showing messages that required action, with PII redacted)*",
            "",
        ]

        if urgent_emails:
            lines.append("### 📧 Urgent Emails (Importance: High)")
            for e in urgent_emails[:5]:
                lines.append(f"**{e['subject']}**")
                lines.append(f"*From: {e['sender']}*")
                lines.append(f"> {e.get('snippet', '')}")
                lines.append("")

        if mentions:
            lines.append("### 💬 @Mentions (Direct Callouts)")
            for m in mentions[:5]:
                lines.append(f"**{m.get('channel', '#general')} — {m.get('user', '?')}**")
                lines.append(f"> {m.get('message', '')}")
                lines.append("")

        if actionable_docs:
            lines.append("### 📄 Documents with Comments")
            for d in actionable_docs[:3]:
                lines.append(f"**{d.get('name', 'Unnamed')}**")
                for comment in d.get("comments", [])[:2]:
                    lines.append(f"> {comment.get('author', '?')}: {comment.get('comment', '')}")
                lines.append("")

        lines.append("---")
        lines.append(f"**Slack Messages**: {len(msgs)} | **Emails**: {len(emails)} | **Docs**: {len(docs)}")
        lines.append("_Brief generated by CatchUp AI (Offline Fallback) • Powered by Google Gemini_")

        return "\n".join(lines)

    except Exception as exc:
        return f"# ☕ CatchUp AI\n\n_Error generating brief: {exc}_"
    

def _fallback_result(time_range: str, role: str, error: str = "") -> dict:
    """Return a complete result dict using offline fallback."""
    logger.warning("Using offline fallback mode. Error: %s", error)
    summary = _fallback_summary(time_range, role)

    action_items_list = [
        {
            "priority": "TODAY",
            "action": "Add your GEMINI_API_KEY to the .env file to enable AI summaries",
            "context": "Required for full AI-powered briefing",
            "source": "system",
            "from": "CatchUp AI",
        }
    ]

    try:
        data = load_mock_data()
        filtered = filter_by_time(data, time_range)
        masked = mask_for_role(filtered, role)

        # FIX: use "importance" == "high" to match mock_data.json structure
        urgent_emails = [e for e in masked.get("emails", []) if e.get("importance") == "high"]
        for e in urgent_emails[:3]:
            action_items_list.append({
                "priority": "URGENT",
                "action": f"Review: {e.get('subject', 'Email')}",
                "context": e.get("snippet", ""),
                "source": "email",
                "from": e.get("sender", "Unknown"),
            })

    except Exception:
        masked = {}

    return {
        "headlines": [
            "CatchUp AI running in offline mode",
            "Gemini API key missing or unavailable",
            "Mock data loaded successfully",
        ],
        "action_items": action_items_list,
        "full_summary": summary,
        "raw_data": masked if "masked" in dir() else {},
        "error": error,
    }


# ===========================================================================
# 5. QUICK SMOKE TEST
# ===========================================================================

if __name__ == "__main__":
    import asyncio
    import io

    # Force UTF-8 output on Windows so emoji/unicode characters don't crash
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    if sys.stderr.encoding and sys.stderr.encoding.lower() != "utf-8":
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

    async def _test():
        result = await run_catchup(time_range="1 week ago", role="manager")
        print("=== SUMMARY ===")
        print(result["full_summary"][:2000])
        print("\n=== ACTION ITEMS ===")
        for item in result["action_items"][:5]:
            print(f"  [{item.get('priority','?')}] {item.get('action','')}")

    asyncio.run(_test())