# ☕ CatchUp AI — Personal Context Rehydrator

> Never miss what matters at work. CatchUp AI scans your Slack, emails & documents and distills everything into a crisp, prioritised brief — in seconds.

![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat-square&logo=python)
![Google ADK](https://img.shields.io/badge/Google%20ADK-Agents-orange?style=flat-square&logo=google)
![Gemini](https://img.shields.io/badge/Gemini-AI-purple?style=flat-square&logo=google)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-red?style=flat-square&logo=streamlit)
![Docker](https://img.shields.io/badge/Docker-Ready-blue?style=flat-square&logo=docker)

---

## 🧠 What is CatchUp AI?

CatchUp AI is an AI-powered personal briefing tool built with **Google Agent Development Kit (ADK)** and **Gemini**. It runs a multi-agent pipeline that collects, classifies, and summarises your missed communications — giving you a structured, role-aware brief so you can get back up to speed instantly.

Built as part of the **5-Day AI Agents: Intensive Vibe Coding Course With Google**.

---

## ✨ Features

- 🤖 **Multi-Agent Pipeline** — 4 specialised agents working in sequence
- 📡 **Smart Collection** — Fetches Slack messages, emails & documents
- 🧠 **AI Classification** — Groups content by topic using Gemini
- 🔍 **Action Mining** — Extracts tasks and decisions relevant to you
- ✍️ **Narrative Generation** — Writes a clean, prioritised brief
- 👤 **Role-Based View** — Manager vs Employee perspectives
- 🌐 **Streamlit Dashboard** — Beautiful light-theme web UI
- 💻 **CLI Support** — Run directly from the terminal
- 📄 **Export** — Download brief as Markdown or PDF
- 🔌 **MCP Server** — Model Context Protocol support
- 🐳 **Docker Ready** — Containerised for easy deployment
- 🔒 **Offline Fallback** — Works with mock data when API is unavailable

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                   CatchUp AI Pipeline                │
│                                                     │
│  📡 Collector Agent                                 │
│     └── Fetches Slack, emails & documents           │
│            ↓                                        │
│  🧠 Classifier Agent                                │
│     └── Groups messages by topic with Gemini        │
│            ↓                                        │
│  🔍 Action Miner Agent                              │
│     └── Extracts your personal action items         │
│            ↓                                        │
│  ✍️  Narrator Agent                                 │
│     └── Writes your polished brief                  │
└─────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
Catchup-AI/
├── app.py              # Streamlit web dashboard
├── agents.py           # Multi-agent pipeline (Google ADK)
├── cli.py              # Command-line interface
├── mcp_server.py       # Model Context Protocol server
├── security.py         # API key & security utilities
├── utils.py            # Helper functions
├── mock_data.json      # Offline fallback mock data
├── brief.md            # Latest generated brief output
├── Dockerfile          # Docker container config
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variable template
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- A Google API Key with Gemini access ([Get one here](https://aistudio.google.com/apikey))

### 1. Clone the repository

```bash
git clone https://github.com/your-username/catchup-ai.git
cd catchup-ai
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up environment variables

```bash
cp .env.example .env
```

Edit `.env` and add your API key:

```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

> ⚠️ **Note:** A billing-enabled Google Cloud account is recommended. Free tier access may have regional restrictions. You can add billing at [console.cloud.google.com/billing](https://console.cloud.google.com/billing) — Google provides $300 in free credits for new accounts.

---

## 💻 Usage

### Web Dashboard (Streamlit)

```bash
streamlit run app.py --server.port 8502
```

Then open [http://localhost:8502](http://localhost:8502) in your browser.

### Command Line Interface

```bash
# Generate a brief for the last week
python cli.py run --since "1 week ago"

# Generate a brief for the last 2 hours
python cli.py run --since "2 hours ago"

# Specify a role
python cli.py run --since "yesterday" --role employee
```

### Docker

```bash
# Build the image
docker build -t catchup-ai .

# Run the container
docker run -p 8502:8502 --env-file .env catchup-ai
```

---

## 🤖 Agent Details

| Agent | Role | Description |
|-------|------|-------------|
| 📡 **Collector** | Data Fetching | Retrieves Slack messages, emails, and documents from the specified time range |
| 🧠 **Classifier** | Topic Grouping | Uses Gemini to group and categorise messages by subject and relevance |
| 🔍 **Action Miner** | Task Extraction | Identifies action items, decisions, and mentions relevant to your role |
| ✍️ **Narrator** | Brief Writing | Synthesises everything into a clean, structured markdown brief |

---

## 📊 Output Format

The generated brief includes:

- **📰 Headlines** — Top 3 things that happened while you were away
- **✅ Action Items** — Prioritised as 🔴 Urgent / 🟡 Today / 🔵 FYI
- **📋 Full Context** — Complete summary with all relevant details
- **📄 Export** — Downloadable as `.md` or `.pdf`

---

## 🔮 Roadmap

- [ ] Gmail OAuth integration for real email fetching
- [ ] Slack workspace connection via OAuth
- [ ] Google Drive document sync
- [ ] Microsoft Teams & Outlook support
- [ ] Scheduled auto-briefing (morning digest)
- [ ] Mobile-friendly PWA

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| AI Agents | [Google Agent Development Kit (ADK)](https://google.github.io/adk-docs/) |
| LLM | Google Gemini 2.0 Flash |
| Web UI | [Streamlit](https://streamlit.io/) |
| Protocol | Model Context Protocol (MCP) |
| Language | Python 3.12 |
| Container | Docker |

---

## ⚙️ Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_API_KEY` | ✅ Yes | Your Gemini API key from [AI Studio](https://aistudio.google.com/apikey) |

---

## 📝 License

This project was built for educational purposes as part of the **Google 5-Day Gen AI Intensive Course**.

---

## 🙏 Acknowledgements

- [Google DeepMind](https://deepmind.google/) for the Gemini API
- [Google Agent Development Kit](https://google.github.io/adk-docs/) team
- [Streamlit](https://streamlit.io/) for the UI framework

---

<div align="center">
  <sub>Built with ☕ and Google Gemini · CatchUp AI v1.0.0</sub>
</div>