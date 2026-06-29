"""
app.py – CatchUp AI Streamlit Dashboard (Light Theme)
Run with:
    streamlit run app.py --server.port 8502
"""

import os
import time
from datetime import datetime
import streamlit as st
from dotenv import load_dotenv

load_dotenv(override=True)

st.set_page_config(
    page_title="CatchUp AI – Personal Context Rehydrator",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

/* ── Reset & Base ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* ── Light background — clean off-white with warm tint ── */
.stApp {
    background: #F7F6F3;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, { visibility: hidden; }

/* ── Sidebar — crisp white with subtle border ── */
section[data-testid="stSidebar"] {
    background: #FFFFFF !important;
    border-right: 1px solid #E8E6E1 !important;
    box-shadow: 2px 0 12px rgba(0,0,0,0.04);
}
section[data-testid="stSidebar"] * { color: #1A1A2E !important; }
section[data-testid="stSidebar"] .stSelectbox label {
    color: #9CA3AF !important;
    font-size: 0.68rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    font-weight: 600 !important;
}

/* ── Sidebar collapse/expand arrow — always visible ── */
button[data-testid="collapsedControl"],
button[data-testid="expandedControl"],
button[data-testid="baseButton-headerNoPadding"] {
    color: #1A1A2E !important;
    background: #FFFFFF !important;
    border: 1.5px solid #1A1A2E !important;
    border-radius: 8px !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.12) !important;
    opacity: 1 !important;
    visibility: visible !important;
}
button[data-testid="collapsedControl"]:hover,
button[data-testid="expandedControl"]:hover,
button[data-testid="baseButton-headerNoPadding"]:hover {
    background: #1A1A2E !important;
}
button[data-testid="collapsedControl"]:hover svg,
button[data-testid="expandedControl"]:hover svg,
button[data-testid="baseButton-headerNoPadding"]:hover svg {
    fill: #FFFFFF !important;
    color: #FFFFFF !important;
    stroke: #FFFFFF !important;
}
button[data-testid="collapsedControl"] svg,
button[data-testid="expandedControl"] svg,
button[data-testid="baseButton-headerNoPadding"] svg {
    fill: #1A1A2E !important;
    color: #1A1A2E !important;
    stroke: #1A1A2E !important;
}

/* ── Selectbox ── */
.stSelectbox > div > div {
    background: #F7F6F3 !important;
    border: 1.5px solid #E8E6E1 !important;
    border-radius: 10px !important;
    color: #1A1A2E !important;
    font-size: 0.88rem !important;
}
.stSelectbox > div > div:focus-within {
    border-color: #1A1A2E !important;
    box-shadow: 0 0 0 3px rgba(26,26,46,0.08) !important;
}

/* ── Generate button — dark with shimmer animation ── */
div[data-testid="stButton"] > button {
    width: 100%;
    background: #1A1A2E !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 14px 0 !important;
    font-size: 0.88rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.02em !important;
    cursor: pointer !important;
    position: relative !important;
    overflow: hidden !important;
    transition: background 0.2s, transform 0.15s, box-shadow 0.2s !important;
    font-family: 'DM Sans', sans-serif !important;
    box-shadow: 0 2px 8px rgba(26,26,46,0.2) !important;
}
div[data-testid="stButton"] > button p {
    color: #FFFFFF !important;
    font-weight: 600 !important;
}
div[data-testid="stButton"] > button::after {
    content: '';
    position: absolute;
    top: -50%; left: -60%;
    width: 40%; height: 200%;
    background: linear-gradient(105deg, transparent, rgba(255,255,255,0.18), transparent);
    transform: skewX(-20deg);
    animation: shimmer 2.4s infinite;
}
@keyframes shimmer {
    0%   { left: -60%; }
    100% { left: 140%; }
}
div[data-testid="stButton"] > button:hover {
    background: #2D2D4E !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(26,26,46,0.25) !important;
}
div[data-testid="stButton"] > button:active {
    transform: translateY(0) !important;
    box-shadow: 0 2px 8px rgba(26,26,46,0.2) !important;
}

/* ── Download buttons ── */
div[data-testid="stDownloadButton"] > button {
    background: #FFFFFF !important;
    border: 1.5px solid #E8E6E1 !important;
    color: #6B7280 !important;
    border-radius: 10px !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    transition: all 0.2s !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04) !important;
}
div[data-testid="stDownloadButton"] > button:hover {
    border-color: #1A1A2E !important;
    color: #1A1A2E !important;
    box-shadow: 0 2px 8px rgba(26,26,46,0.1) !important;
    transform: translateY(-1px) !important;
}

/* ── Cards ── */
.card {
    background: #FFFFFF;
    border: 1px solid #E8E6E1;
    border-radius: 14px;
    padding: 20px 24px;
    margin: 10px 0;
    transition: border-color 0.2s, box-shadow 0.2s, transform 0.15s;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.card:hover {
    border-color: #C8C5BE;
    box-shadow: 0 4px 16px rgba(0,0,0,0.08);
    transform: translateY(-1px);
}

/* ── Stat boxes ── */
.stat-box {
    background: #FFFFFF;
    border: 1px solid #E8E6E1;
    border-radius: 14px;
    padding: 22px 16px;
    text-align: center;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
    transition: box-shadow 0.2s, transform 0.15s;
}
.stat-box:hover {
    box-shadow: 0 4px 16px rgba(0,0,0,0.08);
    transform: translateY(-1px);
}
.stat-num {
    font-family: 'DM Mono', monospace;
    font-size: 2.2rem;
    font-weight: 500;
    color: #1A1A2E;
    line-height: 1;
}
.stat-label {
    font-size: 0.67rem;
    color: #9CA3AF;
    margin-top: 8px;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-weight: 600;
}

/* ── Headline items ── */
.headline-item {
    display: flex;
    align-items: flex-start;
    gap: 14px;
    background: #FFFFFF;
    border: 1px solid #E8E6E1;
    border-radius: 10px;
    padding: 14px 18px;
    margin: 7px 0;
    transition: border-color 0.2s, box-shadow 0.15s;
    box-shadow: 0 1px 3px rgba(0,0,0,0.03);
}
.headline-item:hover {
    border-color: #1A1A2E;
    box-shadow: 0 3px 12px rgba(26,26,46,0.08);
}
.headline-num {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    font-weight: 500;
    color: #FFFFFF;
    background: #1A1A2E;
    border-radius: 6px;
    padding: 3px 8px;
    min-width: 28px;
    text-align: center;
    flex-shrink: 0;
    margin-top: 2px;
}

/* ── Badges ── */
.badge-urgent {
    display: inline-flex; align-items: center;
    background: #FEF2F2; border: 1px solid #FECACA;
    color: #DC2626; border-radius: 6px;
    padding: 3px 10px; font-size: 0.67rem;
    font-weight: 700; letter-spacing: 0.06em;
    text-transform: uppercase; white-space: nowrap; flex-shrink: 0;
}
.badge-today {
    display: inline-flex; align-items: center;
    background: #FFFBEB; border: 1px solid #FDE68A;
    color: #D97706; border-radius: 6px;
    padding: 3px 10px; font-size: 0.67rem;
    font-weight: 700; letter-spacing: 0.06em;
    text-transform: uppercase; white-space: nowrap; flex-shrink: 0;
}
.badge-fyi {
    display: inline-flex; align-items: center;
    background: #EFF6FF; border: 1px solid #BFDBFE;
    color: #2563EB; border-radius: 6px;
    padding: 3px 10px; font-size: 0.67rem;
    font-weight: 700; letter-spacing: 0.06em;
    text-transform: uppercase; white-space: nowrap; flex-shrink: 0;
}

/* ── Action rows ── */
.action-row {
    display: flex; align-items: flex-start; gap: 12px;
    padding: 12px 16px; border-radius: 10px; margin: 6px 0;
    background: #FFFFFF; border: 1px solid #E8E6E1;
    transition: border-color 0.2s, box-shadow 0.15s;
    box-shadow: 0 1px 3px rgba(0,0,0,0.03);
}
.action-row:hover {
    border-color: #1A1A2E;
    box-shadow: 0 3px 12px rgba(26,26,46,0.07);
}

/* ── Section headers ── */
.section-header {
    font-size: 0.67rem; font-weight: 700; color: #9CA3AF;
    letter-spacing: 0.12em; text-transform: uppercase;
    padding-bottom: 10px; margin: 28px 0 14px 0;
    border-bottom: 1px solid #E8E6E1;
}

/* ── Summary content ── */
.summary-content {
    background: #FFFFFF;
    border-radius: 12px;
    border: 1px solid #E8E6E1;
    padding: 28px 32px;
    color: #374151 !important;
    line-height: 1.75;
    font-size: 0.9rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.summary-content h1, .summary-content h2, .summary-content h3 {
    color: #1A1A2E !important;
    font-weight: 700;
}

/* ── Expander ── */
.streamlit-expanderHeader {
    background: #FFFFFF !important;
    border: 1px solid #E8E6E1 !important;
    border-radius: 10px !important;
    color: #374151 !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
}
.streamlit-expanderHeader:hover {
    border-color: #1A1A2E !important;
    color: #1A1A2E !important;
}
.streamlit-expanderHeader p { color: #374151 !important; }
div[data-testid="stExpander"] {
    border: 1px solid #E8E6E1 !important;
    border-radius: 10px !important;
    background: #FFFFFF !important;
}
div[data-testid="stExpander"] summary { color: #374151 !important; }
div[data-testid="stExpander"] svg {
    fill: #6B7280 !important;
    color: #6B7280 !important;
}

/* ── Progress bar ── */
.stProgress > div > div > div {
    background: #1A1A2E !important;
    border-radius: 4px !important;
}

/* ── Spinner ── */
.stSpinner > div { color: #1A1A2E !important; }

/* ── Warning box ── */
.stAlert {
    background: #FFFBEB !important;
    border: 1px solid #FDE68A !important;
    border-radius: 10px !important;
    color: #92400E !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: #F7F6F3; }
::-webkit-scrollbar-thumb { background: #D1D5DB; border-radius: 10px; }
::-webkit-scrollbar-thumb:hover { background: #9CA3AF; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _check_api_key() -> bool:
    return bool(os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"))


def _run_agents_sync(time_range: str, role: str) -> dict:
    """
    FIX: Import and use run_catchup_sync from agents.py which always spins up
    a fresh thread + event loop — safe to call from Streamlit's async context.
    """
    from agents import run_catchup_sync, _fallback_result
    try:
        return run_catchup_sync(time_range, role)
    except Exception as exc:
        st.error(f"Pipeline error: {exc}")
        return _fallback_result(time_range, role, error=str(exc))


def _generate_pdf(markdown_text: str, role: str, time_range: str) -> bytes:
    try:
        from fpdf import FPDF
        import re

        class PDF(FPDF):
            def header(self):
                self.set_font("Helvetica", "B", 14)
                self.set_fill_color(247, 246, 243)
                self.set_text_color(26, 26, 46)
                self.cell(0, 12, "CatchUp AI Brief", new_x="LMARGIN", new_y="NEXT", align="C", fill=True)
                self.set_font("Helvetica", "", 9)
                self.set_text_color(107, 114, 128)
                ts = datetime.now().strftime("%Y-%m-%d %H:%M")
                self.cell(0, 6, f"Role: {role.title()} | Range: {time_range} | {ts}",
                          new_x="LMARGIN", new_y="NEXT", align="C")
                self.ln(4)

            def footer(self):
                self.set_y(-12)
                self.set_font("Helvetica", "I", 8)
                self.set_text_color(156, 163, 175)
                self.cell(0, 10, f"Page {self.page_no()} | Powered by Google Gemini + ADK", align="C")

        pdf = PDF()
        pdf.set_margins(18, 18, 18)
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=20)

        for line in markdown_text.splitlines():
            line = line.strip()
            if not line or line.startswith("<!--"):
                pdf.ln(2); continue
            if line.startswith("# "):
                pdf.set_font("Helvetica", "B", 15); pdf.set_text_color(26, 26, 46)
                pdf.multi_cell(0, 8, line[2:]); pdf.ln(2)
            elif line.startswith("## "):
                pdf.set_font("Helvetica", "B", 12); pdf.set_text_color(26, 26, 46)
                pdf.multi_cell(0, 7, line[3:]); pdf.ln(1)
            elif line.startswith("### "):
                pdf.set_font("Helvetica", "B", 10); pdf.set_text_color(55, 65, 81)
                pdf.multi_cell(0, 6, line[4:])
            elif line.startswith("---"):
                pdf.set_draw_color(232, 230, 225)
                pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + 175, pdf.get_y()); pdf.ln(3)
            elif line.startswith("- [ ]") or line.startswith("- [x]"):
                pdf.set_font("Helvetica", "", 9); pdf.set_text_color(55, 65, 81)
                clean = re.sub(r"\*\*|__|\*|_|`", "", line[6:])
                pdf.multi_cell(0, 5, f"  □ {clean}")
            elif line.startswith("- ") or line.startswith("* "):
                pdf.set_font("Helvetica", "", 9); pdf.set_text_color(55, 65, 81)
                clean = re.sub(r"\*\*|__|\*|_|`", "", line[2:])
                pdf.multi_cell(0, 5, f"  • {clean}")
            else:
                pdf.set_font("Helvetica", "", 9); pdf.set_text_color(55, 65, 81)
                clean = re.sub(r"\*\*(.+?)\*\*", r"\1", line)
                clean = re.sub(r"\*(.+?)\*", r"\1", clean)
                clean = re.sub(r"`(.+?)`", r"\1", clean)
                clean = clean.replace("→", "->").replace("☕", "").replace("📰", "").replace("✅", "")
                pdf.multi_cell(0, 5, clean)

        return bytes(pdf.output())
    except ImportError:
        return (f"CatchUp AI Brief\nGenerated: {datetime.now()}\n\n{markdown_text}").encode("utf-8")


# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
    <div style='padding: 28px 0 20px 0;'>
        <div style='display:flex; align-items:center; gap:10px;'>
            <span style='font-size:1.8rem; line-height:1;'>☕</span>
            <div>
                <div style='font-size:1rem; font-weight:700; color:#1A1A2E !important; letter-spacing:-0.02em;'>CatchUp AI</div>
                <div style='font-size:0.65rem; color:#9CA3AF !important; text-transform:uppercase; letter-spacing:0.1em; margin-top:1px; font-weight:600;'>Context Rehydrator</div>
            </div>
        </div>
    </div>
    <hr style='border:none; border-top:1px solid #E8E6E1; margin:0 0 22px 0;'>
    """, unsafe_allow_html=True)

    time_range = st.selectbox(
        "Time Range",
        options=["2 hours ago", "4 hours ago", "8 hours ago", "1 week ago", "Yesterday"],
        index=3,  # default to "1 week ago" so mock data always shows results
        help="How far back to scan",
    )

    role = st.selectbox(
        "Your Role",
        options=["Manager", "Employee"],
        index=0,
        help="Controls what data is surfaced",
    ).lower()

    st.markdown("<br>", unsafe_allow_html=True)
    generate_btn = st.button("✦ Generate Brief", use_container_width=True)

    st.markdown("<hr style='border:none; border-top:1px solid #E8E6E1; margin:20px 0;'>", unsafe_allow_html=True)

    if _check_api_key():
        st.markdown("""
        <div style='display:flex; align-items:center; gap:8px;'>
            <div style='width:7px; height:7px; border-radius:50%; background:#16A34A;
                        box-shadow:0 0 0 2px #DCFCE7;'></div>
            <span style='color:#15803D !important; font-size:0.78rem; font-weight:600;'>Gemini API connected</span>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='display:flex; align-items:center; gap:8px;'>
            <div style='width:7px; height:7px; border-radius:50%; background:#DC2626;
                        box-shadow:0 0 0 2px #FEE2E2;'></div>
            <span style='color:#DC2626 !important; font-size:0.78rem; font-weight:600;'>Offline mode</span>
        </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div style='color:#D1D5DB; font-size:0.68rem; margin-top:auto; padding-top:24px; letter-spacing:0.04em;'>
        Powered by Google ADK + Gemini
    </div>""", unsafe_allow_html=True)


# ── Main ─────────────────────────────────────────────────────────────────────

st.markdown("""
<div style='padding: 40px 0 12px 0;'>
    <div style='margin-bottom:12px;'>
        <span style='font-size:0.67rem; font-weight:700; letter-spacing:0.14em; text-transform:uppercase;
                     color:#FFFFFF; background:#1A1A2E; border-radius:6px; padding:4px 12px;'>
            AI-Powered Briefing
        </span>
    </div>
    <h1 style='font-size:2.8rem; font-weight:700; color:#1A1A2E; margin:0;
               letter-spacing:-0.03em; line-height:1.1;'>
        Never miss what<br>matters at work.
    </h1>
    <p style='color:#6B7280; font-size:0.95rem; margin-top:14px; max-width:500px; line-height:1.6;'>
        CatchUp AI scans your Slack, email & docs and distills everything into a crisp, prioritised brief — in seconds.
    </p>
</div>
<hr style='border:none; border-top:1px solid #E8E6E1; margin:8px 0 24px 0;'>
""", unsafe_allow_html=True)

# Session state
if "result" not in st.session_state:
    st.session_state.result = None
if "generated_at" not in st.session_state:
    st.session_state.generated_at = None

if not _check_api_key():
    st.markdown("""
    <div style='background:#FFFBEB; border:1px solid #FDE68A; border-radius:10px;
                padding:12px 18px; margin-bottom:16px; display:flex; align-items:center; gap:10px;'>
        <span style='font-size:1rem;'>⚠️</span>
        <span style='color:#92400E; font-size:0.85rem;'>
            <strong>GOOGLE_API_KEY not found.</strong> Running in offline demo mode.
            Add it to your <code style='background:rgba(0,0,0,0.06); padding:1px 6px; border-radius:4px;'>.env</code> file for live AI summaries.
        </span>
    </div>
    """, unsafe_allow_html=True)

# ── Generate ─────────────────────────────────────────────────────────────────
if generate_btn:
    st.session_state.result = None
    start_time = time.time()

    agent_steps = [
        ("📡", "Collector", "Fetching Slack, emails & documents…"),
        ("🧠", "Classifier", "Grouping by topic with Gemini…"),
        ("🔍", "Action Miner", "Extracting your action items…"),
        ("✍️", "Narrator", "Writing your brief…"),
    ]

    progress_placeholder = st.empty()
    status_placeholder = st.empty()

    with progress_placeholder.container():
        progress_bar = st.progress(0)

    for i, (icon, name, desc) in enumerate(agent_steps):
        with status_placeholder.container():
            st.markdown(
                f"<div class='card' style='margin:0; padding:14px 20px;'>"
                f"<span style='font-size:1rem;'>{icon}</span> "
                f"<strong style='color:#1A1A2E; font-size:0.85rem;'>{name}</strong>"
                f"<span style='color:#9CA3AF; font-size:0.85rem;'> — {desc}</span>"
                f"</div>",
                unsafe_allow_html=True,
            )
        progress_bar.progress((i + 1) * 20)
        time.sleep(0.3)

    with status_placeholder.container():
        with st.spinner("Running pipeline…"):
            result = _run_agents_sync(time_range.lower(), role)

    progress_bar.progress(100)
    elapsed = time.time() - start_time
    progress_placeholder.empty()
    status_placeholder.empty()

    st.session_state.result = result
    st.session_state.generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    st.session_state.elapsed = f"{elapsed:.1f}s"

# ── Results ───────────────────────────────────────────────────────────────────
if st.session_state.result:
    result = st.session_state.result
    summary = result.get("full_summary", "")
    headlines = result.get("headlines", [])
    action_items = result.get("action_items", [])
    raw_data = result.get("raw_data", {})
    elapsed_label = st.session_state.get("elapsed", "")

    st.markdown(
        f"<div style='color:#D1D5DB; font-size:0.75rem; text-align:right; margin-bottom:16px;'>"
        f"Generated {st.session_state.generated_at} · {elapsed_label}"
        f"</div>",
        unsafe_allow_html=True,
    )

    # Stats
    msgs_count = len(raw_data.get("slack_messages", []))
    email_count = len(raw_data.get("emails", []))
    docs_count = len(raw_data.get("documents", []))
    urgent_count = sum(1 for a in action_items if a.get("priority") == "URGENT")

    col1, col2, col3, col4 = st.columns(4)
    for col, num, label in [
        (col1, msgs_count, "Slack Messages"),
        (col2, email_count, "Emails"),
        (col3, docs_count, "Documents"),
        (col4, urgent_count, "Urgent Items"),
    ]:
        with col:
            st.markdown(
                f"<div class='stat-box'>"
                f"<div class='stat-num'>{num}</div>"
                f"<div class='stat-label'>{label}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)
    left, right = st.columns([3, 2], gap="large")

    with left:
        st.markdown("<div class='section-header'>Headlines</div>", unsafe_allow_html=True)
        if headlines:
            for i, h in enumerate(headlines, 1):
                st.markdown(
                    f"<div class='headline-item'>"
                    f"<span class='headline-num'>{i:02d}</span>"
                    f"<span style='color:#374151; font-size:0.88rem; line-height:1.5;'>{h}</span>"
                    f"</div>",
                    unsafe_allow_html=True,
                )
        else:
            st.markdown("<div style='color:#9CA3AF; font-size:0.85rem; padding:12px 0;'>No headlines extracted.</div>", unsafe_allow_html=True)

    with right:
        st.markdown("<div class='section-header'>Action Items</div>", unsafe_allow_html=True)
        badge_map = {
            "URGENT": "<span class='badge-urgent'>🔴 Urgent</span>",
            "TODAY":  "<span class='badge-today'>🟡 Today</span>",
            "FYI":    "<span class='badge-fyi'>🔵 FYI</span>",
        }
        if action_items:
            for item in action_items:
                p = item.get("priority", "FYI")
                badge_html = badge_map.get(p, badge_map["FYI"])
                action = item.get("action", "")
                source = item.get("from", "")
                st.markdown(
                    f"<div class='action-row'>"
                    f"{badge_html}"
                    f"<div>"
                    f"<div style='color:#1F2937; font-size:0.85rem; line-height:1.4;'>{action}</div>"
                    f"{'<div style=\"color:#9CA3AF; font-size:0.74rem; margin-top:3px;\">from: ' + source + '</div>' if source else ''}"
                    f"</div></div>",
                    unsafe_allow_html=True,
                )
        else:
            st.markdown("<div style='color:#9CA3AF; font-size:0.85rem; padding:12px 0;'>No action items found.</div>", unsafe_allow_html=True)

    st.markdown("<div class='section-header'>Full Brief</div>", unsafe_allow_html=True)
    with st.expander("View complete brief", expanded=True):
        st.markdown(f"<div class='summary-content'>{summary}</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    dl_col1, dl_col2, dl_col3 = st.columns([2, 2, 3])
    with dl_col1:
        st.download_button(
            label="↓ Download Markdown",
            data=summary.encode("utf-8"),
            file_name=f"catchup_brief_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
            mime="text/markdown",
            use_container_width=True,
        )
    with dl_col3:
        st.markdown(
            "<div style='padding:10px 0; color:#9CA3AF; font-size:0.78rem;'>"
            "☕ Brief generated by CatchUp AI · Powered by Google Gemini + ADK"
            "</div>",
            unsafe_allow_html=True,
        )

else:
    # Welcome screen
    st.markdown("<br>", unsafe_allow_html=True)
    f1, f2, f3 = st.columns(3)
    for col, icon, title, desc in [
        (f1, "📡", "Smart Collection", "Pulls Slack messages, emails & docs automatically. No copy-paste needed."),
        (f2, "🧠", "AI Classification", "Groups everything by topic and urgency using Gemini — so you see what's signal, not noise."),
        (f3, "✅", "Action Mining", "Surfaces only the tasks and decisions that actually need you."),
    ]:
        with col:
            st.markdown(
                f"<div class='card' style='padding:24px;'>"
                f"<div style='font-size:1.5rem; margin-bottom:14px;'>{icon}</div>"
                f"<div style='font-weight:700; color:#1A1A2E; font-size:0.88rem; margin-bottom:6px;'>{title}</div>"
                f"<div style='color:#6B7280; font-size:0.82rem; line-height:1.65;'>{desc}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

    st.markdown("""
    <div style='text-align:center; padding:52px 0 24px 0; color:#D1D5DB; font-size:0.82rem;'>
        Choose a time range and role in the sidebar →
        click <strong style='color:#1A1A2E;'>✦ Generate Brief</strong>
    </div>
    """, unsafe_allow_html=True)