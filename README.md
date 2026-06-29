# ☕ CatchUp AI — Personal Context Rehydrator

> **Never miss what matters at work.**
> CatchUp AI scans your Slack, emails & documents and distills everything into a crisp, prioritised brief — in seconds.

![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat-square&logo=python)
![Google ADK](https://img.shields.io/badge/Google%20ADK-Multi--Agent-orange?style=flat-square&logo=google)
![Gemini](https://img.shields.io/badge/Gemini-2.0%20Flash-purple?style=flat-square&logo=google)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red?style=flat-square&logo=streamlit)
![MCP](https://img.shields.io/badge/MCP-Server-green?style=flat-square)
![Docker](https://img.shields.io/badge/Docker-Ready-blue?style=flat-square&logo=docker)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

---

## 📌 Table of Contents

- [What is CatchUp AI?](#-what-is-catchup-ai)
- [The Problem](#-the-problem)
- [Architecture](#-architecture)
- [Features](#-features)
- [Project Structure](#-project-structure)
- [Quick Start](#-quick-start)
- [Usage](#-usage)
- [MCP Server](#-mcp-server)
- [Security](#-security)
- [Docker Deployment](#-docker-deployment)
- [Environment Variables](#-environment-variables)
- [Tech Stack](#-tech-stack)
- [Roadmap](#-roadmap)

---

## 🧠 What is CatchUp AI?

CatchUp AI is an **AI-powered personal briefing tool** built with the **Google Agent Development Kit (ADK)** and **Gemini 2.0 Flash**. It runs a 4-agent sequential pipeline that automatically collects, classifies, and summarises your missed workplace communications — giving you a structured, role-aware brief so you can get back up to speed instantly.

Built for the **Google 5-Day AI Agents: Intensive Vibe Coding Course**.

---

## 🚨 The Problem

Every professional knows this: you return from a break and face hundreds of unread Slack messages, emails, and document comments. Reading them all takes **2–3 hours**. By the time you're "caught up," half the day is gone.

**CatchUp AI solves this in under 30 seconds.**

---

## 🏗️ Architecture

CatchUp AI runs a **4-agent sequential pipeline** orchestrated by Google ADK:

```
┌─────────────────────────────────────────────────────────────┐
│                     CatchUp AI Pipeline                     │
│                  (Google ADK SequentialAgent)               │
│                                                             │
│  📡 Collector Agent                                         │
│     ├── Tool: fetch_slack_messages(time_range)              │
│     ├── Tool: fetch_emails(time_range)                      │
│     └── Tool: fetch_documents(time_range)                   │
│                         ↓ raw_data                          │
│  🧠 Classifier Agent                                        │
│     └── Groups all data into topics using Gemini            │
│         (Funding & Finance, Engineering, Sales, HR...)      │
│                         ↓ classified_data                   │
│  🔍 Action Miner Agent                                      │
│     └── Extracts URGENT / TODAY / FYI action items          │
│         Role-aware: Manager vs Employee perspective         │
│                         ↓ action_items                      │
│  ✍️  Narrator Agent                                         │
│     └── Writes polished markdown brief with:               │
│         📰 Headlines + ✅ Action Items + 📋 Full Context    │
└─────────────────────────────────────────────────────────────┘
              ↓                           ↓
        Streamlit UI                  CLI (Click)
       (Web Dashboard)            python cli.py run
              ↓
      📄 PDF / Markdown Export
```

### Agent Details

| Agent | Role | Output Key |
|-------|------|------------|
| 📡 **Collector** | Calls 3 tools to fetch all data | `raw_data` |
| 🧠 **Classifier** | Groups by topic with Gemini | `classified_data` |
| 🔍 **Action Miner** | Extracts prioritised tasks | `action_items` |
| ✍️ **Narrator** | Writes the final brief | `full_summary` |

---

## ✨ Features

- 🤖 **Multi-Agent Pipeline** — 4 specialised ADK agents working sequentially
- 📡 **Smart Collection** — Fetches Slack messages, emails & documents
- 🧠 **AI Classification** — Groups content by topic using Gemini 2.0 Flash
- 🔍 **Action Mining** — Extracts 🔴 Urgent / 🟡 Today / 🔵 FYI action items
- ✍️ **Narrative Generation** — Writes a clean, prioritised brief
- 👤 **Role-Based View** — Manager vs Employee data masking
- 🔒 **PII Redaction** — Phones, credit cards, emails sanitised before Gemini
- 🌐 **Streamlit Dashboard** — Beautiful light-theme web UI with PDF export
- 💻 **CLI Support** — Full terminal interface with progress bars
- 🔌 **MCP Server** — Model Context Protocol for tool composability
- 🐳 **Docker Ready** — Container with health check for easy deployment
- 🔋 **Offline Fallback** — Fully functional with mock data, no API key needed

---

## 📁 Project Structure

```
catchup-ai/
├── app.py              # Streamlit web dashboard
├── agents.py           # Multi-agent pipeline (Google ADK)
├── cli.py              # Command-line interface (Click)
├── mcp_server.py       # Model Context Protocol server (FastMCP)
├── security.py         # PII redaction + role-based masking
├── utils.py            # Time filtering, mock data loader
├── mock_data.json      # Offline mock data (Slack, emails, docs)
├── Dockerfile          # Docker container config
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variable template
├── .gitignore          # Git ignore rules (keeps .env safe)
└── README.md           # This file
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- A Google API Key with Gemini access → [Get one free here](https://aistudio.google.com/apikey)

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/catchup-ai.git
cd catchup-ai
```

### 2. Create a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

```bash
cp .env.example .env
```

Open `.env` and add your API key:

```env
GEMINI_API_KEY=your_gemini_api_key_here
CATCHUP_MODE=mock
```

> ⚠️ **Never commit your `.env` file.** It's in `.gitignore` by default.

### 5. Run the app

```bash
streamlit run app.py --server.port 8502
```

Open [http://localhost:8502](http://localhost:8502) in your browser.

---

## 💻 Usage

### Web Dashboard

```bash
streamlit run app.py --server.port 8502
```

1. Select a **Time Range** in the sidebar (e.g. "1 week ago")
2. Select your **Role** (Manager or Employee)
3. Click **✦ Generate Brief**
4. Download as Markdown or PDF

### Command Line Interface

```bash
# Generate a brief for the last week
python cli.py run --since "1 week ago"

# Generate for last 2 hours as an employee
python cli.py run --since "2 hours ago" --role employee

# Save to a custom file with verbose logs
python cli.py run --since "yesterday" --output my_brief.md --verbose

# Check environment status
python cli.py info
```

### CLI Options

| Flag | Default | Description |
|------|---------|-------------|
| `--since` | `2 hours ago` | Time range to look back |
| `--output` | `brief.md` | Output file path |
| `--role` | `manager` | Your role (manager/employee) |
| `--verbose` | off | Show agent debug logs |

---

## 🔌 MCP Server

CatchUp AI includes a **Model Context Protocol (MCP)** server that exposes its data tools to any MCP-compatible client (Claude Desktop, other ADK agents, etc.).

### Run the MCP Server

```bash
python mcp_server.py
```

### Available Tools

| Tool | Description | Returns |
|------|-------------|---------|
| `get_unread_slack` | All Slack messages | `{count, messages}` |
| `get_unread_emails` | All inbox emails | `{count, emails}` |
| `get_recent_docs` | Documents with activity | `{count, documents}` |

### Connect from Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "catchup-ai": {
      "command": "python",
      "args": ["/path/to/catchup-ai/mcp_server.py"]
    }
  }
}
```

---

## 🔒 Security

`security.py` implements a two-layer security model:

### Layer 1 — PII Redaction (all roles)

| Data Type | Before | After |
|-----------|--------|-------|
| Phone numbers | `555-867-5309` | `[PHONE REDACTED]` |
| Credit cards | `4111-1234-5678-9012` | `4111-****-****-9012` |
| Email addresses | `john.doe@gmail.com` | `joh***@gmail.com` |

### Layer 2 — Role-Based Masking

| Data Type | Manager | Employee |
|-----------|---------|----------|
| Financial figures | ✅ Visible | `[AMOUNT REDACTED]` |
| Personal emails | ✅ Visible | `[PERSONAL EMAIL REDACTED]` |
| Phone numbers | `[PHONE REDACTED]` | `[PHONE REDACTED]` |

All masking happens **before data is sent to Gemini** — the LLM never sees raw PII.

---

## 🐳 Docker Deployment

### Build and run

```bash
# Build the image
docker build -t catchup-ai .

# Run with your .env file
docker run -p 8502:8502 --env-file .env catchup-ai

# Or pass the key directly
docker run -p 8502:8502 -e GEMINI_API_KEY=your_key catchup-ai
```

Open [http://localhost:8502](http://localhost:8502)

### Docker Compose (optional)

```yaml
version: '3.8'
services:
  catchup-ai:
    build: .
    ports:
      - "8502:8502"
    env_file:
      - .env
    restart: unless-stopped
```

```bash
docker compose up
```

---

## ⚙️ Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | ✅ For AI mode | Your Gemini API key from [AI Studio](https://aistudio.google.com/apikey) |
| `GOOGLE_API_KEY` | Alternative | Same key, ADK-compatible name |
| `CATCHUP_MODE` | ❌ Optional | Set to `mock` (default) for offline mode |

> 💡 **No API key?** The app runs in offline mode with realistic mock data — great for demos!

---

## 🛠️ Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| AI Agents | [Google Agent Development Kit (ADK)](https://google.github.io/adk-docs/) | ≥1.0.0 |
| LLM | Google Gemini 2.0 Flash | via `google-genai` |
| Protocol | Model Context Protocol (MCP) | ≥1.0.0 |
| Web UI | [Streamlit](https://streamlit.io/) | ≥1.35.0 |
| CLI | [Click](https://click.palletsprojects.com/) | ≥8.1.0 |
| PDF | fpdf2 | ≥2.7.9 |
| Container | Docker | Any |
| Language | Python | 3.12 |

---

## 🔮 Roadmap

- [ ] Gmail OAuth integration for real email fetching
- [ ] Slack workspace connection via OAuth
- [ ] Google Drive document sync
- [ ] Microsoft Teams & Outlook support
- [ ] Scheduled auto-briefing (morning digest at 8 AM)
- [ ] Voice output — brief read aloud via TTS
- [ ] Memory layer — track completed action items
- [ ] Mobile-friendly PWA

---

## 🙏 Acknowledgements

- [Google DeepMind](https://deepmind.google/) for the Gemini API
- [Google Agent Development Kit](https://google.github.io/adk-docs/) team
- [Streamlit](https://streamlit.io/) for the UI framework
- Built during the **Google 5-Day AI Agents Intensive Vibe Coding Course**

---

<div align="center">
  <sub>Built with ☕ and Google Gemini · CatchUp AI v1.0.0</sub>
</div>
