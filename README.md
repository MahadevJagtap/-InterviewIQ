# ⚡ InterviewIQ — AI Interview Question Generator

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-0.2-FF6B35?logo=chainlink&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-llama--3.3--70b-F55036?logo=groq&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

Generate tailored, structured interview questions from any Job Description using **Groq AI**, **LangGraph**, **Pydantic**, and **FastAPI**.

Upload a JD (PDF / DOCX) → Get categorized questions with expected answers, evaluation rubrics, and follow-up probes — in seconds.

---

🚀 Live Demo

Experience **InterviewIQ — JD-Driven Interview Question Generator** in action:

🌐 **Web App:** https://interviewiq-1-jsi0.onrender.com

---
## ✨ Features

| Feature | Details |
|---|---|
| **Document Upload** | Drag-and-drop PDF & DOCX support |
| **JD Analysis** | Extracts role title, skills, experience, responsibilities |
| **Smart Questions** | Technical, Behavioral, Situational, Competency, Culture Fit |
| **Difficulty Levels** | Easy, Medium, Hard — user selectable |
| **Answer Rubric** | Each question has an ideal answer + Excellent / Acceptable / Poor criteria |
| **Follow-Up Probes** | 2–3 follow-up questions per item |
| **Category Filtering** | Filter generated questions by type |
| **Export** | Download the full question set as a file |
| **Structured Output** | Pydantic models for reliable, typed LLM responses |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | [FastAPI](https://fastapi.tiangolo.com/) + [Uvicorn](https://www.uvicorn.org/) |
| **AI Orchestration** | [LangGraph](https://langchain-ai.github.io/langgraph/) — two-node StateGraph pipeline |
| **LLM** | [Groq](https://groq.com/) — `llama-3.3-70b-versatile` via [LangChain-Groq](https://python.langchain.com/docs/integrations/chat/groq/) |
| **Structured I/O** | [Pydantic v2](https://docs.pydantic.dev/) |
| **Document Parsing** | [pypdf](https://pypdf.readthedocs.io/) + [docx2txt](https://github.com/ankushshah89/python-docx2txt) via LangChain loaders |
| **Frontend** | Vanilla HTML/CSS/JS with Jinja2 templating + glassmorphism UI |
| **Observability** | [LangSmith](https://smith.langchain.com/) tracing (optional) |

---

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/your-username/InterviewIQ.git
cd InterviewIQ
```

### 2. Create a virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up your API keys

Copy the example environment file and fill in your keys:

```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

Then edit `.env`:

```env
GROQ_API_KEY=your_groq_api_key_here
```

> Get a **free** Groq API key at [https://console.groq.com/keys](https://console.groq.com/keys)
>
> LangSmith tracing is **optional** — set `LANGSMITH_TRACING=false` to disable it.

### 5. Start the server

```bash
uvicorn main:app --reload --port 8000
```

### 6. Open in browser

```
http://localhost:8000
```

---

## 📋 Usage Guide

1. **Upload** — Drag & drop a Job Description file (PDF or DOCX) onto the upload zone
2. **Configure** — Choose difficulty level, number of questions (3–25), and categories
3. **Generate** — Click "Generate Interview Questions" and wait ~10–15 seconds for AI processing
4. **Review** — Expand each question card to see:
   - **Why Ask** — Relevance to the role
   - **Expected Answer** — Model/ideal answer
   - **Evaluation Criteria** — Excellent / Acceptable / Poor rubric
   - **Follow-Up Questions** — Probing deeper
   - **Skills Tested** — Mapped back to JD skills
5. **Filter** — Use the category filter bar to focus on specific question types
6. **Export** — Download the full set via the "Export" button

---

## 📁 Project Structure

```
InterviewIQ/
│
├── main.py                    # FastAPI entry point & API routes
├── requirements.txt           # Python dependencies
├── .env.example               # API key template — copy to .env
├── .gitignore
│
├── models/
│   └── schemas.py             # Pydantic models (request/response schemas)
│
├── services/
│   ├── graph_pipeline.py      # LangGraph two-node AI pipeline
│   └── document_parser.py     # PDF & DOCX text extraction
│
├── templates/
│   └── index.html             # Web UI (Jinja2 template)
│
└── static/
    ├── css/style.css          # Dark theme with glassmorphism
    └── js/app.js              # Frontend logic
```

---

## 🧠 How It Works

```
┌──────────────┐    ┌──────────────────────┐    ┌──────────────────────┐
│  Upload JD   │───▶│  LangChain Loaders   │───▶│  LangGraph Pipeline  │
│  (PDF/DOCX)  │    │  PyPDF / docx2txt    │    │  (StateGraph)        │
└──────────────┘    └──────────────────────┘    └──────────────────────┘
                                                          │
                              ┌───────────────────────────┤
                              │                           │
                              ▼                           ▼
                   ┌──────────────────┐       ┌──────────────────┐
                   │  Node 1:         │       │  Node 2:         │
                   │  analyze_jd      │──────▶│  generate_       │
                   │  (Groq LLM #1)   │       │  questions       │
                   │  Extracts role,  │       │  (Groq LLM #2)   │
                   │  skills, context │       │  Generates Q&A   │
                   └──────────────────┘       └──────────────────┘
                                                          │
                                                          ▼
                                          ┌───────────────────────────┐
                                          │  Pydantic-Validated JSON  │
                                          │  InterviewQuestionSet     │
                                          └───────────────────────────┘
```

**Two-phase LangGraph pipeline:**
1. **Node 1 — JD Analysis**: Parses the raw text into structured `JobDescriptionAnalysis` (role title, skills, seniority, responsibilities)
2. **Node 2 — Question Generation**: Uses the analysis to generate structured questions with rubrics and follow-up probes

Both nodes use Groq's structured output mode (via `with_structured_output`) to guarantee valid JSON, validated through Pydantic models.

---

## ⚙️ Configuration Options

| Parameter | Options | Default |
|---|---|---|
| Difficulty | Easy, Medium, Hard | Medium |
| Questions | 3 – 25 | 10 |
| Categories | Technical, Behavioral, Situational, Competency-Based, Culture Fit | Technical, Behavioral, Situational |

---

## 🌍 Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GROQ_API_KEY` | ✅ Yes | Your Groq API key |
| `LANGSMITH_TRACING` | ❌ No | Enable LangSmith tracing (`true`/`false`) |
| `LANGSMITH_API_KEY` | ❌ No | LangSmith API key |
| `LANGSMITH_PROJECT` | ❌ No | Project name in LangSmith |

---

## 📝 License

MIT — Feel free to use, modify, and distribute.
