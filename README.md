# 🎓 Codify — Feedback Evaluation Platform

> Inspired by HackerRank and CodeGrade.  
> Codify is a university coding assignment platform that allows students to submit
> code, have it evaluated against teacher-approved micro-skills, and receive
> AI-generated educational feedback — without ever revealing the full solution.

---

## 📌 Table of Contents

- [Overview](#overview)
- [Two-Phase Flow](#two-phase-flow)
- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [Running the App](#running-the-app)
- [Running Tests](#running-tests)
- [Micro-Skill Check Types](#micro-skill-check-types)
- [Example Evaluation](#example-evaluation)

---

## Overview

Codify operates as a two-role platform:

| Role | Responsibility |
|---|---|
| **Teacher** | Creates assignments, triggers AI micro-skill generation, approves or rejects each skill |
| **Student** | Selects an assignment, submits code, receives per-skill verdict with hints |

The core rule:

> ⚠️ **AI-generated micro-skills must be approved by the teacher before they
> can be used to evaluate any student submission. This is a hard rule enforced
> at the service layer.**

---

## Two-Phase Flow

### Phase 1 — Micro-Skill Generation

Called once per assignment when no approved micro-skills exist yet.

```
Input  → assignment title, description, test cases, starter code, language
Output → list of candidate micro-skills (skill_id, title, description, check_type)
```

- The teacher reviews each skill — approving or rejecting one by one
- Approved skills are stored in ChromaDB (vector database)
- Rejected skills are discarded
- If the teacher dislikes a skill, only that skill needs regeneration

### Phase 2 — Student Evaluation

Called after a student submits their code.

```
Input  → student_code + retrieved approved micro-skills
Output → per-skill verdict (passed, reason, student_snippet, fix_hint, affected_lines)
```

- The AI never returns a full corrected solution
- Each verdict includes a guiding hint only
- Line tracing highlights exactly which lines triggered the verdict

---

## Project Structure

```
codify-feedback-evaluation/
├── src/
│   └── app/
│       ├── config.py                      # pydantic BaseSettings
│       ├── models/
│       │   ├── assignment.py              # Assignment model
│       │   ├── micro_skill.py             # MicroSkill, CheckType, SkillStatus
│       │   └── evaluation.py              # SkillVerdict, EvaluationReport
│       ├── repositories/
│       │   ├── assignment_repository.py   # JSON persistence for assignments
│       │   ├── micro_skill_repository.py  # JSON persistence for skill review state
│       │   └── vector_store_repository.py # ChromaDB read/write for approved skills
│       ├── services/
│       │   ├── skill_generation_service.py  # Phase 1 — Groq API call
│       │   └── evaluation_service.py        # Phase 2 — Groq API call
│       └── utils/
│           ├── prompt_builder.py          # Phase 1 & 2 prompt construction
│           └── code_parser.py             # Line number extraction utilities
├── pages/
│   ├── 01_teacher_setup.py               # Teacher UI — assignment + skill review
│   └── 02_student_submit.py              # Student UI — submission + report
├── tests/
│   ├── unit/                             # Pure unit tests per module
│   └── integration/                      # Integration tests (Groq mocked)
├── data/
│   ├── assignments/                      # JSON files per assignment
│   └── skills/                           # Skill review state JSON per assignment
├── streamlit_app.py                      # Landing page entry point
├── requirements.txt
├── .env.example
└── README.md
```

---

## Tech Stack

| Concern | Choice |
|---|---|
| UI & Hosting | Streamlit |
| AI / LLM | Groq API — `llama-3.3-70b-versatile` |
| Vector Database | ChromaDB (embedded — no server needed) |
| Persistence | JSON files |
| Validation | Pydantic v2 |
| Config | pydantic-settings (BaseSettings) |
| Testing | pytest |

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/your-username/codify-feedback-evaluation.git
cd codify-feedback-evaluation
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv

# macOS / Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and fill in your values:

```env
GROQ_API_KEY=your-groq-api-key-here
GROQ_MODEL=llama-3.3-70b-versatile
DATA_DIR=data
CHROMA_PATH=data/chroma
```

Get your free Groq API key at [console.groq.com](https://console.groq.com).

---

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `GROQ_API_KEY` | ✅ Yes | — | Groq API authentication key |
| `GROQ_MODEL` | No | `llama-3.3-70b-versatile` | Groq model identifier |
| `DATA_DIR` | No | `data` | Root directory for JSON persistence |
| `CHROMA_PATH` | No | `data/chroma` | ChromaDB embedded storage path |

> ⚠️ Never commit your `.env` file. It is listed in `.gitignore`.

---

## Running the App

```bash
streamlit run streamlit_app.py
```

The app opens at `http://localhost:8501`.

### Teacher Flow

1. Navigate to **Teacher Setup**
2. Fill in the assignment form and click **Save Assignment**
3. Select the assignment and click **Generate Micro-Skills**
4. Review each skill card — click **Approve** or **Reject**
5. Approved skills are immediately stored in ChromaDB

### Student Flow

1. Navigate to **Student Submission**
2. Select your assignment from the dropdown
3. Paste your code into the editor
4. Click **Submit for Evaluation**
5. Review your per-skill verdict report

---

## Running Tests

### Run all tests

```bash
pytest tests/ -v
```

### Run a specific test file

```bash
pytest tests/unit/test_evaluation_service.py -v
```

### Run with coverage report

```bash
pytest tests/ --cov=src --cov-report=term-missing
```

### Test file map

| Test File | Covers |
|---|---|
| `test_config.py` | Settings loading and validation |
| `test_assignment_model.py` | Assignment pydantic model |
| `test_micro_skill_model.py` | MicroSkill, CheckType, SkillStatus |
| `test_evaluation_model.py` | SkillVerdict, EvaluationReport |
| `test_prompt_builder.py` | Phase 1 & 2 prompt construction |
| `test_code_parser.py` | Line extraction utilities |
| `test_assignment_repository.py` | JSON persistence for assignments |
| `test_micro_skill_repository.py` | JSON persistence for skill review state |
| `test_vector_store_repository.py` | ChromaDB upsert and retrieval |
| `test_skill_generation_service.py` | Phase 1 Groq API call (mocked) |
| `test_evaluation_service.py` | Phase 2 Groq API call (mocked) |

---

## Micro-Skill Check Types

| Check Type | Description | Example |
|---|---|---|
| `syntax` | Correct language structure or construct | Proper loop declaration |
| `input_output` | Reading input or producing correct output | Using `scanf` or `printf` |
| `logic` | Algorithmic correctness and data manipulation | Correct array indexing |

---

## Example Evaluation

**Assignment:** Array Left Shift (C language)

**Generated Micro-Skills:**

| Skill | Check Type | Title |
|---|---|---|
| 1 | `logic` | Access array elements using `arr[i]` |
| 2 | `input_output` | Use `scanf` to read 5 integers |
| 3 | `logic` | Shift elements using `arr[i-1]` correctly |
| 4 | `logic` | Use a temporary variable to avoid data loss |

**Student Verdict — Skill 4 (Failed):**

```
❌ Skill 4 — Use a temporary variable

Verdict : Student overwrites arr[0] before saving its value, causing data loss.
Code    : arr[4] = arr[0];   // arr[0] is already overwritten at this point
Lines   : 18
Hint    : Think about what happens to arr[0] before the loop finishes.
          Can you save it somewhere safe before the loop starts?
```

> The AI never reveals the full corrected solution — only a guiding hint.

---

## Deploying to Streamlit Cloud

1. Push your repository to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. Set the main file path to `streamlit_app.py`
5. Add your environment variables under **Advanced Settings → Secrets**:

```toml
GROQ_API_KEY = "your-groq-api-key-here"
GROQ_MODEL = "llama-3.3-70b-versatile"
DATA_DIR = "data"
CHROMA_PATH = "data/chroma"
```

> ⚠️ On Streamlit Cloud, `data/` is ephemeral — files reset on each redeployment.
> For persistent storage consider replacing the JSON repositories with
> a cloud database such as Supabase or Firebase.

---

## License

MIT License — free to use for educational and portfolio purposes.
```

---