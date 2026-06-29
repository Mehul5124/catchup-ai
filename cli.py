"""
cli.py - CatchUp AI Command-Line Interface (Click)

Usage:
    python cli.py run --since "2 hours ago" --output brief.md --role manager
"""

import io
import os
import sys
import asyncio
import logging
from pathlib import Path
from datetime import datetime

# Force UTF-8 output on Windows so emoji/unicode characters don't crash
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if sys.stderr.encoding and sys.stderr.encoding.lower() != "utf-8":
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import click
from dotenv import load_dotenv

load_dotenv(override=True)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _check_env():
    """Warn if GEMINI_API_KEY is missing."""
    key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not key:
        click.echo(
            click.style(
                "⚠️  Warning: GEMINI_API_KEY not found in environment.\n"
                "   The brief will be generated in offline/fallback mode.\n"
                "   Add GEMINI_API_KEY to your .env file for full AI summaries.",
                fg="yellow",
            ),
            err=True,
        )
    return bool(key)


def _setup_logging(verbose: bool):
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        stream=sys.stderr,
    )


def _print_banner():
    banner = click.style(
        "\n+==========================================+\n"
        "|       [COFFEE]  CatchUp AI  v1.0.0       |\n"
        "|   Personal Context Rehydrator - CLI      |\n"
        "+==========================================+\n",
        fg="cyan",
        bold=True,
    )
    click.echo(banner)


def _print_section(title: str, color: str = "blue"):
    click.echo("\n" + click.style(f"-- {title} ", fg=color, bold=True) + "-" * (40 - len(title)))


# ---------------------------------------------------------------------------
# CLI Group
# ---------------------------------------------------------------------------

@click.group()
@click.version_option(version="1.0.0", prog_name="catchup")
def cli():
    """☕ CatchUp AI – Personal Context Rehydrator.

    Summarises your missed Slack messages, emails, and documents
    using a Google ADK multi-agent pipeline powered by Gemini.
    """
    pass


# ---------------------------------------------------------------------------
# `run` command
# ---------------------------------------------------------------------------

@cli.command()
@click.option(
    "--since",
    default="2 hours ago",
    show_default=True,
    metavar="TIME_RANGE",
    help="Time range to look back (e.g. '2 hours ago', '4 hours ago', 'yesterday').",
)
@click.option(
    "--output",
    default="brief.md",
    show_default=True,
    type=click.Path(dir_okay=False, writable=True),
    help="Path where the markdown brief will be saved.",
)
@click.option(
    "--role",
    default="manager",
    show_default=True,
    type=click.Choice(["manager", "employee"], case_sensitive=False),
    help="Your role — affects role-based data masking.",
)
@click.option(
    "--verbose",
    is_flag=True,
    default=False,
    help="Show detailed agent logs in stderr.",
)
def run(since: str, output: str, role: str, verbose: bool):
    """Generate a CatchUp brief for the given time range.

    \b
    Examples:
        python cli.py run --since "2 hours ago"
        python cli.py run --since yesterday --role employee --output my_brief.md
        python cli.py run --since "4 hours ago" --verbose
    """
    _setup_logging(verbose)
    _print_banner()

    _check_env()

    click.echo(click.style(f"📅 Time range : ", fg="white") + click.style(since, fg="green", bold=True))
    click.echo(click.style(f"👤 Role       : ", fg="white") + click.style(role.title(), fg="green", bold=True))
    click.echo(click.style(f"💾 Output     : ", fg="white") + click.style(output, fg="green", bold=True))

    # ── Agent pipeline steps ──────────────────────────────────────────────
    steps = [
        ("📡 Collector Agent", "Fetching Slack, emails & documents…"),
        ("🧠 Classifier Agent", "Grouping messages by topic…"),
        ("🔍 Action Miner", "Extracting your action items…"),
        ("✍️  Narrator Agent", "Writing your brief…"),
    ]

    click.echo("")
    for icon_name, desc in steps:
        click.echo(
            click.style(f"  {icon_name}: ", fg="cyan") + click.style(desc, fg="white")
        )

    click.echo("")

    # ── Run agents ────────────────────────────────────────────────────────
    with click.progressbar(
        length=4,
        label=click.style("  🚀 Running pipeline", fg="cyan"),
        bar_template="%(label)s  %(bar)s  %(info)s",
        fill_char=click.style("█", fg="cyan"),
        empty_char="░",
    ) as bar:
        # Import here so ADK loads after env is set
        from agents import run_catchup

        result = {}
        error_msg = None

        try:
            result = asyncio.run(run_catchup(time_range=since, role=role))
            bar.update(4)
        except Exception as exc:
            error_msg = str(exc)
            bar.update(4)

    if error_msg:
        click.echo(
            click.style(f"\n❌ Pipeline error: {error_msg}", fg="red"), err=True
        )
        # Try offline fallback
        from agents import _fallback_result
        result = _fallback_result(since, role, error=error_msg)

    full_summary = result.get("full_summary", "")
    headlines   = result.get("headlines", [])
    action_items = result.get("action_items", [])

    # ── Print to terminal ─────────────────────────────────────────────────
    _print_section("📰 HEADLINES", "yellow")
    if headlines:
        for i, h in enumerate(headlines, 1):
            click.echo(f"  {i}. {click.style(h, bold=True)}")
    else:
        click.echo("  (No headlines extracted)")

    _print_section("✅ ACTION ITEMS", "green")
    priority_colors = {"URGENT": "red", "TODAY": "yellow", "FYI": "blue"}
    priority_icons  = {"URGENT": "🔴", "TODAY": "🟡", "FYI": "🔵"}

    if action_items:
        for item in action_items:
            p = item.get("priority", "FYI")
            color = priority_colors.get(p, "white")
            icon  = priority_icons.get(p, "•")
            label = click.style(f"[{p}]", fg=color, bold=True)
            action = item.get("action", "")
            source = item.get("from", "")
            click.echo(f"  {icon} {label} {action}")
            if source:
                click.echo(click.style(f"       ↳ from: {source}", fg="bright_black"))
    else:
        click.echo("  (No action items found)")

    _print_section("📄 FULL BRIEF PREVIEW", "magenta")
    preview_lines = full_summary.splitlines()[:20]
    for line in preview_lines:
        click.echo(f"  {line}")
    if len(full_summary.splitlines()) > 20:
        click.echo(click.style("  … (truncated — see output file for full brief)", fg="bright_black"))

    # ── Save to file ──────────────────────────────────────────────────────
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_content = (
        f"<!-- CatchUp AI Brief | Generated: {timestamp} | Role: {role} | Range: {since} -->\n\n"
        + full_summary
    )

    try:
        output_path.write_text(file_content, encoding="utf-8")
        click.echo(
            "\n" + click.style(f"  ✅ Brief saved to: ", fg="green") +
            click.style(str(output_path.resolve()), fg="cyan", bold=True)
        )
    except Exception as exc:
        click.echo(click.style(f"\n  ❌ Could not save file: {exc}", fg="red"), err=True)

    click.echo(click.style("\n☕ Done! Stay focused.\n", fg="cyan", bold=True))


# ---------------------------------------------------------------------------
# `info` command – quick project info
# ---------------------------------------------------------------------------

@cli.command()
def info():
    """Show CatchUp AI project info and environment status."""
    _print_banner()
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    mode = os.getenv("CATCHUP_MODE", "mock")

    env_status = click.style("✅ Set", fg="green") if api_key else click.style("❌ Missing", fg="red")
    mock_path = Path(__file__).parent / "mock_data.json"
    data_status = (
        click.style(f"✅ Found ({mock_path.stat().st_size // 1024} KB)", fg="green")
        if mock_path.exists()
        else click.style("❌ Not found", fg="red")
    )

    click.echo(f"  GEMINI_API_KEY : {env_status}")
    click.echo(f"  CATCHUP_MODE   : {click.style(mode, fg='cyan')}")
    click.echo(f"  mock_data.json : {data_status}")
    click.echo(f"  Python         : {sys.version.split()[0]}")
    click.echo("")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    cli()
