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
```
codify-feedback-evaluation
├─ .env
├─ .env.example
├─ .pytest_cache
│  ├─ CACHEDIR.TAG
│  ├─ README.md
│  └─ v
│     └─ cache
│        └─ nodeids
├─ data
│  ├─ assignments
│  ├─ chroma
│  │  ├─ chroma.sqlite3
│  │  └─ f752af66-087d-406b-a713-c575596b34c2
│  │     ├─ data_level0.bin
│  │     ├─ header.bin
│  │     ├─ length.bin
│  │     └─ link_lists.bin
│  └─ skills
├─ README.md
├─ requirements.txt
├─ src
│  ├─ app
│  │  ├─ config.py
│  │  ├─ models
│  │  │  ├─ assignment.py
│  │  │  ├─ evaluation.py
│  │  │  ├─ micro_skill.py
│  │  │  ├─ __init__.py
│  │  │  └─ __pycache__
│  │  │     ├─ assignment.cpython-311.pyc
│  │  │     ├─ evaluation.cpython-311.pyc
│  │  │     ├─ micro_skill.cpython-311.pyc
│  │  │     └─ __init__.cpython-311.pyc
│  │  ├─ repositories
│  │  │  ├─ assignment_repository.py
│  │  │  ├─ micro_skill_repository.py
│  │  │  ├─ vector_store_repository.py
│  │  │  ├─ __init__.py
│  │  │  └─ __pycache__
│  │  │     ├─ assignment_repository.cpython-311.pyc
│  │  │     ├─ micro_skill_repository.cpython-311.pyc
│  │  │     ├─ vector_store_repository.cpython-311.pyc
│  │  │     └─ __init__.cpython-311.pyc
│  │  ├─ services
│  │  │  ├─ evaluation_service.py
│  │  │  ├─ skill_generation_service.py
│  │  │  ├─ __init__.py
│  │  │  └─ __pycache__
│  │  │     ├─ evaluation_service.cpython-311.pyc
│  │  │     ├─ skill_generation_service.cpython-311.pyc
│  │  │     └─ __init__.cpython-311.pyc
│  │  ├─ utils
│  │  │  ├─ code_parser.py
│  │  │  ├─ prompt_builder.py
│  │  │  ├─ __init__.py
│  │  │  └─ __pycache__
│  │  │     ├─ code_parser.cpython-311.pyc
│  │  │     ├─ prompt_builder.cpython-311.pyc
│  │  │     └─ __init__.cpython-311.pyc
│  │  ├─ __init__.py
│  │  └─ __pycache__
│  │     ├─ config.cpython-311.pyc
│  │     └─ __init__.cpython-311.pyc
│  ├─ __init__.py
│  └─ __pycache__
│     └─ __init__.cpython-311.pyc
├─ streamlit_app.py
├─ tests
│  ├─ integration
│  │  ├─ test_skill_generation_service.py
│  │  ├─ __init__.py
│  │  └─ __pycache__
│  │     ├─ test_skill_generation_service.cpython-311-pytest-9.0.2.pyc
│  │     └─ __init__.cpython-311.pyc
│  ├─ unit
│  │  ├─ test_assignment_model.py
│  │  ├─ test_assignment_repository.py
│  │  ├─ test_code_parser.py
│  │  ├─ test_config.py
│  │  ├─ test_evaluation_model.py
│  │  ├─ test_evaluation_service.py
│  │  ├─ test_micro_skill_model.py
│  │  ├─ test_micro_skill_repository.py
│  │  ├─ test_prompt_builder.py
│  │  ├─ test_skill_generation_service.py
│  │  ├─ test_vector_store_repository.py
│  │  ├─ __init__.py
│  │  └─ __pycache__
│  │     ├─ test_assignment_model.cpython-311-pytest-9.0.2.pyc
│  │     ├─ test_assignment_repository.cpython-311-pytest-9.0.2.pyc
│  │     ├─ test_code_parser.cpython-311-pytest-9.0.2.pyc
│  │     ├─ test_config.cpython-311-pytest-9.0.2.pyc
│  │     ├─ test_evaluation_model.cpython-311-pytest-9.0.2.pyc
│  │     ├─ test_evaluation_service.cpython-311-pytest-9.0.2.pyc
│  │     ├─ test_micro_skill_model.cpython-311-pytest-9.0.2.pyc
│  │     ├─ test_micro_skill_repository.cpython-311-pytest-9.0.2.pyc
│  │     ├─ test_prompt_builder.cpython-311-pytest-9.0.2.pyc
│  │     ├─ test_skill_generation_service.cpython-311-pytest-9.0.2.pyc
│  │     ├─ test_vector_store_repository.cpython-311-pytest-9.0.2.pyc
│  │     └─ __init__.cpython-311.pyc
│  ├─ __init__.py
│  └─ __pycache__
│     └─ __init__.cpython-311.pyc
└─ venv
   ├─ etc
   │  └─ jupyter
   │     └─ nbconfig
   │        └─ notebook.d
   │           └─ pydeck.json
   ├─ Include
   ├─ Lib
   │  └─ site-packages
   │     ├─ .DS_Store
   │     ├─ 81d243bd2c585b0f4821__mypyc.cp311-win_amd64.pyd
   │     ├─ altair
   │     │  ├─ datasets
   │     │  │  ├─ _cache.py
   │     │  │  ├─ _constraints.py
   │     │  │  ├─ _data.py
   │     │  │  ├─ _exceptions.py
   │     │  │  ├─ _loader.py
   │     │  │  ├─ _metadata
   │     │  │  │  ├─ metadata.csv.gz
   │     │  │  │  ├─ metadata.parquet
   │     │  │  │  └─ schemas.json.gz
   │     │  │  ├─ _reader.py
   │     │  │  ├─ _readimpl.py
   │     │  │  ├─ _typing.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ _cache.cpython-311.pyc
   │     │  │     ├─ _constraints.cpython-311.pyc
   │     │  │     ├─ _data.cpython-311.pyc
   │     │  │     ├─ _exceptions.cpython-311.pyc
   │     │  │     ├─ _loader.cpython-311.pyc
   │     │  │     ├─ _reader.cpython-311.pyc
   │     │  │     ├─ _readimpl.cpython-311.pyc
   │     │  │     ├─ _typing.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ expr
   │     │  │  ├─ consts.py
   │     │  │  ├─ core.py
   │     │  │  ├─ funcs.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ consts.cpython-311.pyc
   │     │  │     ├─ core.cpython-311.pyc
   │     │  │     ├─ funcs.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ jupyter
   │     │  │  ├─ js
   │     │  │  │  ├─ index.js
   │     │  │  │  └─ README.md
   │     │  │  ├─ jupyter_chart.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ jupyter_chart.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ py.typed
   │     │  ├─ theme.py
   │     │  ├─ typing
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ utils
   │     │  │  ├─ compiler.py
   │     │  │  ├─ core.py
   │     │  │  ├─ data.py
   │     │  │  ├─ deprecation.py
   │     │  │  ├─ display.py
   │     │  │  ├─ execeval.py
   │     │  │  ├─ html.py
   │     │  │  ├─ mimebundle.py
   │     │  │  ├─ plugin_registry.py
   │     │  │  ├─ save.py
   │     │  │  ├─ schemapi.py
   │     │  │  ├─ selection.py
   │     │  │  ├─ server.py
   │     │  │  ├─ _dfi_types.py
   │     │  │  ├─ _importers.py
   │     │  │  ├─ _show.py
   │     │  │  ├─ _transformed_data.py
   │     │  │  ├─ _vegafusion_data.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ compiler.cpython-311.pyc
   │     │  │     ├─ core.cpython-311.pyc
   │     │  │     ├─ data.cpython-311.pyc
   │     │  │     ├─ deprecation.cpython-311.pyc
   │     │  │     ├─ display.cpython-311.pyc
   │     │  │     ├─ execeval.cpython-311.pyc
   │     │  │     ├─ html.cpython-311.pyc
   │     │  │     ├─ mimebundle.cpython-311.pyc
   │     │  │     ├─ plugin_registry.cpython-311.pyc
   │     │  │     ├─ save.cpython-311.pyc
   │     │  │     ├─ schemapi.cpython-311.pyc
   │     │  │     ├─ selection.cpython-311.pyc
   │     │  │     ├─ server.cpython-311.pyc
   │     │  │     ├─ _dfi_types.cpython-311.pyc
   │     │  │     ├─ _importers.cpython-311.pyc
   │     │  │     ├─ _show.cpython-311.pyc
   │     │  │     ├─ _transformed_data.cpython-311.pyc
   │     │  │     ├─ _vegafusion_data.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ vegalite
   │     │  │  ├─ api.py
   │     │  │  ├─ data.py
   │     │  │  ├─ display.py
   │     │  │  ├─ schema.py
   │     │  │  ├─ v6
   │     │  │  │  ├─ api.py
   │     │  │  │  ├─ compiler.py
   │     │  │  │  ├─ data.py
   │     │  │  │  ├─ display.py
   │     │  │  │  ├─ schema
   │     │  │  │  │  ├─ channels.py
   │     │  │  │  │  ├─ core.py
   │     │  │  │  │  ├─ mixins.py
   │     │  │  │  │  ├─ vega-lite-schema.json
   │     │  │  │  │  ├─ vega-themes.json
   │     │  │  │  │  ├─ _config.py
   │     │  │  │  │  ├─ _typing.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ channels.cpython-311.pyc
   │     │  │  │  │     ├─ core.cpython-311.pyc
   │     │  │  │  │     ├─ mixins.cpython-311.pyc
   │     │  │  │  │     ├─ _config.cpython-311.pyc
   │     │  │  │  │     ├─ _typing.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ theme.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ api.cpython-311.pyc
   │     │  │  │     ├─ compiler.cpython-311.pyc
   │     │  │  │     ├─ data.cpython-311.pyc
   │     │  │  │     ├─ display.cpython-311.pyc
   │     │  │  │     ├─ theme.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ api.cpython-311.pyc
   │     │  │     ├─ data.cpython-311.pyc
   │     │  │     ├─ display.cpython-311.pyc
   │     │  │     ├─ schema.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ _magics.py
   │     │  ├─ __init__.py
   │     │  └─ __pycache__
   │     │     ├─ theme.cpython-311.pyc
   │     │     ├─ _magics.cpython-311.pyc
   │     │     └─ __init__.cpython-311.pyc
   │     ├─ altair-6.0.0.dist-info
   │     │  ├─ INSTALLER
   │     │  ├─ licenses
   │     │  │  └─ LICENSE
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  └─ WHEEL
   │     ├─ annotated_doc
   │     │  ├─ main.py
   │     │  ├─ py.typed
   │     │  ├─ __init__.py
   │     │  └─ __pycache__
   │     │     ├─ main.cpython-311.pyc
   │     │     └─ __init__.cpython-311.pyc
   │     ├─ annotated_doc-0.0.4.dist-info
   │     │  ├─ entry_points.txt
   │     │  ├─ INSTALLER
   │     │  ├─ licenses
   │     │  │  └─ LICENSE
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  └─ WHEEL
   │     ├─ annotated_types
   │     │  ├─ py.typed
   │     │  ├─ test_cases.py
   │     │  ├─ __init__.py
   │     │  └─ __pycache__
   │     │     ├─ test_cases.cpython-311.pyc
   │     │     └─ __init__.cpython-311.pyc
   │     ├─ annotated_types-0.7.0.dist-info
   │     │  ├─ INSTALLER
   │     │  ├─ licenses
   │     │  │  └─ LICENSE
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  └─ WHEEL
   │     ├─ anyio
   │     │  ├─ abc
   │     │  │  ├─ _eventloop.py
   │     │  │  ├─ _resources.py
   │     │  │  ├─ _sockets.py
   │     │  │  ├─ _streams.py
   │     │  │  ├─ _subprocesses.py
   │     │  │  ├─ _tasks.py
   │     │  │  ├─ _testing.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ _eventloop.cpython-311.pyc
   │     │  │     ├─ _resources.cpython-311.pyc
   │     │  │     ├─ _sockets.cpython-311.pyc
   │     │  │     ├─ _streams.cpython-311.pyc
   │     │  │     ├─ _subprocesses.cpython-311.pyc
   │     │  │     ├─ _tasks.cpython-311.pyc
   │     │  │     ├─ _testing.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ from_thread.py
   │     │  ├─ functools.py
   │     │  ├─ lowlevel.py
   │     │  ├─ py.typed
   │     │  ├─ pytest_plugin.py
   │     │  ├─ streams
   │     │  │  ├─ buffered.py
   │     │  │  ├─ file.py
   │     │  │  ├─ memory.py
   │     │  │  ├─ stapled.py
   │     │  │  ├─ text.py
   │     │  │  ├─ tls.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ buffered.cpython-311.pyc
   │     │  │     ├─ file.cpython-311.pyc
   │     │  │     ├─ memory.cpython-311.pyc
   │     │  │     ├─ stapled.cpython-311.pyc
   │     │  │     ├─ text.cpython-311.pyc
   │     │  │     ├─ tls.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ to_interpreter.py
   │     │  ├─ to_process.py
   │     │  ├─ to_thread.py
   │     │  ├─ _backends
   │     │  │  ├─ _asyncio.py
   │     │  │  ├─ _trio.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ _asyncio.cpython-311.pyc
   │     │  │     ├─ _trio.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ _core
   │     │  │  ├─ _asyncio_selector_thread.py
   │     │  │  ├─ _contextmanagers.py
   │     │  │  ├─ _eventloop.py
   │     │  │  ├─ _exceptions.py
   │     │  │  ├─ _fileio.py
   │     │  │  ├─ _resources.py
   │     │  │  ├─ _signals.py
   │     │  │  ├─ _sockets.py
   │     │  │  ├─ _streams.py
   │     │  │  ├─ _subprocesses.py
   │     │  │  ├─ _synchronization.py
   │     │  │  ├─ _tasks.py
   │     │  │  ├─ _tempfile.py
   │     │  │  ├─ _testing.py
   │     │  │  ├─ _typedattr.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ _asyncio_selector_thread.cpython-311.pyc
   │     │  │     ├─ _contextmanagers.cpython-311.pyc
   │     │  │     ├─ _eventloop.cpython-311.pyc
   │     │  │     ├─ _exceptions.cpython-311.pyc
   │     │  │     ├─ _fileio.cpython-311.pyc
   │     │  │     ├─ _resources.cpython-311.pyc
   │     │  │     ├─ _signals.cpython-311.pyc
   │     │  │     ├─ _sockets.cpython-311.pyc
   │     │  │     ├─ _streams.cpython-311.pyc
   │     │  │     ├─ _subprocesses.cpython-311.pyc
   │     │  │     ├─ _synchronization.cpython-311.pyc
   │     │  │     ├─ _tasks.cpython-311.pyc
   │     │  │     ├─ _tempfile.cpython-311.pyc
   │     │  │     ├─ _testing.cpython-311.pyc
   │     │  │     ├─ _typedattr.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ __init__.py
   │     │  └─ __pycache__
   │     │     ├─ from_thread.cpython-311.pyc
   │     │     ├─ functools.cpython-311.pyc
   │     │     ├─ lowlevel.cpython-311.pyc
   │     │     ├─ pytest_plugin.cpython-311.pyc
   │     │     ├─ to_interpreter.cpython-311.pyc
   │     │     ├─ to_process.cpython-311.pyc
   │     │     ├─ to_thread.cpython-311.pyc
   │     │     └─ __init__.cpython-311.pyc
   │     ├─ anyio-4.13.0.dist-info
   │     │  ├─ entry_points.txt
   │     │  ├─ INSTALLER
   │     │  ├─ licenses
   │     │  │  └─ LICENSE
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  ├─ top_level.txt
   │     │  └─ WHEEL
   │     ├─ attr
   │     │  ├─ converters.py
   │     │  ├─ converters.pyi
   │     │  ├─ exceptions.py
   │     │  ├─ exceptions.pyi
   │     │  ├─ filters.py
   │     │  ├─ filters.pyi
   │     │  ├─ py.typed
   │     │  ├─ setters.py
   │     │  ├─ setters.pyi
   │     │  ├─ validators.py
   │     │  ├─ validators.pyi
   │     │  ├─ _cmp.py
   │     │  ├─ _cmp.pyi
   │     │  ├─ _compat.py
   │     │  ├─ _config.py
   │     │  ├─ _funcs.py
   │     │  ├─ _make.py
   │     │  ├─ _next_gen.py
   │     │  ├─ _typing_compat.pyi
   │     │  ├─ _version_info.py
   │     │  ├─ _version_info.pyi
   │     │  ├─ __init__.py
   │     │  ├─ __init__.pyi
   │     │  └─ __pycache__
   │     │     ├─ converters.cpython-311.pyc
   │     │     ├─ exceptions.cpython-311.pyc
   │     │     ├─ filters.cpython-311.pyc
   │     │     ├─ setters.cpython-311.pyc
   │     │     ├─ validators.cpython-311.pyc
   │     │     ├─ _cmp.cpython-311.pyc
   │     │     ├─ _compat.cpython-311.pyc
   │     │     ├─ _config.cpython-311.pyc
   │     │     ├─ _funcs.cpython-311.pyc
   │     │     ├─ _make.cpython-311.pyc
   │     │     ├─ _next_gen.cpython-311.pyc
   │     │     ├─ _version_info.cpython-311.pyc
   │     │     └─ __init__.cpython-311.pyc
   │     ├─ attrs
   │     │  ├─ converters.py
   │     │  ├─ exceptions.py
   │     │  ├─ filters.py
   │     │  ├─ py.typed
   │     │  ├─ setters.py
   │     │  ├─ validators.py
   │     │  ├─ __init__.py
   │     │  ├─ __init__.pyi
   │     │  └─ __pycache__
   │     │     ├─ converters.cpython-311.pyc
   │     │     ├─ exceptions.cpython-311.pyc
   │     │     ├─ filters.cpython-311.pyc
   │     │     ├─ setters.cpython-311.pyc
   │     │     ├─ validators.cpython-311.pyc
   │     │     └─ __init__.cpython-311.pyc
   │     ├─ attrs-26.1.0.dist-info
   │     │  ├─ INSTALLER
   │     │  ├─ licenses
   │     │  │  └─ LICENSE
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  └─ WHEEL
   │     ├─ bcrypt
   │     │  ├─ py.typed
   │     │  ├─ _bcrypt.pyd
   │     │  ├─ __init__.py
   │     │  ├─ __init__.pyi
   │     │  └─ __pycache__
   │     │     └─ __init__.cpython-311.pyc
   │     ├─ bcrypt-5.0.0.dist-info
   │     │  ├─ INSTALLER
   │     │  ├─ LICENSE
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  ├─ top_level.txt
   │     │  └─ WHEEL
   │     ├─ blinker
   │     │  ├─ base.py
   │     │  ├─ py.typed
   │     │  ├─ _utilities.py
   │     │  ├─ __init__.py
   │     │  └─ __pycache__
   │     │     ├─ base.cpython-311.pyc
   │     │     ├─ _utilities.cpython-311.pyc
   │     │     └─ __init__.cpython-311.pyc
   │     ├─ blinker-1.9.0.dist-info
   │     │  ├─ INSTALLER
   │     │  ├─ LICENSE.txt
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  └─ WHEEL
   │     ├─ build
   │     │  ├─ env.py
   │     │  ├─ py.typed
   │     │  ├─ util.py
   │     │  ├─ _builder.py
   │     │  ├─ _compat
   │     │  │  ├─ importlib.py
   │     │  │  ├─ tarfile.py
   │     │  │  ├─ tomllib.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ importlib.cpython-311.pyc
   │     │  │     ├─ tarfile.cpython-311.pyc
   │     │  │     ├─ tomllib.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ _ctx.py
   │     │  ├─ _exceptions.py
   │     │  ├─ _types.py
   │     │  ├─ _util.py
   │     │  ├─ __init__.py
   │     │  ├─ __main__.py
   │     │  └─ __pycache__
   │     │     ├─ env.cpython-311.pyc
   │     │     ├─ util.cpython-311.pyc
   │     │     ├─ _builder.cpython-311.pyc
   │     │     ├─ _ctx.cpython-311.pyc
   │     │     ├─ _exceptions.cpython-311.pyc
   │     │     ├─ _types.cpython-311.pyc
   │     │     ├─ _util.cpython-311.pyc
   │     │     ├─ __init__.cpython-311.pyc
   │     │     └─ __main__.cpython-311.pyc
   │     ├─ build-1.4.2.dist-info
   │     │  ├─ entry_points.txt
   │     │  ├─ INSTALLER
   │     │  ├─ licenses
   │     │  │  └─ LICENSE
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  └─ WHEEL
   │     ├─ cachetools
   │     │  ├─ func.py
   │     │  ├─ keys.py
   │     │  ├─ _cached.py
   │     │  ├─ _cachedmethod.py
   │     │  ├─ __init__.py
   │     │  └─ __pycache__
   │     │     ├─ func.cpython-311.pyc
   │     │     ├─ keys.cpython-311.pyc
   │     │     ├─ _cached.cpython-311.pyc
   │     │     ├─ _cachedmethod.cpython-311.pyc
   │     │     └─ __init__.cpython-311.pyc
   │     ├─ cachetools-7.0.5.dist-info
   │     │  ├─ INSTALLER
   │     │  ├─ licenses
   │     │  │  └─ LICENSE
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  ├─ top_level.txt
   │     │  └─ WHEEL
   │     ├─ certifi
   │     │  ├─ cacert.pem
   │     │  ├─ core.py
   │     │  ├─ py.typed
   │     │  ├─ __init__.py
   │     │  ├─ __main__.py
   │     │  └─ __pycache__
   │     │     ├─ core.cpython-311.pyc
   │     │     ├─ __init__.cpython-311.pyc
   │     │     └─ __main__.cpython-311.pyc
   │     ├─ certifi-2026.2.25.dist-info
   │     │  ├─ INSTALLER
   │     │  ├─ licenses
   │     │  │  └─ LICENSE
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  ├─ top_level.txt
   │     │  └─ WHEEL
   │     ├─ charset_normalizer
   │     │  ├─ api.py
   │     │  ├─ cd.cp311-win_amd64.pyd
   │     │  ├─ cd.py
   │     │  ├─ cli
   │     │  │  ├─ __init__.py
   │     │  │  ├─ __main__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ __init__.cpython-311.pyc
   │     │  │     └─ __main__.cpython-311.pyc
   │     │  ├─ constant.py
   │     │  ├─ legacy.py
   │     │  ├─ md.cp311-win_amd64.pyd
   │     │  ├─ md.py
   │     │  ├─ models.py
   │     │  ├─ py.typed
   │     │  ├─ utils.py
   │     │  ├─ version.py
   │     │  ├─ __init__.py
   │     │  ├─ __main__.py
   │     │  └─ __pycache__
   │     │     ├─ api.cpython-311.pyc
   │     │     ├─ cd.cpython-311.pyc
   │     │     ├─ constant.cpython-311.pyc
   │     │     ├─ legacy.cpython-311.pyc
   │     │     ├─ md.cpython-311.pyc
   │     │     ├─ models.cpython-311.pyc
   │     │     ├─ utils.cpython-311.pyc
   │     │     ├─ version.cpython-311.pyc
   │     │     ├─ __init__.cpython-311.pyc
   │     │     └─ __main__.cpython-311.pyc
   │     ├─ charset_normalizer-3.4.7.dist-info
   │     │  ├─ entry_points.txt
   │     │  ├─ INSTALLER
   │     │  ├─ licenses
   │     │  │  └─ LICENSE
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  ├─ top_level.txt
   │     │  └─ WHEEL
   │     ├─ chromadb
   │     │  ├─ api
   │     │  │  ├─ async_api.py
   │     │  │  ├─ async_client.py
   │     │  │  ├─ async_fastapi.py
   │     │  │  ├─ base_http_client.py
   │     │  │  ├─ client.py
   │     │  │  ├─ collection_configuration.py
   │     │  │  ├─ configuration.py
   │     │  │  ├─ fastapi.py
   │     │  │  ├─ functions.py
   │     │  │  ├─ models
   │     │  │  │  ├─ AsyncCollection.py
   │     │  │  │  ├─ AttachedFunction.py
   │     │  │  │  ├─ Collection.py
   │     │  │  │  ├─ CollectionCommon.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ AsyncCollection.cpython-311.pyc
   │     │  │  │     ├─ AttachedFunction.cpython-311.pyc
   │     │  │  │     ├─ Collection.cpython-311.pyc
   │     │  │  │     └─ CollectionCommon.cpython-311.pyc
   │     │  │  ├─ rust.py
   │     │  │  ├─ segment.py
   │     │  │  ├─ shared_system_client.py
   │     │  │  ├─ types.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ async_api.cpython-311.pyc
   │     │  │     ├─ async_client.cpython-311.pyc
   │     │  │     ├─ async_fastapi.cpython-311.pyc
   │     │  │     ├─ base_http_client.cpython-311.pyc
   │     │  │     ├─ client.cpython-311.pyc
   │     │  │     ├─ collection_configuration.cpython-311.pyc
   │     │  │     ├─ configuration.cpython-311.pyc
   │     │  │     ├─ fastapi.cpython-311.pyc
   │     │  │     ├─ functions.cpython-311.pyc
   │     │  │     ├─ rust.cpython-311.pyc
   │     │  │     ├─ segment.cpython-311.pyc
   │     │  │     ├─ shared_system_client.cpython-311.pyc
   │     │  │     ├─ types.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ app.py
   │     │  ├─ auth
   │     │  │  ├─ basic_authn
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ simple_rbac_authz
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ token_authn
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ utils
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ base_types.py
   │     │  ├─ chromadb_rust_bindings.pyi
   │     │  ├─ cli
   │     │  │  ├─ cli.py
   │     │  │  ├─ utils.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ cli.cpython-311.pyc
   │     │  │     ├─ utils.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ config.py
   │     │  ├─ db
   │     │  │  ├─ base.py
   │     │  │  ├─ impl
   │     │  │  │  ├─ grpc
   │     │  │  │  │  ├─ client.py
   │     │  │  │  │  ├─ server.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ client.cpython-311.pyc
   │     │  │  │  │     └─ server.cpython-311.pyc
   │     │  │  │  ├─ sqlite.py
   │     │  │  │  ├─ sqlite_pool.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ sqlite.cpython-311.pyc
   │     │  │  │     ├─ sqlite_pool.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ migrations.py
   │     │  │  ├─ mixins
   │     │  │  │  ├─ embeddings_queue.py
   │     │  │  │  ├─ sysdb.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ embeddings_queue.cpython-311.pyc
   │     │  │  │     └─ sysdb.cpython-311.pyc
   │     │  │  ├─ system.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ base.cpython-311.pyc
   │     │  │     ├─ migrations.cpython-311.pyc
   │     │  │     ├─ system.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ errors.py
   │     │  ├─ execution
   │     │  │  ├─ executor
   │     │  │  │  ├─ abstract.py
   │     │  │  │  ├─ distributed.py
   │     │  │  │  ├─ local.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ abstract.cpython-311.pyc
   │     │  │  │     ├─ distributed.cpython-311.pyc
   │     │  │  │     └─ local.cpython-311.pyc
   │     │  │  ├─ expression
   │     │  │  │  ├─ operator.py
   │     │  │  │  ├─ plan.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ operator.cpython-311.pyc
   │     │  │  │     ├─ plan.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ experimental
   │     │  │  └─ density_relevance.ipynb
   │     │  ├─ ingest
   │     │  │  ├─ impl
   │     │  │  │  ├─ utils.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     └─ utils.cpython-311.pyc
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ logservice
   │     │  │  ├─ logservice.py
   │     │  │  └─ __pycache__
   │     │  │     └─ logservice.cpython-311.pyc
   │     │  ├─ log_config.yml
   │     │  ├─ migrations
   │     │  │  ├─ embeddings_queue
   │     │  │  │  ├─ 00001-embeddings.sqlite.sql
   │     │  │  │  └─ 00002-embeddings-queue-config.sqlite.sql
   │     │  │  ├─ metadb
   │     │  │  │  ├─ 00001-embedding-metadata.sqlite.sql
   │     │  │  │  ├─ 00002-embedding-metadata.sqlite.sql
   │     │  │  │  ├─ 00003-full-text-tokenize.sqlite.sql
   │     │  │  │  ├─ 00004-metadata-indices.sqlite.sql
   │     │  │  │  └─ 00005-max-seq-id-int.sqlite.sql
   │     │  │  ├─ sysdb
   │     │  │  │  ├─ 00001-collections.sqlite.sql
   │     │  │  │  ├─ 00002-segments.sqlite.sql
   │     │  │  │  ├─ 00003-collection-dimension.sqlite.sql
   │     │  │  │  ├─ 00004-tenants-databases.sqlite.sql
   │     │  │  │  ├─ 00005-remove-topic.sqlite.sql
   │     │  │  │  ├─ 00006-collection-segment-metadata.sqlite.sql
   │     │  │  │  ├─ 00007-collection-config.sqlite.sql
   │     │  │  │  ├─ 00008-maintenance-log.sqlite.sql
   │     │  │  │  └─ 00009-segment-collection-not-null.sqlite.sql
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ proto
   │     │  │  ├─ convert.py
   │     │  │  ├─ utils.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ convert.cpython-311.pyc
   │     │  │     ├─ utils.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ py.typed
   │     │  ├─ quota
   │     │  │  ├─ simple_quota_enforcer
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ rate_limit
   │     │  │  ├─ simple_rate_limit
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ segment
   │     │  │  ├─ distributed
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ impl
   │     │  │  │  ├─ distributed
   │     │  │  │  │  ├─ segment_directory.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     └─ segment_directory.cpython-311.pyc
   │     │  │  │  ├─ manager
   │     │  │  │  │  ├─ cache
   │     │  │  │  │  │  ├─ cache.py
   │     │  │  │  │  │  ├─ __init__.py
   │     │  │  │  │  │  └─ __pycache__
   │     │  │  │  │  │     ├─ cache.cpython-311.pyc
   │     │  │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  │  ├─ distributed.py
   │     │  │  │  │  ├─ local.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ distributed.cpython-311.pyc
   │     │  │  │  │     ├─ local.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ metadata
   │     │  │  │  │  ├─ sqlite.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     └─ sqlite.cpython-311.pyc
   │     │  │  │  ├─ vector
   │     │  │  │  │  ├─ batch.py
   │     │  │  │  │  ├─ brute_force_index.py
   │     │  │  │  │  ├─ hnsw_params.py
   │     │  │  │  │  ├─ local_hnsw.py
   │     │  │  │  │  ├─ local_persistent_hnsw.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ batch.cpython-311.pyc
   │     │  │  │  │     ├─ brute_force_index.cpython-311.pyc
   │     │  │  │  │     ├─ hnsw_params.cpython-311.pyc
   │     │  │  │  │     ├─ local_hnsw.cpython-311.pyc
   │     │  │  │  │     └─ local_persistent_hnsw.cpython-311.pyc
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ serde.py
   │     │  ├─ server
   │     │  │  ├─ fastapi
   │     │  │  │  ├─ types.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ types.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ telemetry
   │     │  │  ├─ opentelemetry
   │     │  │  │  ├─ fastapi.py
   │     │  │  │  ├─ grpc.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ fastapi.cpython-311.pyc
   │     │  │  │     ├─ grpc.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ product
   │     │  │  │  ├─ events.py
   │     │  │  │  ├─ posthog.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ events.cpython-311.pyc
   │     │  │  │     ├─ posthog.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ README.md
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ test
   │     │  │  ├─ api
   │     │  │  │  ├─ test_collection.py
   │     │  │  │  ├─ test_count_api.py
   │     │  │  │  ├─ test_delete_database.py
   │     │  │  │  ├─ test_fork_count_api.py
   │     │  │  │  ├─ test_get_database.py
   │     │  │  │  ├─ test_indexing_status.py
   │     │  │  │  ├─ test_invalid_update.py
   │     │  │  │  ├─ test_limit_offset.py
   │     │  │  │  ├─ test_list_databases.py
   │     │  │  │  ├─ test_numpy_list_inputs.py
   │     │  │  │  ├─ test_schema.py
   │     │  │  │  ├─ test_schema_e2e.py
   │     │  │  │  ├─ test_search_api.py
   │     │  │  │  ├─ test_shared_system_client.py
   │     │  │  │  ├─ test_types.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ test_collection.cpython-311.pyc
   │     │  │  │     ├─ test_count_api.cpython-311.pyc
   │     │  │  │     ├─ test_delete_database.cpython-311.pyc
   │     │  │  │     ├─ test_fork_count_api.cpython-311.pyc
   │     │  │  │     ├─ test_get_database.cpython-311.pyc
   │     │  │  │     ├─ test_indexing_status.cpython-311.pyc
   │     │  │  │     ├─ test_invalid_update.cpython-311.pyc
   │     │  │  │     ├─ test_limit_offset.cpython-311.pyc
   │     │  │  │     ├─ test_list_databases.cpython-311.pyc
   │     │  │  │     ├─ test_numpy_list_inputs.cpython-311.pyc
   │     │  │  │     ├─ test_schema.cpython-311.pyc
   │     │  │  │     ├─ test_schema_e2e.cpython-311.pyc
   │     │  │  │     ├─ test_search_api.cpython-311.pyc
   │     │  │  │     ├─ test_shared_system_client.cpython-311.pyc
   │     │  │  │     └─ test_types.cpython-311.pyc
   │     │  │  ├─ auth
   │     │  │  │  ├─ test_auth_utils.py
   │     │  │  │  ├─ test_rbac_authz.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ test_auth_utils.cpython-311.pyc
   │     │  │  │     └─ test_rbac_authz.cpython-311.pyc
   │     │  │  ├─ client
   │     │  │  │  ├─ create_http_client_with_basic_auth.py
   │     │  │  │  ├─ test_cloud_client.py
   │     │  │  │  ├─ test_create_http_client.py
   │     │  │  │  ├─ test_database_tenant.py
   │     │  │  │  ├─ test_database_tenant_auth.py
   │     │  │  │  ├─ test_multiple_clients_concurrency.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ create_http_client_with_basic_auth.cpython-311.pyc
   │     │  │  │     ├─ test_cloud_client.cpython-311.pyc
   │     │  │  │     ├─ test_create_http_client.cpython-311.pyc
   │     │  │  │     ├─ test_database_tenant.cpython-311.pyc
   │     │  │  │     ├─ test_database_tenant_auth.cpython-311.pyc
   │     │  │  │     ├─ test_multiple_clients_concurrency.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ configurations
   │     │  │  │  ├─ test_collection_configuration.py
   │     │  │  │  ├─ test_configurations.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ test_collection_configuration.cpython-311.pyc
   │     │  │  │     └─ test_configurations.cpython-311.pyc
   │     │  │  ├─ conftest.py
   │     │  │  ├─ data_loader
   │     │  │  │  ├─ test_data_loader.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     └─ test_data_loader.cpython-311.pyc
   │     │  │  ├─ db
   │     │  │  │  ├─ test_log_purge.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     └─ test_log_purge.cpython-311.pyc
   │     │  │  ├─ distributed
   │     │  │  │  ├─ README.md
   │     │  │  │  ├─ test_log_backpressure.py
   │     │  │  │  ├─ test_repair_collection_log_offset.py
   │     │  │  │  ├─ test_reroute.py
   │     │  │  │  ├─ test_sanity.py
   │     │  │  │  ├─ test_statistics_wrapper.py
   │     │  │  │  ├─ test_task_api.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ test_log_backpressure.cpython-311.pyc
   │     │  │  │     ├─ test_repair_collection_log_offset.cpython-311.pyc
   │     │  │  │     ├─ test_reroute.cpython-311.pyc
   │     │  │  │     ├─ test_sanity.cpython-311.pyc
   │     │  │  │     ├─ test_statistics_wrapper.cpython-311.pyc
   │     │  │  │     └─ test_task_api.cpython-311.pyc
   │     │  │  ├─ ef
   │     │  │  │  ├─ test_chroma_bm25_embedding_function.py
   │     │  │  │  ├─ test_custom_ef.py
   │     │  │  │  ├─ test_default_ef.py
   │     │  │  │  ├─ test_ef.py
   │     │  │  │  ├─ test_morph_ef.py
   │     │  │  │  ├─ test_multimodal_ef.py
   │     │  │  │  ├─ test_ollama_ef.py
   │     │  │  │  ├─ test_onnx_mini_lm_l6_v2.py
   │     │  │  │  ├─ test_openai_ef.py
   │     │  │  │  ├─ test_voyageai_ef.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ test_chroma_bm25_embedding_function.cpython-311.pyc
   │     │  │  │     ├─ test_custom_ef.cpython-311.pyc
   │     │  │  │     ├─ test_default_ef.cpython-311.pyc
   │     │  │  │     ├─ test_ef.cpython-311.pyc
   │     │  │  │     ├─ test_morph_ef.cpython-311.pyc
   │     │  │  │     ├─ test_multimodal_ef.cpython-311.pyc
   │     │  │  │     ├─ test_ollama_ef.cpython-311.pyc
   │     │  │  │     ├─ test_onnx_mini_lm_l6_v2.cpython-311.pyc
   │     │  │  │     ├─ test_openai_ef.cpython-311.pyc
   │     │  │  │     └─ test_voyageai_ef.cpython-311.pyc
   │     │  │  ├─ openssl.cnf
   │     │  │  ├─ property
   │     │  │  │  ├─ invariants.py
   │     │  │  │  ├─ strategies.py
   │     │  │  │  ├─ test_add.py
   │     │  │  │  ├─ test_base64_conversion.py
   │     │  │  │  ├─ test_client_url.py
   │     │  │  │  ├─ test_collections.py
   │     │  │  │  ├─ test_collections_with_database_tenant.py
   │     │  │  │  ├─ test_collections_with_database_tenant_overwrite.py
   │     │  │  │  ├─ test_cross_version_persist.py
   │     │  │  │  ├─ test_embeddings.py
   │     │  │  │  ├─ test_filtering.py
   │     │  │  │  ├─ test_fork.py
   │     │  │  │  ├─ test_persist.py
   │     │  │  │  ├─ test_restart_persist.py
   │     │  │  │  ├─ test_schema.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ invariants.cpython-311.pyc
   │     │  │  │     ├─ strategies.cpython-311.pyc
   │     │  │  │     ├─ test_add.cpython-311.pyc
   │     │  │  │     ├─ test_base64_conversion.cpython-311.pyc
   │     │  │  │     ├─ test_client_url.cpython-311.pyc
   │     │  │  │     ├─ test_collections.cpython-311.pyc
   │     │  │  │     ├─ test_collections_with_database_tenant.cpython-311.pyc
   │     │  │  │     ├─ test_collections_with_database_tenant_overwrite.cpython-311.pyc
   │     │  │  │     ├─ test_cross_version_persist.cpython-311.pyc
   │     │  │  │     ├─ test_embeddings.cpython-311.pyc
   │     │  │  │     ├─ test_filtering.cpython-311.pyc
   │     │  │  │     ├─ test_fork.cpython-311.pyc
   │     │  │  │     ├─ test_persist.cpython-311.pyc
   │     │  │  │     ├─ test_restart_persist.cpython-311.pyc
   │     │  │  │     └─ test_schema.cpython-311.pyc
   │     │  │  ├─ segment
   │     │  │  │  └─ distributed
   │     │  │  │     ├─ test_memberlist_provider.py
   │     │  │  │     ├─ test_rendezvous_hash.py
   │     │  │  │     └─ __pycache__
   │     │  │  │        ├─ test_memberlist_provider.cpython-311.pyc
   │     │  │  │        └─ test_rendezvous_hash.cpython-311.pyc
   │     │  │  ├─ stress
   │     │  │  │  ├─ test_many_collections.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     └─ test_many_collections.cpython-311.pyc
   │     │  │  ├─ test_api.py
   │     │  │  ├─ test_chroma.py
   │     │  │  ├─ test_cli.py
   │     │  │  ├─ test_client.py
   │     │  │  ├─ test_config.py
   │     │  │  ├─ test_multithreaded.py
   │     │  │  ├─ utils
   │     │  │  │  ├─ cross_version.py
   │     │  │  │  ├─ distance_functions.py
   │     │  │  │  ├─ test_embedding_function_schemas.py
   │     │  │  │  ├─ test_result_df_transform.py
   │     │  │  │  ├─ test_wait_for_version_increase.py
   │     │  │  │  ├─ wait_for_version_increase.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ cross_version.cpython-311.pyc
   │     │  │  │     ├─ distance_functions.cpython-311.pyc
   │     │  │  │     ├─ test_embedding_function_schemas.cpython-311.pyc
   │     │  │  │     ├─ test_result_df_transform.cpython-311.pyc
   │     │  │  │     ├─ test_wait_for_version_increase.cpython-311.pyc
   │     │  │  │     └─ wait_for_version_increase.cpython-311.pyc
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ conftest.cpython-311.pyc
   │     │  │     ├─ test_api.cpython-311.pyc
   │     │  │     ├─ test_chroma.cpython-311.pyc
   │     │  │     ├─ test_cli.cpython-311.pyc
   │     │  │     ├─ test_client.cpython-311.pyc
   │     │  │     ├─ test_config.cpython-311.pyc
   │     │  │     ├─ test_multithreaded.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ types.py
   │     │  ├─ utils
   │     │  │  ├─ async_to_sync.py
   │     │  │  ├─ batch_utils.py
   │     │  │  ├─ data_loaders.py
   │     │  │  ├─ delete_file.py
   │     │  │  ├─ directory.py
   │     │  │  ├─ distance_functions.py
   │     │  │  ├─ embedding_functions
   │     │  │  │  ├─ amazon_bedrock_embedding_function.py
   │     │  │  │  ├─ baseten_embedding_function.py
   │     │  │  │  ├─ bm25_embedding_function.py
   │     │  │  │  ├─ chroma_bm25_embedding_function.py
   │     │  │  │  ├─ chroma_cloud_qwen_embedding_function.py
   │     │  │  │  ├─ chroma_cloud_splade_embedding_function.py
   │     │  │  │  ├─ chroma_langchain_embedding_function.py
   │     │  │  │  ├─ cloudflare_workers_ai_embedding_function.py
   │     │  │  │  ├─ cohere_embedding_function.py
   │     │  │  │  ├─ fastembed_sparse_embedding_function.py
   │     │  │  │  ├─ google_embedding_function.py
   │     │  │  │  ├─ huggingface_embedding_function.py
   │     │  │  │  ├─ huggingface_sparse_embedding_function.py
   │     │  │  │  ├─ instructor_embedding_function.py
   │     │  │  │  ├─ jina_embedding_function.py
   │     │  │  │  ├─ mistral_embedding_function.py
   │     │  │  │  ├─ morph_embedding_function.py
   │     │  │  │  ├─ nomic_embedding_function.py
   │     │  │  │  ├─ ollama_embedding_function.py
   │     │  │  │  ├─ onnx_mini_lm_l6_v2.py
   │     │  │  │  ├─ openai_embedding_function.py
   │     │  │  │  ├─ open_clip_embedding_function.py
   │     │  │  │  ├─ perplexity_embedding_function.py
   │     │  │  │  ├─ roboflow_embedding_function.py
   │     │  │  │  ├─ schemas
   │     │  │  │  │  ├─ bm25_tokenizer.py
   │     │  │  │  │  ├─ README.md
   │     │  │  │  │  ├─ registry.py
   │     │  │  │  │  ├─ schema_utils.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ bm25_tokenizer.cpython-311.pyc
   │     │  │  │  │     ├─ registry.cpython-311.pyc
   │     │  │  │  │     ├─ schema_utils.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ sentence_transformer_embedding_function.py
   │     │  │  │  ├─ text2vec_embedding_function.py
   │     │  │  │  ├─ together_ai_embedding_function.py
   │     │  │  │  ├─ utils.py
   │     │  │  │  ├─ voyageai_embedding_function.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ amazon_bedrock_embedding_function.cpython-311.pyc
   │     │  │  │     ├─ baseten_embedding_function.cpython-311.pyc
   │     │  │  │     ├─ bm25_embedding_function.cpython-311.pyc
   │     │  │  │     ├─ chroma_bm25_embedding_function.cpython-311.pyc
   │     │  │  │     ├─ chroma_cloud_qwen_embedding_function.cpython-311.pyc
   │     │  │  │     ├─ chroma_cloud_splade_embedding_function.cpython-311.pyc
   │     │  │  │     ├─ chroma_langchain_embedding_function.cpython-311.pyc
   │     │  │  │     ├─ cloudflare_workers_ai_embedding_function.cpython-311.pyc
   │     │  │  │     ├─ cohere_embedding_function.cpython-311.pyc
   │     │  │  │     ├─ fastembed_sparse_embedding_function.cpython-311.pyc
   │     │  │  │     ├─ google_embedding_function.cpython-311.pyc
   │     │  │  │     ├─ huggingface_embedding_function.cpython-311.pyc
   │     │  │  │     ├─ huggingface_sparse_embedding_function.cpython-311.pyc
   │     │  │  │     ├─ instructor_embedding_function.cpython-311.pyc
   │     │  │  │     ├─ jina_embedding_function.cpython-311.pyc
   │     │  │  │     ├─ mistral_embedding_function.cpython-311.pyc
   │     │  │  │     ├─ morph_embedding_function.cpython-311.pyc
   │     │  │  │     ├─ nomic_embedding_function.cpython-311.pyc
   │     │  │  │     ├─ ollama_embedding_function.cpython-311.pyc
   │     │  │  │     ├─ onnx_mini_lm_l6_v2.cpython-311.pyc
   │     │  │  │     ├─ openai_embedding_function.cpython-311.pyc
   │     │  │  │     ├─ open_clip_embedding_function.cpython-311.pyc
   │     │  │  │     ├─ perplexity_embedding_function.cpython-311.pyc
   │     │  │  │     ├─ roboflow_embedding_function.cpython-311.pyc
   │     │  │  │     ├─ sentence_transformer_embedding_function.cpython-311.pyc
   │     │  │  │     ├─ text2vec_embedding_function.cpython-311.pyc
   │     │  │  │     ├─ together_ai_embedding_function.cpython-311.pyc
   │     │  │  │     ├─ utils.cpython-311.pyc
   │     │  │  │     ├─ voyageai_embedding_function.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ fastapi.py
   │     │  │  ├─ lru_cache.py
   │     │  │  ├─ messageid.py
   │     │  │  ├─ read_write_lock.py
   │     │  │  ├─ rendezvous_hash.py
   │     │  │  ├─ results.py
   │     │  │  ├─ sparse_embedding_utils.py
   │     │  │  ├─ statistics.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ async_to_sync.cpython-311.pyc
   │     │  │     ├─ batch_utils.cpython-311.pyc
   │     │  │     ├─ data_loaders.cpython-311.pyc
   │     │  │     ├─ delete_file.cpython-311.pyc
   │     │  │     ├─ directory.cpython-311.pyc
   │     │  │     ├─ distance_functions.cpython-311.pyc
   │     │  │     ├─ fastapi.cpython-311.pyc
   │     │  │     ├─ lru_cache.cpython-311.pyc
   │     │  │     ├─ messageid.cpython-311.pyc
   │     │  │     ├─ read_write_lock.cpython-311.pyc
   │     │  │     ├─ rendezvous_hash.cpython-311.pyc
   │     │  │     ├─ results.cpython-311.pyc
   │     │  │     ├─ sparse_embedding_utils.cpython-311.pyc
   │     │  │     ├─ statistics.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ __init__.py
   │     │  └─ __pycache__
   │     │     ├─ app.cpython-311.pyc
   │     │     ├─ base_types.cpython-311.pyc
   │     │     ├─ config.cpython-311.pyc
   │     │     ├─ errors.cpython-311.pyc
   │     │     ├─ serde.cpython-311.pyc
   │     │     ├─ types.cpython-311.pyc
   │     │     └─ __init__.cpython-311.pyc
   │     ├─ chromadb-1.5.7.dist-info
   │     │  ├─ entry_points.txt
   │     │  ├─ INSTALLER
   │     │  ├─ licenses
   │     │  │  └─ LICENSE
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  ├─ REQUESTED
   │     │  ├─ sboms
   │     │  │  └─ chromadb_rust_bindings.cyclonedx.json
   │     │  └─ WHEEL
   │     ├─ chromadb_rust_bindings
   │     │  ├─ chromadb_rust_bindings.pyd
   │     │  ├─ __init__.py
   │     │  └─ __pycache__
   │     │     └─ __init__.cpython-311.pyc
   │     ├─ click
   │     │  ├─ core.py
   │     │  ├─ decorators.py
   │     │  ├─ exceptions.py
   │     │  ├─ formatting.py
   │     │  ├─ globals.py
   │     │  ├─ parser.py
   │     │  ├─ py.typed
   │     │  ├─ shell_completion.py
   │     │  ├─ termui.py
   │     │  ├─ testing.py
   │     │  ├─ types.py
   │     │  ├─ utils.py
   │     │  ├─ _compat.py
   │     │  ├─ _termui_impl.py
   │     │  ├─ _textwrap.py
   │     │  ├─ _utils.py
   │     │  ├─ _winconsole.py
   │     │  ├─ __init__.py
   │     │  └─ __pycache__
   │     │     ├─ core.cpython-311.pyc
   │     │     ├─ decorators.cpython-311.pyc
   │     │     ├─ exceptions.cpython-311.pyc
   │     │     ├─ formatting.cpython-311.pyc
   │     │     ├─ globals.cpython-311.pyc
   │     │     ├─ parser.cpython-311.pyc
   │     │     ├─ shell_completion.cpython-311.pyc
   │     │     ├─ termui.cpython-311.pyc
   │     │     ├─ testing.cpython-311.pyc
   │     │     ├─ types.cpython-311.pyc
   │     │     ├─ utils.cpython-311.pyc
   │     │     ├─ _compat.cpython-311.pyc
   │     │     ├─ _termui_impl.cpython-311.pyc
   │     │     ├─ _textwrap.cpython-311.pyc
   │     │     ├─ _utils.cpython-311.pyc
   │     │     ├─ _winconsole.cpython-311.pyc
   │     │     └─ __init__.cpython-311.pyc
   │     ├─ click-8.3.2.dist-info
   │     │  ├─ INSTALLER
   │     │  ├─ licenses
   │     │  │  └─ LICENSE.txt
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  └─ WHEEL
   │     ├─ colorama
   │     │  ├─ ansi.py
   │     │  ├─ ansitowin32.py
   │     │  ├─ initialise.py
   │     │  ├─ tests
   │     │  │  ├─ ansitowin32_test.py
   │     │  │  ├─ ansi_test.py
   │     │  │  ├─ initialise_test.py
   │     │  │  ├─ isatty_test.py
   │     │  │  ├─ utils.py
   │     │  │  ├─ winterm_test.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ ansitowin32_test.cpython-311.pyc
   │     │  │     ├─ ansi_test.cpython-311.pyc
   │     │  │     ├─ initialise_test.cpython-311.pyc
   │     │  │     ├─ isatty_test.cpython-311.pyc
   │     │  │     ├─ utils.cpython-311.pyc
   │     │  │     ├─ winterm_test.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ win32.py
   │     │  ├─ winterm.py
   │     │  ├─ __init__.py
   │     │  └─ __pycache__
   │     │     ├─ ansi.cpython-311.pyc
   │     │     ├─ ansitowin32.cpython-311.pyc
   │     │     ├─ initialise.cpython-311.pyc
   │     │     ├─ win32.cpython-311.pyc
   │     │     ├─ winterm.cpython-311.pyc
   │     │     └─ __init__.cpython-311.pyc
   │     ├─ colorama-0.4.6.dist-info
   │     │  ├─ INSTALLER
   │     │  ├─ licenses
   │     │  │  └─ LICENSE.txt
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  └─ WHEEL
   │     ├─ dateutil
   │     │  ├─ easter.py
   │     │  ├─ parser
   │     │  │  ├─ isoparser.py
   │     │  │  ├─ _parser.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ isoparser.cpython-311.pyc
   │     │  │     ├─ _parser.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ relativedelta.py
   │     │  ├─ rrule.py
   │     │  ├─ tz
   │     │  │  ├─ tz.py
   │     │  │  ├─ win.py
   │     │  │  ├─ _common.py
   │     │  │  ├─ _factories.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ tz.cpython-311.pyc
   │     │  │     ├─ win.cpython-311.pyc
   │     │  │     ├─ _common.cpython-311.pyc
   │     │  │     ├─ _factories.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ tzwin.py
   │     │  ├─ utils.py
   │     │  ├─ zoneinfo
   │     │  │  ├─ dateutil-zoneinfo.tar.gz
   │     │  │  ├─ rebuild.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ rebuild.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ _common.py
   │     │  ├─ _version.py
   │     │  ├─ __init__.py
   │     │  └─ __pycache__
   │     │     ├─ easter.cpython-311.pyc
   │     │     ├─ relativedelta.cpython-311.pyc
   │     │     ├─ rrule.cpython-311.pyc
   │     │     ├─ tzwin.cpython-311.pyc
   │     │     ├─ utils.cpython-311.pyc
   │     │     ├─ _common.cpython-311.pyc
   │     │     ├─ _version.cpython-311.pyc
   │     │     └─ __init__.cpython-311.pyc
   │     ├─ distro
   │     │  ├─ distro.py
   │     │  ├─ py.typed
   │     │  ├─ __init__.py
   │     │  ├─ __main__.py
   │     │  └─ __pycache__
   │     │     ├─ distro.cpython-311.pyc
   │     │     ├─ __init__.cpython-311.pyc
   │     │     └─ __main__.cpython-311.pyc
   │     ├─ distro-1.9.0.dist-info
   │     │  ├─ entry_points.txt
   │     │  ├─ INSTALLER
   │     │  ├─ LICENSE
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  ├─ top_level.txt
   │     │  └─ WHEEL
   │     ├─ distutils-precedence.pth
   │     ├─ dotenv
   │     │  ├─ cli.py
   │     │  ├─ ipython.py
   │     │  ├─ main.py
   │     │  ├─ parser.py
   │     │  ├─ py.typed
   │     │  ├─ variables.py
   │     │  ├─ version.py
   │     │  ├─ __init__.py
   │     │  ├─ __main__.py
   │     │  └─ __pycache__
   │     │     ├─ cli.cpython-311.pyc
   │     │     ├─ ipython.cpython-311.pyc
   │     │     ├─ main.cpython-311.pyc
   │     │     ├─ parser.cpython-311.pyc
   │     │     ├─ variables.cpython-311.pyc
   │     │     ├─ version.cpython-311.pyc
   │     │     ├─ __init__.cpython-311.pyc
   │     │     └─ __main__.cpython-311.pyc
   │     ├─ durationpy
   │     │  ├─ duration.py
   │     │  ├─ py.typed
   │     │  ├─ __init__.py
   │     │  ├─ __init__.pyi
   │     │  └─ __pycache__
   │     │     ├─ duration.cpython-311.pyc
   │     │     └─ __init__.cpython-311.pyc
   │     ├─ durationpy-0.10.dist-info
   │     │  ├─ INSTALLER
   │     │  ├─ LICENSE
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  ├─ top_level.txt
   │     │  └─ WHEEL
   │     ├─ filelock
   │     │  ├─ asyncio.py
   │     │  ├─ py.typed
   │     │  ├─ version.py
   │     │  ├─ _api.py
   │     │  ├─ _async_read_write.py
   │     │  ├─ _error.py
   │     │  ├─ _read_write.py
   │     │  ├─ _soft.py
   │     │  ├─ _unix.py
   │     │  ├─ _util.py
   │     │  ├─ _windows.py
   │     │  ├─ __init__.py
   │     │  └─ __pycache__
   │     │     ├─ asyncio.cpython-311.pyc
   │     │     ├─ version.cpython-311.pyc
   │     │     ├─ _api.cpython-311.pyc
   │     │     ├─ _async_read_write.cpython-311.pyc
   │     │     ├─ _error.cpython-311.pyc
   │     │     ├─ _read_write.cpython-311.pyc
   │     │     ├─ _soft.cpython-311.pyc
   │     │     ├─ _unix.cpython-311.pyc
   │     │     ├─ _util.cpython-311.pyc
   │     │     ├─ _windows.cpython-311.pyc
   │     │     └─ __init__.cpython-311.pyc
   │     ├─ filelock-3.25.2.dist-info
   │     │  ├─ INSTALLER
   │     │  ├─ licenses
   │     │  │  └─ LICENSE
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  └─ WHEEL
   │     ├─ flatbuffers
   │     │  ├─ builder.py
   │     │  ├─ compat.py
   │     │  ├─ encode.py
   │     │  ├─ flexbuffers.py
   │     │  ├─ number_types.py
   │     │  ├─ packer.py
   │     │  ├─ table.py
   │     │  ├─ util.py
   │     │  ├─ _version.py
   │     │  ├─ __init__.py
   │     │  └─ __pycache__
   │     │     ├─ builder.cpython-311.pyc
   │     │     ├─ compat.cpython-311.pyc
   │     │     ├─ encode.cpython-311.pyc
   │     │     ├─ flexbuffers.cpython-311.pyc
   │     │     ├─ number_types.cpython-311.pyc
   │     │     ├─ packer.cpython-311.pyc
   │     │     ├─ table.cpython-311.pyc
   │     │     ├─ util.cpython-311.pyc
   │     │     ├─ _version.cpython-311.pyc
   │     │     └─ __init__.cpython-311.pyc
   │     ├─ flatbuffers-25.12.19.dist-info
   │     │  ├─ INSTALLER
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  ├─ top_level.txt
   │     │  └─ WHEEL
   │     ├─ fsspec
   │     │  ├─ archive.py
   │     │  ├─ asyn.py
   │     │  ├─ caching.py
   │     │  ├─ callbacks.py
   │     │  ├─ compression.py
   │     │  ├─ config.py
   │     │  ├─ conftest.py
   │     │  ├─ core.py
   │     │  ├─ dircache.py
   │     │  ├─ exceptions.py
   │     │  ├─ fuse.py
   │     │  ├─ generic.py
   │     │  ├─ gui.py
   │     │  ├─ implementations
   │     │  │  ├─ arrow.py
   │     │  │  ├─ asyn_wrapper.py
   │     │  │  ├─ cached.py
   │     │  │  ├─ cache_mapper.py
   │     │  │  ├─ cache_metadata.py
   │     │  │  ├─ chained.py
   │     │  │  ├─ dask.py
   │     │  │  ├─ data.py
   │     │  │  ├─ dbfs.py
   │     │  │  ├─ dirfs.py
   │     │  │  ├─ ftp.py
   │     │  │  ├─ gist.py
   │     │  │  ├─ git.py
   │     │  │  ├─ github.py
   │     │  │  ├─ http.py
   │     │  │  ├─ http_sync.py
   │     │  │  ├─ jupyter.py
   │     │  │  ├─ libarchive.py
   │     │  │  ├─ local.py
   │     │  │  ├─ memory.py
   │     │  │  ├─ reference.py
   │     │  │  ├─ sftp.py
   │     │  │  ├─ smb.py
   │     │  │  ├─ tar.py
   │     │  │  ├─ webhdfs.py
   │     │  │  ├─ zip.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ arrow.cpython-311.pyc
   │     │  │     ├─ asyn_wrapper.cpython-311.pyc
   │     │  │     ├─ cached.cpython-311.pyc
   │     │  │     ├─ cache_mapper.cpython-311.pyc
   │     │  │     ├─ cache_metadata.cpython-311.pyc
   │     │  │     ├─ chained.cpython-311.pyc
   │     │  │     ├─ dask.cpython-311.pyc
   │     │  │     ├─ data.cpython-311.pyc
   │     │  │     ├─ dbfs.cpython-311.pyc
   │     │  │     ├─ dirfs.cpython-311.pyc
   │     │  │     ├─ ftp.cpython-311.pyc
   │     │  │     ├─ gist.cpython-311.pyc
   │     │  │     ├─ git.cpython-311.pyc
   │     │  │     ├─ github.cpython-311.pyc
   │     │  │     ├─ http.cpython-311.pyc
   │     │  │     ├─ http_sync.cpython-311.pyc
   │     │  │     ├─ jupyter.cpython-311.pyc
   │     │  │     ├─ libarchive.cpython-311.pyc
   │     │  │     ├─ local.cpython-311.pyc
   │     │  │     ├─ memory.cpython-311.pyc
   │     │  │     ├─ reference.cpython-311.pyc
   │     │  │     ├─ sftp.cpython-311.pyc
   │     │  │     ├─ smb.cpython-311.pyc
   │     │  │     ├─ tar.cpython-311.pyc
   │     │  │     ├─ webhdfs.cpython-311.pyc
   │     │  │     ├─ zip.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ json.py
   │     │  ├─ mapping.py
   │     │  ├─ parquet.py
   │     │  ├─ registry.py
   │     │  ├─ spec.py
   │     │  ├─ tests
   │     │  │  └─ abstract
   │     │  │     ├─ common.py
   │     │  │     ├─ copy.py
   │     │  │     ├─ get.py
   │     │  │     ├─ mv.py
   │     │  │     ├─ open.py
   │     │  │     ├─ pipe.py
   │     │  │     ├─ put.py
   │     │  │     ├─ __init__.py
   │     │  │     └─ __pycache__
   │     │  │        ├─ common.cpython-311.pyc
   │     │  │        ├─ copy.cpython-311.pyc
   │     │  │        ├─ get.cpython-311.pyc
   │     │  │        ├─ mv.cpython-311.pyc
   │     │  │        ├─ open.cpython-311.pyc
   │     │  │        ├─ pipe.cpython-311.pyc
   │     │  │        ├─ put.cpython-311.pyc
   │     │  │        └─ __init__.cpython-311.pyc
   │     │  ├─ transaction.py
   │     │  ├─ utils.py
   │     │  ├─ _version.py
   │     │  ├─ __init__.py
   │     │  └─ __pycache__
   │     │     ├─ archive.cpython-311.pyc
   │     │     ├─ asyn.cpython-311.pyc
   │     │     ├─ caching.cpython-311.pyc
   │     │     ├─ callbacks.cpython-311.pyc
   │     │     ├─ compression.cpython-311.pyc
   │     │     ├─ config.cpython-311.pyc
   │     │     ├─ conftest.cpython-311.pyc
   │     │     ├─ core.cpython-311.pyc
   │     │     ├─ dircache.cpython-311.pyc
   │     │     ├─ exceptions.cpython-311.pyc
   │     │     ├─ fuse.cpython-311.pyc
   │     │     ├─ generic.cpython-311.pyc
   │     │     ├─ gui.cpython-311.pyc
   │     │     ├─ json.cpython-311.pyc
   │     │     ├─ mapping.cpython-311.pyc
   │     │     ├─ parquet.cpython-311.pyc
   │     │     ├─ registry.cpython-311.pyc
   │     │     ├─ spec.cpython-311.pyc
   │     │     ├─ transaction.cpython-311.pyc
   │     │     ├─ utils.cpython-311.pyc
   │     │     ├─ _version.cpython-311.pyc
   │     │     └─ __init__.cpython-311.pyc
   │     ├─ fsspec-2026.3.0.dist-info
   │     │  ├─ INSTALLER
   │     │  ├─ licenses
   │     │  │  └─ LICENSE
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  └─ WHEEL
   │     ├─ git
   │     │  ├─ cmd.py
   │     │  ├─ compat.py
   │     │  ├─ config.py
   │     │  ├─ db.py
   │     │  ├─ diff.py
   │     │  ├─ exc.py
   │     │  ├─ index
   │     │  │  ├─ base.py
   │     │  │  ├─ fun.py
   │     │  │  ├─ typ.py
   │     │  │  ├─ util.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ base.cpython-311.pyc
   │     │  │     ├─ fun.cpython-311.pyc
   │     │  │     ├─ typ.cpython-311.pyc
   │     │  │     ├─ util.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ objects
   │     │  │  ├─ base.py
   │     │  │  ├─ blob.py
   │     │  │  ├─ commit.py
   │     │  │  ├─ fun.py
   │     │  │  ├─ submodule
   │     │  │  │  ├─ base.py
   │     │  │  │  ├─ root.py
   │     │  │  │  ├─ util.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ base.cpython-311.pyc
   │     │  │  │     ├─ root.cpython-311.pyc
   │     │  │  │     ├─ util.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ tag.py
   │     │  │  ├─ tree.py
   │     │  │  ├─ util.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ base.cpython-311.pyc
   │     │  │     ├─ blob.cpython-311.pyc
   │     │  │     ├─ commit.cpython-311.pyc
   │     │  │     ├─ fun.cpython-311.pyc
   │     │  │     ├─ tag.cpython-311.pyc
   │     │  │     ├─ tree.cpython-311.pyc
   │     │  │     ├─ util.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ py.typed
   │     │  ├─ refs
   │     │  │  ├─ head.py
   │     │  │  ├─ log.py
   │     │  │  ├─ reference.py
   │     │  │  ├─ remote.py
   │     │  │  ├─ symbolic.py
   │     │  │  ├─ tag.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ head.cpython-311.pyc
   │     │  │     ├─ log.cpython-311.pyc
   │     │  │     ├─ reference.cpython-311.pyc
   │     │  │     ├─ remote.cpython-311.pyc
   │     │  │     ├─ symbolic.cpython-311.pyc
   │     │  │     ├─ tag.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ remote.py
   │     │  ├─ repo
   │     │  │  ├─ base.py
   │     │  │  ├─ fun.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ base.cpython-311.pyc
   │     │  │     ├─ fun.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ types.py
   │     │  ├─ util.py
   │     │  ├─ __init__.py
   │     │  └─ __pycache__
   │     │     ├─ cmd.cpython-311.pyc
   │     │     ├─ compat.cpython-311.pyc
   │     │     ├─ config.cpython-311.pyc
   │     │     ├─ db.cpython-311.pyc
   │     │     ├─ diff.cpython-311.pyc
   │     │     ├─ exc.cpython-311.pyc
   │     │     ├─ remote.cpython-311.pyc
   │     │     ├─ types.cpython-311.pyc
   │     │     ├─ util.cpython-311.pyc
   │     │     └─ __init__.cpython-311.pyc
   │     ├─ gitdb
   │     │  ├─ base.py
   │     │  ├─ const.py
   │     │  ├─ db
   │     │  │  ├─ base.py
   │     │  │  ├─ git.py
   │     │  │  ├─ loose.py
   │     │  │  ├─ mem.py
   │     │  │  ├─ pack.py
   │     │  │  ├─ ref.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ base.cpython-311.pyc
   │     │  │     ├─ git.cpython-311.pyc
   │     │  │     ├─ loose.cpython-311.pyc
   │     │  │     ├─ mem.cpython-311.pyc
   │     │  │     ├─ pack.cpython-311.pyc
   │     │  │     ├─ ref.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ exc.py
   │     │  ├─ fun.py
   │     │  ├─ pack.py
   │     │  ├─ stream.py
   │     │  ├─ test
   │     │  │  ├─ lib.py
   │     │  │  ├─ test_base.py
   │     │  │  ├─ test_example.py
   │     │  │  ├─ test_pack.py
   │     │  │  ├─ test_stream.py
   │     │  │  ├─ test_util.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ lib.cpython-311.pyc
   │     │  │     ├─ test_base.cpython-311.pyc
   │     │  │     ├─ test_example.cpython-311.pyc
   │     │  │     ├─ test_pack.cpython-311.pyc
   │     │  │     ├─ test_stream.cpython-311.pyc
   │     │  │     ├─ test_util.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ typ.py
   │     │  ├─ util.py
   │     │  ├─ utils
   │     │  │  ├─ encoding.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ encoding.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ __init__.py
   │     │  └─ __pycache__
   │     │     ├─ base.cpython-311.pyc
   │     │     ├─ const.cpython-311.pyc
   │     │     ├─ exc.cpython-311.pyc
   │     │     ├─ fun.cpython-311.pyc
   │     │     ├─ pack.cpython-311.pyc
   │     │     ├─ stream.cpython-311.pyc
   │     │     ├─ typ.cpython-311.pyc
   │     │     ├─ util.cpython-311.pyc
   │     │     └─ __init__.cpython-311.pyc
   │     ├─ gitdb-4.0.12.dist-info
   │     │  ├─ AUTHORS
   │     │  ├─ INSTALLER
   │     │  ├─ LICENSE
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  ├─ top_level.txt
   │     │  └─ WHEEL
   │     ├─ gitpython-3.1.46.dist-info
   │     │  ├─ INSTALLER
   │     │  ├─ licenses
   │     │  │  ├─ AUTHORS
   │     │  │  └─ LICENSE
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  ├─ top_level.txt
   │     │  └─ WHEEL
   │     ├─ google
   │     │  ├─ api
   │     │  │  ├─ annotations.proto
   │     │  │  ├─ annotations_pb2.py
   │     │  │  ├─ annotations_pb2.pyi
   │     │  │  ├─ auth.proto
   │     │  │  ├─ auth_pb2.py
   │     │  │  ├─ auth_pb2.pyi
   │     │  │  ├─ backend.proto
   │     │  │  ├─ backend_pb2.py
   │     │  │  ├─ backend_pb2.pyi
   │     │  │  ├─ billing.proto
   │     │  │  ├─ billing_pb2.py
   │     │  │  ├─ billing_pb2.pyi
   │     │  │  ├─ client.proto
   │     │  │  ├─ client_pb2.py
   │     │  │  ├─ client_pb2.pyi
   │     │  │  ├─ config_change.proto
   │     │  │  ├─ config_change_pb2.py
   │     │  │  ├─ config_change_pb2.pyi
   │     │  │  ├─ consumer.proto
   │     │  │  ├─ consumer_pb2.py
   │     │  │  ├─ consumer_pb2.pyi
   │     │  │  ├─ context.proto
   │     │  │  ├─ context_pb2.py
   │     │  │  ├─ context_pb2.pyi
   │     │  │  ├─ control.proto
   │     │  │  ├─ control_pb2.py
   │     │  │  ├─ control_pb2.pyi
   │     │  │  ├─ distribution.proto
   │     │  │  ├─ distribution_pb2.py
   │     │  │  ├─ distribution_pb2.pyi
   │     │  │  ├─ documentation.proto
   │     │  │  ├─ documentation_pb2.py
   │     │  │  ├─ documentation_pb2.pyi
   │     │  │  ├─ endpoint.proto
   │     │  │  ├─ endpoint_pb2.py
   │     │  │  ├─ endpoint_pb2.pyi
   │     │  │  ├─ error_reason.proto
   │     │  │  ├─ error_reason_pb2.py
   │     │  │  ├─ error_reason_pb2.pyi
   │     │  │  ├─ field_behavior.proto
   │     │  │  ├─ field_behavior_pb2.py
   │     │  │  ├─ field_behavior_pb2.pyi
   │     │  │  ├─ field_info.proto
   │     │  │  ├─ field_info_pb2.py
   │     │  │  ├─ field_info_pb2.pyi
   │     │  │  ├─ http.proto
   │     │  │  ├─ httpbody.proto
   │     │  │  ├─ httpbody_pb2.py
   │     │  │  ├─ httpbody_pb2.pyi
   │     │  │  ├─ http_pb2.py
   │     │  │  ├─ http_pb2.pyi
   │     │  │  ├─ label.proto
   │     │  │  ├─ label_pb2.py
   │     │  │  ├─ label_pb2.pyi
   │     │  │  ├─ launch_stage.proto
   │     │  │  ├─ launch_stage_pb2.py
   │     │  │  ├─ launch_stage_pb2.pyi
   │     │  │  ├─ log.proto
   │     │  │  ├─ logging.proto
   │     │  │  ├─ logging_pb2.py
   │     │  │  ├─ logging_pb2.pyi
   │     │  │  ├─ log_pb2.py
   │     │  │  ├─ log_pb2.pyi
   │     │  │  ├─ metric.proto
   │     │  │  ├─ metric_pb2.py
   │     │  │  ├─ metric_pb2.pyi
   │     │  │  ├─ monitored_resource.proto
   │     │  │  ├─ monitored_resource_pb2.py
   │     │  │  ├─ monitored_resource_pb2.pyi
   │     │  │  ├─ monitoring.proto
   │     │  │  ├─ monitoring_pb2.py
   │     │  │  ├─ monitoring_pb2.pyi
   │     │  │  ├─ policy.proto
   │     │  │  ├─ policy_pb2.py
   │     │  │  ├─ policy_pb2.pyi
   │     │  │  ├─ quota.proto
   │     │  │  ├─ quota_pb2.py
   │     │  │  ├─ quota_pb2.pyi
   │     │  │  ├─ resource.proto
   │     │  │  ├─ resource_pb2.py
   │     │  │  ├─ resource_pb2.pyi
   │     │  │  ├─ routing.proto
   │     │  │  ├─ routing_pb2.py
   │     │  │  ├─ routing_pb2.pyi
   │     │  │  ├─ service.proto
   │     │  │  ├─ service_pb2.py
   │     │  │  ├─ service_pb2.pyi
   │     │  │  ├─ source_info.proto
   │     │  │  ├─ source_info_pb2.py
   │     │  │  ├─ source_info_pb2.pyi
   │     │  │  ├─ system_parameter.proto
   │     │  │  ├─ system_parameter_pb2.py
   │     │  │  ├─ system_parameter_pb2.pyi
   │     │  │  ├─ usage.proto
   │     │  │  ├─ usage_pb2.py
   │     │  │  ├─ usage_pb2.pyi
   │     │  │  ├─ visibility.proto
   │     │  │  ├─ visibility_pb2.py
   │     │  │  ├─ visibility_pb2.pyi
   │     │  │  └─ __pycache__
   │     │  │     ├─ annotations_pb2.cpython-311.pyc
   │     │  │     ├─ auth_pb2.cpython-311.pyc
   │     │  │     ├─ backend_pb2.cpython-311.pyc
   │     │  │     ├─ billing_pb2.cpython-311.pyc
   │     │  │     ├─ client_pb2.cpython-311.pyc
   │     │  │     ├─ config_change_pb2.cpython-311.pyc
   │     │  │     ├─ consumer_pb2.cpython-311.pyc
   │     │  │     ├─ context_pb2.cpython-311.pyc
   │     │  │     ├─ control_pb2.cpython-311.pyc
   │     │  │     ├─ distribution_pb2.cpython-311.pyc
   │     │  │     ├─ documentation_pb2.cpython-311.pyc
   │     │  │     ├─ endpoint_pb2.cpython-311.pyc
   │     │  │     ├─ error_reason_pb2.cpython-311.pyc
   │     │  │     ├─ field_behavior_pb2.cpython-311.pyc
   │     │  │     ├─ field_info_pb2.cpython-311.pyc
   │     │  │     ├─ httpbody_pb2.cpython-311.pyc
   │     │  │     ├─ http_pb2.cpython-311.pyc
   │     │  │     ├─ label_pb2.cpython-311.pyc
   │     │  │     ├─ launch_stage_pb2.cpython-311.pyc
   │     │  │     ├─ logging_pb2.cpython-311.pyc
   │     │  │     ├─ log_pb2.cpython-311.pyc
   │     │  │     ├─ metric_pb2.cpython-311.pyc
   │     │  │     ├─ monitored_resource_pb2.cpython-311.pyc
   │     │  │     ├─ monitoring_pb2.cpython-311.pyc
   │     │  │     ├─ policy_pb2.cpython-311.pyc
   │     │  │     ├─ quota_pb2.cpython-311.pyc
   │     │  │     ├─ resource_pb2.cpython-311.pyc
   │     │  │     ├─ routing_pb2.cpython-311.pyc
   │     │  │     ├─ service_pb2.cpython-311.pyc
   │     │  │     ├─ source_info_pb2.cpython-311.pyc
   │     │  │     ├─ system_parameter_pb2.cpython-311.pyc
   │     │  │     ├─ usage_pb2.cpython-311.pyc
   │     │  │     └─ visibility_pb2.cpython-311.pyc
   │     │  ├─ cloud
   │     │  │  ├─ common_resources.proto
   │     │  │  ├─ common_resources_pb2.py
   │     │  │  ├─ common_resources_pb2.pyi
   │     │  │  ├─ extended_operations.proto
   │     │  │  ├─ extended_operations_pb2.py
   │     │  │  ├─ extended_operations_pb2.pyi
   │     │  │  ├─ location
   │     │  │  │  ├─ locations.proto
   │     │  │  │  ├─ locations_pb2.py
   │     │  │  │  ├─ locations_pb2.pyi
   │     │  │  │  └─ __pycache__
   │     │  │  │     └─ locations_pb2.cpython-311.pyc
   │     │  │  └─ __pycache__
   │     │  │     ├─ common_resources_pb2.cpython-311.pyc
   │     │  │     └─ extended_operations_pb2.cpython-311.pyc
   │     │  ├─ gapic
   │     │  │  └─ metadata
   │     │  │     ├─ gapic_metadata.proto
   │     │  │     ├─ gapic_metadata_pb2.py
   │     │  │     ├─ gapic_metadata_pb2.pyi
   │     │  │     └─ __pycache__
   │     │  │        └─ gapic_metadata_pb2.cpython-311.pyc
   │     │  ├─ logging
   │     │  │  └─ type
   │     │  │     ├─ http_request.proto
   │     │  │     ├─ http_request_pb2.py
   │     │  │     ├─ http_request_pb2.pyi
   │     │  │     ├─ log_severity.proto
   │     │  │     ├─ log_severity_pb2.py
   │     │  │     ├─ log_severity_pb2.pyi
   │     │  │     └─ __pycache__
   │     │  │        ├─ http_request_pb2.cpython-311.pyc
   │     │  │        └─ log_severity_pb2.cpython-311.pyc
   │     │  ├─ longrunning
   │     │  │  ├─ operations_grpc.py
   │     │  │  ├─ operations_grpc_pb2.py
   │     │  │  ├─ operations_pb2.py
   │     │  │  ├─ operations_pb2_grpc.py
   │     │  │  ├─ operations_proto.proto
   │     │  │  ├─ operations_proto.py
   │     │  │  ├─ operations_proto_pb2.py
   │     │  │  ├─ operations_proto_pb2.pyi
   │     │  │  └─ __pycache__
   │     │  │     ├─ operations_grpc.cpython-311.pyc
   │     │  │     ├─ operations_grpc_pb2.cpython-311.pyc
   │     │  │     ├─ operations_pb2.cpython-311.pyc
   │     │  │     ├─ operations_pb2_grpc.cpython-311.pyc
   │     │  │     ├─ operations_proto.cpython-311.pyc
   │     │  │     └─ operations_proto_pb2.cpython-311.pyc
   │     │  ├─ protobuf
   │     │  │  ├─ any.py
   │     │  │  ├─ any_pb2.py
   │     │  │  ├─ api_pb2.py
   │     │  │  ├─ compiler
   │     │  │  │  ├─ plugin_pb2.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ plugin_pb2.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ descriptor.py
   │     │  │  ├─ descriptor_database.py
   │     │  │  ├─ descriptor_pb2.py
   │     │  │  ├─ descriptor_pool.py
   │     │  │  ├─ duration.py
   │     │  │  ├─ duration_pb2.py
   │     │  │  ├─ empty_pb2.py
   │     │  │  ├─ field_mask_pb2.py
   │     │  │  ├─ internal
   │     │  │  │  ├─ api_implementation.py
   │     │  │  │  ├─ builder.py
   │     │  │  │  ├─ containers.py
   │     │  │  │  ├─ decoder.py
   │     │  │  │  ├─ encoder.py
   │     │  │  │  ├─ enum_type_wrapper.py
   │     │  │  │  ├─ extension_dict.py
   │     │  │  │  ├─ field_mask.py
   │     │  │  │  ├─ message_listener.py
   │     │  │  │  ├─ python_edition_defaults.py
   │     │  │  │  ├─ python_message.py
   │     │  │  │  ├─ testing_refleaks.py
   │     │  │  │  ├─ type_checkers.py
   │     │  │  │  ├─ well_known_types.py
   │     │  │  │  ├─ wire_format.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ api_implementation.cpython-311.pyc
   │     │  │  │     ├─ builder.cpython-311.pyc
   │     │  │  │     ├─ containers.cpython-311.pyc
   │     │  │  │     ├─ decoder.cpython-311.pyc
   │     │  │  │     ├─ encoder.cpython-311.pyc
   │     │  │  │     ├─ enum_type_wrapper.cpython-311.pyc
   │     │  │  │     ├─ extension_dict.cpython-311.pyc
   │     │  │  │     ├─ field_mask.cpython-311.pyc
   │     │  │  │     ├─ message_listener.cpython-311.pyc
   │     │  │  │     ├─ python_edition_defaults.cpython-311.pyc
   │     │  │  │     ├─ python_message.cpython-311.pyc
   │     │  │  │     ├─ testing_refleaks.cpython-311.pyc
   │     │  │  │     ├─ type_checkers.cpython-311.pyc
   │     │  │  │     ├─ well_known_types.cpython-311.pyc
   │     │  │  │     ├─ wire_format.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ json_format.py
   │     │  │  ├─ message.py
   │     │  │  ├─ message_factory.py
   │     │  │  ├─ proto.py
   │     │  │  ├─ proto_builder.py
   │     │  │  ├─ proto_json.py
   │     │  │  ├─ proto_text.py
   │     │  │  ├─ pyext
   │     │  │  │  ├─ cpp_message.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ cpp_message.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ reflection.py
   │     │  │  ├─ runtime_version.py
   │     │  │  ├─ service_reflection.py
   │     │  │  ├─ source_context_pb2.py
   │     │  │  ├─ struct_pb2.py
   │     │  │  ├─ symbol_database.py
   │     │  │  ├─ testdata
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ text_encoding.py
   │     │  │  ├─ text_format.py
   │     │  │  ├─ timestamp.py
   │     │  │  ├─ timestamp_pb2.py
   │     │  │  ├─ type_pb2.py
   │     │  │  ├─ unknown_fields.py
   │     │  │  ├─ util
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ wrappers_pb2.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ any.cpython-311.pyc
   │     │  │     ├─ any_pb2.cpython-311.pyc
   │     │  │     ├─ api_pb2.cpython-311.pyc
   │     │  │     ├─ descriptor.cpython-311.pyc
   │     │  │     ├─ descriptor_database.cpython-311.pyc
   │     │  │     ├─ descriptor_pb2.cpython-311.pyc
   │     │  │     ├─ descriptor_pool.cpython-311.pyc
   │     │  │     ├─ duration.cpython-311.pyc
   │     │  │     ├─ duration_pb2.cpython-311.pyc
   │     │  │     ├─ empty_pb2.cpython-311.pyc
   │     │  │     ├─ field_mask_pb2.cpython-311.pyc
   │     │  │     ├─ json_format.cpython-311.pyc
   │     │  │     ├─ message.cpython-311.pyc
   │     │  │     ├─ message_factory.cpython-311.pyc
   │     │  │     ├─ proto.cpython-311.pyc
   │     │  │     ├─ proto_builder.cpython-311.pyc
   │     │  │     ├─ proto_json.cpython-311.pyc
   │     │  │     ├─ proto_text.cpython-311.pyc
   │     │  │     ├─ reflection.cpython-311.pyc
   │     │  │     ├─ runtime_version.cpython-311.pyc
   │     │  │     ├─ service_reflection.cpython-311.pyc
   │     │  │     ├─ source_context_pb2.cpython-311.pyc
   │     │  │     ├─ struct_pb2.cpython-311.pyc
   │     │  │     ├─ symbol_database.cpython-311.pyc
   │     │  │     ├─ text_encoding.cpython-311.pyc
   │     │  │     ├─ text_format.cpython-311.pyc
   │     │  │     ├─ timestamp.cpython-311.pyc
   │     │  │     ├─ timestamp_pb2.cpython-311.pyc
   │     │  │     ├─ type_pb2.cpython-311.pyc
   │     │  │     ├─ unknown_fields.cpython-311.pyc
   │     │  │     ├─ wrappers_pb2.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ rpc
   │     │  │  ├─ code.proto
   │     │  │  ├─ code_pb2.py
   │     │  │  ├─ code_pb2.pyi
   │     │  │  ├─ context
   │     │  │  │  ├─ attribute_context.proto
   │     │  │  │  ├─ attribute_context_pb2.py
   │     │  │  │  ├─ attribute_context_pb2.pyi
   │     │  │  │  ├─ audit_context.proto
   │     │  │  │  ├─ audit_context_pb2.py
   │     │  │  │  ├─ audit_context_pb2.pyi
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ attribute_context_pb2.cpython-311.pyc
   │     │  │  │     └─ audit_context_pb2.cpython-311.pyc
   │     │  │  ├─ error_details.proto
   │     │  │  ├─ error_details_pb2.py
   │     │  │  ├─ error_details_pb2.pyi
   │     │  │  ├─ http.proto
   │     │  │  ├─ http_pb2.py
   │     │  │  ├─ http_pb2.pyi
   │     │  │  ├─ status.proto
   │     │  │  ├─ status_pb2.py
   │     │  │  ├─ status_pb2.pyi
   │     │  │  └─ __pycache__
   │     │  │     ├─ code_pb2.cpython-311.pyc
   │     │  │     ├─ error_details_pb2.cpython-311.pyc
   │     │  │     ├─ http_pb2.cpython-311.pyc
   │     │  │     └─ status_pb2.cpython-311.pyc
   │     │  ├─ type
   │     │  │  ├─ calendar_period.proto
   │     │  │  ├─ calendar_period_pb2.py
   │     │  │  ├─ calendar_period_pb2.pyi
   │     │  │  ├─ color.proto
   │     │  │  ├─ color_pb2.py
   │     │  │  ├─ color_pb2.pyi
   │     │  │  ├─ date.proto
   │     │  │  ├─ datetime.proto
   │     │  │  ├─ datetime_pb2.py
   │     │  │  ├─ datetime_pb2.pyi
   │     │  │  ├─ date_pb2.py
   │     │  │  ├─ date_pb2.pyi
   │     │  │  ├─ dayofweek.proto
   │     │  │  ├─ dayofweek_pb2.py
   │     │  │  ├─ dayofweek_pb2.pyi
   │     │  │  ├─ decimal.proto
   │     │  │  ├─ decimal_pb2.py
   │     │  │  ├─ decimal_pb2.pyi
   │     │  │  ├─ expr.proto
   │     │  │  ├─ expr_pb2.py
   │     │  │  ├─ expr_pb2.pyi
   │     │  │  ├─ fraction.proto
   │     │  │  ├─ fraction_pb2.py
   │     │  │  ├─ fraction_pb2.pyi
   │     │  │  ├─ interval.proto
   │     │  │  ├─ interval_pb2.py
   │     │  │  ├─ interval_pb2.pyi
   │     │  │  ├─ latlng.proto
   │     │  │  ├─ latlng_pb2.py
   │     │  │  ├─ latlng_pb2.pyi
   │     │  │  ├─ localized_text.proto
   │     │  │  ├─ localized_text_pb2.py
   │     │  │  ├─ localized_text_pb2.pyi
   │     │  │  ├─ money.proto
   │     │  │  ├─ money_pb2.py
   │     │  │  ├─ money_pb2.pyi
   │     │  │  ├─ month.proto
   │     │  │  ├─ month_pb2.py
   │     │  │  ├─ month_pb2.pyi
   │     │  │  ├─ phone_number.proto
   │     │  │  ├─ phone_number_pb2.py
   │     │  │  ├─ phone_number_pb2.pyi
   │     │  │  ├─ postal_address.proto
   │     │  │  ├─ postal_address_pb2.py
   │     │  │  ├─ postal_address_pb2.pyi
   │     │  │  ├─ quaternion.proto
   │     │  │  ├─ quaternion_pb2.py
   │     │  │  ├─ quaternion_pb2.pyi
   │     │  │  ├─ timeofday.proto
   │     │  │  ├─ timeofday_pb2.py
   │     │  │  ├─ timeofday_pb2.pyi
   │     │  │  └─ __pycache__
   │     │  │     ├─ calendar_period_pb2.cpython-311.pyc
   │     │  │     ├─ color_pb2.cpython-311.pyc
   │     │  │     ├─ datetime_pb2.cpython-311.pyc
   │     │  │     ├─ date_pb2.cpython-311.pyc
   │     │  │     ├─ dayofweek_pb2.cpython-311.pyc
   │     │  │     ├─ decimal_pb2.cpython-311.pyc
   │     │  │     ├─ expr_pb2.cpython-311.pyc
   │     │  │     ├─ fraction_pb2.cpython-311.pyc
   │     │  │     ├─ interval_pb2.cpython-311.pyc
   │     │  │     ├─ latlng_pb2.cpython-311.pyc
   │     │  │     ├─ localized_text_pb2.cpython-311.pyc
   │     │  │     ├─ money_pb2.cpython-311.pyc
   │     │  │     ├─ month_pb2.cpython-311.pyc
   │     │  │     ├─ phone_number_pb2.cpython-311.pyc
   │     │  │     ├─ postal_address_pb2.cpython-311.pyc
   │     │  │     ├─ quaternion_pb2.cpython-311.pyc
   │     │  │     └─ timeofday_pb2.cpython-311.pyc
   │     │  └─ _upb
   │     │     └─ _message.pyd
   │     ├─ googleapis_common_protos-1.74.0.dist-info
   │     │  ├─ INSTALLER
   │     │  ├─ licenses
   │     │  │  └─ LICENSE
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  ├─ top_level.txt
   │     │  └─ WHEEL
   │     ├─ groq
   │     │  ├─ lib
   │     │  │  └─ .keep
   │     │  ├─ py.typed
   │     │  ├─ resources
   │     │  │  ├─ audio
   │     │  │  │  ├─ audio.py
   │     │  │  │  ├─ speech.py
   │     │  │  │  ├─ transcriptions.py
   │     │  │  │  ├─ translations.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ audio.cpython-311.pyc
   │     │  │  │     ├─ speech.cpython-311.pyc
   │     │  │  │     ├─ transcriptions.cpython-311.pyc
   │     │  │  │     ├─ translations.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ batches.py
   │     │  │  ├─ chat
   │     │  │  │  ├─ chat.py
   │     │  │  │  ├─ completions.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ chat.cpython-311.pyc
   │     │  │  │     ├─ completions.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ embeddings.py
   │     │  │  ├─ files.py
   │     │  │  ├─ models.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ batches.cpython-311.pyc
   │     │  │     ├─ embeddings.cpython-311.pyc
   │     │  │     ├─ files.cpython-311.pyc
   │     │  │     ├─ models.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ types
   │     │  │  ├─ audio
   │     │  │  │  ├─ speech_create_params.py
   │     │  │  │  ├─ transcription.py
   │     │  │  │  ├─ transcription_create_params.py
   │     │  │  │  ├─ translation.py
   │     │  │  │  ├─ translation_create_params.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ speech_create_params.cpython-311.pyc
   │     │  │  │     ├─ transcription.cpython-311.pyc
   │     │  │  │     ├─ transcription_create_params.cpython-311.pyc
   │     │  │  │     ├─ translation.cpython-311.pyc
   │     │  │  │     ├─ translation_create_params.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ batch_cancel_response.py
   │     │  │  ├─ batch_create_params.py
   │     │  │  ├─ batch_create_response.py
   │     │  │  ├─ batch_list_response.py
   │     │  │  ├─ batch_retrieve_response.py
   │     │  │  ├─ chat
   │     │  │  │  ├─ chat_completion.py
   │     │  │  │  ├─ chat_completion_assistant_message_param.py
   │     │  │  │  ├─ chat_completion_chunk.py
   │     │  │  │  ├─ chat_completion_content_part_image_param.py
   │     │  │  │  ├─ chat_completion_content_part_param.py
   │     │  │  │  ├─ chat_completion_content_part_text_param.py
   │     │  │  │  ├─ chat_completion_function_call_option_param.py
   │     │  │  │  ├─ chat_completion_function_message_param.py
   │     │  │  │  ├─ chat_completion_message.py
   │     │  │  │  ├─ chat_completion_message_param.py
   │     │  │  │  ├─ chat_completion_message_tool_call.py
   │     │  │  │  ├─ chat_completion_message_tool_call_param.py
   │     │  │  │  ├─ chat_completion_named_tool_choice_param.py
   │     │  │  │  ├─ chat_completion_role.py
   │     │  │  │  ├─ chat_completion_system_message_param.py
   │     │  │  │  ├─ chat_completion_token_logprob.py
   │     │  │  │  ├─ chat_completion_tool_choice_option_param.py
   │     │  │  │  ├─ chat_completion_tool_message_param.py
   │     │  │  │  ├─ chat_completion_tool_param.py
   │     │  │  │  ├─ chat_completion_user_message_param.py
   │     │  │  │  ├─ completion_create_params.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ chat_completion.cpython-311.pyc
   │     │  │  │     ├─ chat_completion_assistant_message_param.cpython-311.pyc
   │     │  │  │     ├─ chat_completion_chunk.cpython-311.pyc
   │     │  │  │     ├─ chat_completion_content_part_image_param.cpython-311.pyc
   │     │  │  │     ├─ chat_completion_content_part_param.cpython-311.pyc
   │     │  │  │     ├─ chat_completion_content_part_text_param.cpython-311.pyc
   │     │  │  │     ├─ chat_completion_function_call_option_param.cpython-311.pyc
   │     │  │  │     ├─ chat_completion_function_message_param.cpython-311.pyc
   │     │  │  │     ├─ chat_completion_message.cpython-311.pyc
   │     │  │  │     ├─ chat_completion_message_param.cpython-311.pyc
   │     │  │  │     ├─ chat_completion_message_tool_call.cpython-311.pyc
   │     │  │  │     ├─ chat_completion_message_tool_call_param.cpython-311.pyc
   │     │  │  │     ├─ chat_completion_named_tool_choice_param.cpython-311.pyc
   │     │  │  │     ├─ chat_completion_role.cpython-311.pyc
   │     │  │  │     ├─ chat_completion_system_message_param.cpython-311.pyc
   │     │  │  │     ├─ chat_completion_token_logprob.cpython-311.pyc
   │     │  │  │     ├─ chat_completion_tool_choice_option_param.cpython-311.pyc
   │     │  │  │     ├─ chat_completion_tool_message_param.cpython-311.pyc
   │     │  │  │     ├─ chat_completion_tool_param.cpython-311.pyc
   │     │  │  │     ├─ chat_completion_user_message_param.cpython-311.pyc
   │     │  │  │     ├─ completion_create_params.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ completion_usage.py
   │     │  │  ├─ create_embedding_response.py
   │     │  │  ├─ embedding.py
   │     │  │  ├─ embedding_create_params.py
   │     │  │  ├─ file_create_params.py
   │     │  │  ├─ file_create_response.py
   │     │  │  ├─ file_delete_response.py
   │     │  │  ├─ file_info_response.py
   │     │  │  ├─ file_list_response.py
   │     │  │  ├─ model.py
   │     │  │  ├─ model_deleted.py
   │     │  │  ├─ model_list_response.py
   │     │  │  ├─ shared
   │     │  │  │  ├─ error_object.py
   │     │  │  │  ├─ function_definition.py
   │     │  │  │  ├─ function_parameters.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ error_object.cpython-311.pyc
   │     │  │  │     ├─ function_definition.cpython-311.pyc
   │     │  │  │     ├─ function_parameters.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ shared_params
   │     │  │  │  ├─ function_definition.py
   │     │  │  │  ├─ function_parameters.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ function_definition.cpython-311.pyc
   │     │  │  │     ├─ function_parameters.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ batch_cancel_response.cpython-311.pyc
   │     │  │     ├─ batch_create_params.cpython-311.pyc
   │     │  │     ├─ batch_create_response.cpython-311.pyc
   │     │  │     ├─ batch_list_response.cpython-311.pyc
   │     │  │     ├─ batch_retrieve_response.cpython-311.pyc
   │     │  │     ├─ completion_usage.cpython-311.pyc
   │     │  │     ├─ create_embedding_response.cpython-311.pyc
   │     │  │     ├─ embedding.cpython-311.pyc
   │     │  │     ├─ embedding_create_params.cpython-311.pyc
   │     │  │     ├─ file_create_params.cpython-311.pyc
   │     │  │     ├─ file_create_response.cpython-311.pyc
   │     │  │     ├─ file_delete_response.cpython-311.pyc
   │     │  │     ├─ file_info_response.cpython-311.pyc
   │     │  │     ├─ file_list_response.cpython-311.pyc
   │     │  │     ├─ model.cpython-311.pyc
   │     │  │     ├─ model_deleted.cpython-311.pyc
   │     │  │     ├─ model_list_response.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ _base_client.py
   │     │  ├─ _client.py
   │     │  ├─ _compat.py
   │     │  ├─ _constants.py
   │     │  ├─ _exceptions.py
   │     │  ├─ _files.py
   │     │  ├─ _models.py
   │     │  ├─ _qs.py
   │     │  ├─ _resource.py
   │     │  ├─ _response.py
   │     │  ├─ _streaming.py
   │     │  ├─ _types.py
   │     │  ├─ _utils
   │     │  │  ├─ _compat.py
   │     │  │  ├─ _datetime_parse.py
   │     │  │  ├─ _json.py
   │     │  │  ├─ _logs.py
   │     │  │  ├─ _path.py
   │     │  │  ├─ _proxy.py
   │     │  │  ├─ _reflection.py
   │     │  │  ├─ _resources_proxy.py
   │     │  │  ├─ _streams.py
   │     │  │  ├─ _sync.py
   │     │  │  ├─ _transform.py
   │     │  │  ├─ _typing.py
   │     │  │  ├─ _utils.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ _compat.cpython-311.pyc
   │     │  │     ├─ _datetime_parse.cpython-311.pyc
   │     │  │     ├─ _json.cpython-311.pyc
   │     │  │     ├─ _logs.cpython-311.pyc
   │     │  │     ├─ _path.cpython-311.pyc
   │     │  │     ├─ _proxy.cpython-311.pyc
   │     │  │     ├─ _reflection.cpython-311.pyc
   │     │  │     ├─ _resources_proxy.cpython-311.pyc
   │     │  │     ├─ _streams.cpython-311.pyc
   │     │  │     ├─ _sync.cpython-311.pyc
   │     │  │     ├─ _transform.cpython-311.pyc
   │     │  │     ├─ _typing.cpython-311.pyc
   │     │  │     ├─ _utils.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ _version.py
   │     │  ├─ __init__.py
   │     │  └─ __pycache__
   │     │     ├─ _base_client.cpython-311.pyc
   │     │     ├─ _client.cpython-311.pyc
   │     │     ├─ _compat.cpython-311.pyc
   │     │     ├─ _constants.cpython-311.pyc
   │     │     ├─ _exceptions.cpython-311.pyc
   │     │     ├─ _files.cpython-311.pyc
   │     │     ├─ _models.cpython-311.pyc
   │     │     ├─ _qs.cpython-311.pyc
   │     │     ├─ _resource.cpython-311.pyc
   │     │     ├─ _response.cpython-311.pyc
   │     │     ├─ _streaming.cpython-311.pyc
   │     │     ├─ _types.cpython-311.pyc
   │     │     ├─ _version.cpython-311.pyc
   │     │     └─ __init__.cpython-311.pyc
   │     ├─ groq-1.1.2.dist-info
   │     │  ├─ INSTALLER
   │     │  ├─ licenses
   │     │  │  └─ LICENSE
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  ├─ REQUESTED
   │     │  └─ WHEEL
   │     ├─ grpc
   │     │  ├─ aio
   │     │  │  ├─ _base_call.py
   │     │  │  ├─ _base_channel.py
   │     │  │  ├─ _base_server.py
   │     │  │  ├─ _call.py
   │     │  │  ├─ _channel.py
   │     │  │  ├─ _interceptor.py
   │     │  │  ├─ _metadata.py
   │     │  │  ├─ _server.py
   │     │  │  ├─ _typing.py
   │     │  │  ├─ _utils.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ _base_call.cpython-311.pyc
   │     │  │     ├─ _base_channel.cpython-311.pyc
   │     │  │     ├─ _base_server.cpython-311.pyc
   │     │  │     ├─ _call.cpython-311.pyc
   │     │  │     ├─ _channel.cpython-311.pyc
   │     │  │     ├─ _interceptor.cpython-311.pyc
   │     │  │     ├─ _metadata.cpython-311.pyc
   │     │  │     ├─ _server.cpython-311.pyc
   │     │  │     ├─ _typing.cpython-311.pyc
   │     │  │     ├─ _utils.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ beta
   │     │  │  ├─ implementations.py
   │     │  │  ├─ interfaces.py
   │     │  │  ├─ utilities.py
   │     │  │  ├─ _client_adaptations.py
   │     │  │  ├─ _metadata.py
   │     │  │  ├─ _server_adaptations.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ implementations.cpython-311.pyc
   │     │  │     ├─ interfaces.cpython-311.pyc
   │     │  │     ├─ utilities.cpython-311.pyc
   │     │  │     ├─ _client_adaptations.cpython-311.pyc
   │     │  │     ├─ _metadata.cpython-311.pyc
   │     │  │     ├─ _server_adaptations.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ experimental
   │     │  │  ├─ aio
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ gevent.py
   │     │  │  ├─ session_cache.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ gevent.cpython-311.pyc
   │     │  │     ├─ session_cache.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ framework
   │     │  │  ├─ common
   │     │  │  │  ├─ cardinality.py
   │     │  │  │  ├─ style.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ cardinality.cpython-311.pyc
   │     │  │  │     ├─ style.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ foundation
   │     │  │  │  ├─ abandonment.py
   │     │  │  │  ├─ callable_util.py
   │     │  │  │  ├─ future.py
   │     │  │  │  ├─ logging_pool.py
   │     │  │  │  ├─ stream.py
   │     │  │  │  ├─ stream_util.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ abandonment.cpython-311.pyc
   │     │  │  │     ├─ callable_util.cpython-311.pyc
   │     │  │  │     ├─ future.cpython-311.pyc
   │     │  │  │     ├─ logging_pool.cpython-311.pyc
   │     │  │  │     ├─ stream.cpython-311.pyc
   │     │  │  │     ├─ stream_util.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ interfaces
   │     │  │  │  ├─ base
   │     │  │  │  │  ├─ base.py
   │     │  │  │  │  ├─ utilities.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ base.cpython-311.pyc
   │     │  │  │  │     ├─ utilities.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ face
   │     │  │  │  │  ├─ face.py
   │     │  │  │  │  ├─ utilities.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ face.cpython-311.pyc
   │     │  │  │  │     ├─ utilities.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ _auth.py
   │     │  ├─ _channel.py
   │     │  ├─ _common.py
   │     │  ├─ _compression.py
   │     │  ├─ _cython
   │     │  │  ├─ cygrpc.cp311-win_amd64.pyd
   │     │  │  ├─ _credentials
   │     │  │  │  └─ roots.pem
   │     │  │  ├─ _cygrpc
   │     │  │  │  ├─ private_key_signing
   │     │  │  │  │  ├─ private_key_signer_py_wrapper.cc
   │     │  │  │  │  └─ private_key_signer_py_wrapper.h
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ _grpcio_metadata.py
   │     │  ├─ _interceptor.py
   │     │  ├─ _observability.py
   │     │  ├─ _plugin_wrapping.py
   │     │  ├─ _runtime_protos.py
   │     │  ├─ _server.py
   │     │  ├─ _simple_stubs.py
   │     │  ├─ _typing.py
   │     │  ├─ _utilities.py
   │     │  ├─ __init__.py
   │     │  └─ __pycache__
   │     │     ├─ _auth.cpython-311.pyc
   │     │     ├─ _channel.cpython-311.pyc
   │     │     ├─ _common.cpython-311.pyc
   │     │     ├─ _compression.cpython-311.pyc
   │     │     ├─ _grpcio_metadata.cpython-311.pyc
   │     │     ├─ _interceptor.cpython-311.pyc
   │     │     ├─ _observability.cpython-311.pyc
   │     │     ├─ _plugin_wrapping.cpython-311.pyc
   │     │     ├─ _runtime_protos.cpython-311.pyc
   │     │     ├─ _server.cpython-311.pyc
   │     │     ├─ _simple_stubs.cpython-311.pyc
   │     │     ├─ _typing.cpython-311.pyc
   │     │     ├─ _utilities.cpython-311.pyc
   │     │     └─ __init__.cpython-311.pyc
   │     ├─ grpcio-1.80.0.dist-info
   │     │  ├─ INSTALLER
   │     │  ├─ licenses
   │     │  │  └─ LICENSE
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  ├─ top_level.txt
   │     │  └─ WHEEL
   │     ├─ h11
   │     │  ├─ py.typed
   │     │  ├─ _abnf.py
   │     │  ├─ _connection.py
   │     │  ├─ _events.py
   │     │  ├─ _headers.py
   │     │  ├─ _readers.py
   │     │  ├─ _receivebuffer.py
   │     │  ├─ _state.py
   │     │  ├─ _util.py
   │     │  ├─ _version.py
   │     │  ├─ _writers.py
   │     │  ├─ __init__.py
   │     │  └─ __pycache__
   │     │     ├─ _abnf.cpython-311.pyc
   │     │     ├─ _connection.cpython-311.pyc
   │     │     ├─ _events.cpython-311.pyc
   │     │     ├─ _headers.cpython-311.pyc
   │     │     ├─ _readers.cpython-311.pyc
   │     │     ├─ _receivebuffer.cpython-311.pyc
   │     │     ├─ _state.cpython-311.pyc
   │     │     ├─ _util.cpython-311.pyc
   │     │     ├─ _version.cpython-311.pyc
   │     │     ├─ _writers.cpython-311.pyc
   │     │     └─ __init__.cpython-311.pyc
   │     ├─ h11-0.16.0.dist-info
   │     │  ├─ INSTALLER
   │     │  ├─ licenses
   │     │  │  └─ LICENSE.txt
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  ├─ top_level.txt
   │     │  └─ WHEEL
   │     ├─ hf_xet
   │     │  ├─ hf_xet.pyd
   │     │  ├─ __init__.py
   │     │  └─ __pycache__
   │     │     └─ __init__.cpython-311.pyc
   │     ├─ hf_xet-1.4.3.dist-info
   │     │  ├─ INSTALLER
   │     │  ├─ licenses
   │     │  │  └─ LICENSE
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  ├─ sboms
   │     │  │  └─ hf_xet.cyclonedx.json
   │     │  └─ WHEEL
   │     ├─ httpcore
   │     │  ├─ py.typed
   │     │  ├─ _api.py
   │     │  ├─ _async
   │     │  │  ├─ connection.py
   │     │  │  ├─ connection_pool.py
   │     │  │  ├─ http11.py
   │     │  │  ├─ http2.py
   │     │  │  ├─ http_proxy.py
   │     │  │  ├─ interfaces.py
   │     │  │  ├─ socks_proxy.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ connection.cpython-311.pyc
   │     │  │     ├─ connection_pool.cpython-311.pyc
   │     │  │     ├─ http11.cpython-311.pyc
   │     │  │     ├─ http2.cpython-311.pyc
   │     │  │     ├─ http_proxy.cpython-311.pyc
   │     │  │     ├─ interfaces.cpython-311.pyc
   │     │  │     ├─ socks_proxy.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ _backends
   │     │  │  ├─ anyio.py
   │     │  │  ├─ auto.py
   │     │  │  ├─ base.py
   │     │  │  ├─ mock.py
   │     │  │  ├─ sync.py
   │     │  │  ├─ trio.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ anyio.cpython-311.pyc
   │     │  │     ├─ auto.cpython-311.pyc
   │     │  │     ├─ base.cpython-311.pyc
   │     │  │     ├─ mock.cpython-311.pyc
   │     │  │     ├─ sync.cpython-311.pyc
   │     │  │     ├─ trio.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ _exceptions.py
   │     │  ├─ _models.py
   │     │  ├─ _ssl.py
   │     │  ├─ _sync
   │     │  │  ├─ connection.py
   │     │  │  ├─ connection_pool.py
   │     │  │  ├─ http11.py
   │     │  │  ├─ http2.py
   │     │  │  ├─ http_proxy.py
   │     │  │  ├─ interfaces.py
   │     │  │  ├─ socks_proxy.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ connection.cpython-311.pyc
   │     │  │     ├─ connection_pool.cpython-311.pyc
   │     │  │     ├─ http11.cpython-311.pyc
   │     │  │     ├─ http2.cpython-311.pyc
   │     │  │     ├─ http_proxy.cpython-311.pyc
   │     │  │     ├─ interfaces.cpython-311.pyc
   │     │  │     ├─ socks_proxy.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ _synchronization.py
   │     │  ├─ _trace.py
   │     │  ├─ _utils.py
   │     │  ├─ __init__.py
   │     │  └─ __pycache__
   │     │     ├─ _api.cpython-311.pyc
   │     │     ├─ _exceptions.cpython-311.pyc
   │     │     ├─ _models.cpython-311.pyc
   │     │     ├─ _ssl.cpython-311.pyc
   │     │     ├─ _synchronization.cpython-311.pyc
   │     │     ├─ _trace.cpython-311.pyc
   │     │     ├─ _utils.cpython-311.pyc
   │     │     └─ __init__.cpython-311.pyc
   │     ├─ httpcore-1.0.9.dist-info
   │     │  ├─ INSTALLER
   │     │  ├─ licenses
   │     │  │  └─ LICENSE.md
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  └─ WHEEL
   │     ├─ httptools
   │     │  ├─ parser
   │     │  │  ├─ cparser.pxd
   │     │  │  ├─ errors.py
   │     │  │  ├─ parser.cp311-win_amd64.pyd
   │     │  │  ├─ parser.pyi
   │     │  │  ├─ parser.pyx
   │     │  │  ├─ protocol.py
   │     │  │  ├─ python.pxd
   │     │  │  ├─ url_cparser.pxd
   │     │  │  ├─ url_parser.cp311-win_amd64.pyd
   │     │  │  ├─ url_parser.pyi
   │     │  │  ├─ url_parser.pyx
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ errors.cpython-311.pyc
   │     │  │     ├─ protocol.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ _version.py
   │     │  ├─ __init__.py
   │     │  └─ __pycache__
   │     │     ├─ _version.cpython-311.pyc
   │     │     └─ __init__.cpython-311.pyc
   │     ├─ httptools-0.7.1.dist-info
   │     │  ├─ INSTALLER
   │     │  ├─ licenses
   │     │  │  └─ LICENSE
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  ├─ top_level.txt
   │     │  └─ WHEEL
   │     ├─ httpx
   │     │  ├─ py.typed
   │     │  ├─ _api.py
   │     │  ├─ _auth.py
   │     │  ├─ _client.py
   │     │  ├─ _config.py
   │     │  ├─ _content.py
   │     │  ├─ _decoders.py
   │     │  ├─ _exceptions.py
   │     │  ├─ _main.py
   │     │  ├─ _models.py
   │     │  ├─ _multipart.py
   │     │  ├─ _status_codes.py
   │     │  ├─ _transports
   │     │  │  ├─ asgi.py
   │     │  │  ├─ base.py
   │     │  │  ├─ default.py
   │     │  │  ├─ mock.py
   │     │  │  ├─ wsgi.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ asgi.cpython-311.pyc
   │     │  │     ├─ base.cpython-311.pyc
   │     │  │     ├─ default.cpython-311.pyc
   │     │  │     ├─ mock.cpython-311.pyc
   │     │  │     ├─ wsgi.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ _types.py
   │     │  ├─ _urlparse.py
   │     │  ├─ _urls.py
   │     │  ├─ _utils.py
   │     │  ├─ __init__.py
   │     │  ├─ __pycache__
   │     │  │  ├─ _api.cpython-311.pyc
   │     │  │  ├─ _auth.cpython-311.pyc
   │     │  │  ├─ _client.cpython-311.pyc
   │     │  │  ├─ _config.cpython-311.pyc
   │     │  │  ├─ _content.cpython-311.pyc
   │     │  │  ├─ _decoders.cpython-311.pyc
   │     │  │  ├─ _exceptions.cpython-311.pyc
   │     │  │  ├─ _main.cpython-311.pyc
   │     │  │  ├─ _models.cpython-311.pyc
   │     │  │  ├─ _multipart.cpython-311.pyc
   │     │  │  ├─ _status_codes.cpython-311.pyc
   │     │  │  ├─ _types.cpython-311.pyc
   │     │  │  ├─ _urlparse.cpython-311.pyc
   │     │  │  ├─ _urls.cpython-311.pyc
   │     │  │  ├─ _utils.cpython-311.pyc
   │     │  │  ├─ __init__.cpython-311.pyc
   │     │  │  └─ __version__.cpython-311.pyc
   │     │  └─ __version__.py
   │     ├─ httpx-0.28.1.dist-info
   │     │  ├─ entry_points.txt
   │     │  ├─ INSTALLER
   │     │  ├─ licenses
   │     │  │  └─ LICENSE.md
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  └─ WHEEL
   │     ├─ huggingface_hub
   │     │  ├─ cli
   │     │  │  ├─ auth.py
   │     │  │  ├─ buckets.py
   │     │  │  ├─ cache.py
   │     │  │  ├─ collections.py
   │     │  │  ├─ datasets.py
   │     │  │  ├─ deprecated_cli.py
   │     │  │  ├─ discussions.py
   │     │  │  ├─ download.py
   │     │  │  ├─ extensions.py
   │     │  │  ├─ hf.py
   │     │  │  ├─ inference_endpoints.py
   │     │  │  ├─ jobs.py
   │     │  │  ├─ lfs.py
   │     │  │  ├─ models.py
   │     │  │  ├─ papers.py
   │     │  │  ├─ repos.py
   │     │  │  ├─ repo_files.py
   │     │  │  ├─ skills.py
   │     │  │  ├─ spaces.py
   │     │  │  ├─ system.py
   │     │  │  ├─ upload.py
   │     │  │  ├─ upload_large_folder.py
   │     │  │  ├─ webhooks.py
   │     │  │  ├─ _cli_utils.py
   │     │  │  ├─ _errors.py
   │     │  │  ├─ _output.py
   │     │  │  ├─ _skills.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ auth.cpython-311.pyc
   │     │  │     ├─ buckets.cpython-311.pyc
   │     │  │     ├─ cache.cpython-311.pyc
   │     │  │     ├─ collections.cpython-311.pyc
   │     │  │     ├─ datasets.cpython-311.pyc
   │     │  │     ├─ deprecated_cli.cpython-311.pyc
   │     │  │     ├─ discussions.cpython-311.pyc
   │     │  │     ├─ download.cpython-311.pyc
   │     │  │     ├─ extensions.cpython-311.pyc
   │     │  │     ├─ hf.cpython-311.pyc
   │     │  │     ├─ inference_endpoints.cpython-311.pyc
   │     │  │     ├─ jobs.cpython-311.pyc
   │     │  │     ├─ lfs.cpython-311.pyc
   │     │  │     ├─ models.cpython-311.pyc
   │     │  │     ├─ papers.cpython-311.pyc
   │     │  │     ├─ repos.cpython-311.pyc
   │     │  │     ├─ repo_files.cpython-311.pyc
   │     │  │     ├─ skills.cpython-311.pyc
   │     │  │     ├─ spaces.cpython-311.pyc
   │     │  │     ├─ system.cpython-311.pyc
   │     │  │     ├─ upload.cpython-311.pyc
   │     │  │     ├─ upload_large_folder.cpython-311.pyc
   │     │  │     ├─ webhooks.cpython-311.pyc
   │     │  │     ├─ _cli_utils.cpython-311.pyc
   │     │  │     ├─ _errors.cpython-311.pyc
   │     │  │     ├─ _output.cpython-311.pyc
   │     │  │     ├─ _skills.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ community.py
   │     │  ├─ constants.py
   │     │  ├─ dataclasses.py
   │     │  ├─ errors.py
   │     │  ├─ fastai_utils.py
   │     │  ├─ file_download.py
   │     │  ├─ hf_api.py
   │     │  ├─ hf_file_system.py
   │     │  ├─ hub_mixin.py
   │     │  ├─ inference
   │     │  │  ├─ _client.py
   │     │  │  ├─ _common.py
   │     │  │  ├─ _generated
   │     │  │  │  ├─ types
   │     │  │  │  │  ├─ audio_classification.py
   │     │  │  │  │  ├─ audio_to_audio.py
   │     │  │  │  │  ├─ automatic_speech_recognition.py
   │     │  │  │  │  ├─ base.py
   │     │  │  │  │  ├─ chat_completion.py
   │     │  │  │  │  ├─ depth_estimation.py
   │     │  │  │  │  ├─ document_question_answering.py
   │     │  │  │  │  ├─ feature_extraction.py
   │     │  │  │  │  ├─ fill_mask.py
   │     │  │  │  │  ├─ image_classification.py
   │     │  │  │  │  ├─ image_segmentation.py
   │     │  │  │  │  ├─ image_text_to_image.py
   │     │  │  │  │  ├─ image_text_to_video.py
   │     │  │  │  │  ├─ image_to_image.py
   │     │  │  │  │  ├─ image_to_text.py
   │     │  │  │  │  ├─ image_to_video.py
   │     │  │  │  │  ├─ object_detection.py
   │     │  │  │  │  ├─ question_answering.py
   │     │  │  │  │  ├─ sentence_similarity.py
   │     │  │  │  │  ├─ summarization.py
   │     │  │  │  │  ├─ table_question_answering.py
   │     │  │  │  │  ├─ text2text_generation.py
   │     │  │  │  │  ├─ text_classification.py
   │     │  │  │  │  ├─ text_generation.py
   │     │  │  │  │  ├─ text_to_audio.py
   │     │  │  │  │  ├─ text_to_image.py
   │     │  │  │  │  ├─ text_to_speech.py
   │     │  │  │  │  ├─ text_to_video.py
   │     │  │  │  │  ├─ token_classification.py
   │     │  │  │  │  ├─ translation.py
   │     │  │  │  │  ├─ video_classification.py
   │     │  │  │  │  ├─ visual_question_answering.py
   │     │  │  │  │  ├─ zero_shot_classification.py
   │     │  │  │  │  ├─ zero_shot_image_classification.py
   │     │  │  │  │  ├─ zero_shot_object_detection.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ audio_classification.cpython-311.pyc
   │     │  │  │  │     ├─ audio_to_audio.cpython-311.pyc
   │     │  │  │  │     ├─ automatic_speech_recognition.cpython-311.pyc
   │     │  │  │  │     ├─ base.cpython-311.pyc
   │     │  │  │  │     ├─ chat_completion.cpython-311.pyc
   │     │  │  │  │     ├─ depth_estimation.cpython-311.pyc
   │     │  │  │  │     ├─ document_question_answering.cpython-311.pyc
   │     │  │  │  │     ├─ feature_extraction.cpython-311.pyc
   │     │  │  │  │     ├─ fill_mask.cpython-311.pyc
   │     │  │  │  │     ├─ image_classification.cpython-311.pyc
   │     │  │  │  │     ├─ image_segmentation.cpython-311.pyc
   │     │  │  │  │     ├─ image_text_to_image.cpython-311.pyc
   │     │  │  │  │     ├─ image_text_to_video.cpython-311.pyc
   │     │  │  │  │     ├─ image_to_image.cpython-311.pyc
   │     │  │  │  │     ├─ image_to_text.cpython-311.pyc
   │     │  │  │  │     ├─ image_to_video.cpython-311.pyc
   │     │  │  │  │     ├─ object_detection.cpython-311.pyc
   │     │  │  │  │     ├─ question_answering.cpython-311.pyc
   │     │  │  │  │     ├─ sentence_similarity.cpython-311.pyc
   │     │  │  │  │     ├─ summarization.cpython-311.pyc
   │     │  │  │  │     ├─ table_question_answering.cpython-311.pyc
   │     │  │  │  │     ├─ text2text_generation.cpython-311.pyc
   │     │  │  │  │     ├─ text_classification.cpython-311.pyc
   │     │  │  │  │     ├─ text_generation.cpython-311.pyc
   │     │  │  │  │     ├─ text_to_audio.cpython-311.pyc
   │     │  │  │  │     ├─ text_to_image.cpython-311.pyc
   │     │  │  │  │     ├─ text_to_speech.cpython-311.pyc
   │     │  │  │  │     ├─ text_to_video.cpython-311.pyc
   │     │  │  │  │     ├─ token_classification.cpython-311.pyc
   │     │  │  │  │     ├─ translation.cpython-311.pyc
   │     │  │  │  │     ├─ video_classification.cpython-311.pyc
   │     │  │  │  │     ├─ visual_question_answering.cpython-311.pyc
   │     │  │  │  │     ├─ zero_shot_classification.cpython-311.pyc
   │     │  │  │  │     ├─ zero_shot_image_classification.cpython-311.pyc
   │     │  │  │  │     ├─ zero_shot_object_detection.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ _async_client.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ _async_client.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ _mcp
   │     │  │  │  ├─ agent.py
   │     │  │  │  ├─ cli.py
   │     │  │  │  ├─ constants.py
   │     │  │  │  ├─ mcp_client.py
   │     │  │  │  ├─ types.py
   │     │  │  │  ├─ utils.py
   │     │  │  │  ├─ _cli_hacks.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ agent.cpython-311.pyc
   │     │  │  │     ├─ cli.cpython-311.pyc
   │     │  │  │     ├─ constants.cpython-311.pyc
   │     │  │  │     ├─ mcp_client.cpython-311.pyc
   │     │  │  │     ├─ types.cpython-311.pyc
   │     │  │  │     ├─ utils.cpython-311.pyc
   │     │  │  │     ├─ _cli_hacks.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ _providers
   │     │  │  │  ├─ black_forest_labs.py
   │     │  │  │  ├─ cerebras.py
   │     │  │  │  ├─ clarifai.py
   │     │  │  │  ├─ cohere.py
   │     │  │  │  ├─ fal_ai.py
   │     │  │  │  ├─ featherless_ai.py
   │     │  │  │  ├─ fireworks_ai.py
   │     │  │  │  ├─ groq.py
   │     │  │  │  ├─ hf_inference.py
   │     │  │  │  ├─ hyperbolic.py
   │     │  │  │  ├─ nebius.py
   │     │  │  │  ├─ novita.py
   │     │  │  │  ├─ nscale.py
   │     │  │  │  ├─ nvidia.py
   │     │  │  │  ├─ openai.py
   │     │  │  │  ├─ ovhcloud.py
   │     │  │  │  ├─ publicai.py
   │     │  │  │  ├─ replicate.py
   │     │  │  │  ├─ sambanova.py
   │     │  │  │  ├─ scaleway.py
   │     │  │  │  ├─ together.py
   │     │  │  │  ├─ wavespeed.py
   │     │  │  │  ├─ zai_org.py
   │     │  │  │  ├─ _common.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ black_forest_labs.cpython-311.pyc
   │     │  │  │     ├─ cerebras.cpython-311.pyc
   │     │  │  │     ├─ clarifai.cpython-311.pyc
   │     │  │  │     ├─ cohere.cpython-311.pyc
   │     │  │  │     ├─ fal_ai.cpython-311.pyc
   │     │  │  │     ├─ featherless_ai.cpython-311.pyc
   │     │  │  │     ├─ fireworks_ai.cpython-311.pyc
   │     │  │  │     ├─ groq.cpython-311.pyc
   │     │  │  │     ├─ hf_inference.cpython-311.pyc
   │     │  │  │     ├─ hyperbolic.cpython-311.pyc
   │     │  │  │     ├─ nebius.cpython-311.pyc
   │     │  │  │     ├─ novita.cpython-311.pyc
   │     │  │  │     ├─ nscale.cpython-311.pyc
   │     │  │  │     ├─ nvidia.cpython-311.pyc
   │     │  │  │     ├─ openai.cpython-311.pyc
   │     │  │  │     ├─ ovhcloud.cpython-311.pyc
   │     │  │  │     ├─ publicai.cpython-311.pyc
   │     │  │  │     ├─ replicate.cpython-311.pyc
   │     │  │  │     ├─ sambanova.cpython-311.pyc
   │     │  │  │     ├─ scaleway.cpython-311.pyc
   │     │  │  │     ├─ together.cpython-311.pyc
   │     │  │  │     ├─ wavespeed.cpython-311.pyc
   │     │  │  │     ├─ zai_org.cpython-311.pyc
   │     │  │  │     ├─ _common.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ _client.cpython-311.pyc
   │     │  │     ├─ _common.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ lfs.py
   │     │  ├─ py.typed
   │     │  ├─ repocard.py
   │     │  ├─ repocard_data.py
   │     │  ├─ serialization
   │     │  │  ├─ _base.py
   │     │  │  ├─ _dduf.py
   │     │  │  ├─ _torch.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ _base.cpython-311.pyc
   │     │  │     ├─ _dduf.cpython-311.pyc
   │     │  │     ├─ _torch.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ templates
   │     │  │  ├─ datasetcard_template.md
   │     │  │  └─ modelcard_template.md
   │     │  ├─ utils
   │     │  │  ├─ endpoint_helpers.py
   │     │  │  ├─ insecure_hashlib.py
   │     │  │  ├─ logging.py
   │     │  │  ├─ sha.py
   │     │  │  ├─ tqdm.py
   │     │  │  ├─ _auth.py
   │     │  │  ├─ _cache_assets.py
   │     │  │  ├─ _cache_manager.py
   │     │  │  ├─ _chunk_utils.py
   │     │  │  ├─ _datetime.py
   │     │  │  ├─ _deprecation.py
   │     │  │  ├─ _detect_agent.py
   │     │  │  ├─ _dotenv.py
   │     │  │  ├─ _experimental.py
   │     │  │  ├─ _fixes.py
   │     │  │  ├─ _git_credential.py
   │     │  │  ├─ _headers.py
   │     │  │  ├─ _http.py
   │     │  │  ├─ _lfs.py
   │     │  │  ├─ _pagination.py
   │     │  │  ├─ _parsing.py
   │     │  │  ├─ _paths.py
   │     │  │  ├─ _runtime.py
   │     │  │  ├─ _safetensors.py
   │     │  │  ├─ _subprocess.py
   │     │  │  ├─ _telemetry.py
   │     │  │  ├─ _terminal.py
   │     │  │  ├─ _typing.py
   │     │  │  ├─ _validators.py
   │     │  │  ├─ _verification.py
   │     │  │  ├─ _xet.py
   │     │  │  ├─ _xet_progress_reporting.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ endpoint_helpers.cpython-311.pyc
   │     │  │     ├─ insecure_hashlib.cpython-311.pyc
   │     │  │     ├─ logging.cpython-311.pyc
   │     │  │     ├─ sha.cpython-311.pyc
   │     │  │     ├─ tqdm.cpython-311.pyc
   │     │  │     ├─ _auth.cpython-311.pyc
   │     │  │     ├─ _cache_assets.cpython-311.pyc
   │     │  │     ├─ _cache_manager.cpython-311.pyc
   │     │  │     ├─ _chunk_utils.cpython-311.pyc
   │     │  │     ├─ _datetime.cpython-311.pyc
   │     │  │     ├─ _deprecation.cpython-311.pyc
   │     │  │     ├─ _detect_agent.cpython-311.pyc
   │     │  │     ├─ _dotenv.cpython-311.pyc
   │     │  │     ├─ _experimental.cpython-311.pyc
   │     │  │     ├─ _fixes.cpython-311.pyc
   │     │  │     ├─ _git_credential.cpython-311.pyc
   │     │  │     ├─ _headers.cpython-311.pyc
   │     │  │     ├─ _http.cpython-311.pyc
   │     │  │     ├─ _lfs.cpython-311.pyc
   │     │  │     ├─ _pagination.cpython-311.pyc
   │     │  │     ├─ _parsing.cpython-311.pyc
   │     │  │     ├─ _paths.cpython-311.pyc
   │     │  │     ├─ _runtime.cpython-311.pyc
   │     │  │     ├─ _safetensors.cpython-311.pyc
   │     │  │     ├─ _subprocess.cpython-311.pyc
   │     │  │     ├─ _telemetry.cpython-311.pyc
   │     │  │     ├─ _terminal.cpython-311.pyc
   │     │  │     ├─ _typing.cpython-311.pyc
   │     │  │     ├─ _validators.cpython-311.pyc
   │     │  │     ├─ _verification.cpython-311.pyc
   │     │  │     ├─ _xet.cpython-311.pyc
   │     │  │     ├─ _xet_progress_reporting.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ _buckets.py
   │     │  ├─ _commit_api.py
   │     │  ├─ _commit_scheduler.py
   │     │  ├─ _dataset_viewer.py
   │     │  ├─ _eval_results.py
   │     │  ├─ _hot_reload
   │     │  │  ├─ client.py
   │     │  │  ├─ sse_client.py
   │     │  │  ├─ types.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ client.cpython-311.pyc
   │     │  │     ├─ sse_client.cpython-311.pyc
   │     │  │     ├─ types.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ _inference_endpoints.py
   │     │  ├─ _jobs_api.py
   │     │  ├─ _local_folder.py
   │     │  ├─ _login.py
   │     │  ├─ _oauth.py
   │     │  ├─ _snapshot_download.py
   │     │  ├─ _space_api.py
   │     │  ├─ _tensorboard_logger.py
   │     │  ├─ _upload_large_folder.py
   │     │  ├─ _webhooks_payload.py
   │     │  ├─ _webhooks_server.py
   │     │  ├─ __init__.py
   │     │  └─ __pycache__
   │     │     ├─ community.cpython-311.pyc
   │     │     ├─ constants.cpython-311.pyc
   │     │     ├─ dataclasses.cpython-311.pyc
   │     │     ├─ errors.cpython-311.pyc
   │     │     ├─ fastai_utils.cpython-311.pyc
   │     │     ├─ file_download.cpython-311.pyc
   │     │     ├─ hf_api.cpython-311.pyc
   │     │     ├─ hf_file_system.cpython-311.pyc
   │     │     ├─ hub_mixin.cpython-311.pyc
   │     │     ├─ lfs.cpython-311.pyc
   │     │     ├─ repocard.cpython-311.pyc
   │     │     ├─ repocard_data.cpython-311.pyc
   │     │     ├─ _buckets.cpython-311.pyc
   │     │     ├─ _commit_api.cpython-311.pyc
   │     │     ├─ _commit_scheduler.cpython-311.pyc
   │     │     ├─ _dataset_viewer.cpython-311.pyc
   │     │     ├─ _eval_results.cpython-311.pyc
   │     │     ├─ _inference_endpoints.cpython-311.pyc
   │     │     ├─ _jobs_api.cpython-311.pyc
   │     │     ├─ _local_folder.cpython-311.pyc
   │     │     ├─ _login.cpython-311.pyc
   │     │     ├─ _oauth.cpython-311.pyc
   │     │     ├─ _snapshot_download.cpython-311.pyc
   │     │     ├─ _space_api.cpython-311.pyc
   │     │     ├─ _tensorboard_logger.cpython-311.pyc
   │     │     ├─ _upload_large_folder.cpython-311.pyc
   │     │     ├─ _webhooks_payload.cpython-311.pyc
   │     │     ├─ _webhooks_server.cpython-311.pyc
   │     │     └─ __init__.cpython-311.pyc
   │     ├─ huggingface_hub-1.10.1.dist-info
   │     │  ├─ entry_points.txt
   │     │  ├─ INSTALLER
   │     │  ├─ licenses
   │     │  │  └─ LICENSE
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  ├─ top_level.txt
   │     │  └─ WHEEL
   │     ├─ idna
   │     │  ├─ codec.py
   │     │  ├─ compat.py
   │     │  ├─ core.py
   │     │  ├─ idnadata.py
   │     │  ├─ intranges.py
   │     │  ├─ package_data.py
   │     │  ├─ py.typed
   │     │  ├─ uts46data.py
   │     │  ├─ __init__.py
   │     │  └─ __pycache__
   │     │     ├─ codec.cpython-311.pyc
   │     │     ├─ compat.cpython-311.pyc
   │     │     ├─ core.cpython-311.pyc
   │     │     ├─ idnadata.cpython-311.pyc
   │     │     ├─ intranges.cpython-311.pyc
   │     │     ├─ package_data.cpython-311.pyc
   │     │     ├─ uts46data.cpython-311.pyc
   │     │     └─ __init__.cpython-311.pyc
   │     ├─ idna-3.11.dist-info
   │     │  ├─ INSTALLER
   │     │  ├─ licenses
   │     │  │  └─ LICENSE.md
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  └─ WHEEL
   │     ├─ importlib_metadata
   │     │  ├─ compat
   │     │  │  ├─ py311.py
   │     │  │  ├─ py39.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ py311.cpython-311.pyc
   │     │  │     ├─ py39.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ diagnose.py
   │     │  ├─ py.typed
   │     │  ├─ _adapters.py
   │     │  ├─ _collections.py
   │     │  ├─ _compat.py
   │     │  ├─ _functools.py
   │     │  ├─ _itertools.py
   │     │  ├─ _meta.py
   │     │  ├─ _text.py
   │     │  ├─ _typing.py
   │     │  ├─ __init__.py
   │     │  └─ __pycache__
   │     │     ├─ diagnose.cpython-311.pyc
   │     │     ├─ _adapters.cpython-311.pyc
   │     │     ├─ _collections.cpython-311.pyc
   │     │     ├─ _compat.cpython-311.pyc
   │     │     ├─ _functools.cpython-311.pyc
   │     │     ├─ _itertools.cpython-311.pyc
   │     │     ├─ _meta.cpython-311.pyc
   │     │     ├─ _text.cpython-311.pyc
   │     │     ├─ _typing.cpython-311.pyc
   │     │     └─ __init__.cpython-311.pyc
   │     ├─ importlib_metadata-8.7.1.dist-info
   │     │  ├─ INSTALLER
   │     │  ├─ licenses
   │     │  │  └─ LICENSE
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  ├─ top_level.txt
   │     │  └─ WHEEL
   │     ├─ importlib_resources
   │     │  ├─ abc.py
   │     │  ├─ compat
   │     │  │  ├─ py39.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ py39.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ future
   │     │  │  ├─ adapters.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ adapters.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ py.typed
   │     │  ├─ readers.py
   │     │  ├─ simple.py
   │     │  ├─ tests
   │     │  │  ├─ compat
   │     │  │  │  ├─ py312.py
   │     │  │  │  ├─ py39.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ py312.cpython-311.pyc
   │     │  │  │     ├─ py39.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ test_compatibilty_files.py
   │     │  │  ├─ test_contents.py
   │     │  │  ├─ test_custom.py
   │     │  │  ├─ test_files.py
   │     │  │  ├─ test_functional.py
   │     │  │  ├─ test_open.py
   │     │  │  ├─ test_path.py
   │     │  │  ├─ test_read.py
   │     │  │  ├─ test_reader.py
   │     │  │  ├─ test_resource.py
   │     │  │  ├─ test_util.py
   │     │  │  ├─ util.py
   │     │  │  ├─ zip.py
   │     │  │  ├─ _path.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ test_compatibilty_files.cpython-311.pyc
   │     │  │     ├─ test_contents.cpython-311.pyc
   │     │  │     ├─ test_custom.cpython-311.pyc
   │     │  │     ├─ test_files.cpython-311.pyc
   │     │  │     ├─ test_functional.cpython-311.pyc
   │     │  │     ├─ test_open.cpython-311.pyc
   │     │  │     ├─ test_path.cpython-311.pyc
   │     │  │     ├─ test_read.cpython-311.pyc
   │     │  │     ├─ test_reader.cpython-311.pyc
   │     │  │     ├─ test_resource.cpython-311.pyc
   │     │  │     ├─ test_util.cpython-311.pyc
   │     │  │     ├─ util.cpython-311.pyc
   │     │  │     ├─ zip.cpython-311.pyc
   │     │  │     ├─ _path.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ _adapters.py
   │     │  ├─ _common.py
   │     │  ├─ _functional.py
   │     │  ├─ _itertools.py
   │     │  ├─ __init__.py
   │     │  └─ __pycache__
   │     │     ├─ abc.cpython-311.pyc
   │     │     ├─ readers.cpython-311.pyc
   │     │     ├─ simple.cpython-311.pyc
   │     │     ├─ _adapters.cpython-311.pyc
   │     │     ├─ _common.cpython-311.pyc
   │     │     ├─ _functional.cpython-311.pyc
   │     │     ├─ _itertools.cpython-311.pyc
   │     │     └─ __init__.cpython-311.pyc
   │     ├─ importlib_resources-6.5.2.dist-info
   │     │  ├─ INSTALLER
   │     │  ├─ LICENSE
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  ├─ top_level.txt
   │     │  └─ WHEEL
   │     ├─ isympy.py
   │     ├─ jinja2
   │     │  ├─ async_utils.py
   │     │  ├─ bccache.py
   │     │  ├─ compiler.py
   │     │  ├─ constants.py
   │     │  ├─ debug.py
   │     │  ├─ defaults.py
   │     │  ├─ environment.py
   │     │  ├─ exceptions.py
   │     │  ├─ ext.py
   │     │  ├─ filters.py
   │     │  ├─ idtracking.py
   │     │  ├─ lexer.py
   │     │  ├─ loaders.py
   │     │  ├─ meta.py
   │     │  ├─ nativetypes.py
   │     │  ├─ nodes.py
   │     │  ├─ optimizer.py
   │     │  ├─ parser.py
   │     │  ├─ py.typed
   │     │  ├─ runtime.py
   │     │  ├─ sandbox.py
   │     │  ├─ tests.py
   │     │  ├─ utils.py
   │     │  ├─ visitor.py
   │     │  ├─ _identifier.py
   │     │  ├─ __init__.py
   │     │  └─ __pycache__
   │     │     ├─ async_utils.cpython-311.pyc
   │     │     ├─ bccache.cpython-311.pyc
   │     │     ├─ compiler.cpython-311.pyc
   │     │     ├─ constants.cpython-311.pyc
   │     │     ├─ debug.cpython-311.pyc
   │     │     ├─ defaults.cpython-311.pyc
   │     │     ├─ environment.cpython-311.pyc
   │     │     ├─ exceptions.cpython-311.pyc
   │     │     ├─ ext.cpython-311.pyc
   │     │     ├─ filters.cpython-311.pyc
   │     │     ├─ idtracking.cpython-311.pyc
   │     │     ├─ lexer.cpython-311.pyc
   │     │     ├─ loaders.cpython-311.pyc
   │     │     ├─ meta.cpython-311.pyc
   │     │     ├─ nativetypes.cpython-311.pyc
   │     │     ├─ nodes.cpython-311.pyc
   │     │     ├─ optimizer.cpython-311.pyc
   │     │     ├─ parser.cpython-311.pyc
   │     │     ├─ runtime.cpython-311.pyc
   │     │     ├─ sandbox.cpython-311.pyc
   │     │     ├─ tests.cpython-311.pyc
   │     │     ├─ utils.cpython-311.pyc
   │     │     ├─ visitor.cpython-311.pyc
   │     │     ├─ _identifier.cpython-311.pyc
   │     │     └─ __init__.cpython-311.pyc
   │     ├─ jinja2-3.1.6.dist-info
   │     │  ├─ entry_points.txt
   │     │  ├─ INSTALLER
   │     │  ├─ licenses
   │     │  │  └─ LICENSE.txt
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  └─ WHEEL
   │     ├─ jsonschema
   │     │  ├─ benchmarks
   │     │  │  ├─ const_vs_enum.py
   │     │  │  ├─ contains.py
   │     │  │  ├─ import_benchmark.py
   │     │  │  ├─ issue232
   │     │  │  │  └─ issue.json
   │     │  │  ├─ issue232.py
   │     │  │  ├─ json_schema_test_suite.py
   │     │  │  ├─ nested_schemas.py
   │     │  │  ├─ subcomponents.py
   │     │  │  ├─ unused_registry.py
   │     │  │  ├─ useless_applicator_schemas.py
   │     │  │  ├─ useless_keywords.py
   │     │  │  ├─ validator_creation.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ const_vs_enum.cpython-311.pyc
   │     │  │     ├─ contains.cpython-311.pyc
   │     │  │     ├─ import_benchmark.cpython-311.pyc
   │     │  │     ├─ issue232.cpython-311.pyc
   │     │  │     ├─ json_schema_test_suite.cpython-311.pyc
   │     │  │     ├─ nested_schemas.cpython-311.pyc
   │     │  │     ├─ subcomponents.cpython-311.pyc
   │     │  │     ├─ unused_registry.cpython-311.pyc
   │     │  │     ├─ useless_applicator_schemas.cpython-311.pyc
   │     │  │     ├─ useless_keywords.cpython-311.pyc
   │     │  │     ├─ validator_creation.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ cli.py
   │     │  ├─ exceptions.py
   │     │  ├─ protocols.py
   │     │  ├─ tests
   │     │  │  ├─ fuzz_validate.py
   │     │  │  ├─ test_cli.py
   │     │  │  ├─ test_deprecations.py
   │     │  │  ├─ test_exceptions.py
   │     │  │  ├─ test_format.py
   │     │  │  ├─ test_jsonschema_test_suite.py
   │     │  │  ├─ test_types.py
   │     │  │  ├─ test_utils.py
   │     │  │  ├─ test_validators.py
   │     │  │  ├─ typing
   │     │  │  │  ├─ test_all_concrete_validators_match_protocol.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ test_all_concrete_validators_match_protocol.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ _suite.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ fuzz_validate.cpython-311.pyc
   │     │  │     ├─ test_cli.cpython-311.pyc
   │     │  │     ├─ test_deprecations.cpython-311.pyc
   │     │  │     ├─ test_exceptions.cpython-311.pyc
   │     │  │     ├─ test_format.cpython-311.pyc
   │     │  │     ├─ test_jsonschema_test_suite.cpython-311.pyc
   │     │  │     ├─ test_types.cpython-311.pyc
   │     │  │     ├─ test_utils.cpython-311.pyc
   │     │  │     ├─ test_validators.cpython-311.pyc
   │     │  │     ├─ _suite.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ validators.py
   │     │  ├─ _format.py
   │     │  ├─ _keywords.py
   │     │  ├─ _legacy_keywords.py
   │     │  ├─ _types.py
   │     │  ├─ _typing.py
   │     │  ├─ _utils.py
   │     │  ├─ __init__.py
   │     │  ├─ __main__.py
   │     │  └─ __pycache__
   │     │     ├─ cli.cpython-311.pyc
   │     │     ├─ exceptions.cpython-311.pyc
   │     │     ├─ protocols.cpython-311.pyc
   │     │     ├─ validators.cpython-311.pyc
   │     │     ├─ _format.cpython-311.pyc
   │     │     ├─ _keywords.cpython-311.pyc
   │     │     ├─ _legacy_keywords.cpython-311.pyc
   │     │     ├─ _types.cpython-311.pyc
   │     │     ├─ _typing.cpython-311.pyc
   │     │     ├─ _utils.cpython-311.pyc
   │     │     ├─ __init__.cpython-311.pyc
   │     │     └─ __main__.cpython-311.pyc
   │     ├─ jsonschema-4.26.0.dist-info
   │     │  ├─ entry_points.txt
   │     │  ├─ INSTALLER
   │     │  ├─ licenses
   │     │  │  └─ COPYING
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  └─ WHEEL
   │     ├─ jsonschema_specifications
   │     │  ├─ schemas
   │     │  │  ├─ draft201909
   │     │  │  │  ├─ metaschema.json
   │     │  │  │  └─ vocabularies
   │     │  │  │     ├─ applicator
   │     │  │  │     ├─ content
   │     │  │  │     ├─ core
   │     │  │  │     ├─ format
   │     │  │  │     ├─ meta-data
   │     │  │  │     └─ validation
   │     │  │  ├─ draft202012
   │     │  │  │  ├─ metaschema.json
   │     │  │  │  └─ vocabularies
   │     │  │  │     ├─ applicator
   │     │  │  │     ├─ content
   │     │  │  │     ├─ core
   │     │  │  │     ├─ format-annotation
   │     │  │  │     ├─ format-assertion
   │     │  │  │     ├─ meta-data
   │     │  │  │     ├─ unevaluated
   │     │  │  │     └─ validation
   │     │  │  ├─ draft3
   │     │  │  │  └─ metaschema.json
   │     │  │  ├─ draft4
   │     │  │  │  └─ metaschema.json
   │     │  │  ├─ draft6
   │     │  │  │  └─ metaschema.json
   │     │  │  └─ draft7
   │     │  │     └─ metaschema.json
   │     │  ├─ tests
   │     │  │  ├─ test_jsonschema_specifications.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ test_jsonschema_specifications.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ _core.py
   │     │  ├─ __init__.py
   │     │  └─ __pycache__
   │     │     ├─ _core.cpython-311.pyc
   │     │     └─ __init__.cpython-311.pyc
   │     ├─ jsonschema_specifications-2025.9.1.dist-info
   │     │  ├─ INSTALLER
   │     │  ├─ licenses
   │     │  │  └─ COPYING
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  └─ WHEEL
   │     ├─ kubernetes
   │     │  ├─ client
   │     │  │  ├─ api
   │     │  │  │  ├─ admissionregistration_api.py
   │     │  │  │  ├─ admissionregistration_v1alpha1_api.py
   │     │  │  │  ├─ admissionregistration_v1beta1_api.py
   │     │  │  │  ├─ admissionregistration_v1_api.py
   │     │  │  │  ├─ apiextensions_api.py
   │     │  │  │  ├─ apiextensions_v1_api.py
   │     │  │  │  ├─ apiregistration_api.py
   │     │  │  │  ├─ apiregistration_v1_api.py
   │     │  │  │  ├─ apis_api.py
   │     │  │  │  ├─ apps_api.py
   │     │  │  │  ├─ apps_v1_api.py
   │     │  │  │  ├─ authentication_api.py
   │     │  │  │  ├─ authentication_v1_api.py
   │     │  │  │  ├─ authorization_api.py
   │     │  │  │  ├─ authorization_v1_api.py
   │     │  │  │  ├─ autoscaling_api.py
   │     │  │  │  ├─ autoscaling_v1_api.py
   │     │  │  │  ├─ autoscaling_v2_api.py
   │     │  │  │  ├─ batch_api.py
   │     │  │  │  ├─ batch_v1_api.py
   │     │  │  │  ├─ certificates_api.py
   │     │  │  │  ├─ certificates_v1alpha1_api.py
   │     │  │  │  ├─ certificates_v1beta1_api.py
   │     │  │  │  ├─ certificates_v1_api.py
   │     │  │  │  ├─ coordination_api.py
   │     │  │  │  ├─ coordination_v1alpha2_api.py
   │     │  │  │  ├─ coordination_v1beta1_api.py
   │     │  │  │  ├─ coordination_v1_api.py
   │     │  │  │  ├─ core_api.py
   │     │  │  │  ├─ core_v1_api.py
   │     │  │  │  ├─ custom_objects_api.py
   │     │  │  │  ├─ discovery_api.py
   │     │  │  │  ├─ discovery_v1_api.py
   │     │  │  │  ├─ events_api.py
   │     │  │  │  ├─ events_v1_api.py
   │     │  │  │  ├─ flowcontrol_apiserver_api.py
   │     │  │  │  ├─ flowcontrol_apiserver_v1_api.py
   │     │  │  │  ├─ internal_apiserver_api.py
   │     │  │  │  ├─ internal_apiserver_v1alpha1_api.py
   │     │  │  │  ├─ logs_api.py
   │     │  │  │  ├─ networking_api.py
   │     │  │  │  ├─ networking_v1beta1_api.py
   │     │  │  │  ├─ networking_v1_api.py
   │     │  │  │  ├─ node_api.py
   │     │  │  │  ├─ node_v1_api.py
   │     │  │  │  ├─ openid_api.py
   │     │  │  │  ├─ policy_api.py
   │     │  │  │  ├─ policy_v1_api.py
   │     │  │  │  ├─ rbac_authorization_api.py
   │     │  │  │  ├─ rbac_authorization_v1_api.py
   │     │  │  │  ├─ resource_api.py
   │     │  │  │  ├─ resource_v1alpha3_api.py
   │     │  │  │  ├─ resource_v1beta1_api.py
   │     │  │  │  ├─ resource_v1beta2_api.py
   │     │  │  │  ├─ resource_v1_api.py
   │     │  │  │  ├─ scheduling_api.py
   │     │  │  │  ├─ scheduling_v1alpha1_api.py
   │     │  │  │  ├─ scheduling_v1_api.py
   │     │  │  │  ├─ storagemigration_api.py
   │     │  │  │  ├─ storagemigration_v1beta1_api.py
   │     │  │  │  ├─ storage_api.py
   │     │  │  │  ├─ storage_v1beta1_api.py
   │     │  │  │  ├─ storage_v1_api.py
   │     │  │  │  ├─ version_api.py
   │     │  │  │  ├─ well_known_api.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ admissionregistration_api.cpython-311.pyc
   │     │  │  │     ├─ admissionregistration_v1alpha1_api.cpython-311.pyc
   │     │  │  │     ├─ admissionregistration_v1beta1_api.cpython-311.pyc
   │     │  │  │     ├─ admissionregistration_v1_api.cpython-311.pyc
   │     │  │  │     ├─ apiextensions_api.cpython-311.pyc
   │     │  │  │     ├─ apiextensions_v1_api.cpython-311.pyc
   │     │  │  │     ├─ apiregistration_api.cpython-311.pyc
   │     │  │  │     ├─ apiregistration_v1_api.cpython-311.pyc
   │     │  │  │     ├─ apis_api.cpython-311.pyc
   │     │  │  │     ├─ apps_api.cpython-311.pyc
   │     │  │  │     ├─ apps_v1_api.cpython-311.pyc
   │     │  │  │     ├─ authentication_api.cpython-311.pyc
   │     │  │  │     ├─ authentication_v1_api.cpython-311.pyc
   │     │  │  │     ├─ authorization_api.cpython-311.pyc
   │     │  │  │     ├─ authorization_v1_api.cpython-311.pyc
   │     │  │  │     ├─ autoscaling_api.cpython-311.pyc
   │     │  │  │     ├─ autoscaling_v1_api.cpython-311.pyc
   │     │  │  │     ├─ autoscaling_v2_api.cpython-311.pyc
   │     │  │  │     ├─ batch_api.cpython-311.pyc
   │     │  │  │     ├─ batch_v1_api.cpython-311.pyc
   │     │  │  │     ├─ certificates_api.cpython-311.pyc
   │     │  │  │     ├─ certificates_v1alpha1_api.cpython-311.pyc
   │     │  │  │     ├─ certificates_v1beta1_api.cpython-311.pyc
   │     │  │  │     ├─ certificates_v1_api.cpython-311.pyc
   │     │  │  │     ├─ coordination_api.cpython-311.pyc
   │     │  │  │     ├─ coordination_v1alpha2_api.cpython-311.pyc
   │     │  │  │     ├─ coordination_v1beta1_api.cpython-311.pyc
   │     │  │  │     ├─ coordination_v1_api.cpython-311.pyc
   │     │  │  │     ├─ core_api.cpython-311.pyc
   │     │  │  │     ├─ core_v1_api.cpython-311.pyc
   │     │  │  │     ├─ custom_objects_api.cpython-311.pyc
   │     │  │  │     ├─ discovery_api.cpython-311.pyc
   │     │  │  │     ├─ discovery_v1_api.cpython-311.pyc
   │     │  │  │     ├─ events_api.cpython-311.pyc
   │     │  │  │     ├─ events_v1_api.cpython-311.pyc
   │     │  │  │     ├─ flowcontrol_apiserver_api.cpython-311.pyc
   │     │  │  │     ├─ flowcontrol_apiserver_v1_api.cpython-311.pyc
   │     │  │  │     ├─ internal_apiserver_api.cpython-311.pyc
   │     │  │  │     ├─ internal_apiserver_v1alpha1_api.cpython-311.pyc
   │     │  │  │     ├─ logs_api.cpython-311.pyc
   │     │  │  │     ├─ networking_api.cpython-311.pyc
   │     │  │  │     ├─ networking_v1beta1_api.cpython-311.pyc
   │     │  │  │     ├─ networking_v1_api.cpython-311.pyc
   │     │  │  │     ├─ node_api.cpython-311.pyc
   │     │  │  │     ├─ node_v1_api.cpython-311.pyc
   │     │  │  │     ├─ openid_api.cpython-311.pyc
   │     │  │  │     ├─ policy_api.cpython-311.pyc
   │     │  │  │     ├─ policy_v1_api.cpython-311.pyc
   │     │  │  │     ├─ rbac_authorization_api.cpython-311.pyc
   │     │  │  │     ├─ rbac_authorization_v1_api.cpython-311.pyc
   │     │  │  │     ├─ resource_api.cpython-311.pyc
   │     │  │  │     ├─ resource_v1alpha3_api.cpython-311.pyc
   │     │  │  │     ├─ resource_v1beta1_api.cpython-311.pyc
   │     │  │  │     ├─ resource_v1beta2_api.cpython-311.pyc
   │     │  │  │     ├─ resource_v1_api.cpython-311.pyc
   │     │  │  │     ├─ scheduling_api.cpython-311.pyc
   │     │  │  │     ├─ scheduling_v1alpha1_api.cpython-311.pyc
   │     │  │  │     ├─ scheduling_v1_api.cpython-311.pyc
   │     │  │  │     ├─ storagemigration_api.cpython-311.pyc
   │     │  │  │     ├─ storagemigration_v1beta1_api.cpython-311.pyc
   │     │  │  │     ├─ storage_api.cpython-311.pyc
   │     │  │  │     ├─ storage_v1beta1_api.cpython-311.pyc
   │     │  │  │     ├─ storage_v1_api.cpython-311.pyc
   │     │  │  │     ├─ version_api.cpython-311.pyc
   │     │  │  │     ├─ well_known_api.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ apis
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ api_client.py
   │     │  │  ├─ configuration.py
   │     │  │  ├─ exceptions.py
   │     │  │  ├─ models
   │     │  │  │  ├─ admissionregistration_v1_service_reference.py
   │     │  │  │  ├─ admissionregistration_v1_webhook_client_config.py
   │     │  │  │  ├─ apiextensions_v1_service_reference.py
   │     │  │  │  ├─ apiextensions_v1_webhook_client_config.py
   │     │  │  │  ├─ apiregistration_v1_service_reference.py
   │     │  │  │  ├─ authentication_v1_token_request.py
   │     │  │  │  ├─ core_v1_endpoint_port.py
   │     │  │  │  ├─ core_v1_event.py
   │     │  │  │  ├─ core_v1_event_list.py
   │     │  │  │  ├─ core_v1_event_series.py
   │     │  │  │  ├─ core_v1_resource_claim.py
   │     │  │  │  ├─ discovery_v1_endpoint_port.py
   │     │  │  │  ├─ events_v1_event.py
   │     │  │  │  ├─ events_v1_event_list.py
   │     │  │  │  ├─ events_v1_event_series.py
   │     │  │  │  ├─ flowcontrol_v1_subject.py
   │     │  │  │  ├─ rbac_v1_subject.py
   │     │  │  │  ├─ resource_v1_resource_claim.py
   │     │  │  │  ├─ storage_v1_token_request.py
   │     │  │  │  ├─ v1alpha1_apply_configuration.py
   │     │  │  │  ├─ v1alpha1_cluster_trust_bundle.py
   │     │  │  │  ├─ v1alpha1_cluster_trust_bundle_list.py
   │     │  │  │  ├─ v1alpha1_cluster_trust_bundle_spec.py
   │     │  │  │  ├─ v1alpha1_gang_scheduling_policy.py
   │     │  │  │  ├─ v1alpha1_json_patch.py
   │     │  │  │  ├─ v1alpha1_match_condition.py
   │     │  │  │  ├─ v1alpha1_match_resources.py
   │     │  │  │  ├─ v1alpha1_mutating_admission_policy.py
   │     │  │  │  ├─ v1alpha1_mutating_admission_policy_binding.py
   │     │  │  │  ├─ v1alpha1_mutating_admission_policy_binding_list.py
   │     │  │  │  ├─ v1alpha1_mutating_admission_policy_binding_spec.py
   │     │  │  │  ├─ v1alpha1_mutating_admission_policy_list.py
   │     │  │  │  ├─ v1alpha1_mutating_admission_policy_spec.py
   │     │  │  │  ├─ v1alpha1_mutation.py
   │     │  │  │  ├─ v1alpha1_named_rule_with_operations.py
   │     │  │  │  ├─ v1alpha1_param_kind.py
   │     │  │  │  ├─ v1alpha1_param_ref.py
   │     │  │  │  ├─ v1alpha1_pod_group.py
   │     │  │  │  ├─ v1alpha1_pod_group_policy.py
   │     │  │  │  ├─ v1alpha1_server_storage_version.py
   │     │  │  │  ├─ v1alpha1_storage_version.py
   │     │  │  │  ├─ v1alpha1_storage_version_condition.py
   │     │  │  │  ├─ v1alpha1_storage_version_list.py
   │     │  │  │  ├─ v1alpha1_storage_version_status.py
   │     │  │  │  ├─ v1alpha1_typed_local_object_reference.py
   │     │  │  │  ├─ v1alpha1_variable.py
   │     │  │  │  ├─ v1alpha1_workload.py
   │     │  │  │  ├─ v1alpha1_workload_list.py
   │     │  │  │  ├─ v1alpha1_workload_spec.py
   │     │  │  │  ├─ v1alpha2_lease_candidate.py
   │     │  │  │  ├─ v1alpha2_lease_candidate_list.py
   │     │  │  │  ├─ v1alpha2_lease_candidate_spec.py
   │     │  │  │  ├─ v1alpha3_device_taint.py
   │     │  │  │  ├─ v1alpha3_device_taint_rule.py
   │     │  │  │  ├─ v1alpha3_device_taint_rule_list.py
   │     │  │  │  ├─ v1alpha3_device_taint_rule_spec.py
   │     │  │  │  ├─ v1alpha3_device_taint_rule_status.py
   │     │  │  │  ├─ v1alpha3_device_taint_selector.py
   │     │  │  │  ├─ v1beta1_allocated_device_status.py
   │     │  │  │  ├─ v1beta1_allocation_result.py
   │     │  │  │  ├─ v1beta1_apply_configuration.py
   │     │  │  │  ├─ v1beta1_basic_device.py
   │     │  │  │  ├─ v1beta1_capacity_request_policy.py
   │     │  │  │  ├─ v1beta1_capacity_request_policy_range.py
   │     │  │  │  ├─ v1beta1_capacity_requirements.py
   │     │  │  │  ├─ v1beta1_cel_device_selector.py
   │     │  │  │  ├─ v1beta1_cluster_trust_bundle.py
   │     │  │  │  ├─ v1beta1_cluster_trust_bundle_list.py
   │     │  │  │  ├─ v1beta1_cluster_trust_bundle_spec.py
   │     │  │  │  ├─ v1beta1_counter.py
   │     │  │  │  ├─ v1beta1_counter_set.py
   │     │  │  │  ├─ v1beta1_device.py
   │     │  │  │  ├─ v1beta1_device_allocation_configuration.py
   │     │  │  │  ├─ v1beta1_device_allocation_result.py
   │     │  │  │  ├─ v1beta1_device_attribute.py
   │     │  │  │  ├─ v1beta1_device_capacity.py
   │     │  │  │  ├─ v1beta1_device_claim.py
   │     │  │  │  ├─ v1beta1_device_claim_configuration.py
   │     │  │  │  ├─ v1beta1_device_class.py
   │     │  │  │  ├─ v1beta1_device_class_configuration.py
   │     │  │  │  ├─ v1beta1_device_class_list.py
   │     │  │  │  ├─ v1beta1_device_class_spec.py
   │     │  │  │  ├─ v1beta1_device_constraint.py
   │     │  │  │  ├─ v1beta1_device_counter_consumption.py
   │     │  │  │  ├─ v1beta1_device_request.py
   │     │  │  │  ├─ v1beta1_device_request_allocation_result.py
   │     │  │  │  ├─ v1beta1_device_selector.py
   │     │  │  │  ├─ v1beta1_device_sub_request.py
   │     │  │  │  ├─ v1beta1_device_taint.py
   │     │  │  │  ├─ v1beta1_device_toleration.py
   │     │  │  │  ├─ v1beta1_ip_address.py
   │     │  │  │  ├─ v1beta1_ip_address_list.py
   │     │  │  │  ├─ v1beta1_ip_address_spec.py
   │     │  │  │  ├─ v1beta1_json_patch.py
   │     │  │  │  ├─ v1beta1_lease_candidate.py
   │     │  │  │  ├─ v1beta1_lease_candidate_list.py
   │     │  │  │  ├─ v1beta1_lease_candidate_spec.py
   │     │  │  │  ├─ v1beta1_match_condition.py
   │     │  │  │  ├─ v1beta1_match_resources.py
   │     │  │  │  ├─ v1beta1_mutating_admission_policy.py
   │     │  │  │  ├─ v1beta1_mutating_admission_policy_binding.py
   │     │  │  │  ├─ v1beta1_mutating_admission_policy_binding_list.py
   │     │  │  │  ├─ v1beta1_mutating_admission_policy_binding_spec.py
   │     │  │  │  ├─ v1beta1_mutating_admission_policy_list.py
   │     │  │  │  ├─ v1beta1_mutating_admission_policy_spec.py
   │     │  │  │  ├─ v1beta1_mutation.py
   │     │  │  │  ├─ v1beta1_named_rule_with_operations.py
   │     │  │  │  ├─ v1beta1_network_device_data.py
   │     │  │  │  ├─ v1beta1_opaque_device_configuration.py
   │     │  │  │  ├─ v1beta1_param_kind.py
   │     │  │  │  ├─ v1beta1_param_ref.py
   │     │  │  │  ├─ v1beta1_parent_reference.py
   │     │  │  │  ├─ v1beta1_pod_certificate_request.py
   │     │  │  │  ├─ v1beta1_pod_certificate_request_list.py
   │     │  │  │  ├─ v1beta1_pod_certificate_request_spec.py
   │     │  │  │  ├─ v1beta1_pod_certificate_request_status.py
   │     │  │  │  ├─ v1beta1_resource_claim.py
   │     │  │  │  ├─ v1beta1_resource_claim_consumer_reference.py
   │     │  │  │  ├─ v1beta1_resource_claim_list.py
   │     │  │  │  ├─ v1beta1_resource_claim_spec.py
   │     │  │  │  ├─ v1beta1_resource_claim_status.py
   │     │  │  │  ├─ v1beta1_resource_claim_template.py
   │     │  │  │  ├─ v1beta1_resource_claim_template_list.py
   │     │  │  │  ├─ v1beta1_resource_claim_template_spec.py
   │     │  │  │  ├─ v1beta1_resource_pool.py
   │     │  │  │  ├─ v1beta1_resource_slice.py
   │     │  │  │  ├─ v1beta1_resource_slice_list.py
   │     │  │  │  ├─ v1beta1_resource_slice_spec.py
   │     │  │  │  ├─ v1beta1_service_cidr.py
   │     │  │  │  ├─ v1beta1_service_cidr_list.py
   │     │  │  │  ├─ v1beta1_service_cidr_spec.py
   │     │  │  │  ├─ v1beta1_service_cidr_status.py
   │     │  │  │  ├─ v1beta1_storage_version_migration.py
   │     │  │  │  ├─ v1beta1_storage_version_migration_list.py
   │     │  │  │  ├─ v1beta1_storage_version_migration_spec.py
   │     │  │  │  ├─ v1beta1_storage_version_migration_status.py
   │     │  │  │  ├─ v1beta1_variable.py
   │     │  │  │  ├─ v1beta1_volume_attributes_class.py
   │     │  │  │  ├─ v1beta1_volume_attributes_class_list.py
   │     │  │  │  ├─ v1beta2_allocated_device_status.py
   │     │  │  │  ├─ v1beta2_allocation_result.py
   │     │  │  │  ├─ v1beta2_capacity_request_policy.py
   │     │  │  │  ├─ v1beta2_capacity_request_policy_range.py
   │     │  │  │  ├─ v1beta2_capacity_requirements.py
   │     │  │  │  ├─ v1beta2_cel_device_selector.py
   │     │  │  │  ├─ v1beta2_counter.py
   │     │  │  │  ├─ v1beta2_counter_set.py
   │     │  │  │  ├─ v1beta2_device.py
   │     │  │  │  ├─ v1beta2_device_allocation_configuration.py
   │     │  │  │  ├─ v1beta2_device_allocation_result.py
   │     │  │  │  ├─ v1beta2_device_attribute.py
   │     │  │  │  ├─ v1beta2_device_capacity.py
   │     │  │  │  ├─ v1beta2_device_claim.py
   │     │  │  │  ├─ v1beta2_device_claim_configuration.py
   │     │  │  │  ├─ v1beta2_device_class.py
   │     │  │  │  ├─ v1beta2_device_class_configuration.py
   │     │  │  │  ├─ v1beta2_device_class_list.py
   │     │  │  │  ├─ v1beta2_device_class_spec.py
   │     │  │  │  ├─ v1beta2_device_constraint.py
   │     │  │  │  ├─ v1beta2_device_counter_consumption.py
   │     │  │  │  ├─ v1beta2_device_request.py
   │     │  │  │  ├─ v1beta2_device_request_allocation_result.py
   │     │  │  │  ├─ v1beta2_device_selector.py
   │     │  │  │  ├─ v1beta2_device_sub_request.py
   │     │  │  │  ├─ v1beta2_device_taint.py
   │     │  │  │  ├─ v1beta2_device_toleration.py
   │     │  │  │  ├─ v1beta2_exact_device_request.py
   │     │  │  │  ├─ v1beta2_network_device_data.py
   │     │  │  │  ├─ v1beta2_opaque_device_configuration.py
   │     │  │  │  ├─ v1beta2_resource_claim.py
   │     │  │  │  ├─ v1beta2_resource_claim_consumer_reference.py
   │     │  │  │  ├─ v1beta2_resource_claim_list.py
   │     │  │  │  ├─ v1beta2_resource_claim_spec.py
   │     │  │  │  ├─ v1beta2_resource_claim_status.py
   │     │  │  │  ├─ v1beta2_resource_claim_template.py
   │     │  │  │  ├─ v1beta2_resource_claim_template_list.py
   │     │  │  │  ├─ v1beta2_resource_claim_template_spec.py
   │     │  │  │  ├─ v1beta2_resource_pool.py
   │     │  │  │  ├─ v1beta2_resource_slice.py
   │     │  │  │  ├─ v1beta2_resource_slice_list.py
   │     │  │  │  ├─ v1beta2_resource_slice_spec.py
   │     │  │  │  ├─ v1_affinity.py
   │     │  │  │  ├─ v1_aggregation_rule.py
   │     │  │  │  ├─ v1_allocated_device_status.py
   │     │  │  │  ├─ v1_allocation_result.py
   │     │  │  │  ├─ v1_api_group.py
   │     │  │  │  ├─ v1_api_group_list.py
   │     │  │  │  ├─ v1_api_resource.py
   │     │  │  │  ├─ v1_api_resource_list.py
   │     │  │  │  ├─ v1_api_service.py
   │     │  │  │  ├─ v1_api_service_condition.py
   │     │  │  │  ├─ v1_api_service_list.py
   │     │  │  │  ├─ v1_api_service_spec.py
   │     │  │  │  ├─ v1_api_service_status.py
   │     │  │  │  ├─ v1_api_versions.py
   │     │  │  │  ├─ v1_app_armor_profile.py
   │     │  │  │  ├─ v1_attached_volume.py
   │     │  │  │  ├─ v1_audit_annotation.py
   │     │  │  │  ├─ v1_aws_elastic_block_store_volume_source.py
   │     │  │  │  ├─ v1_azure_disk_volume_source.py
   │     │  │  │  ├─ v1_azure_file_persistent_volume_source.py
   │     │  │  │  ├─ v1_azure_file_volume_source.py
   │     │  │  │  ├─ v1_binding.py
   │     │  │  │  ├─ v1_bound_object_reference.py
   │     │  │  │  ├─ v1_capabilities.py
   │     │  │  │  ├─ v1_capacity_request_policy.py
   │     │  │  │  ├─ v1_capacity_request_policy_range.py
   │     │  │  │  ├─ v1_capacity_requirements.py
   │     │  │  │  ├─ v1_cel_device_selector.py
   │     │  │  │  ├─ v1_ceph_fs_persistent_volume_source.py
   │     │  │  │  ├─ v1_ceph_fs_volume_source.py
   │     │  │  │  ├─ v1_certificate_signing_request.py
   │     │  │  │  ├─ v1_certificate_signing_request_condition.py
   │     │  │  │  ├─ v1_certificate_signing_request_list.py
   │     │  │  │  ├─ v1_certificate_signing_request_spec.py
   │     │  │  │  ├─ v1_certificate_signing_request_status.py
   │     │  │  │  ├─ v1_cinder_persistent_volume_source.py
   │     │  │  │  ├─ v1_cinder_volume_source.py
   │     │  │  │  ├─ v1_client_ip_config.py
   │     │  │  │  ├─ v1_cluster_role.py
   │     │  │  │  ├─ v1_cluster_role_binding.py
   │     │  │  │  ├─ v1_cluster_role_binding_list.py
   │     │  │  │  ├─ v1_cluster_role_list.py
   │     │  │  │  ├─ v1_cluster_trust_bundle_projection.py
   │     │  │  │  ├─ v1_component_condition.py
   │     │  │  │  ├─ v1_component_status.py
   │     │  │  │  ├─ v1_component_status_list.py
   │     │  │  │  ├─ v1_condition.py
   │     │  │  │  ├─ v1_config_map.py
   │     │  │  │  ├─ v1_config_map_env_source.py
   │     │  │  │  ├─ v1_config_map_key_selector.py
   │     │  │  │  ├─ v1_config_map_list.py
   │     │  │  │  ├─ v1_config_map_node_config_source.py
   │     │  │  │  ├─ v1_config_map_projection.py
   │     │  │  │  ├─ v1_config_map_volume_source.py
   │     │  │  │  ├─ v1_container.py
   │     │  │  │  ├─ v1_container_extended_resource_request.py
   │     │  │  │  ├─ v1_container_image.py
   │     │  │  │  ├─ v1_container_port.py
   │     │  │  │  ├─ v1_container_resize_policy.py
   │     │  │  │  ├─ v1_container_restart_rule.py
   │     │  │  │  ├─ v1_container_restart_rule_on_exit_codes.py
   │     │  │  │  ├─ v1_container_state.py
   │     │  │  │  ├─ v1_container_state_running.py
   │     │  │  │  ├─ v1_container_state_terminated.py
   │     │  │  │  ├─ v1_container_state_waiting.py
   │     │  │  │  ├─ v1_container_status.py
   │     │  │  │  ├─ v1_container_user.py
   │     │  │  │  ├─ v1_controller_revision.py
   │     │  │  │  ├─ v1_controller_revision_list.py
   │     │  │  │  ├─ v1_counter.py
   │     │  │  │  ├─ v1_counter_set.py
   │     │  │  │  ├─ v1_cron_job.py
   │     │  │  │  ├─ v1_cron_job_list.py
   │     │  │  │  ├─ v1_cron_job_spec.py
   │     │  │  │  ├─ v1_cron_job_status.py
   │     │  │  │  ├─ v1_cross_version_object_reference.py
   │     │  │  │  ├─ v1_csi_driver.py
   │     │  │  │  ├─ v1_csi_driver_list.py
   │     │  │  │  ├─ v1_csi_driver_spec.py
   │     │  │  │  ├─ v1_csi_node.py
   │     │  │  │  ├─ v1_csi_node_driver.py
   │     │  │  │  ├─ v1_csi_node_list.py
   │     │  │  │  ├─ v1_csi_node_spec.py
   │     │  │  │  ├─ v1_csi_persistent_volume_source.py
   │     │  │  │  ├─ v1_csi_storage_capacity.py
   │     │  │  │  ├─ v1_csi_storage_capacity_list.py
   │     │  │  │  ├─ v1_csi_volume_source.py
   │     │  │  │  ├─ v1_custom_resource_column_definition.py
   │     │  │  │  ├─ v1_custom_resource_conversion.py
   │     │  │  │  ├─ v1_custom_resource_definition.py
   │     │  │  │  ├─ v1_custom_resource_definition_condition.py
   │     │  │  │  ├─ v1_custom_resource_definition_list.py
   │     │  │  │  ├─ v1_custom_resource_definition_names.py
   │     │  │  │  ├─ v1_custom_resource_definition_spec.py
   │     │  │  │  ├─ v1_custom_resource_definition_status.py
   │     │  │  │  ├─ v1_custom_resource_definition_version.py
   │     │  │  │  ├─ v1_custom_resource_subresources.py
   │     │  │  │  ├─ v1_custom_resource_subresource_scale.py
   │     │  │  │  ├─ v1_custom_resource_validation.py
   │     │  │  │  ├─ v1_daemon_endpoint.py
   │     │  │  │  ├─ v1_daemon_set.py
   │     │  │  │  ├─ v1_daemon_set_condition.py
   │     │  │  │  ├─ v1_daemon_set_list.py
   │     │  │  │  ├─ v1_daemon_set_spec.py
   │     │  │  │  ├─ v1_daemon_set_status.py
   │     │  │  │  ├─ v1_daemon_set_update_strategy.py
   │     │  │  │  ├─ v1_delete_options.py
   │     │  │  │  ├─ v1_deployment.py
   │     │  │  │  ├─ v1_deployment_condition.py
   │     │  │  │  ├─ v1_deployment_list.py
   │     │  │  │  ├─ v1_deployment_spec.py
   │     │  │  │  ├─ v1_deployment_status.py
   │     │  │  │  ├─ v1_deployment_strategy.py
   │     │  │  │  ├─ v1_device.py
   │     │  │  │  ├─ v1_device_allocation_configuration.py
   │     │  │  │  ├─ v1_device_allocation_result.py
   │     │  │  │  ├─ v1_device_attribute.py
   │     │  │  │  ├─ v1_device_capacity.py
   │     │  │  │  ├─ v1_device_claim.py
   │     │  │  │  ├─ v1_device_claim_configuration.py
   │     │  │  │  ├─ v1_device_class.py
   │     │  │  │  ├─ v1_device_class_configuration.py
   │     │  │  │  ├─ v1_device_class_list.py
   │     │  │  │  ├─ v1_device_class_spec.py
   │     │  │  │  ├─ v1_device_constraint.py
   │     │  │  │  ├─ v1_device_counter_consumption.py
   │     │  │  │  ├─ v1_device_request.py
   │     │  │  │  ├─ v1_device_request_allocation_result.py
   │     │  │  │  ├─ v1_device_selector.py
   │     │  │  │  ├─ v1_device_sub_request.py
   │     │  │  │  ├─ v1_device_taint.py
   │     │  │  │  ├─ v1_device_toleration.py
   │     │  │  │  ├─ v1_downward_api_projection.py
   │     │  │  │  ├─ v1_downward_api_volume_file.py
   │     │  │  │  ├─ v1_downward_api_volume_source.py
   │     │  │  │  ├─ v1_empty_dir_volume_source.py
   │     │  │  │  ├─ v1_endpoint.py
   │     │  │  │  ├─ v1_endpoints.py
   │     │  │  │  ├─ v1_endpoints_list.py
   │     │  │  │  ├─ v1_endpoint_address.py
   │     │  │  │  ├─ v1_endpoint_conditions.py
   │     │  │  │  ├─ v1_endpoint_hints.py
   │     │  │  │  ├─ v1_endpoint_slice.py
   │     │  │  │  ├─ v1_endpoint_slice_list.py
   │     │  │  │  ├─ v1_endpoint_subset.py
   │     │  │  │  ├─ v1_env_from_source.py
   │     │  │  │  ├─ v1_env_var.py
   │     │  │  │  ├─ v1_env_var_source.py
   │     │  │  │  ├─ v1_ephemeral_container.py
   │     │  │  │  ├─ v1_ephemeral_volume_source.py
   │     │  │  │  ├─ v1_event_source.py
   │     │  │  │  ├─ v1_eviction.py
   │     │  │  │  ├─ v1_exact_device_request.py
   │     │  │  │  ├─ v1_exec_action.py
   │     │  │  │  ├─ v1_exempt_priority_level_configuration.py
   │     │  │  │  ├─ v1_expression_warning.py
   │     │  │  │  ├─ v1_external_documentation.py
   │     │  │  │  ├─ v1_fc_volume_source.py
   │     │  │  │  ├─ v1_field_selector_attributes.py
   │     │  │  │  ├─ v1_field_selector_requirement.py
   │     │  │  │  ├─ v1_file_key_selector.py
   │     │  │  │  ├─ v1_flex_persistent_volume_source.py
   │     │  │  │  ├─ v1_flex_volume_source.py
   │     │  │  │  ├─ v1_flocker_volume_source.py
   │     │  │  │  ├─ v1_flow_distinguisher_method.py
   │     │  │  │  ├─ v1_flow_schema.py
   │     │  │  │  ├─ v1_flow_schema_condition.py
   │     │  │  │  ├─ v1_flow_schema_list.py
   │     │  │  │  ├─ v1_flow_schema_spec.py
   │     │  │  │  ├─ v1_flow_schema_status.py
   │     │  │  │  ├─ v1_for_node.py
   │     │  │  │  ├─ v1_for_zone.py
   │     │  │  │  ├─ v1_gce_persistent_disk_volume_source.py
   │     │  │  │  ├─ v1_git_repo_volume_source.py
   │     │  │  │  ├─ v1_glusterfs_persistent_volume_source.py
   │     │  │  │  ├─ v1_glusterfs_volume_source.py
   │     │  │  │  ├─ v1_group_resource.py
   │     │  │  │  ├─ v1_group_subject.py
   │     │  │  │  ├─ v1_group_version_for_discovery.py
   │     │  │  │  ├─ v1_grpc_action.py
   │     │  │  │  ├─ v1_horizontal_pod_autoscaler.py
   │     │  │  │  ├─ v1_horizontal_pod_autoscaler_list.py
   │     │  │  │  ├─ v1_horizontal_pod_autoscaler_spec.py
   │     │  │  │  ├─ v1_horizontal_pod_autoscaler_status.py
   │     │  │  │  ├─ v1_host_alias.py
   │     │  │  │  ├─ v1_host_ip.py
   │     │  │  │  ├─ v1_host_path_volume_source.py
   │     │  │  │  ├─ v1_http_get_action.py
   │     │  │  │  ├─ v1_http_header.py
   │     │  │  │  ├─ v1_http_ingress_path.py
   │     │  │  │  ├─ v1_http_ingress_rule_value.py
   │     │  │  │  ├─ v1_image_volume_source.py
   │     │  │  │  ├─ v1_ingress.py
   │     │  │  │  ├─ v1_ingress_backend.py
   │     │  │  │  ├─ v1_ingress_class.py
   │     │  │  │  ├─ v1_ingress_class_list.py
   │     │  │  │  ├─ v1_ingress_class_parameters_reference.py
   │     │  │  │  ├─ v1_ingress_class_spec.py
   │     │  │  │  ├─ v1_ingress_list.py
   │     │  │  │  ├─ v1_ingress_load_balancer_ingress.py
   │     │  │  │  ├─ v1_ingress_load_balancer_status.py
   │     │  │  │  ├─ v1_ingress_port_status.py
   │     │  │  │  ├─ v1_ingress_rule.py
   │     │  │  │  ├─ v1_ingress_service_backend.py
   │     │  │  │  ├─ v1_ingress_spec.py
   │     │  │  │  ├─ v1_ingress_status.py
   │     │  │  │  ├─ v1_ingress_tls.py
   │     │  │  │  ├─ v1_ip_address.py
   │     │  │  │  ├─ v1_ip_address_list.py
   │     │  │  │  ├─ v1_ip_address_spec.py
   │     │  │  │  ├─ v1_ip_block.py
   │     │  │  │  ├─ v1_iscsi_persistent_volume_source.py
   │     │  │  │  ├─ v1_iscsi_volume_source.py
   │     │  │  │  ├─ v1_job.py
   │     │  │  │  ├─ v1_job_condition.py
   │     │  │  │  ├─ v1_job_list.py
   │     │  │  │  ├─ v1_job_spec.py
   │     │  │  │  ├─ v1_job_status.py
   │     │  │  │  ├─ v1_job_template_spec.py
   │     │  │  │  ├─ v1_json_schema_props.py
   │     │  │  │  ├─ v1_key_to_path.py
   │     │  │  │  ├─ v1_label_selector.py
   │     │  │  │  ├─ v1_label_selector_attributes.py
   │     │  │  │  ├─ v1_label_selector_requirement.py
   │     │  │  │  ├─ v1_lease.py
   │     │  │  │  ├─ v1_lease_list.py
   │     │  │  │  ├─ v1_lease_spec.py
   │     │  │  │  ├─ v1_lifecycle.py
   │     │  │  │  ├─ v1_lifecycle_handler.py
   │     │  │  │  ├─ v1_limited_priority_level_configuration.py
   │     │  │  │  ├─ v1_limit_range.py
   │     │  │  │  ├─ v1_limit_range_item.py
   │     │  │  │  ├─ v1_limit_range_list.py
   │     │  │  │  ├─ v1_limit_range_spec.py
   │     │  │  │  ├─ v1_limit_response.py
   │     │  │  │  ├─ v1_linux_container_user.py
   │     │  │  │  ├─ v1_list_meta.py
   │     │  │  │  ├─ v1_load_balancer_ingress.py
   │     │  │  │  ├─ v1_load_balancer_status.py
   │     │  │  │  ├─ v1_local_object_reference.py
   │     │  │  │  ├─ v1_local_subject_access_review.py
   │     │  │  │  ├─ v1_local_volume_source.py
   │     │  │  │  ├─ v1_managed_fields_entry.py
   │     │  │  │  ├─ v1_match_condition.py
   │     │  │  │  ├─ v1_match_resources.py
   │     │  │  │  ├─ v1_modify_volume_status.py
   │     │  │  │  ├─ v1_mutating_webhook.py
   │     │  │  │  ├─ v1_mutating_webhook_configuration.py
   │     │  │  │  ├─ v1_mutating_webhook_configuration_list.py
   │     │  │  │  ├─ v1_named_rule_with_operations.py
   │     │  │  │  ├─ v1_namespace.py
   │     │  │  │  ├─ v1_namespace_condition.py
   │     │  │  │  ├─ v1_namespace_list.py
   │     │  │  │  ├─ v1_namespace_spec.py
   │     │  │  │  ├─ v1_namespace_status.py
   │     │  │  │  ├─ v1_network_device_data.py
   │     │  │  │  ├─ v1_network_policy.py
   │     │  │  │  ├─ v1_network_policy_egress_rule.py
   │     │  │  │  ├─ v1_network_policy_ingress_rule.py
   │     │  │  │  ├─ v1_network_policy_list.py
   │     │  │  │  ├─ v1_network_policy_peer.py
   │     │  │  │  ├─ v1_network_policy_port.py
   │     │  │  │  ├─ v1_network_policy_spec.py
   │     │  │  │  ├─ v1_nfs_volume_source.py
   │     │  │  │  ├─ v1_node.py
   │     │  │  │  ├─ v1_node_address.py
   │     │  │  │  ├─ v1_node_affinity.py
   │     │  │  │  ├─ v1_node_condition.py
   │     │  │  │  ├─ v1_node_config_source.py
   │     │  │  │  ├─ v1_node_config_status.py
   │     │  │  │  ├─ v1_node_daemon_endpoints.py
   │     │  │  │  ├─ v1_node_features.py
   │     │  │  │  ├─ v1_node_list.py
   │     │  │  │  ├─ v1_node_runtime_handler.py
   │     │  │  │  ├─ v1_node_runtime_handler_features.py
   │     │  │  │  ├─ v1_node_selector.py
   │     │  │  │  ├─ v1_node_selector_requirement.py
   │     │  │  │  ├─ v1_node_selector_term.py
   │     │  │  │  ├─ v1_node_spec.py
   │     │  │  │  ├─ v1_node_status.py
   │     │  │  │  ├─ v1_node_swap_status.py
   │     │  │  │  ├─ v1_node_system_info.py
   │     │  │  │  ├─ v1_non_resource_attributes.py
   │     │  │  │  ├─ v1_non_resource_policy_rule.py
   │     │  │  │  ├─ v1_non_resource_rule.py
   │     │  │  │  ├─ v1_object_field_selector.py
   │     │  │  │  ├─ v1_object_meta.py
   │     │  │  │  ├─ v1_object_reference.py
   │     │  │  │  ├─ v1_opaque_device_configuration.py
   │     │  │  │  ├─ v1_overhead.py
   │     │  │  │  ├─ v1_owner_reference.py
   │     │  │  │  ├─ v1_param_kind.py
   │     │  │  │  ├─ v1_param_ref.py
   │     │  │  │  ├─ v1_parent_reference.py
   │     │  │  │  ├─ v1_persistent_volume.py
   │     │  │  │  ├─ v1_persistent_volume_claim.py
   │     │  │  │  ├─ v1_persistent_volume_claim_condition.py
   │     │  │  │  ├─ v1_persistent_volume_claim_list.py
   │     │  │  │  ├─ v1_persistent_volume_claim_spec.py
   │     │  │  │  ├─ v1_persistent_volume_claim_status.py
   │     │  │  │  ├─ v1_persistent_volume_claim_template.py
   │     │  │  │  ├─ v1_persistent_volume_claim_volume_source.py
   │     │  │  │  ├─ v1_persistent_volume_list.py
   │     │  │  │  ├─ v1_persistent_volume_spec.py
   │     │  │  │  ├─ v1_persistent_volume_status.py
   │     │  │  │  ├─ v1_photon_persistent_disk_volume_source.py
   │     │  │  │  ├─ v1_pod.py
   │     │  │  │  ├─ v1_pod_affinity.py
   │     │  │  │  ├─ v1_pod_affinity_term.py
   │     │  │  │  ├─ v1_pod_anti_affinity.py
   │     │  │  │  ├─ v1_pod_certificate_projection.py
   │     │  │  │  ├─ v1_pod_condition.py
   │     │  │  │  ├─ v1_pod_disruption_budget.py
   │     │  │  │  ├─ v1_pod_disruption_budget_list.py
   │     │  │  │  ├─ v1_pod_disruption_budget_spec.py
   │     │  │  │  ├─ v1_pod_disruption_budget_status.py
   │     │  │  │  ├─ v1_pod_dns_config.py
   │     │  │  │  ├─ v1_pod_dns_config_option.py
   │     │  │  │  ├─ v1_pod_extended_resource_claim_status.py
   │     │  │  │  ├─ v1_pod_failure_policy.py
   │     │  │  │  ├─ v1_pod_failure_policy_on_exit_codes_requirement.py
   │     │  │  │  ├─ v1_pod_failure_policy_on_pod_conditions_pattern.py
   │     │  │  │  ├─ v1_pod_failure_policy_rule.py
   │     │  │  │  ├─ v1_pod_ip.py
   │     │  │  │  ├─ v1_pod_list.py
   │     │  │  │  ├─ v1_pod_os.py
   │     │  │  │  ├─ v1_pod_readiness_gate.py
   │     │  │  │  ├─ v1_pod_resource_claim.py
   │     │  │  │  ├─ v1_pod_resource_claim_status.py
   │     │  │  │  ├─ v1_pod_scheduling_gate.py
   │     │  │  │  ├─ v1_pod_security_context.py
   │     │  │  │  ├─ v1_pod_spec.py
   │     │  │  │  ├─ v1_pod_status.py
   │     │  │  │  ├─ v1_pod_template.py
   │     │  │  │  ├─ v1_pod_template_list.py
   │     │  │  │  ├─ v1_pod_template_spec.py
   │     │  │  │  ├─ v1_policy_rule.py
   │     │  │  │  ├─ v1_policy_rules_with_subjects.py
   │     │  │  │  ├─ v1_portworx_volume_source.py
   │     │  │  │  ├─ v1_port_status.py
   │     │  │  │  ├─ v1_preconditions.py
   │     │  │  │  ├─ v1_preferred_scheduling_term.py
   │     │  │  │  ├─ v1_priority_class.py
   │     │  │  │  ├─ v1_priority_class_list.py
   │     │  │  │  ├─ v1_priority_level_configuration.py
   │     │  │  │  ├─ v1_priority_level_configuration_condition.py
   │     │  │  │  ├─ v1_priority_level_configuration_list.py
   │     │  │  │  ├─ v1_priority_level_configuration_reference.py
   │     │  │  │  ├─ v1_priority_level_configuration_spec.py
   │     │  │  │  ├─ v1_priority_level_configuration_status.py
   │     │  │  │  ├─ v1_probe.py
   │     │  │  │  ├─ v1_projected_volume_source.py
   │     │  │  │  ├─ v1_queuing_configuration.py
   │     │  │  │  ├─ v1_quobyte_volume_source.py
   │     │  │  │  ├─ v1_rbd_persistent_volume_source.py
   │     │  │  │  ├─ v1_rbd_volume_source.py
   │     │  │  │  ├─ v1_replication_controller.py
   │     │  │  │  ├─ v1_replication_controller_condition.py
   │     │  │  │  ├─ v1_replication_controller_list.py
   │     │  │  │  ├─ v1_replication_controller_spec.py
   │     │  │  │  ├─ v1_replication_controller_status.py
   │     │  │  │  ├─ v1_replica_set.py
   │     │  │  │  ├─ v1_replica_set_condition.py
   │     │  │  │  ├─ v1_replica_set_list.py
   │     │  │  │  ├─ v1_replica_set_spec.py
   │     │  │  │  ├─ v1_replica_set_status.py
   │     │  │  │  ├─ v1_resource_attributes.py
   │     │  │  │  ├─ v1_resource_claim_consumer_reference.py
   │     │  │  │  ├─ v1_resource_claim_list.py
   │     │  │  │  ├─ v1_resource_claim_spec.py
   │     │  │  │  ├─ v1_resource_claim_status.py
   │     │  │  │  ├─ v1_resource_claim_template.py
   │     │  │  │  ├─ v1_resource_claim_template_list.py
   │     │  │  │  ├─ v1_resource_claim_template_spec.py
   │     │  │  │  ├─ v1_resource_field_selector.py
   │     │  │  │  ├─ v1_resource_health.py
   │     │  │  │  ├─ v1_resource_policy_rule.py
   │     │  │  │  ├─ v1_resource_pool.py
   │     │  │  │  ├─ v1_resource_quota.py
   │     │  │  │  ├─ v1_resource_quota_list.py
   │     │  │  │  ├─ v1_resource_quota_spec.py
   │     │  │  │  ├─ v1_resource_quota_status.py
   │     │  │  │  ├─ v1_resource_requirements.py
   │     │  │  │  ├─ v1_resource_rule.py
   │     │  │  │  ├─ v1_resource_slice.py
   │     │  │  │  ├─ v1_resource_slice_list.py
   │     │  │  │  ├─ v1_resource_slice_spec.py
   │     │  │  │  ├─ v1_resource_status.py
   │     │  │  │  ├─ v1_role.py
   │     │  │  │  ├─ v1_role_binding.py
   │     │  │  │  ├─ v1_role_binding_list.py
   │     │  │  │  ├─ v1_role_list.py
   │     │  │  │  ├─ v1_role_ref.py
   │     │  │  │  ├─ v1_rolling_update_daemon_set.py
   │     │  │  │  ├─ v1_rolling_update_deployment.py
   │     │  │  │  ├─ v1_rolling_update_stateful_set_strategy.py
   │     │  │  │  ├─ v1_rule_with_operations.py
   │     │  │  │  ├─ v1_runtime_class.py
   │     │  │  │  ├─ v1_runtime_class_list.py
   │     │  │  │  ├─ v1_scale.py
   │     │  │  │  ├─ v1_scale_io_persistent_volume_source.py
   │     │  │  │  ├─ v1_scale_io_volume_source.py
   │     │  │  │  ├─ v1_scale_spec.py
   │     │  │  │  ├─ v1_scale_status.py
   │     │  │  │  ├─ v1_scheduling.py
   │     │  │  │  ├─ v1_scoped_resource_selector_requirement.py
   │     │  │  │  ├─ v1_scope_selector.py
   │     │  │  │  ├─ v1_seccomp_profile.py
   │     │  │  │  ├─ v1_secret.py
   │     │  │  │  ├─ v1_secret_env_source.py
   │     │  │  │  ├─ v1_secret_key_selector.py
   │     │  │  │  ├─ v1_secret_list.py
   │     │  │  │  ├─ v1_secret_projection.py
   │     │  │  │  ├─ v1_secret_reference.py
   │     │  │  │  ├─ v1_secret_volume_source.py
   │     │  │  │  ├─ v1_security_context.py
   │     │  │  │  ├─ v1_selectable_field.py
   │     │  │  │  ├─ v1_self_subject_access_review.py
   │     │  │  │  ├─ v1_self_subject_access_review_spec.py
   │     │  │  │  ├─ v1_self_subject_review.py
   │     │  │  │  ├─ v1_self_subject_review_status.py
   │     │  │  │  ├─ v1_self_subject_rules_review.py
   │     │  │  │  ├─ v1_self_subject_rules_review_spec.py
   │     │  │  │  ├─ v1_server_address_by_client_cidr.py
   │     │  │  │  ├─ v1_service.py
   │     │  │  │  ├─ v1_service_account.py
   │     │  │  │  ├─ v1_service_account_list.py
   │     │  │  │  ├─ v1_service_account_subject.py
   │     │  │  │  ├─ v1_service_account_token_projection.py
   │     │  │  │  ├─ v1_service_backend_port.py
   │     │  │  │  ├─ v1_service_cidr.py
   │     │  │  │  ├─ v1_service_cidr_list.py
   │     │  │  │  ├─ v1_service_cidr_spec.py
   │     │  │  │  ├─ v1_service_cidr_status.py
   │     │  │  │  ├─ v1_service_list.py
   │     │  │  │  ├─ v1_service_port.py
   │     │  │  │  ├─ v1_service_spec.py
   │     │  │  │  ├─ v1_service_status.py
   │     │  │  │  ├─ v1_session_affinity_config.py
   │     │  │  │  ├─ v1_se_linux_options.py
   │     │  │  │  ├─ v1_sleep_action.py
   │     │  │  │  ├─ v1_stateful_set.py
   │     │  │  │  ├─ v1_stateful_set_condition.py
   │     │  │  │  ├─ v1_stateful_set_list.py
   │     │  │  │  ├─ v1_stateful_set_ordinals.py
   │     │  │  │  ├─ v1_stateful_set_persistent_volume_claim_retention_policy.py
   │     │  │  │  ├─ v1_stateful_set_spec.py
   │     │  │  │  ├─ v1_stateful_set_status.py
   │     │  │  │  ├─ v1_stateful_set_update_strategy.py
   │     │  │  │  ├─ v1_status.py
   │     │  │  │  ├─ v1_status_cause.py
   │     │  │  │  ├─ v1_status_details.py
   │     │  │  │  ├─ v1_storage_class.py
   │     │  │  │  ├─ v1_storage_class_list.py
   │     │  │  │  ├─ v1_storage_os_persistent_volume_source.py
   │     │  │  │  ├─ v1_storage_os_volume_source.py
   │     │  │  │  ├─ v1_subject_access_review.py
   │     │  │  │  ├─ v1_subject_access_review_spec.py
   │     │  │  │  ├─ v1_subject_access_review_status.py
   │     │  │  │  ├─ v1_subject_rules_review_status.py
   │     │  │  │  ├─ v1_success_policy.py
   │     │  │  │  ├─ v1_success_policy_rule.py
   │     │  │  │  ├─ v1_sysctl.py
   │     │  │  │  ├─ v1_taint.py
   │     │  │  │  ├─ v1_tcp_socket_action.py
   │     │  │  │  ├─ v1_token_request_spec.py
   │     │  │  │  ├─ v1_token_request_status.py
   │     │  │  │  ├─ v1_token_review.py
   │     │  │  │  ├─ v1_token_review_spec.py
   │     │  │  │  ├─ v1_token_review_status.py
   │     │  │  │  ├─ v1_toleration.py
   │     │  │  │  ├─ v1_topology_selector_label_requirement.py
   │     │  │  │  ├─ v1_topology_selector_term.py
   │     │  │  │  ├─ v1_topology_spread_constraint.py
   │     │  │  │  ├─ v1_typed_local_object_reference.py
   │     │  │  │  ├─ v1_typed_object_reference.py
   │     │  │  │  ├─ v1_type_checking.py
   │     │  │  │  ├─ v1_uncounted_terminated_pods.py
   │     │  │  │  ├─ v1_user_info.py
   │     │  │  │  ├─ v1_user_subject.py
   │     │  │  │  ├─ v1_validating_admission_policy.py
   │     │  │  │  ├─ v1_validating_admission_policy_binding.py
   │     │  │  │  ├─ v1_validating_admission_policy_binding_list.py
   │     │  │  │  ├─ v1_validating_admission_policy_binding_spec.py
   │     │  │  │  ├─ v1_validating_admission_policy_list.py
   │     │  │  │  ├─ v1_validating_admission_policy_spec.py
   │     │  │  │  ├─ v1_validating_admission_policy_status.py
   │     │  │  │  ├─ v1_validating_webhook.py
   │     │  │  │  ├─ v1_validating_webhook_configuration.py
   │     │  │  │  ├─ v1_validating_webhook_configuration_list.py
   │     │  │  │  ├─ v1_validation.py
   │     │  │  │  ├─ v1_validation_rule.py
   │     │  │  │  ├─ v1_variable.py
   │     │  │  │  ├─ v1_volume.py
   │     │  │  │  ├─ v1_volume_attachment.py
   │     │  │  │  ├─ v1_volume_attachment_list.py
   │     │  │  │  ├─ v1_volume_attachment_source.py
   │     │  │  │  ├─ v1_volume_attachment_spec.py
   │     │  │  │  ├─ v1_volume_attachment_status.py
   │     │  │  │  ├─ v1_volume_attributes_class.py
   │     │  │  │  ├─ v1_volume_attributes_class_list.py
   │     │  │  │  ├─ v1_volume_device.py
   │     │  │  │  ├─ v1_volume_error.py
   │     │  │  │  ├─ v1_volume_mount.py
   │     │  │  │  ├─ v1_volume_mount_status.py
   │     │  │  │  ├─ v1_volume_node_affinity.py
   │     │  │  │  ├─ v1_volume_node_resources.py
   │     │  │  │  ├─ v1_volume_projection.py
   │     │  │  │  ├─ v1_volume_resource_requirements.py
   │     │  │  │  ├─ v1_vsphere_virtual_disk_volume_source.py
   │     │  │  │  ├─ v1_watch_event.py
   │     │  │  │  ├─ v1_webhook_conversion.py
   │     │  │  │  ├─ v1_weighted_pod_affinity_term.py
   │     │  │  │  ├─ v1_windows_security_context_options.py
   │     │  │  │  ├─ v1_workload_reference.py
   │     │  │  │  ├─ v2_container_resource_metric_source.py
   │     │  │  │  ├─ v2_container_resource_metric_status.py
   │     │  │  │  ├─ v2_cross_version_object_reference.py
   │     │  │  │  ├─ v2_external_metric_source.py
   │     │  │  │  ├─ v2_external_metric_status.py
   │     │  │  │  ├─ v2_horizontal_pod_autoscaler.py
   │     │  │  │  ├─ v2_horizontal_pod_autoscaler_behavior.py
   │     │  │  │  ├─ v2_horizontal_pod_autoscaler_condition.py
   │     │  │  │  ├─ v2_horizontal_pod_autoscaler_list.py
   │     │  │  │  ├─ v2_horizontal_pod_autoscaler_spec.py
   │     │  │  │  ├─ v2_horizontal_pod_autoscaler_status.py
   │     │  │  │  ├─ v2_hpa_scaling_policy.py
   │     │  │  │  ├─ v2_hpa_scaling_rules.py
   │     │  │  │  ├─ v2_metric_identifier.py
   │     │  │  │  ├─ v2_metric_spec.py
   │     │  │  │  ├─ v2_metric_status.py
   │     │  │  │  ├─ v2_metric_target.py
   │     │  │  │  ├─ v2_metric_value_status.py
   │     │  │  │  ├─ v2_object_metric_source.py
   │     │  │  │  ├─ v2_object_metric_status.py
   │     │  │  │  ├─ v2_pods_metric_source.py
   │     │  │  │  ├─ v2_pods_metric_status.py
   │     │  │  │  ├─ v2_resource_metric_source.py
   │     │  │  │  ├─ v2_resource_metric_status.py
   │     │  │  │  ├─ version_info.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ admissionregistration_v1_service_reference.cpython-311.pyc
   │     │  │  │     ├─ admissionregistration_v1_webhook_client_config.cpython-311.pyc
   │     │  │  │     ├─ apiextensions_v1_service_reference.cpython-311.pyc
   │     │  │  │     ├─ apiextensions_v1_webhook_client_config.cpython-311.pyc
   │     │  │  │     ├─ apiregistration_v1_service_reference.cpython-311.pyc
   │     │  │  │     ├─ authentication_v1_token_request.cpython-311.pyc
   │     │  │  │     ├─ core_v1_endpoint_port.cpython-311.pyc
   │     │  │  │     ├─ core_v1_event.cpython-311.pyc
   │     │  │  │     ├─ core_v1_event_list.cpython-311.pyc
   │     │  │  │     ├─ core_v1_event_series.cpython-311.pyc
   │     │  │  │     ├─ core_v1_resource_claim.cpython-311.pyc
   │     │  │  │     ├─ discovery_v1_endpoint_port.cpython-311.pyc
   │     │  │  │     ├─ events_v1_event.cpython-311.pyc
   │     │  │  │     ├─ events_v1_event_list.cpython-311.pyc
   │     │  │  │     ├─ events_v1_event_series.cpython-311.pyc
   │     │  │  │     ├─ flowcontrol_v1_subject.cpython-311.pyc
   │     │  │  │     ├─ rbac_v1_subject.cpython-311.pyc
   │     │  │  │     ├─ resource_v1_resource_claim.cpython-311.pyc
   │     │  │  │     ├─ storage_v1_token_request.cpython-311.pyc
   │     │  │  │     ├─ v1alpha1_apply_configuration.cpython-311.pyc
   │     │  │  │     ├─ v1alpha1_cluster_trust_bundle.cpython-311.pyc
   │     │  │  │     ├─ v1alpha1_cluster_trust_bundle_list.cpython-311.pyc
   │     │  │  │     ├─ v1alpha1_cluster_trust_bundle_spec.cpython-311.pyc
   │     │  │  │     ├─ v1alpha1_gang_scheduling_policy.cpython-311.pyc
   │     │  │  │     ├─ v1alpha1_json_patch.cpython-311.pyc
   │     │  │  │     ├─ v1alpha1_match_condition.cpython-311.pyc
   │     │  │  │     ├─ v1alpha1_match_resources.cpython-311.pyc
   │     │  │  │     ├─ v1alpha1_mutating_admission_policy.cpython-311.pyc
   │     │  │  │     ├─ v1alpha1_mutating_admission_policy_binding.cpython-311.pyc
   │     │  │  │     ├─ v1alpha1_mutating_admission_policy_binding_list.cpython-311.pyc
   │     │  │  │     ├─ v1alpha1_mutating_admission_policy_binding_spec.cpython-311.pyc
   │     │  │  │     ├─ v1alpha1_mutating_admission_policy_list.cpython-311.pyc
   │     │  │  │     ├─ v1alpha1_mutating_admission_policy_spec.cpython-311.pyc
   │     │  │  │     ├─ v1alpha1_mutation.cpython-311.pyc
   │     │  │  │     ├─ v1alpha1_named_rule_with_operations.cpython-311.pyc
   │     │  │  │     ├─ v1alpha1_param_kind.cpython-311.pyc
   │     │  │  │     ├─ v1alpha1_param_ref.cpython-311.pyc
   │     │  │  │     ├─ v1alpha1_pod_group.cpython-311.pyc
   │     │  │  │     ├─ v1alpha1_pod_group_policy.cpython-311.pyc
   │     │  │  │     ├─ v1alpha1_server_storage_version.cpython-311.pyc
   │     │  │  │     ├─ v1alpha1_storage_version.cpython-311.pyc
   │     │  │  │     ├─ v1alpha1_storage_version_condition.cpython-311.pyc
   │     │  │  │     ├─ v1alpha1_storage_version_list.cpython-311.pyc
   │     │  │  │     ├─ v1alpha1_storage_version_status.cpython-311.pyc
   │     │  │  │     ├─ v1alpha1_typed_local_object_reference.cpython-311.pyc
   │     │  │  │     ├─ v1alpha1_variable.cpython-311.pyc
   │     │  │  │     ├─ v1alpha1_workload.cpython-311.pyc
   │     │  │  │     ├─ v1alpha1_workload_list.cpython-311.pyc
   │     │  │  │     ├─ v1alpha1_workload_spec.cpython-311.pyc
   │     │  │  │     ├─ v1alpha2_lease_candidate.cpython-311.pyc
   │     │  │  │     ├─ v1alpha2_lease_candidate_list.cpython-311.pyc
   │     │  │  │     ├─ v1alpha2_lease_candidate_spec.cpython-311.pyc
   │     │  │  │     ├─ v1alpha3_device_taint.cpython-311.pyc
   │     │  │  │     ├─ v1alpha3_device_taint_rule.cpython-311.pyc
   │     │  │  │     ├─ v1alpha3_device_taint_rule_list.cpython-311.pyc
   │     │  │  │     ├─ v1alpha3_device_taint_rule_spec.cpython-311.pyc
   │     │  │  │     ├─ v1alpha3_device_taint_rule_status.cpython-311.pyc
   │     │  │  │     ├─ v1alpha3_device_taint_selector.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_allocated_device_status.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_allocation_result.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_apply_configuration.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_basic_device.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_capacity_request_policy.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_capacity_request_policy_range.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_capacity_requirements.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_cel_device_selector.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_cluster_trust_bundle.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_cluster_trust_bundle_list.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_cluster_trust_bundle_spec.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_counter.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_counter_set.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_device.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_device_allocation_configuration.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_device_allocation_result.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_device_attribute.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_device_capacity.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_device_claim.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_device_claim_configuration.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_device_class.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_device_class_configuration.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_device_class_list.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_device_class_spec.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_device_constraint.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_device_counter_consumption.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_device_request.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_device_request_allocation_result.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_device_selector.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_device_sub_request.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_device_taint.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_device_toleration.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_ip_address.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_ip_address_list.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_ip_address_spec.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_json_patch.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_lease_candidate.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_lease_candidate_list.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_lease_candidate_spec.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_match_condition.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_match_resources.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_mutating_admission_policy.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_mutating_admission_policy_binding.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_mutating_admission_policy_binding_list.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_mutating_admission_policy_binding_spec.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_mutating_admission_policy_list.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_mutating_admission_policy_spec.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_mutation.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_named_rule_with_operations.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_network_device_data.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_opaque_device_configuration.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_param_kind.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_param_ref.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_parent_reference.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_pod_certificate_request.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_pod_certificate_request_list.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_pod_certificate_request_spec.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_pod_certificate_request_status.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_resource_claim.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_resource_claim_consumer_reference.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_resource_claim_list.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_resource_claim_spec.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_resource_claim_status.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_resource_claim_template.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_resource_claim_template_list.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_resource_claim_template_spec.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_resource_pool.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_resource_slice.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_resource_slice_list.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_resource_slice_spec.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_service_cidr.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_service_cidr_list.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_service_cidr_spec.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_service_cidr_status.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_storage_version_migration.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_storage_version_migration_list.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_storage_version_migration_spec.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_storage_version_migration_status.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_variable.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_volume_attributes_class.cpython-311.pyc
   │     │  │  │     ├─ v1beta1_volume_attributes_class_list.cpython-311.pyc
   │     │  │  │     ├─ v1beta2_allocated_device_status.cpython-311.pyc
   │     │  │  │     ├─ v1beta2_allocation_result.cpython-311.pyc
   │     │  │  │     ├─ v1beta2_capacity_request_policy.cpython-311.pyc
   │     │  │  │     ├─ v1beta2_capacity_request_policy_range.cpython-311.pyc
   │     │  │  │     ├─ v1beta2_capacity_requirements.cpython-311.pyc
   │     │  │  │     ├─ v1beta2_cel_device_selector.cpython-311.pyc
   │     │  │  │     ├─ v1beta2_counter.cpython-311.pyc
   │     │  │  │     ├─ v1beta2_counter_set.cpython-311.pyc
   │     │  │  │     ├─ v1beta2_device.cpython-311.pyc
   │     │  │  │     ├─ v1beta2_device_allocation_configuration.cpython-311.pyc
   │     │  │  │     ├─ v1beta2_device_allocation_result.cpython-311.pyc
   │     │  │  │     ├─ v1beta2_device_attribute.cpython-311.pyc
   │     │  │  │     ├─ v1beta2_device_capacity.cpython-311.pyc
   │     │  │  │     ├─ v1beta2_device_claim.cpython-311.pyc
   │     │  │  │     ├─ v1beta2_device_claim_configuration.cpython-311.pyc
   │     │  │  │     ├─ v1beta2_device_class.cpython-311.pyc
   │     │  │  │     ├─ v1beta2_device_class_configuration.cpython-311.pyc
   │     │  │  │     ├─ v1beta2_device_class_list.cpython-311.pyc
   │     │  │  │     ├─ v1beta2_device_class_spec.cpython-311.pyc
   │     │  │  │     ├─ v1beta2_device_constraint.cpython-311.pyc
   │     │  │  │     ├─ v1beta2_device_counter_consumption.cpython-311.pyc
   │     │  │  │     ├─ v1beta2_device_request.cpython-311.pyc
   │     │  │  │     ├─ v1beta2_device_request_allocation_result.cpython-311.pyc
   │     │  │  │     ├─ v1beta2_device_selector.cpython-311.pyc
   │     │  │  │     ├─ v1beta2_device_sub_request.cpython-311.pyc
   │     │  │  │     ├─ v1beta2_device_taint.cpython-311.pyc
   │     │  │  │     ├─ v1beta2_device_toleration.cpython-311.pyc
   │     │  │  │     ├─ v1beta2_exact_device_request.cpython-311.pyc
   │     │  │  │     ├─ v1beta2_network_device_data.cpython-311.pyc
   │     │  │  │     ├─ v1beta2_opaque_device_configuration.cpython-311.pyc
   │     │  │  │     ├─ v1beta2_resource_claim.cpython-311.pyc
   │     │  │  │     ├─ v1beta2_resource_claim_consumer_reference.cpython-311.pyc
   │     │  │  │     ├─ v1beta2_resource_claim_list.cpython-311.pyc
   │     │  │  │     ├─ v1beta2_resource_claim_spec.cpython-311.pyc
   │     │  │  │     ├─ v1beta2_resource_claim_status.cpython-311.pyc
   │     │  │  │     ├─ v1beta2_resource_claim_template.cpython-311.pyc
   │     │  │  │     ├─ v1beta2_resource_claim_template_list.cpython-311.pyc
   │     │  │  │     ├─ v1beta2_resource_claim_template_spec.cpython-311.pyc
   │     │  │  │     ├─ v1beta2_resource_pool.cpython-311.pyc
   │     │  │  │     ├─ v1beta2_resource_slice.cpython-311.pyc
   │     │  │  │     ├─ v1beta2_resource_slice_list.cpython-311.pyc
   │     │  │  │     ├─ v1beta2_resource_slice_spec.cpython-311.pyc
   │     │  │  │     ├─ v1_affinity.cpython-311.pyc
   │     │  │  │     ├─ v1_aggregation_rule.cpython-311.pyc
   │     │  │  │     ├─ v1_allocated_device_status.cpython-311.pyc
   │     │  │  │     ├─ v1_allocation_result.cpython-311.pyc
   │     │  │  │     ├─ v1_api_group.cpython-311.pyc
   │     │  │  │     ├─ v1_api_group_list.cpython-311.pyc
   │     │  │  │     ├─ v1_api_resource.cpython-311.pyc
   │     │  │  │     ├─ v1_api_resource_list.cpython-311.pyc
   │     │  │  │     ├─ v1_api_service.cpython-311.pyc
   │     │  │  │     ├─ v1_api_service_condition.cpython-311.pyc
   │     │  │  │     ├─ v1_api_service_list.cpython-311.pyc
   │     │  │  │     ├─ v1_api_service_spec.cpython-311.pyc
   │     │  │  │     ├─ v1_api_service_status.cpython-311.pyc
   │     │  │  │     ├─ v1_api_versions.cpython-311.pyc
   │     │  │  │     ├─ v1_app_armor_profile.cpython-311.pyc
   │     │  │  │     ├─ v1_attached_volume.cpython-311.pyc
   │     │  │  │     ├─ v1_audit_annotation.cpython-311.pyc
   │     │  │  │     ├─ v1_aws_elastic_block_store_volume_source.cpython-311.pyc
   │     │  │  │     ├─ v1_azure_disk_volume_source.cpython-311.pyc
   │     │  │  │     ├─ v1_azure_file_persistent_volume_source.cpython-311.pyc
   │     │  │  │     ├─ v1_azure_file_volume_source.cpython-311.pyc
   │     │  │  │     ├─ v1_binding.cpython-311.pyc
   │     │  │  │     ├─ v1_bound_object_reference.cpython-311.pyc
   │     │  │  │     ├─ v1_capabilities.cpython-311.pyc
   │     │  │  │     ├─ v1_capacity_request_policy.cpython-311.pyc
   │     │  │  │     ├─ v1_capacity_request_policy_range.cpython-311.pyc
   │     │  │  │     ├─ v1_capacity_requirements.cpython-311.pyc
   │     │  │  │     ├─ v1_cel_device_selector.cpython-311.pyc
   │     │  │  │     ├─ v1_ceph_fs_persistent_volume_source.cpython-311.pyc
   │     │  │  │     ├─ v1_ceph_fs_volume_source.cpython-311.pyc
   │     │  │  │     ├─ v1_certificate_signing_request.cpython-311.pyc
   │     │  │  │     ├─ v1_certificate_signing_request_condition.cpython-311.pyc
   │     │  │  │     ├─ v1_certificate_signing_request_list.cpython-311.pyc
   │     │  │  │     ├─ v1_certificate_signing_request_spec.cpython-311.pyc
   │     │  │  │     ├─ v1_certificate_signing_request_status.cpython-311.pyc
   │     │  │  │     ├─ v1_cinder_persistent_volume_source.cpython-311.pyc
   │     │  │  │     ├─ v1_cinder_volume_source.cpython-311.pyc
   │     │  │  │     ├─ v1_client_ip_config.cpython-311.pyc
   │     │  │  │     ├─ v1_cluster_role.cpython-311.pyc
   │     │  │  │     ├─ v1_cluster_role_binding.cpython-311.pyc
   │     │  │  │     ├─ v1_cluster_role_binding_list.cpython-311.pyc
   │     │  │  │     ├─ v1_cluster_role_list.cpython-311.pyc
   │     │  │  │     ├─ v1_cluster_trust_bundle_projection.cpython-311.pyc
   │     │  │  │     ├─ v1_component_condition.cpython-311.pyc
   │     │  │  │     ├─ v1_component_status.cpython-311.pyc
   │     │  │  │     ├─ v1_component_status_list.cpython-311.pyc
   │     │  │  │     ├─ v1_condition.cpython-311.pyc
   │     │  │  │     ├─ v1_config_map.cpython-311.pyc
   │     │  │  │     ├─ v1_config_map_env_source.cpython-311.pyc
   │     │  │  │     ├─ v1_config_map_key_selector.cpython-311.pyc
   │     │  │  │     ├─ v1_config_map_list.cpython-311.pyc
   │     │  │  │     ├─ v1_config_map_node_config_source.cpython-311.pyc
   │     │  │  │     ├─ v1_config_map_projection.cpython-311.pyc
   │     │  │  │     ├─ v1_config_map_volume_source.cpython-311.pyc
   │     │  │  │     ├─ v1_container.cpython-311.pyc
   │     │  │  │     ├─ v1_container_extended_resource_request.cpython-311.pyc
   │     │  │  │     ├─ v1_container_image.cpython-311.pyc
   │     │  │  │     ├─ v1_container_port.cpython-311.pyc
   │     │  │  │     ├─ v1_container_resize_policy.cpython-311.pyc
   │     │  │  │     ├─ v1_container_restart_rule.cpython-311.pyc
   │     │  │  │     ├─ v1_container_restart_rule_on_exit_codes.cpython-311.pyc
   │     │  │  │     ├─ v1_container_state.cpython-311.pyc
   │     │  │  │     ├─ v1_container_state_running.cpython-311.pyc
   │     │  │  │     ├─ v1_container_state_terminated.cpython-311.pyc
   │     │  │  │     ├─ v1_container_state_waiting.cpython-311.pyc
   │     │  │  │     ├─ v1_container_status.cpython-311.pyc
   │     │  │  │     ├─ v1_container_user.cpython-311.pyc
   │     │  │  │     ├─ v1_controller_revision.cpython-311.pyc
   │     │  │  │     ├─ v1_controller_revision_list.cpython-311.pyc
   │     │  │  │     ├─ v1_counter.cpython-311.pyc
   │     │  │  │     ├─ v1_counter_set.cpython-311.pyc
   │     │  │  │     ├─ v1_cron_job.cpython-311.pyc
   │     │  │  │     ├─ v1_cron_job_list.cpython-311.pyc
   │     │  │  │     ├─ v1_cron_job_spec.cpython-311.pyc
   │     │  │  │     ├─ v1_cron_job_status.cpython-311.pyc
   │     │  │  │     ├─ v1_cross_version_object_reference.cpython-311.pyc
   │     │  │  │     ├─ v1_csi_driver.cpython-311.pyc
   │     │  │  │     ├─ v1_csi_driver_list.cpython-311.pyc
   │     │  │  │     ├─ v1_csi_driver_spec.cpython-311.pyc
   │     │  │  │     ├─ v1_csi_node.cpython-311.pyc
   │     │  │  │     ├─ v1_csi_node_driver.cpython-311.pyc
   │     │  │  │     ├─ v1_csi_node_list.cpython-311.pyc
   │     │  │  │     ├─ v1_csi_node_spec.cpython-311.pyc
   │     │  │  │     ├─ v1_csi_persistent_volume_source.cpython-311.pyc
   │     │  │  │     ├─ v1_csi_storage_capacity.cpython-311.pyc
   │     │  │  │     ├─ v1_csi_storage_capacity_list.cpython-311.pyc
   │     │  │  │     ├─ v1_csi_volume_source.cpython-311.pyc
   │     │  │  │     ├─ v1_custom_resource_column_definition.cpython-311.pyc
   │     │  │  │     ├─ v1_custom_resource_conversion.cpython-311.pyc
   │     │  │  │     ├─ v1_custom_resource_definition.cpython-311.pyc
   │     │  │  │     ├─ v1_custom_resource_definition_condition.cpython-311.pyc
   │     │  │  │     ├─ v1_custom_resource_definition_list.cpython-311.pyc
   │     │  │  │     ├─ v1_custom_resource_definition_names.cpython-311.pyc
   │     │  │  │     ├─ v1_custom_resource_definition_spec.cpython-311.pyc
   │     │  │  │     ├─ v1_custom_resource_definition_status.cpython-311.pyc
   │     │  │  │     ├─ v1_custom_resource_definition_version.cpython-311.pyc
   │     │  │  │     ├─ v1_custom_resource_subresources.cpython-311.pyc
   │     │  │  │     ├─ v1_custom_resource_subresource_scale.cpython-311.pyc
   │     │  │  │     ├─ v1_custom_resource_validation.cpython-311.pyc
   │     │  │  │     ├─ v1_daemon_endpoint.cpython-311.pyc
   │     │  │  │     ├─ v1_daemon_set.cpython-311.pyc
   │     │  │  │     ├─ v1_daemon_set_condition.cpython-311.pyc
   │     │  │  │     ├─ v1_daemon_set_list.cpython-311.pyc
   │     │  │  │     ├─ v1_daemon_set_spec.cpython-311.pyc
   │     │  │  │     ├─ v1_daemon_set_status.cpython-311.pyc
   │     │  │  │     ├─ v1_daemon_set_update_strategy.cpython-311.pyc
   │     │  │  │     ├─ v1_delete_options.cpython-311.pyc
   │     │  │  │     ├─ v1_deployment.cpython-311.pyc
   │     │  │  │     ├─ v1_deployment_condition.cpython-311.pyc
   │     │  │  │     ├─ v1_deployment_list.cpython-311.pyc
   │     │  │  │     ├─ v1_deployment_spec.cpython-311.pyc
   │     │  │  │     ├─ v1_deployment_status.cpython-311.pyc
   │     │  │  │     ├─ v1_deployment_strategy.cpython-311.pyc
   │     │  │  │     ├─ v1_device.cpython-311.pyc
   │     │  │  │     ├─ v1_device_allocation_configuration.cpython-311.pyc
   │     │  │  │     ├─ v1_device_allocation_result.cpython-311.pyc
   │     │  │  │     ├─ v1_device_attribute.cpython-311.pyc
   │     │  │  │     ├─ v1_device_capacity.cpython-311.pyc
   │     │  │  │     ├─ v1_device_claim.cpython-311.pyc
   │     │  │  │     ├─ v1_device_claim_configuration.cpython-311.pyc
   │     │  │  │     ├─ v1_device_class.cpython-311.pyc
   │     │  │  │     ├─ v1_device_class_configuration.cpython-311.pyc
   │     │  │  │     ├─ v1_device_class_list.cpython-311.pyc
   │     │  │  │     ├─ v1_device_class_spec.cpython-311.pyc
   │     │  │  │     ├─ v1_device_constraint.cpython-311.pyc
   │     │  │  │     ├─ v1_device_counter_consumption.cpython-311.pyc
   │     │  │  │     ├─ v1_device_request.cpython-311.pyc
   │     │  │  │     ├─ v1_device_request_allocation_result.cpython-311.pyc
   │     │  │  │     ├─ v1_device_selector.cpython-311.pyc
   │     │  │  │     ├─ v1_device_sub_request.cpython-311.pyc
   │     │  │  │     ├─ v1_device_taint.cpython-311.pyc
   │     │  │  │     ├─ v1_device_toleration.cpython-311.pyc
   │     │  │  │     ├─ v1_downward_api_projection.cpython-311.pyc
   │     │  │  │     ├─ v1_downward_api_volume_file.cpython-311.pyc
   │     │  │  │     ├─ v1_downward_api_volume_source.cpython-311.pyc
   │     │  │  │     ├─ v1_empty_dir_volume_source.cpython-311.pyc
   │     │  │  │     ├─ v1_endpoint.cpython-311.pyc
   │     │  │  │     ├─ v1_endpoints.cpython-311.pyc
   │     │  │  │     ├─ v1_endpoints_list.cpython-311.pyc
   │     │  │  │     ├─ v1_endpoint_address.cpython-311.pyc
   │     │  │  │     ├─ v1_endpoint_conditions.cpython-311.pyc
   │     │  │  │     ├─ v1_endpoint_hints.cpython-311.pyc
   │     │  │  │     ├─ v1_endpoint_slice.cpython-311.pyc
   │     │  │  │     ├─ v1_endpoint_slice_list.cpython-311.pyc
   │     │  │  │     ├─ v1_endpoint_subset.cpython-311.pyc
   │     │  │  │     ├─ v1_env_from_source.cpython-311.pyc
   │     │  │  │     ├─ v1_env_var.cpython-311.pyc
   │     │  │  │     ├─ v1_env_var_source.cpython-311.pyc
   │     │  │  │     ├─ v1_ephemeral_container.cpython-311.pyc
   │     │  │  │     ├─ v1_ephemeral_volume_source.cpython-311.pyc
   │     │  │  │     ├─ v1_event_source.cpython-311.pyc
   │     │  │  │     ├─ v1_eviction.cpython-311.pyc
   │     │  │  │     ├─ v1_exact_device_request.cpython-311.pyc
   │     │  │  │     ├─ v1_exec_action.cpython-311.pyc
   │     │  │  │     ├─ v1_exempt_priority_level_configuration.cpython-311.pyc
   │     │  │  │     ├─ v1_expression_warning.cpython-311.pyc
   │     │  │  │     ├─ v1_external_documentation.cpython-311.pyc
   │     │  │  │     ├─ v1_fc_volume_source.cpython-311.pyc
   │     │  │  │     ├─ v1_field_selector_attributes.cpython-311.pyc
   │     │  │  │     ├─ v1_field_selector_requirement.cpython-311.pyc
   │     │  │  │     ├─ v1_file_key_selector.cpython-311.pyc
   │     │  │  │     ├─ v1_flex_persistent_volume_source.cpython-311.pyc
   │     │  │  │     ├─ v1_flex_volume_source.cpython-311.pyc
   │     │  │  │     ├─ v1_flocker_volume_source.cpython-311.pyc
   │     │  │  │     ├─ v1_flow_distinguisher_method.cpython-311.pyc
   │     │  │  │     ├─ v1_flow_schema.cpython-311.pyc
   │     │  │  │     ├─ v1_flow_schema_condition.cpython-311.pyc
   │     │  │  │     ├─ v1_flow_schema_list.cpython-311.pyc
   │     │  │  │     ├─ v1_flow_schema_spec.cpython-311.pyc
   │     │  │  │     ├─ v1_flow_schema_status.cpython-311.pyc
   │     │  │  │     ├─ v1_for_node.cpython-311.pyc
   │     │  │  │     ├─ v1_for_zone.cpython-311.pyc
   │     │  │  │     ├─ v1_gce_persistent_disk_volume_source.cpython-311.pyc
   │     │  │  │     ├─ v1_git_repo_volume_source.cpython-311.pyc
   │     │  │  │     ├─ v1_glusterfs_persistent_volume_source.cpython-311.pyc
   │     │  │  │     ├─ v1_glusterfs_volume_source.cpython-311.pyc
   │     │  │  │     ├─ v1_group_resource.cpython-311.pyc
   │     │  │  │     ├─ v1_group_subject.cpython-311.pyc
   │     │  │  │     ├─ v1_group_version_for_discovery.cpython-311.pyc
   │     │  │  │     ├─ v1_grpc_action.cpython-311.pyc
   │     │  │  │     ├─ v1_horizontal_pod_autoscaler.cpython-311.pyc
   │     │  │  │     ├─ v1_horizontal_pod_autoscaler_list.cpython-311.pyc
   │     │  │  │     ├─ v1_horizontal_pod_autoscaler_spec.cpython-311.pyc
   │     │  │  │     ├─ v1_horizontal_pod_autoscaler_status.cpython-311.pyc
   │     │  │  │     ├─ v1_host_alias.cpython-311.pyc
   │     │  │  │     ├─ v1_host_ip.cpython-311.pyc
   │     │  │  │     ├─ v1_host_path_volume_source.cpython-311.pyc
   │     │  │  │     ├─ v1_http_get_action.cpython-311.pyc
   │     │  │  │     ├─ v1_http_header.cpython-311.pyc
   │     │  │  │     ├─ v1_http_ingress_path.cpython-311.pyc
   │     │  │  │     ├─ v1_http_ingress_rule_value.cpython-311.pyc
   │     │  │  │     ├─ v1_image_volume_source.cpython-311.pyc
   │     │  │  │     ├─ v1_ingress.cpython-311.pyc
   │     │  │  │     ├─ v1_ingress_backend.cpython-311.pyc
   │     │  │  │     ├─ v1_ingress_class.cpython-311.pyc
   │     │  │  │     ├─ v1_ingress_class_list.cpython-311.pyc
   │     │  │  │     ├─ v1_ingress_class_parameters_reference.cpython-311.pyc
   │     │  │  │     ├─ v1_ingress_class_spec.cpython-311.pyc
   │     │  │  │     ├─ v1_ingress_list.cpython-311.pyc
   │     │  │  │     ├─ v1_ingress_load_balancer_ingress.cpython-311.pyc
   │     │  │  │     ├─ v1_ingress_load_balancer_status.cpython-311.pyc
   │     │  │  │     ├─ v1_ingress_port_status.cpython-311.pyc
   │     │  │  │     ├─ v1_ingress_rule.cpython-311.pyc
   │     │  │  │     ├─ v1_ingress_service_backend.cpython-311.pyc
   │     │  │  │     ├─ v1_ingress_spec.cpython-311.pyc
   │     │  │  │     ├─ v1_ingress_status.cpython-311.pyc
   │     │  │  │     ├─ v1_ingress_tls.cpython-311.pyc
   │     │  │  │     ├─ v1_ip_address.cpython-311.pyc
   │     │  │  │     ├─ v1_ip_address_list.cpython-311.pyc
   │     │  │  │     ├─ v1_ip_address_spec.cpython-311.pyc
   │     │  │  │     ├─ v1_ip_block.cpython-311.pyc
   │     │  │  │     ├─ v1_iscsi_persistent_volume_source.cpython-311.pyc
   │     │  │  │     ├─ v1_iscsi_volume_source.cpython-311.pyc
   │     │  │  │     ├─ v1_job.cpython-311.pyc
   │     │  │  │     ├─ v1_job_condition.cpython-311.pyc
   │     │  │  │     ├─ v1_job_list.cpython-311.pyc
   │     │  │  │     ├─ v1_job_spec.cpython-311.pyc
   │     │  │  │     ├─ v1_job_status.cpython-311.pyc
   │     │  │  │     ├─ v1_job_template_spec.cpython-311.pyc
   │     │  │  │     ├─ v1_json_schema_props.cpython-311.pyc
   │     │  │  │     ├─ v1_key_to_path.cpython-311.pyc
   │     │  │  │     ├─ v1_label_selector.cpython-311.pyc
   │     │  │  │     ├─ v1_label_selector_attributes.cpython-311.pyc
   │     │  │  │     ├─ v1_label_selector_requirement.cpython-311.pyc
   │     │  │  │     ├─ v1_lease.cpython-311.pyc
   │     │  │  │     ├─ v1_lease_list.cpython-311.pyc
   │     │  │  │     ├─ v1_lease_spec.cpython-311.pyc
   │     │  │  │     ├─ v1_lifecycle.cpython-311.pyc
   │     │  │  │     ├─ v1_lifecycle_handler.cpython-311.pyc
   │     │  │  │     ├─ v1_limited_priority_level_configuration.cpython-311.pyc
   │     │  │  │     ├─ v1_limit_range.cpython-311.pyc
   │     │  │  │     ├─ v1_limit_range_item.cpython-311.pyc
   │     │  │  │     ├─ v1_limit_range_list.cpython-311.pyc
   │     │  │  │     ├─ v1_limit_range_spec.cpython-311.pyc
   │     │  │  │     ├─ v1_limit_response.cpython-311.pyc
   │     │  │  │     ├─ v1_linux_container_user.cpython-311.pyc
   │     │  │  │     ├─ v1_list_meta.cpython-311.pyc
   │     │  │  │     ├─ v1_load_balancer_ingress.cpython-311.pyc
   │     │  │  │     ├─ v1_load_balancer_status.cpython-311.pyc
   │     │  │  │     ├─ v1_local_object_reference.cpython-311.pyc
   │     │  │  │     ├─ v1_local_subject_access_review.cpython-311.pyc
   │     │  │  │     ├─ v1_local_volume_source.cpython-311.pyc
   │     │  │  │     ├─ v1_managed_fields_entry.cpython-311.pyc
   │     │  │  │     ├─ v1_match_condition.cpython-311.pyc
   │     │  │  │     ├─ v1_match_resources.cpython-311.pyc
   │     │  │  │     ├─ v1_modify_volume_status.cpython-311.pyc
   │     │  │  │     ├─ v1_mutating_webhook.cpython-311.pyc
   │     │  │  │     ├─ v1_mutating_webhook_configuration.cpython-311.pyc
   │     │  │  │     ├─ v1_mutating_webhook_configuration_list.cpython-311.pyc
   │     │  │  │     ├─ v1_named_rule_with_operations.cpython-311.pyc
   │     │  │  │     ├─ v1_namespace.cpython-311.pyc
   │     │  │  │     ├─ v1_namespace_condition.cpython-311.pyc
   │     │  │  │     ├─ v1_namespace_list.cpython-311.pyc
   │     │  │  │     ├─ v1_namespace_spec.cpython-311.pyc
   │     │  │  │     ├─ v1_namespace_status.cpython-311.pyc
   │     │  │  │     ├─ v1_network_device_data.cpython-311.pyc
   │     │  │  │     ├─ v1_network_policy.cpython-311.pyc
   │     │  │  │     ├─ v1_network_policy_egress_rule.cpython-311.pyc
   │     │  │  │     ├─ v1_network_policy_ingress_rule.cpython-311.pyc
   │     │  │  │     ├─ v1_network_policy_list.cpython-311.pyc
   │     │  │  │     ├─ v1_network_policy_peer.cpython-311.pyc
   │     │  │  │     ├─ v1_network_policy_port.cpython-311.pyc
   │     │  │  │     ├─ v1_network_policy_spec.cpython-311.pyc
   │     │  │  │     ├─ v1_nfs_volume_source.cpython-311.pyc
   │     │  │  │     ├─ v1_node.cpython-311.pyc
   │     │  │  │     ├─ v1_node_address.cpython-311.pyc
   │     │  │  │     ├─ v1_node_affinity.cpython-311.pyc
   │     │  │  │     ├─ v1_node_condition.cpython-311.pyc
   │     │  │  │     ├─ v1_node_config_source.cpython-311.pyc
   │     │  │  │     ├─ v1_node_config_status.cpython-311.pyc
   │     │  │  │     ├─ v1_node_daemon_endpoints.cpython-311.pyc
   │     │  │  │     ├─ v1_node_features.cpython-311.pyc
   │     │  │  │     ├─ v1_node_list.cpython-311.pyc
   │     │  │  │     ├─ v1_node_runtime_handler.cpython-311.pyc
   │     │  │  │     ├─ v1_node_runtime_handler_features.cpython-311.pyc
   │     │  │  │     ├─ v1_node_selector.cpython-311.pyc
   │     │  │  │     ├─ v1_node_selector_requirement.cpython-311.pyc
   │     │  │  │     ├─ v1_node_selector_term.cpython-311.pyc
   │     │  │  │     ├─ v1_node_spec.cpython-311.pyc
   │     │  │  │     ├─ v1_node_status.cpython-311.pyc
   │     │  │  │     ├─ v1_node_swap_status.cpython-311.pyc
   │     │  │  │     ├─ v1_node_system_info.cpython-311.pyc
   │     │  │  │     ├─ v1_non_resource_attributes.cpython-311.pyc
   │     │  │  │     ├─ v1_non_resource_policy_rule.cpython-311.pyc
   │     │  │  │     ├─ v1_non_resource_rule.cpython-311.pyc
   │     │  │  │     ├─ v1_object_field_selector.cpython-311.pyc
   │     │  │  │     ├─ v1_object_meta.cpython-311.pyc
   │     │  │  │     ├─ v1_object_reference.cpython-311.pyc
   │     │  │  │     ├─ v1_opaque_device_configuration.cpython-311.pyc
   │     │  │  │     ├─ v1_overhead.cpython-311.pyc
   │     │  │  │     ├─ v1_owner_reference.cpython-311.pyc
   │     │  │  │     ├─ v1_param_kind.cpython-311.pyc
   │     │  │  │     ├─ v1_param_ref.cpython-311.pyc
   │     │  │  │     ├─ v1_parent_reference.cpython-311.pyc
   │     │  │  │     ├─ v1_persistent_volume.cpython-311.pyc
   │     │  │  │     ├─ v1_persistent_volume_claim.cpython-311.pyc
   │     │  │  │     ├─ v1_persistent_volume_claim_condition.cpython-311.pyc
   │     │  │  │     ├─ v1_persistent_volume_claim_list.cpython-311.pyc
   │     │  │  │     ├─ v1_persistent_volume_claim_spec.cpython-311.pyc
   │     │  │  │     ├─ v1_persistent_volume_claim_status.cpython-311.pyc
   │     │  │  │     ├─ v1_persistent_volume_claim_template.cpython-311.pyc
   │     │  │  │     ├─ v1_persistent_volume_claim_volume_source.cpython-311.pyc
   │     │  │  │     ├─ v1_persistent_volume_list.cpython-311.pyc
   │     │  │  │     ├─ v1_persistent_volume_spec.cpython-311.pyc
   │     │  │  │     ├─ v1_persistent_volume_status.cpython-311.pyc
   │     │  │  │     ├─ v1_photon_persistent_disk_volume_source.cpython-311.pyc
   │     │  │  │     ├─ v1_pod.cpython-311.pyc
   │     │  │  │     ├─ v1_pod_affinity.cpython-311.pyc
   │     │  │  │     ├─ v1_pod_affinity_term.cpython-311.pyc
   │     │  │  │     ├─ v1_pod_anti_affinity.cpython-311.pyc
   │     │  │  │     ├─ v1_pod_certificate_projection.cpython-311.pyc
   │     │  │  │     ├─ v1_pod_condition.cpython-311.pyc
   │     │  │  │     ├─ v1_pod_disruption_budget.cpython-311.pyc
   │     │  │  │     ├─ v1_pod_disruption_budget_list.cpython-311.pyc
   │     │  │  │     ├─ v1_pod_disruption_budget_spec.cpython-311.pyc
   │     │  │  │     ├─ v1_pod_disruption_budget_status.cpython-311.pyc
   │     │  │  │     ├─ v1_pod_dns_config.cpython-311.pyc
   │     │  │  │     ├─ v1_pod_dns_config_option.cpython-311.pyc
   │     │  │  │     ├─ v1_pod_extended_resource_claim_status.cpython-311.pyc
   │     │  │  │     ├─ v1_pod_failure_policy.cpython-311.pyc
   │     │  │  │     ├─ v1_pod_failure_policy_on_exit_codes_requirement.cpython-311.pyc
   │     │  │  │     ├─ v1_pod_failure_policy_on_pod_conditions_pattern.cpython-311.pyc
   │     │  │  │     ├─ v1_pod_failure_policy_rule.cpython-311.pyc
   │     │  │  │     ├─ v1_pod_ip.cpython-311.pyc
   │     │  │  │     ├─ v1_pod_list.cpython-311.pyc
   │     │  │  │     ├─ v1_pod_os.cpython-311.pyc
   │     │  │  │     ├─ v1_pod_readiness_gate.cpython-311.pyc
   │     │  │  │     ├─ v1_pod_resource_claim.cpython-311.pyc
   │     │  │  │     ├─ v1_pod_resource_claim_status.cpython-311.pyc
   │     │  │  │     ├─ v1_pod_scheduling_gate.cpython-311.pyc
   │     │  │  │     ├─ v1_pod_security_context.cpython-311.pyc
   │     │  │  │     ├─ v1_pod_spec.cpython-311.pyc
   │     │  │  │     ├─ v1_pod_status.cpython-311.pyc
   │     │  │  │     ├─ v1_pod_template.cpython-311.pyc
   │     │  │  │     ├─ v1_pod_template_list.cpython-311.pyc
   │     │  │  │     ├─ v1_pod_template_spec.cpython-311.pyc
   │     │  │  │     ├─ v1_policy_rule.cpython-311.pyc
   │     │  │  │     ├─ v1_policy_rules_with_subjects.cpython-311.pyc
   │     │  │  │     ├─ v1_portworx_volume_source.cpython-311.pyc
   │     │  │  │     ├─ v1_port_status.cpython-311.pyc
   │     │  │  │     ├─ v1_preconditions.cpython-311.pyc
   │     │  │  │     ├─ v1_preferred_scheduling_term.cpython-311.pyc
   │     │  │  │     ├─ v1_priority_class.cpython-311.pyc
   │     │  │  │     ├─ v1_priority_class_list.cpython-311.pyc
   │     │  │  │     ├─ v1_priority_level_configuration.cpython-311.pyc
   │     │  │  │     ├─ v1_priority_level_configuration_condition.cpython-311.pyc
   │     │  │  │     ├─ v1_priority_level_configuration_list.cpython-311.pyc
   │     │  │  │     ├─ v1_priority_level_configuration_reference.cpython-311.pyc
   │     │  │  │     ├─ v1_priority_level_configuration_spec.cpython-311.pyc
   │     │  │  │     ├─ v1_priority_level_configuration_status.cpython-311.pyc
   │     │  │  │     ├─ v1_probe.cpython-311.pyc
   │     │  │  │     ├─ v1_projected_volume_source.cpython-311.pyc
   │     │  │  │     ├─ v1_queuing_configuration.cpython-311.pyc
   │     │  │  │     ├─ v1_quobyte_volume_source.cpython-311.pyc
   │     │  │  │     ├─ v1_rbd_persistent_volume_source.cpython-311.pyc
   │     │  │  │     ├─ v1_rbd_volume_source.cpython-311.pyc
   │     │  │  │     ├─ v1_replication_controller.cpython-311.pyc
   │     │  │  │     ├─ v1_replication_controller_condition.cpython-311.pyc
   │     │  │  │     ├─ v1_replication_controller_list.cpython-311.pyc
   │     │  │  │     ├─ v1_replication_controller_spec.cpython-311.pyc
   │     │  │  │     ├─ v1_replication_controller_status.cpython-311.pyc
   │     │  │  │     ├─ v1_replica_set.cpython-311.pyc
   │     │  │  │     ├─ v1_replica_set_condition.cpython-311.pyc
   │     │  │  │     ├─ v1_replica_set_list.cpython-311.pyc
   │     │  │  │     ├─ v1_replica_set_spec.cpython-311.pyc
   │     │  │  │     ├─ v1_replica_set_status.cpython-311.pyc
   │     │  │  │     ├─ v1_resource_attributes.cpython-311.pyc
   │     │  │  │     ├─ v1_resource_claim_consumer_reference.cpython-311.pyc
   │     │  │  │     ├─ v1_resource_claim_list.cpython-311.pyc
   │     │  │  │     ├─ v1_resource_claim_spec.cpython-311.pyc
   │     │  │  │     ├─ v1_resource_claim_status.cpython-311.pyc
   │     │  │  │     ├─ v1_resource_claim_template.cpython-311.pyc
   │     │  │  │     ├─ v1_resource_claim_template_list.cpython-311.pyc
   │     │  │  │     ├─ v1_resource_claim_template_spec.cpython-311.pyc
   │     │  │  │     ├─ v1_resource_field_selector.cpython-311.pyc
   │     │  │  │     ├─ v1_resource_health.cpython-311.pyc
   │     │  │  │     ├─ v1_resource_policy_rule.cpython-311.pyc
   │     │  │  │     ├─ v1_resource_pool.cpython-311.pyc
   │     │  │  │     ├─ v1_resource_quota.cpython-311.pyc
   │     │  │  │     ├─ v1_resource_quota_list.cpython-311.pyc
   │     │  │  │     ├─ v1_resource_quota_spec.cpython-311.pyc
   │     │  │  │     ├─ v1_resource_quota_status.cpython-311.pyc
   │     │  │  │     ├─ v1_resource_requirements.cpython-311.pyc
   │     │  │  │     ├─ v1_resource_rule.cpython-311.pyc
   │     │  │  │     ├─ v1_resource_slice.cpython-311.pyc
   │     │  │  │     ├─ v1_resource_slice_list.cpython-311.pyc
   │     │  │  │     ├─ v1_resource_slice_spec.cpython-311.pyc
   │     │  │  │     ├─ v1_resource_status.cpython-311.pyc
   │     │  │  │     ├─ v1_role.cpython-311.pyc
   │     │  │  │     ├─ v1_role_binding.cpython-311.pyc
   │     │  │  │     ├─ v1_role_binding_list.cpython-311.pyc
   │     │  │  │     ├─ v1_role_list.cpython-311.pyc
   │     │  │  │     ├─ v1_role_ref.cpython-311.pyc
   │     │  │  │     ├─ v1_rolling_update_daemon_set.cpython-311.pyc
   │     │  │  │     ├─ v1_rolling_update_deployment.cpython-311.pyc
   │     │  │  │     ├─ v1_rolling_update_stateful_set_strategy.cpython-311.pyc
   │     │  │  │     ├─ v1_rule_with_operations.cpython-311.pyc
   │     │  │  │     ├─ v1_runtime_class.cpython-311.pyc
   │     │  │  │     ├─ v1_runtime_class_list.cpython-311.pyc
   │     │  │  │     ├─ v1_scale.cpython-311.pyc
   │     │  │  │     ├─ v1_scale_io_persistent_volume_source.cpython-311.pyc
   │     │  │  │     ├─ v1_scale_io_volume_source.cpython-311.pyc
   │     │  │  │     ├─ v1_scale_spec.cpython-311.pyc
   │     │  │  │     ├─ v1_scale_status.cpython-311.pyc
   │     │  │  │     ├─ v1_scheduling.cpython-311.pyc
   │     │  │  │     ├─ v1_scoped_resource_selector_requirement.cpython-311.pyc
   │     │  │  │     ├─ v1_scope_selector.cpython-311.pyc
   │     │  │  │     ├─ v1_seccomp_profile.cpython-311.pyc
   │     │  │  │     ├─ v1_secret.cpython-311.pyc
   │     │  │  │     ├─ v1_secret_env_source.cpython-311.pyc
   │     │  │  │     ├─ v1_secret_key_selector.cpython-311.pyc
   │     │  │  │     ├─ v1_secret_list.cpython-311.pyc
   │     │  │  │     ├─ v1_secret_projection.cpython-311.pyc
   │     │  │  │     ├─ v1_secret_reference.cpython-311.pyc
   │     │  │  │     ├─ v1_secret_volume_source.cpython-311.pyc
   │     │  │  │     ├─ v1_security_context.cpython-311.pyc
   │     │  │  │     ├─ v1_selectable_field.cpython-311.pyc
   │     │  │  │     ├─ v1_self_subject_access_review.cpython-311.pyc
   │     │  │  │     ├─ v1_self_subject_access_review_spec.cpython-311.pyc
   │     │  │  │     ├─ v1_self_subject_review.cpython-311.pyc
   │     │  │  │     ├─ v1_self_subject_review_status.cpython-311.pyc
   │     │  │  │     ├─ v1_self_subject_rules_review.cpython-311.pyc
   │     │  │  │     ├─ v1_self_subject_rules_review_spec.cpython-311.pyc
   │     │  │  │     ├─ v1_server_address_by_client_cidr.cpython-311.pyc
   │     │  │  │     ├─ v1_service.cpython-311.pyc
   │     │  │  │     ├─ v1_service_account.cpython-311.pyc
   │     │  │  │     ├─ v1_service_account_list.cpython-311.pyc
   │     │  │  │     ├─ v1_service_account_subject.cpython-311.pyc
   │     │  │  │     ├─ v1_service_account_token_projection.cpython-311.pyc
   │     │  │  │     ├─ v1_service_backend_port.cpython-311.pyc
   │     │  │  │     ├─ v1_service_cidr.cpython-311.pyc
   │     │  │  │     ├─ v1_service_cidr_list.cpython-311.pyc
   │     │  │  │     ├─ v1_service_cidr_spec.cpython-311.pyc
   │     │  │  │     ├─ v1_service_cidr_status.cpython-311.pyc
   │     │  │  │     ├─ v1_service_list.cpython-311.pyc
   │     │  │  │     ├─ v1_service_port.cpython-311.pyc
   │     │  │  │     ├─ v1_service_spec.cpython-311.pyc
   │     │  │  │     ├─ v1_service_status.cpython-311.pyc
   │     │  │  │     ├─ v1_session_affinity_config.cpython-311.pyc
   │     │  │  │     ├─ v1_se_linux_options.cpython-311.pyc
   │     │  │  │     ├─ v1_sleep_action.cpython-311.pyc
   │     │  │  │     ├─ v1_stateful_set.cpython-311.pyc
   │     │  │  │     ├─ v1_stateful_set_condition.cpython-311.pyc
   │     │  │  │     ├─ v1_stateful_set_list.cpython-311.pyc
   │     │  │  │     ├─ v1_stateful_set_ordinals.cpython-311.pyc
   │     │  │  │     ├─ v1_stateful_set_persistent_volume_claim_retention_policy.cpython-311.pyc
   │     │  │  │     ├─ v1_stateful_set_spec.cpython-311.pyc
   │     │  │  │     ├─ v1_stateful_set_status.cpython-311.pyc
   │     │  │  │     ├─ v1_stateful_set_update_strategy.cpython-311.pyc
   │     │  │  │     ├─ v1_status.cpython-311.pyc
   │     │  │  │     ├─ v1_status_cause.cpython-311.pyc
   │     │  │  │     ├─ v1_status_details.cpython-311.pyc
   │     │  │  │     ├─ v1_storage_class.cpython-311.pyc
   │     │  │  │     ├─ v1_storage_class_list.cpython-311.pyc
   │     │  │  │     ├─ v1_storage_os_persistent_volume_source.cpython-311.pyc
   │     │  │  │     ├─ v1_storage_os_volume_source.cpython-311.pyc
   │     │  │  │     ├─ v1_subject_access_review.cpython-311.pyc
   │     │  │  │     ├─ v1_subject_access_review_spec.cpython-311.pyc
   │     │  │  │     ├─ v1_subject_access_review_status.cpython-311.pyc
   │     │  │  │     ├─ v1_subject_rules_review_status.cpython-311.pyc
   │     │  │  │     ├─ v1_success_policy.cpython-311.pyc
   │     │  │  │     ├─ v1_success_policy_rule.cpython-311.pyc
   │     │  │  │     ├─ v1_sysctl.cpython-311.pyc
   │     │  │  │     ├─ v1_taint.cpython-311.pyc
   │     │  │  │     ├─ v1_tcp_socket_action.cpython-311.pyc
   │     │  │  │     ├─ v1_token_request_spec.cpython-311.pyc
   │     │  │  │     ├─ v1_token_request_status.cpython-311.pyc
   │     │  │  │     ├─ v1_token_review.cpython-311.pyc
   │     │  │  │     ├─ v1_token_review_spec.cpython-311.pyc
   │     │  │  │     ├─ v1_token_review_status.cpython-311.pyc
   │     │  │  │     ├─ v1_toleration.cpython-311.pyc
   │     │  │  │     ├─ v1_topology_selector_label_requirement.cpython-311.pyc
   │     │  │  │     ├─ v1_topology_selector_term.cpython-311.pyc
   │     │  │  │     ├─ v1_topology_spread_constraint.cpython-311.pyc
   │     │  │  │     ├─ v1_typed_local_object_reference.cpython-311.pyc
   │     │  │  │     ├─ v1_typed_object_reference.cpython-311.pyc
   │     │  │  │     ├─ v1_type_checking.cpython-311.pyc
   │     │  │  │     ├─ v1_uncounted_terminated_pods.cpython-311.pyc
   │     │  │  │     ├─ v1_user_info.cpython-311.pyc
   │     │  │  │     ├─ v1_user_subject.cpython-311.pyc
   │     │  │  │     ├─ v1_validating_admission_policy.cpython-311.pyc
   │     │  │  │     ├─ v1_validating_admission_policy_binding.cpython-311.pyc
   │     │  │  │     ├─ v1_validating_admission_policy_binding_list.cpython-311.pyc
   │     │  │  │     ├─ v1_validating_admission_policy_binding_spec.cpython-311.pyc
   │     │  │  │     ├─ v1_validating_admission_policy_list.cpython-311.pyc
   │     │  │  │     ├─ v1_validating_admission_policy_spec.cpython-311.pyc
   │     │  │  │     ├─ v1_validating_admission_policy_status.cpython-311.pyc
   │     │  │  │     ├─ v1_validating_webhook.cpython-311.pyc
   │     │  │  │     ├─ v1_validating_webhook_configuration.cpython-311.pyc
   │     │  │  │     ├─ v1_validating_webhook_configuration_list.cpython-311.pyc
   │     │  │  │     ├─ v1_validation.cpython-311.pyc
   │     │  │  │     ├─ v1_validation_rule.cpython-311.pyc
   │     │  │  │     ├─ v1_variable.cpython-311.pyc
   │     │  │  │     ├─ v1_volume.cpython-311.pyc
   │     │  │  │     ├─ v1_volume_attachment.cpython-311.pyc
   │     │  │  │     ├─ v1_volume_attachment_list.cpython-311.pyc
   │     │  │  │     ├─ v1_volume_attachment_source.cpython-311.pyc
   │     │  │  │     ├─ v1_volume_attachment_spec.cpython-311.pyc
   │     │  │  │     ├─ v1_volume_attachment_status.cpython-311.pyc
   │     │  │  │     ├─ v1_volume_attributes_class.cpython-311.pyc
   │     │  │  │     ├─ v1_volume_attributes_class_list.cpython-311.pyc
   │     │  │  │     ├─ v1_volume_device.cpython-311.pyc
   │     │  │  │     ├─ v1_volume_error.cpython-311.pyc
   │     │  │  │     ├─ v1_volume_mount.cpython-311.pyc
   │     │  │  │     ├─ v1_volume_mount_status.cpython-311.pyc
   │     │  │  │     ├─ v1_volume_node_affinity.cpython-311.pyc
   │     │  │  │     ├─ v1_volume_node_resources.cpython-311.pyc
   │     │  │  │     ├─ v1_volume_projection.cpython-311.pyc
   │     │  │  │     ├─ v1_volume_resource_requirements.cpython-311.pyc
   │     │  │  │     ├─ v1_vsphere_virtual_disk_volume_source.cpython-311.pyc
   │     │  │  │     ├─ v1_watch_event.cpython-311.pyc
   │     │  │  │     ├─ v1_webhook_conversion.cpython-311.pyc
   │     │  │  │     ├─ v1_weighted_pod_affinity_term.cpython-311.pyc
   │     │  │  │     ├─ v1_windows_security_context_options.cpython-311.pyc
   │     │  │  │     ├─ v1_workload_reference.cpython-311.pyc
   │     │  │  │     ├─ v2_container_resource_metric_source.cpython-311.pyc
   │     │  │  │     ├─ v2_container_resource_metric_status.cpython-311.pyc
   │     │  │  │     ├─ v2_cross_version_object_reference.cpython-311.pyc
   │     │  │  │     ├─ v2_external_metric_source.cpython-311.pyc
   │     │  │  │     ├─ v2_external_metric_status.cpython-311.pyc
   │     │  │  │     ├─ v2_horizontal_pod_autoscaler.cpython-311.pyc
   │     │  │  │     ├─ v2_horizontal_pod_autoscaler_behavior.cpython-311.pyc
   │     │  │  │     ├─ v2_horizontal_pod_autoscaler_condition.cpython-311.pyc
   │     │  │  │     ├─ v2_horizontal_pod_autoscaler_list.cpython-311.pyc
   │     │  │  │     ├─ v2_horizontal_pod_autoscaler_spec.cpython-311.pyc
   │     │  │  │     ├─ v2_horizontal_pod_autoscaler_status.cpython-311.pyc
   │     │  │  │     ├─ v2_hpa_scaling_policy.cpython-311.pyc
   │     │  │  │     ├─ v2_hpa_scaling_rules.cpython-311.pyc
   │     │  │  │     ├─ v2_metric_identifier.cpython-311.pyc
   │     │  │  │     ├─ v2_metric_spec.cpython-311.pyc
   │     │  │  │     ├─ v2_metric_status.cpython-311.pyc
   │     │  │  │     ├─ v2_metric_target.cpython-311.pyc
   │     │  │  │     ├─ v2_metric_value_status.cpython-311.pyc
   │     │  │  │     ├─ v2_object_metric_source.cpython-311.pyc
   │     │  │  │     ├─ v2_object_metric_status.cpython-311.pyc
   │     │  │  │     ├─ v2_pods_metric_source.cpython-311.pyc
   │     │  │  │     ├─ v2_pods_metric_status.cpython-311.pyc
   │     │  │  │     ├─ v2_resource_metric_source.cpython-311.pyc
   │     │  │  │     ├─ v2_resource_metric_status.cpython-311.pyc
   │     │  │  │     ├─ version_info.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ rest.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ api_client.cpython-311.pyc
   │     │  │     ├─ configuration.cpython-311.pyc
   │     │  │     ├─ exceptions.cpython-311.pyc
   │     │  │     ├─ rest.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ config
   │     │  │  ├─ config_exception.py
   │     │  │  ├─ dateutil.py
   │     │  │  ├─ dateutil_test.py
   │     │  │  ├─ exec_provider.py
   │     │  │  ├─ exec_provider_test.py
   │     │  │  ├─ incluster_config.py
   │     │  │  ├─ incluster_config_test.py
   │     │  │  ├─ kube_config.py
   │     │  │  ├─ kube_config_test.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ config_exception.cpython-311.pyc
   │     │  │     ├─ dateutil.cpython-311.pyc
   │     │  │     ├─ dateutil_test.cpython-311.pyc
   │     │  │     ├─ exec_provider.cpython-311.pyc
   │     │  │     ├─ exec_provider_test.cpython-311.pyc
   │     │  │     ├─ incluster_config.cpython-311.pyc
   │     │  │     ├─ incluster_config_test.cpython-311.pyc
   │     │  │     ├─ kube_config.cpython-311.pyc
   │     │  │     ├─ kube_config_test.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ dynamic
   │     │  │  ├─ client.py
   │     │  │  ├─ discovery.py
   │     │  │  ├─ exceptions.py
   │     │  │  ├─ resource.py
   │     │  │  ├─ test_client.py
   │     │  │  ├─ test_discovery.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ client.cpython-311.pyc
   │     │  │     ├─ discovery.cpython-311.pyc
   │     │  │     ├─ exceptions.cpython-311.pyc
   │     │  │     ├─ resource.cpython-311.pyc
   │     │  │     ├─ test_client.cpython-311.pyc
   │     │  │     ├─ test_discovery.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ leaderelection
   │     │  │  ├─ electionconfig.py
   │     │  │  ├─ example.py
   │     │  │  ├─ leaderelection.py
   │     │  │  ├─ leaderelectionrecord.py
   │     │  │  ├─ leaderelection_test.py
   │     │  │  ├─ resourcelock
   │     │  │  │  ├─ configmaplock.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ configmaplock.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ electionconfig.cpython-311.pyc
   │     │  │     ├─ example.cpython-311.pyc
   │     │  │     ├─ leaderelection.cpython-311.pyc
   │     │  │     ├─ leaderelectionrecord.cpython-311.pyc
   │     │  │     ├─ leaderelection_test.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ stream
   │     │  │  ├─ stream.py
   │     │  │  ├─ ws_client.py
   │     │  │  ├─ ws_client_test.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ stream.cpython-311.pyc
   │     │  │     ├─ ws_client.cpython-311.pyc
   │     │  │     ├─ ws_client_test.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ utils
   │     │  │  ├─ create_from_yaml.py
   │     │  │  ├─ duration.py
   │     │  │  ├─ quantity.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ create_from_yaml.cpython-311.pyc
   │     │  │     ├─ duration.cpython-311.pyc
   │     │  │     ├─ quantity.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ watch
   │     │  │  ├─ watch.py
   │     │  │  ├─ watch_test.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ watch.cpython-311.pyc
   │     │  │     ├─ watch_test.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ __init__.py
   │     │  └─ __pycache__
   │     │     └─ __init__.cpython-311.pyc
   │     ├─ kubernetes-35.0.0.dist-info
   │     │  ├─ INSTALLER
   │     │  ├─ licenses
   │     │  │  └─ LICENSE
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  ├─ top_level.txt
   │     │  └─ WHEEL
   │     ├─ markdown_it
   │     │  ├─ cli
   │     │  │  ├─ parse.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ parse.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ common
   │     │  │  ├─ entities.py
   │     │  │  ├─ html_blocks.py
   │     │  │  ├─ html_re.py
   │     │  │  ├─ normalize_url.py
   │     │  │  ├─ utils.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ entities.cpython-311.pyc
   │     │  │     ├─ html_blocks.cpython-311.pyc
   │     │  │     ├─ html_re.cpython-311.pyc
   │     │  │     ├─ normalize_url.cpython-311.pyc
   │     │  │     ├─ utils.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ helpers
   │     │  │  ├─ parse_link_destination.py
   │     │  │  ├─ parse_link_label.py
   │     │  │  ├─ parse_link_title.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ parse_link_destination.cpython-311.pyc
   │     │  │     ├─ parse_link_label.cpython-311.pyc
   │     │  │     ├─ parse_link_title.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ main.py
   │     │  ├─ parser_block.py
   │     │  ├─ parser_core.py
   │     │  ├─ parser_inline.py
   │     │  ├─ port.yaml
   │     │  ├─ presets
   │     │  │  ├─ commonmark.py
   │     │  │  ├─ default.py
   │     │  │  ├─ zero.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ commonmark.cpython-311.pyc
   │     │  │     ├─ default.cpython-311.pyc
   │     │  │     ├─ zero.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ py.typed
   │     │  ├─ renderer.py
   │     │  ├─ ruler.py
   │     │  ├─ rules_block
   │     │  │  ├─ blockquote.py
   │     │  │  ├─ code.py
   │     │  │  ├─ fence.py
   │     │  │  ├─ heading.py
   │     │  │  ├─ hr.py
   │     │  │  ├─ html_block.py
   │     │  │  ├─ lheading.py
   │     │  │  ├─ list.py
   │     │  │  ├─ paragraph.py
   │     │  │  ├─ reference.py
   │     │  │  ├─ state_block.py
   │     │  │  ├─ table.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ blockquote.cpython-311.pyc
   │     │  │     ├─ code.cpython-311.pyc
   │     │  │     ├─ fence.cpython-311.pyc
   │     │  │     ├─ heading.cpython-311.pyc
   │     │  │     ├─ hr.cpython-311.pyc
   │     │  │     ├─ html_block.cpython-311.pyc
   │     │  │     ├─ lheading.cpython-311.pyc
   │     │  │     ├─ list.cpython-311.pyc
   │     │  │     ├─ paragraph.cpython-311.pyc
   │     │  │     ├─ reference.cpython-311.pyc
   │     │  │     ├─ state_block.cpython-311.pyc
   │     │  │     ├─ table.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ rules_core
   │     │  │  ├─ block.py
   │     │  │  ├─ inline.py
   │     │  │  ├─ linkify.py
   │     │  │  ├─ normalize.py
   │     │  │  ├─ replacements.py
   │     │  │  ├─ smartquotes.py
   │     │  │  ├─ state_core.py
   │     │  │  ├─ text_join.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ block.cpython-311.pyc
   │     │  │     ├─ inline.cpython-311.pyc
   │     │  │     ├─ linkify.cpython-311.pyc
   │     │  │     ├─ normalize.cpython-311.pyc
   │     │  │     ├─ replacements.cpython-311.pyc
   │     │  │     ├─ smartquotes.cpython-311.pyc
   │     │  │     ├─ state_core.cpython-311.pyc
   │     │  │     ├─ text_join.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ rules_inline
   │     │  │  ├─ autolink.py
   │     │  │  ├─ backticks.py
   │     │  │  ├─ balance_pairs.py
   │     │  │  ├─ emphasis.py
   │     │  │  ├─ entity.py
   │     │  │  ├─ escape.py
   │     │  │  ├─ fragments_join.py
   │     │  │  ├─ html_inline.py
   │     │  │  ├─ image.py
   │     │  │  ├─ link.py
   │     │  │  ├─ linkify.py
   │     │  │  ├─ newline.py
   │     │  │  ├─ state_inline.py
   │     │  │  ├─ strikethrough.py
   │     │  │  ├─ text.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ autolink.cpython-311.pyc
   │     │  │     ├─ backticks.cpython-311.pyc
   │     │  │     ├─ balance_pairs.cpython-311.pyc
   │     │  │     ├─ emphasis.cpython-311.pyc
   │     │  │     ├─ entity.cpython-311.pyc
   │     │  │     ├─ escape.cpython-311.pyc
   │     │  │     ├─ fragments_join.cpython-311.pyc
   │     │  │     ├─ html_inline.cpython-311.pyc
   │     │  │     ├─ image.cpython-311.pyc
   │     │  │     ├─ link.cpython-311.pyc
   │     │  │     ├─ linkify.cpython-311.pyc
   │     │  │     ├─ newline.cpython-311.pyc
   │     │  │     ├─ state_inline.cpython-311.pyc
   │     │  │     ├─ strikethrough.cpython-311.pyc
   │     │  │     ├─ text.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ token.py
   │     │  ├─ tree.py
   │     │  ├─ utils.py
   │     │  ├─ _compat.py
   │     │  ├─ _punycode.py
   │     │  ├─ __init__.py
   │     │  └─ __pycache__
   │     │     ├─ main.cpython-311.pyc
   │     │     ├─ parser_block.cpython-311.pyc
   │     │     ├─ parser_core.cpython-311.pyc
   │     │     ├─ parser_inline.cpython-311.pyc
   │     │     ├─ renderer.cpython-311.pyc
   │     │     ├─ ruler.cpython-311.pyc
   │     │     ├─ token.cpython-311.pyc
   │     │     ├─ tree.cpython-311.pyc
   │     │     ├─ utils.cpython-311.pyc
   │     │     ├─ _compat.cpython-311.pyc
   │     │     ├─ _punycode.cpython-311.pyc
   │     │     └─ __init__.cpython-311.pyc
   │     ├─ markdown_it_py-4.0.0.dist-info
   │     │  ├─ entry_points.txt
   │     │  ├─ INSTALLER
   │     │  ├─ licenses
   │     │  │  ├─ LICENSE
   │     │  │  └─ LICENSE.markdown-it
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  └─ WHEEL
   │     ├─ markupsafe
   │     │  ├─ py.typed
   │     │  ├─ _native.py
   │     │  ├─ _speedups.c
   │     │  ├─ _speedups.cp311-win_amd64.pyd
   │     │  ├─ _speedups.pyi
   │     │  ├─ __init__.py
   │     │  └─ __pycache__
   │     │     ├─ _native.cpython-311.pyc
   │     │     └─ __init__.cpython-311.pyc
   │     ├─ markupsafe-3.0.3.dist-info
   │     │  ├─ INSTALLER
   │     │  ├─ licenses
   │     │  │  └─ LICENSE.txt
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  ├─ top_level.txt
   │     │  └─ WHEEL
   │     ├─ mdurl
   │     │  ├─ py.typed
   │     │  ├─ _decode.py
   │     │  ├─ _encode.py
   │     │  ├─ _format.py
   │     │  ├─ _parse.py
   │     │  ├─ _url.py
   │     │  ├─ __init__.py
   │     │  └─ __pycache__
   │     │     ├─ _decode.cpython-311.pyc
   │     │     ├─ _encode.cpython-311.pyc
   │     │     ├─ _format.cpython-311.pyc
   │     │     ├─ _parse.cpython-311.pyc
   │     │     ├─ _url.cpython-311.pyc
   │     │     └─ __init__.cpython-311.pyc
   │     ├─ mdurl-0.1.2.dist-info
   │     │  ├─ INSTALLER
   │     │  ├─ LICENSE
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  └─ WHEEL
   │     ├─ mmh3
   │     │  ├─ hashlib.h
   │     │  ├─ mmh3module.c
   │     │  ├─ murmurhash3.c
   │     │  ├─ murmurhash3.h
   │     │  ├─ py.typed
   │     │  └─ __init__.pyi
   │     ├─ mmh3-5.2.1.dist-info
   │     │  ├─ INSTALLER
   │     │  ├─ licenses
   │     │  │  └─ LICENSE
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  ├─ top_level.txt
   │     │  └─ WHEEL
   │     ├─ mmh3.cp311-win_amd64.pyd
   │     ├─ mpmath
   │     │  ├─ calculus
   │     │  │  ├─ approximation.py
   │     │  │  ├─ calculus.py
   │     │  │  ├─ differentiation.py
   │     │  │  ├─ extrapolation.py
   │     │  │  ├─ inverselaplace.py
   │     │  │  ├─ odes.py
   │     │  │  ├─ optimization.py
   │     │  │  ├─ polynomials.py
   │     │  │  ├─ quadrature.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ approximation.cpython-311.pyc
   │     │  │     ├─ calculus.cpython-311.pyc
   │     │  │     ├─ differentiation.cpython-311.pyc
   │     │  │     ├─ extrapolation.cpython-311.pyc
   │     │  │     ├─ inverselaplace.cpython-311.pyc
   │     │  │     ├─ odes.cpython-311.pyc
   │     │  │     ├─ optimization.cpython-311.pyc
   │     │  │     ├─ polynomials.cpython-311.pyc
   │     │  │     ├─ quadrature.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ ctx_base.py
   │     │  ├─ ctx_fp.py
   │     │  ├─ ctx_iv.py
   │     │  ├─ ctx_mp.py
   │     │  ├─ ctx_mp_python.py
   │     │  ├─ functions
   │     │  │  ├─ bessel.py
   │     │  │  ├─ elliptic.py
   │     │  │  ├─ expintegrals.py
   │     │  │  ├─ factorials.py
   │     │  │  ├─ functions.py
   │     │  │  ├─ hypergeometric.py
   │     │  │  ├─ orthogonal.py
   │     │  │  ├─ qfunctions.py
   │     │  │  ├─ rszeta.py
   │     │  │  ├─ signals.py
   │     │  │  ├─ theta.py
   │     │  │  ├─ zeta.py
   │     │  │  ├─ zetazeros.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ bessel.cpython-311.pyc
   │     │  │     ├─ elliptic.cpython-311.pyc
   │     │  │     ├─ expintegrals.cpython-311.pyc
   │     │  │     ├─ factorials.cpython-311.pyc
   │     │  │     ├─ functions.cpython-311.pyc
   │     │  │     ├─ hypergeometric.cpython-311.pyc
   │     │  │     ├─ orthogonal.cpython-311.pyc
   │     │  │     ├─ qfunctions.cpython-311.pyc
   │     │  │     ├─ rszeta.cpython-311.pyc
   │     │  │     ├─ signals.cpython-311.pyc
   │     │  │     ├─ theta.cpython-311.pyc
   │     │  │     ├─ zeta.cpython-311.pyc
   │     │  │     ├─ zetazeros.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ function_docs.py
   │     │  ├─ identification.py
   │     │  ├─ libmp
   │     │  │  ├─ backend.py
   │     │  │  ├─ gammazeta.py
   │     │  │  ├─ libelefun.py
   │     │  │  ├─ libhyper.py
   │     │  │  ├─ libintmath.py
   │     │  │  ├─ libmpc.py
   │     │  │  ├─ libmpf.py
   │     │  │  ├─ libmpi.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ backend.cpython-311.pyc
   │     │  │     ├─ gammazeta.cpython-311.pyc
   │     │  │     ├─ libelefun.cpython-311.pyc
   │     │  │     ├─ libhyper.cpython-311.pyc
   │     │  │     ├─ libintmath.cpython-311.pyc
   │     │  │     ├─ libmpc.cpython-311.pyc
   │     │  │     ├─ libmpf.cpython-311.pyc
   │     │  │     ├─ libmpi.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ math2.py
   │     │  ├─ matrices
   │     │  │  ├─ calculus.py
   │     │  │  ├─ eigen.py
   │     │  │  ├─ eigen_symmetric.py
   │     │  │  ├─ linalg.py
   │     │  │  ├─ matrices.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ calculus.cpython-311.pyc
   │     │  │     ├─ eigen.cpython-311.pyc
   │     │  │     ├─ eigen_symmetric.cpython-311.pyc
   │     │  │     ├─ linalg.cpython-311.pyc
   │     │  │     ├─ matrices.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ rational.py
   │     │  ├─ tests
   │     │  │  ├─ extratest_gamma.py
   │     │  │  ├─ extratest_zeta.py
   │     │  │  ├─ runtests.py
   │     │  │  ├─ test_basic_ops.py
   │     │  │  ├─ test_bitwise.py
   │     │  │  ├─ test_calculus.py
   │     │  │  ├─ test_compatibility.py
   │     │  │  ├─ test_convert.py
   │     │  │  ├─ test_diff.py
   │     │  │  ├─ test_division.py
   │     │  │  ├─ test_eigen.py
   │     │  │  ├─ test_eigen_symmetric.py
   │     │  │  ├─ test_elliptic.py
   │     │  │  ├─ test_fp.py
   │     │  │  ├─ test_functions.py
   │     │  │  ├─ test_functions2.py
   │     │  │  ├─ test_gammazeta.py
   │     │  │  ├─ test_hp.py
   │     │  │  ├─ test_identify.py
   │     │  │  ├─ test_interval.py
   │     │  │  ├─ test_levin.py
   │     │  │  ├─ test_linalg.py
   │     │  │  ├─ test_matrices.py
   │     │  │  ├─ test_mpmath.py
   │     │  │  ├─ test_ode.py
   │     │  │  ├─ test_pickle.py
   │     │  │  ├─ test_power.py
   │     │  │  ├─ test_quad.py
   │     │  │  ├─ test_rootfinding.py
   │     │  │  ├─ test_special.py
   │     │  │  ├─ test_str.py
   │     │  │  ├─ test_summation.py
   │     │  │  ├─ test_trig.py
   │     │  │  ├─ test_visualization.py
   │     │  │  ├─ torture.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ extratest_gamma.cpython-311.pyc
   │     │  │     ├─ extratest_zeta.cpython-311.pyc
   │     │  │     ├─ runtests.cpython-311.pyc
   │     │  │     ├─ test_basic_ops.cpython-311.pyc
   │     │  │     ├─ test_bitwise.cpython-311.pyc
   │     │  │     ├─ test_calculus.cpython-311.pyc
   │     │  │     ├─ test_compatibility.cpython-311.pyc
   │     │  │     ├─ test_convert.cpython-311.pyc
   │     │  │     ├─ test_diff.cpython-311.pyc
   │     │  │     ├─ test_division.cpython-311.pyc
   │     │  │     ├─ test_eigen.cpython-311.pyc
   │     │  │     ├─ test_eigen_symmetric.cpython-311.pyc
   │     │  │     ├─ test_elliptic.cpython-311.pyc
   │     │  │     ├─ test_fp.cpython-311.pyc
   │     │  │     ├─ test_functions.cpython-311.pyc
   │     │  │     ├─ test_functions2.cpython-311.pyc
   │     │  │     ├─ test_gammazeta.cpython-311.pyc
   │     │  │     ├─ test_hp.cpython-311.pyc
   │     │  │     ├─ test_identify.cpython-311.pyc
   │     │  │     ├─ test_interval.cpython-311.pyc
   │     │  │     ├─ test_levin.cpython-311.pyc
   │     │  │     ├─ test_linalg.cpython-311.pyc
   │     │  │     ├─ test_matrices.cpython-311.pyc
   │     │  │     ├─ test_mpmath.cpython-311.pyc
   │     │  │     ├─ test_ode.cpython-311.pyc
   │     │  │     ├─ test_pickle.cpython-311.pyc
   │     │  │     ├─ test_power.cpython-311.pyc
   │     │  │     ├─ test_quad.cpython-311.pyc
   │     │  │     ├─ test_rootfinding.cpython-311.pyc
   │     │  │     ├─ test_special.cpython-311.pyc
   │     │  │     ├─ test_str.cpython-311.pyc
   │     │  │     ├─ test_summation.cpython-311.pyc
   │     │  │     ├─ test_trig.cpython-311.pyc
   │     │  │     ├─ test_visualization.cpython-311.pyc
   │     │  │     ├─ torture.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ usertools.py
   │     │  ├─ visualization.py
   │     │  ├─ __init__.py
   │     │  └─ __pycache__
   │     │     ├─ ctx_base.cpython-311.pyc
   │     │     ├─ ctx_fp.cpython-311.pyc
   │     │     ├─ ctx_iv.cpython-311.pyc
   │     │     ├─ ctx_mp.cpython-311.pyc
   │     │     ├─ ctx_mp_python.cpython-311.pyc
   │     │     ├─ function_docs.cpython-311.pyc
   │     │     ├─ identification.cpython-311.pyc
   │     │     ├─ math2.cpython-311.pyc
   │     │     ├─ rational.cpython-311.pyc
   │     │     ├─ usertools.cpython-311.pyc
   │     │     ├─ visualization.cpython-311.pyc
   │     │     └─ __init__.cpython-311.pyc
   │     ├─ mpmath-1.3.0.dist-info
   │     │  ├─ INSTALLER
   │     │  ├─ LICENSE
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  ├─ top_level.txt
   │     │  └─ WHEEL
   │     ├─ narwhals
   │     │  ├─ compliant.py
   │     │  ├─ dataframe.py
   │     │  ├─ dependencies.py
   │     │  ├─ dtypes.py
   │     │  ├─ exceptions.py
   │     │  ├─ expr.py
   │     │  ├─ expr_cat.py
   │     │  ├─ expr_dt.py
   │     │  ├─ expr_list.py
   │     │  ├─ expr_name.py
   │     │  ├─ expr_str.py
   │     │  ├─ expr_struct.py
   │     │  ├─ functions.py
   │     │  ├─ group_by.py
   │     │  ├─ plugins.py
   │     │  ├─ py.typed
   │     │  ├─ schema.py
   │     │  ├─ selectors.py
   │     │  ├─ series.py
   │     │  ├─ series_cat.py
   │     │  ├─ series_dt.py
   │     │  ├─ series_list.py
   │     │  ├─ series_str.py
   │     │  ├─ series_struct.py
   │     │  ├─ sql.py
   │     │  ├─ stable
   │     │  │  ├─ v1
   │     │  │  │  ├─ dependencies.py
   │     │  │  │  ├─ dtypes.py
   │     │  │  │  ├─ selectors.py
   │     │  │  │  ├─ typing.py
   │     │  │  │  ├─ _dtypes.py
   │     │  │  │  ├─ _namespace.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ dependencies.cpython-311.pyc
   │     │  │  │     ├─ dtypes.cpython-311.pyc
   │     │  │  │     ├─ selectors.cpython-311.pyc
   │     │  │  │     ├─ typing.cpython-311.pyc
   │     │  │  │     ├─ _dtypes.cpython-311.pyc
   │     │  │  │     ├─ _namespace.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ v2
   │     │  │  │  ├─ dependencies.py
   │     │  │  │  ├─ dtypes.py
   │     │  │  │  ├─ selectors.py
   │     │  │  │  ├─ typing.py
   │     │  │  │  ├─ _namespace.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ dependencies.cpython-311.pyc
   │     │  │  │     ├─ dtypes.cpython-311.pyc
   │     │  │  │     ├─ selectors.cpython-311.pyc
   │     │  │  │     ├─ typing.cpython-311.pyc
   │     │  │  │     ├─ _namespace.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ testing
   │     │  │  ├─ asserts
   │     │  │  │  ├─ frame.py
   │     │  │  │  ├─ series.py
   │     │  │  │  ├─ utils.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ frame.cpython-311.pyc
   │     │  │  │     ├─ series.cpython-311.pyc
   │     │  │  │     ├─ utils.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ this.py
   │     │  ├─ translate.py
   │     │  ├─ typing.py
   │     │  ├─ utils.py
   │     │  ├─ _arrow
   │     │  │  ├─ dataframe.py
   │     │  │  ├─ expr.py
   │     │  │  ├─ group_by.py
   │     │  │  ├─ namespace.py
   │     │  │  ├─ selectors.py
   │     │  │  ├─ series.py
   │     │  │  ├─ series_cat.py
   │     │  │  ├─ series_dt.py
   │     │  │  ├─ series_list.py
   │     │  │  ├─ series_str.py
   │     │  │  ├─ series_struct.py
   │     │  │  ├─ typing.py
   │     │  │  ├─ utils.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ dataframe.cpython-311.pyc
   │     │  │     ├─ expr.cpython-311.pyc
   │     │  │     ├─ group_by.cpython-311.pyc
   │     │  │     ├─ namespace.cpython-311.pyc
   │     │  │     ├─ selectors.cpython-311.pyc
   │     │  │     ├─ series.cpython-311.pyc
   │     │  │     ├─ series_cat.cpython-311.pyc
   │     │  │     ├─ series_dt.cpython-311.pyc
   │     │  │     ├─ series_list.cpython-311.pyc
   │     │  │     ├─ series_str.cpython-311.pyc
   │     │  │     ├─ series_struct.cpython-311.pyc
   │     │  │     ├─ typing.cpython-311.pyc
   │     │  │     ├─ utils.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ _compliant
   │     │  │  ├─ any_namespace.py
   │     │  │  ├─ column.py
   │     │  │  ├─ dataframe.py
   │     │  │  ├─ expr.py
   │     │  │  ├─ group_by.py
   │     │  │  ├─ namespace.py
   │     │  │  ├─ selectors.py
   │     │  │  ├─ series.py
   │     │  │  ├─ typing.py
   │     │  │  ├─ window.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ any_namespace.cpython-311.pyc
   │     │  │     ├─ column.cpython-311.pyc
   │     │  │     ├─ dataframe.cpython-311.pyc
   │     │  │     ├─ expr.cpython-311.pyc
   │     │  │     ├─ group_by.cpython-311.pyc
   │     │  │     ├─ namespace.cpython-311.pyc
   │     │  │     ├─ selectors.cpython-311.pyc
   │     │  │     ├─ series.cpython-311.pyc
   │     │  │     ├─ typing.cpython-311.pyc
   │     │  │     ├─ window.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ _constants.py
   │     │  ├─ _dask
   │     │  │  ├─ dataframe.py
   │     │  │  ├─ expr.py
   │     │  │  ├─ expr_dt.py
   │     │  │  ├─ expr_str.py
   │     │  │  ├─ group_by.py
   │     │  │  ├─ namespace.py
   │     │  │  ├─ selectors.py
   │     │  │  ├─ utils.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ dataframe.cpython-311.pyc
   │     │  │     ├─ expr.cpython-311.pyc
   │     │  │     ├─ expr_dt.cpython-311.pyc
   │     │  │     ├─ expr_str.cpython-311.pyc
   │     │  │     ├─ group_by.cpython-311.pyc
   │     │  │     ├─ namespace.cpython-311.pyc
   │     │  │     ├─ selectors.cpython-311.pyc
   │     │  │     ├─ utils.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ _duckdb
   │     │  │  ├─ dataframe.py
   │     │  │  ├─ expr.py
   │     │  │  ├─ expr_dt.py
   │     │  │  ├─ expr_list.py
   │     │  │  ├─ expr_str.py
   │     │  │  ├─ expr_struct.py
   │     │  │  ├─ group_by.py
   │     │  │  ├─ namespace.py
   │     │  │  ├─ selectors.py
   │     │  │  ├─ series.py
   │     │  │  ├─ typing.py
   │     │  │  ├─ utils.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ dataframe.cpython-311.pyc
   │     │  │     ├─ expr.cpython-311.pyc
   │     │  │     ├─ expr_dt.cpython-311.pyc
   │     │  │     ├─ expr_list.cpython-311.pyc
   │     │  │     ├─ expr_str.cpython-311.pyc
   │     │  │     ├─ expr_struct.cpython-311.pyc
   │     │  │     ├─ group_by.cpython-311.pyc
   │     │  │     ├─ namespace.cpython-311.pyc
   │     │  │     ├─ selectors.cpython-311.pyc
   │     │  │     ├─ series.cpython-311.pyc
   │     │  │     ├─ typing.cpython-311.pyc
   │     │  │     ├─ utils.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ _duration.py
   │     │  ├─ _enum.py
   │     │  ├─ _exceptions.py
   │     │  ├─ _expression_parsing.py
   │     │  ├─ _ibis
   │     │  │  ├─ dataframe.py
   │     │  │  ├─ expr.py
   │     │  │  ├─ expr_dt.py
   │     │  │  ├─ expr_list.py
   │     │  │  ├─ expr_str.py
   │     │  │  ├─ expr_struct.py
   │     │  │  ├─ group_by.py
   │     │  │  ├─ namespace.py
   │     │  │  ├─ selectors.py
   │     │  │  ├─ series.py
   │     │  │  ├─ utils.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ dataframe.cpython-311.pyc
   │     │  │     ├─ expr.cpython-311.pyc
   │     │  │     ├─ expr_dt.cpython-311.pyc
   │     │  │     ├─ expr_list.cpython-311.pyc
   │     │  │     ├─ expr_str.cpython-311.pyc
   │     │  │     ├─ expr_struct.cpython-311.pyc
   │     │  │     ├─ group_by.cpython-311.pyc
   │     │  │     ├─ namespace.cpython-311.pyc
   │     │  │     ├─ selectors.cpython-311.pyc
   │     │  │     ├─ series.cpython-311.pyc
   │     │  │     ├─ utils.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ _interchange
   │     │  │  ├─ dataframe.py
   │     │  │  ├─ series.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ dataframe.cpython-311.pyc
   │     │  │     ├─ series.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ _namespace.py
   │     │  ├─ _native.py
   │     │  ├─ _pandas_like
   │     │  │  ├─ dataframe.py
   │     │  │  ├─ expr.py
   │     │  │  ├─ group_by.py
   │     │  │  ├─ namespace.py
   │     │  │  ├─ selectors.py
   │     │  │  ├─ series.py
   │     │  │  ├─ series_cat.py
   │     │  │  ├─ series_dt.py
   │     │  │  ├─ series_list.py
   │     │  │  ├─ series_str.py
   │     │  │  ├─ series_struct.py
   │     │  │  ├─ typing.py
   │     │  │  ├─ utils.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ dataframe.cpython-311.pyc
   │     │  │     ├─ expr.cpython-311.pyc
   │     │  │     ├─ group_by.cpython-311.pyc
   │     │  │     ├─ namespace.cpython-311.pyc
   │     │  │     ├─ selectors.cpython-311.pyc
   │     │  │     ├─ series.cpython-311.pyc
   │     │  │     ├─ series_cat.cpython-311.pyc
   │     │  │     ├─ series_dt.cpython-311.pyc
   │     │  │     ├─ series_list.cpython-311.pyc
   │     │  │     ├─ series_str.cpython-311.pyc
   │     │  │     ├─ series_struct.cpython-311.pyc
   │     │  │     ├─ typing.cpython-311.pyc
   │     │  │     ├─ utils.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ _polars
   │     │  │  ├─ dataframe.py
   │     │  │  ├─ expr.py
   │     │  │  ├─ group_by.py
   │     │  │  ├─ namespace.py
   │     │  │  ├─ series.py
   │     │  │  ├─ typing.py
   │     │  │  ├─ utils.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ dataframe.cpython-311.pyc
   │     │  │     ├─ expr.cpython-311.pyc
   │     │  │     ├─ group_by.cpython-311.pyc
   │     │  │     ├─ namespace.cpython-311.pyc
   │     │  │     ├─ series.cpython-311.pyc
   │     │  │     ├─ typing.cpython-311.pyc
   │     │  │     ├─ utils.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ _spark_like
   │     │  │  ├─ dataframe.py
   │     │  │  ├─ expr.py
   │     │  │  ├─ expr_dt.py
   │     │  │  ├─ expr_list.py
   │     │  │  ├─ expr_str.py
   │     │  │  ├─ expr_struct.py
   │     │  │  ├─ group_by.py
   │     │  │  ├─ namespace.py
   │     │  │  ├─ selectors.py
   │     │  │  ├─ utils.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ dataframe.cpython-311.pyc
   │     │  │     ├─ expr.cpython-311.pyc
   │     │  │     ├─ expr_dt.cpython-311.pyc
   │     │  │     ├─ expr_list.cpython-311.pyc
   │     │  │     ├─ expr_str.cpython-311.pyc
   │     │  │     ├─ expr_struct.cpython-311.pyc
   │     │  │     ├─ group_by.cpython-311.pyc
   │     │  │     ├─ namespace.cpython-311.pyc
   │     │  │     ├─ selectors.cpython-311.pyc
   │     │  │     ├─ utils.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ _sql
   │     │  │  ├─ dataframe.py
   │     │  │  ├─ expr.py
   │     │  │  ├─ expr_dt.py
   │     │  │  ├─ expr_str.py
   │     │  │  ├─ group_by.py
   │     │  │  ├─ namespace.py
   │     │  │  ├─ typing.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ dataframe.cpython-311.pyc
   │     │  │     ├─ expr.cpython-311.pyc
   │     │  │     ├─ expr_dt.cpython-311.pyc
   │     │  │     ├─ expr_str.cpython-311.pyc
   │     │  │     ├─ group_by.cpython-311.pyc
   │     │  │     ├─ namespace.cpython-311.pyc
   │     │  │     ├─ typing.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ _translate.py
   │     │  ├─ _typing.py
   │     │  ├─ _typing_compat.py
   │     │  ├─ _utils.py
   │     │  ├─ __init__.py
   │     │  └─ __pycache__
   │     │     ├─ compliant.cpython-311.pyc
   │     │     ├─ dataframe.cpython-311.pyc
   │     │     ├─ dependencies.cpython-311.pyc
   │     │     ├─ dtypes.cpython-311.pyc
   │     │     ├─ exceptions.cpython-311.pyc
   │     │     ├─ expr.cpython-311.pyc
   │     │     ├─ expr_cat.cpython-311.pyc
   │     │     ├─ expr_dt.cpython-311.pyc
   │     │     ├─ expr_list.cpython-311.pyc
   │     │     ├─ expr_name.cpython-311.pyc
   │     │     ├─ expr_str.cpython-311.pyc
   │     │     ├─ expr_struct.cpython-311.pyc
   │     │     ├─ functions.cpython-311.pyc
   │     │     ├─ group_by.cpython-311.pyc
   │     │     ├─ plugins.cpython-311.pyc
   │     │     ├─ schema.cpython-311.pyc
   │     │     ├─ selectors.cpython-311.pyc
   │     │     ├─ series.cpython-311.pyc
   │     │     ├─ series_cat.cpython-311.pyc
   │     │     ├─ series_dt.cpython-311.pyc
   │     │     ├─ series_list.cpython-311.pyc
   │     │     ├─ series_str.cpython-311.pyc
   │     │     ├─ series_struct.cpython-311.pyc
   │     │     ├─ sql.cpython-311.pyc
   │     │     ├─ this.cpython-311.pyc
   │     │     ├─ translate.cpython-311.pyc
   │     │     ├─ typing.cpython-311.pyc
   │     │     ├─ utils.cpython-311.pyc
   │     │     ├─ _constants.cpython-311.pyc
   │     │     ├─ _duration.cpython-311.pyc
   │     │     ├─ _enum.cpython-311.pyc
   │     │     ├─ _exceptions.cpython-311.pyc
   │     │     ├─ _expression_parsing.cpython-311.pyc
   │     │     ├─ _namespace.cpython-311.pyc
   │     │     ├─ _native.cpython-311.pyc
   │     │     ├─ _translate.cpython-311.pyc
   │     │     ├─ _typing.cpython-311.pyc
   │     │     ├─ _typing_compat.cpython-311.pyc
   │     │     ├─ _utils.cpython-311.pyc
   │     │     └─ __init__.cpython-311.pyc
   │     ├─ narwhals-2.19.0.dist-info
   │     │  ├─ INSTALLER
   │     │  ├─ licenses
   │     │  │  └─ LICENSE.md
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  └─ WHEEL
   │     ├─ numpy
   │     │  ├─ char
   │     │  │  ├─ __init__.py
   │     │  │  ├─ __init__.pyi
   │     │  │  └─ __pycache__
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ conftest.py
   │     │  ├─ core
   │     │  │  ├─ arrayprint.py
   │     │  │  ├─ defchararray.py
   │     │  │  ├─ einsumfunc.py
   │     │  │  ├─ fromnumeric.py
   │     │  │  ├─ function_base.py
   │     │  │  ├─ getlimits.py
   │     │  │  ├─ multiarray.py
   │     │  │  ├─ numeric.py
   │     │  │  ├─ numerictypes.py
   │     │  │  ├─ overrides.py
   │     │  │  ├─ overrides.pyi
   │     │  │  ├─ records.py
   │     │  │  ├─ shape_base.py
   │     │  │  ├─ umath.py
   │     │  │  ├─ _dtype.py
   │     │  │  ├─ _dtype.pyi
   │     │  │  ├─ _dtype_ctypes.py
   │     │  │  ├─ _dtype_ctypes.pyi
   │     │  │  ├─ _internal.py
   │     │  │  ├─ _multiarray_umath.py
   │     │  │  ├─ _utils.py
   │     │  │  ├─ __init__.py
   │     │  │  ├─ __init__.pyi
   │     │  │  └─ __pycache__
   │     │  │     ├─ arrayprint.cpython-311.pyc
   │     │  │     ├─ defchararray.cpython-311.pyc
   │     │  │     ├─ einsumfunc.cpython-311.pyc
   │     │  │     ├─ fromnumeric.cpython-311.pyc
   │     │  │     ├─ function_base.cpython-311.pyc
   │     │  │     ├─ getlimits.cpython-311.pyc
   │     │  │     ├─ multiarray.cpython-311.pyc
   │     │  │     ├─ numeric.cpython-311.pyc
   │     │  │     ├─ numerictypes.cpython-311.pyc
   │     │  │     ├─ overrides.cpython-311.pyc
   │     │  │     ├─ records.cpython-311.pyc
   │     │  │     ├─ shape_base.cpython-311.pyc
   │     │  │     ├─ umath.cpython-311.pyc
   │     │  │     ├─ _dtype.cpython-311.pyc
   │     │  │     ├─ _dtype_ctypes.cpython-311.pyc
   │     │  │     ├─ _internal.cpython-311.pyc
   │     │  │     ├─ _multiarray_umath.cpython-311.pyc
   │     │  │     ├─ _utils.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ ctypeslib
   │     │  │  ├─ _ctypeslib.py
   │     │  │  ├─ _ctypeslib.pyi
   │     │  │  ├─ __init__.py
   │     │  │  ├─ __init__.pyi
   │     │  │  └─ __pycache__
   │     │  │     ├─ _ctypeslib.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ distutils
   │     │  │  ├─ armccompiler.py
   │     │  │  ├─ ccompiler.py
   │     │  │  ├─ ccompiler_opt.py
   │     │  │  ├─ checks
   │     │  │  │  ├─ cpu_asimd.c
   │     │  │  │  ├─ cpu_asimddp.c
   │     │  │  │  ├─ cpu_asimdfhm.c
   │     │  │  │  ├─ cpu_asimdhp.c
   │     │  │  │  ├─ cpu_avx.c
   │     │  │  │  ├─ cpu_avx2.c
   │     │  │  │  ├─ cpu_avx512cd.c
   │     │  │  │  ├─ cpu_avx512f.c
   │     │  │  │  ├─ cpu_avx512_clx.c
   │     │  │  │  ├─ cpu_avx512_cnl.c
   │     │  │  │  ├─ cpu_avx512_icl.c
   │     │  │  │  ├─ cpu_avx512_knl.c
   │     │  │  │  ├─ cpu_avx512_knm.c
   │     │  │  │  ├─ cpu_avx512_skx.c
   │     │  │  │  ├─ cpu_avx512_spr.c
   │     │  │  │  ├─ cpu_f16c.c
   │     │  │  │  ├─ cpu_fma3.c
   │     │  │  │  ├─ cpu_fma4.c
   │     │  │  │  ├─ cpu_lsx.c
   │     │  │  │  ├─ cpu_neon.c
   │     │  │  │  ├─ cpu_neon_fp16.c
   │     │  │  │  ├─ cpu_neon_vfpv4.c
   │     │  │  │  ├─ cpu_popcnt.c
   │     │  │  │  ├─ cpu_rvv.c
   │     │  │  │  ├─ cpu_sse.c
   │     │  │  │  ├─ cpu_sse2.c
   │     │  │  │  ├─ cpu_sse3.c
   │     │  │  │  ├─ cpu_sse41.c
   │     │  │  │  ├─ cpu_sse42.c
   │     │  │  │  ├─ cpu_ssse3.c
   │     │  │  │  ├─ cpu_sve.c
   │     │  │  │  ├─ cpu_vsx.c
   │     │  │  │  ├─ cpu_vsx2.c
   │     │  │  │  ├─ cpu_vsx3.c
   │     │  │  │  ├─ cpu_vsx4.c
   │     │  │  │  ├─ cpu_vx.c
   │     │  │  │  ├─ cpu_vxe.c
   │     │  │  │  ├─ cpu_vxe2.c
   │     │  │  │  ├─ cpu_xop.c
   │     │  │  │  ├─ extra_avx512bw_mask.c
   │     │  │  │  ├─ extra_avx512dq_mask.c
   │     │  │  │  ├─ extra_avx512f_reduce.c
   │     │  │  │  ├─ extra_vsx3_half_double.c
   │     │  │  │  ├─ extra_vsx4_mma.c
   │     │  │  │  ├─ extra_vsx_asm.c
   │     │  │  │  └─ test_flags.c
   │     │  │  ├─ command
   │     │  │  │  ├─ autodist.py
   │     │  │  │  ├─ bdist_rpm.py
   │     │  │  │  ├─ build.py
   │     │  │  │  ├─ build_clib.py
   │     │  │  │  ├─ build_ext.py
   │     │  │  │  ├─ build_py.py
   │     │  │  │  ├─ build_scripts.py
   │     │  │  │  ├─ build_src.py
   │     │  │  │  ├─ config.py
   │     │  │  │  ├─ config_compiler.py
   │     │  │  │  ├─ develop.py
   │     │  │  │  ├─ egg_info.py
   │     │  │  │  ├─ install.py
   │     │  │  │  ├─ install_clib.py
   │     │  │  │  ├─ install_data.py
   │     │  │  │  ├─ install_headers.py
   │     │  │  │  ├─ sdist.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ autodist.cpython-311.pyc
   │     │  │  │     ├─ bdist_rpm.cpython-311.pyc
   │     │  │  │     ├─ build.cpython-311.pyc
   │     │  │  │     ├─ build_clib.cpython-311.pyc
   │     │  │  │     ├─ build_ext.cpython-311.pyc
   │     │  │  │     ├─ build_py.cpython-311.pyc
   │     │  │  │     ├─ build_scripts.cpython-311.pyc
   │     │  │  │     ├─ build_src.cpython-311.pyc
   │     │  │  │     ├─ config.cpython-311.pyc
   │     │  │  │     ├─ config_compiler.cpython-311.pyc
   │     │  │  │     ├─ develop.cpython-311.pyc
   │     │  │  │     ├─ egg_info.cpython-311.pyc
   │     │  │  │     ├─ install.cpython-311.pyc
   │     │  │  │     ├─ install_clib.cpython-311.pyc
   │     │  │  │     ├─ install_data.cpython-311.pyc
   │     │  │  │     ├─ install_headers.cpython-311.pyc
   │     │  │  │     ├─ sdist.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ conv_template.py
   │     │  │  ├─ core.py
   │     │  │  ├─ cpuinfo.py
   │     │  │  ├─ exec_command.py
   │     │  │  ├─ extension.py
   │     │  │  ├─ fcompiler
   │     │  │  │  ├─ absoft.py
   │     │  │  │  ├─ arm.py
   │     │  │  │  ├─ compaq.py
   │     │  │  │  ├─ environment.py
   │     │  │  │  ├─ fujitsu.py
   │     │  │  │  ├─ g95.py
   │     │  │  │  ├─ gnu.py
   │     │  │  │  ├─ hpux.py
   │     │  │  │  ├─ ibm.py
   │     │  │  │  ├─ intel.py
   │     │  │  │  ├─ lahey.py
   │     │  │  │  ├─ mips.py
   │     │  │  │  ├─ nag.py
   │     │  │  │  ├─ none.py
   │     │  │  │  ├─ nv.py
   │     │  │  │  ├─ pathf95.py
   │     │  │  │  ├─ pg.py
   │     │  │  │  ├─ sun.py
   │     │  │  │  ├─ vast.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ absoft.cpython-311.pyc
   │     │  │  │     ├─ arm.cpython-311.pyc
   │     │  │  │     ├─ compaq.cpython-311.pyc
   │     │  │  │     ├─ environment.cpython-311.pyc
   │     │  │  │     ├─ fujitsu.cpython-311.pyc
   │     │  │  │     ├─ g95.cpython-311.pyc
   │     │  │  │     ├─ gnu.cpython-311.pyc
   │     │  │  │     ├─ hpux.cpython-311.pyc
   │     │  │  │     ├─ ibm.cpython-311.pyc
   │     │  │  │     ├─ intel.cpython-311.pyc
   │     │  │  │     ├─ lahey.cpython-311.pyc
   │     │  │  │     ├─ mips.cpython-311.pyc
   │     │  │  │     ├─ nag.cpython-311.pyc
   │     │  │  │     ├─ none.cpython-311.pyc
   │     │  │  │     ├─ nv.cpython-311.pyc
   │     │  │  │     ├─ pathf95.cpython-311.pyc
   │     │  │  │     ├─ pg.cpython-311.pyc
   │     │  │  │     ├─ sun.cpython-311.pyc
   │     │  │  │     ├─ vast.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ from_template.py
   │     │  │  ├─ fujitsuccompiler.py
   │     │  │  ├─ intelccompiler.py
   │     │  │  ├─ lib2def.py
   │     │  │  ├─ line_endings.py
   │     │  │  ├─ log.py
   │     │  │  ├─ mingw
   │     │  │  │  └─ gfortran_vs2003_hack.c
   │     │  │  ├─ mingw32ccompiler.py
   │     │  │  ├─ misc_util.py
   │     │  │  ├─ msvc9compiler.py
   │     │  │  ├─ msvccompiler.py
   │     │  │  ├─ npy_pkg_config.py
   │     │  │  ├─ numpy_distribution.py
   │     │  │  ├─ pathccompiler.py
   │     │  │  ├─ system_info.py
   │     │  │  ├─ tests
   │     │  │  │  ├─ test_build_ext.py
   │     │  │  │  ├─ test_ccompiler_opt.py
   │     │  │  │  ├─ test_ccompiler_opt_conf.py
   │     │  │  │  ├─ test_exec_command.py
   │     │  │  │  ├─ test_fcompiler.py
   │     │  │  │  ├─ test_fcompiler_gnu.py
   │     │  │  │  ├─ test_fcompiler_intel.py
   │     │  │  │  ├─ test_fcompiler_nagfor.py
   │     │  │  │  ├─ test_from_template.py
   │     │  │  │  ├─ test_log.py
   │     │  │  │  ├─ test_mingw32ccompiler.py
   │     │  │  │  ├─ test_misc_util.py
   │     │  │  │  ├─ test_npy_pkg_config.py
   │     │  │  │  ├─ test_shell_utils.py
   │     │  │  │  ├─ test_system_info.py
   │     │  │  │  ├─ utilities.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ test_build_ext.cpython-311.pyc
   │     │  │  │     ├─ test_ccompiler_opt.cpython-311.pyc
   │     │  │  │     ├─ test_ccompiler_opt_conf.cpython-311.pyc
   │     │  │  │     ├─ test_exec_command.cpython-311.pyc
   │     │  │  │     ├─ test_fcompiler.cpython-311.pyc
   │     │  │  │     ├─ test_fcompiler_gnu.cpython-311.pyc
   │     │  │  │     ├─ test_fcompiler_intel.cpython-311.pyc
   │     │  │  │     ├─ test_fcompiler_nagfor.cpython-311.pyc
   │     │  │  │     ├─ test_from_template.cpython-311.pyc
   │     │  │  │     ├─ test_log.cpython-311.pyc
   │     │  │  │     ├─ test_mingw32ccompiler.cpython-311.pyc
   │     │  │  │     ├─ test_misc_util.cpython-311.pyc
   │     │  │  │     ├─ test_npy_pkg_config.cpython-311.pyc
   │     │  │  │     ├─ test_shell_utils.cpython-311.pyc
   │     │  │  │     ├─ test_system_info.cpython-311.pyc
   │     │  │  │     ├─ utilities.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ unixccompiler.py
   │     │  │  ├─ _shell_utils.py
   │     │  │  ├─ __init__.py
   │     │  │  ├─ __init__.pyi
   │     │  │  └─ __pycache__
   │     │  │     ├─ armccompiler.cpython-311.pyc
   │     │  │     ├─ ccompiler.cpython-311.pyc
   │     │  │     ├─ ccompiler_opt.cpython-311.pyc
   │     │  │     ├─ conv_template.cpython-311.pyc
   │     │  │     ├─ core.cpython-311.pyc
   │     │  │     ├─ cpuinfo.cpython-311.pyc
   │     │  │     ├─ exec_command.cpython-311.pyc
   │     │  │     ├─ extension.cpython-311.pyc
   │     │  │     ├─ from_template.cpython-311.pyc
   │     │  │     ├─ fujitsuccompiler.cpython-311.pyc
   │     │  │     ├─ intelccompiler.cpython-311.pyc
   │     │  │     ├─ lib2def.cpython-311.pyc
   │     │  │     ├─ line_endings.cpython-311.pyc
   │     │  │     ├─ log.cpython-311.pyc
   │     │  │     ├─ mingw32ccompiler.cpython-311.pyc
   │     │  │     ├─ misc_util.cpython-311.pyc
   │     │  │     ├─ msvc9compiler.cpython-311.pyc
   │     │  │     ├─ msvccompiler.cpython-311.pyc
   │     │  │     ├─ npy_pkg_config.cpython-311.pyc
   │     │  │     ├─ numpy_distribution.cpython-311.pyc
   │     │  │     ├─ pathccompiler.cpython-311.pyc
   │     │  │     ├─ system_info.cpython-311.pyc
   │     │  │     ├─ unixccompiler.cpython-311.pyc
   │     │  │     ├─ _shell_utils.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ doc
   │     │  │  ├─ ufuncs.py
   │     │  │  └─ __pycache__
   │     │  │     └─ ufuncs.cpython-311.pyc
   │     │  ├─ dtypes.py
   │     │  ├─ dtypes.pyi
   │     │  ├─ exceptions.py
   │     │  ├─ exceptions.pyi
   │     │  ├─ f2py
   │     │  │  ├─ auxfuncs.py
   │     │  │  ├─ auxfuncs.pyi
   │     │  │  ├─ capi_maps.py
   │     │  │  ├─ capi_maps.pyi
   │     │  │  ├─ cb_rules.py
   │     │  │  ├─ cb_rules.pyi
   │     │  │  ├─ cfuncs.py
   │     │  │  ├─ cfuncs.pyi
   │     │  │  ├─ common_rules.py
   │     │  │  ├─ common_rules.pyi
   │     │  │  ├─ crackfortran.py
   │     │  │  ├─ crackfortran.pyi
   │     │  │  ├─ diagnose.py
   │     │  │  ├─ diagnose.pyi
   │     │  │  ├─ f2py2e.py
   │     │  │  ├─ f2py2e.pyi
   │     │  │  ├─ f90mod_rules.py
   │     │  │  ├─ f90mod_rules.pyi
   │     │  │  ├─ func2subr.py
   │     │  │  ├─ func2subr.pyi
   │     │  │  ├─ rules.py
   │     │  │  ├─ rules.pyi
   │     │  │  ├─ setup.cfg
   │     │  │  ├─ src
   │     │  │  │  ├─ fortranobject.c
   │     │  │  │  └─ fortranobject.h
   │     │  │  ├─ symbolic.py
   │     │  │  ├─ symbolic.pyi
   │     │  │  ├─ tests
   │     │  │  │  ├─ src
   │     │  │  │  │  ├─ abstract_interface
   │     │  │  │  │  │  ├─ foo.f90
   │     │  │  │  │  │  └─ gh18403_mod.f90
   │     │  │  │  │  ├─ array_from_pyobj
   │     │  │  │  │  │  └─ wrapmodule.c
   │     │  │  │  │  ├─ assumed_shape
   │     │  │  │  │  │  ├─ .f2py_f2cmap
   │     │  │  │  │  │  ├─ foo_free.f90
   │     │  │  │  │  │  ├─ foo_mod.f90
   │     │  │  │  │  │  ├─ foo_use.f90
   │     │  │  │  │  │  └─ precision.f90
   │     │  │  │  │  ├─ block_docstring
   │     │  │  │  │  │  └─ foo.f
   │     │  │  │  │  ├─ callback
   │     │  │  │  │  │  ├─ foo.f
   │     │  │  │  │  │  ├─ gh17797.f90
   │     │  │  │  │  │  ├─ gh18335.f90
   │     │  │  │  │  │  ├─ gh25211.f
   │     │  │  │  │  │  ├─ gh25211.pyf
   │     │  │  │  │  │  └─ gh26681.f90
   │     │  │  │  │  ├─ cli
   │     │  │  │  │  │  ├─ gh_22819.pyf
   │     │  │  │  │  │  ├─ hi77.f
   │     │  │  │  │  │  └─ hiworld.f90
   │     │  │  │  │  ├─ common
   │     │  │  │  │  │  ├─ block.f
   │     │  │  │  │  │  └─ gh19161.f90
   │     │  │  │  │  ├─ crackfortran
   │     │  │  │  │  │  ├─ accesstype.f90
   │     │  │  │  │  │  ├─ common_with_division.f
   │     │  │  │  │  │  ├─ data_common.f
   │     │  │  │  │  │  ├─ data_multiplier.f
   │     │  │  │  │  │  ├─ data_stmts.f90
   │     │  │  │  │  │  ├─ data_with_comments.f
   │     │  │  │  │  │  ├─ foo_deps.f90
   │     │  │  │  │  │  ├─ gh15035.f
   │     │  │  │  │  │  ├─ gh17859.f
   │     │  │  │  │  │  ├─ gh22648.pyf
   │     │  │  │  │  │  ├─ gh23533.f
   │     │  │  │  │  │  ├─ gh23598.f90
   │     │  │  │  │  │  ├─ gh23598Warn.f90
   │     │  │  │  │  │  ├─ gh23879.f90
   │     │  │  │  │  │  ├─ gh27697.f90
   │     │  │  │  │  │  ├─ gh2848.f90
   │     │  │  │  │  │  ├─ operators.f90
   │     │  │  │  │  │  ├─ privatemod.f90
   │     │  │  │  │  │  ├─ publicmod.f90
   │     │  │  │  │  │  ├─ pubprivmod.f90
   │     │  │  │  │  │  └─ unicode_comment.f90
   │     │  │  │  │  ├─ f2cmap
   │     │  │  │  │  │  ├─ .f2py_f2cmap
   │     │  │  │  │  │  └─ isoFortranEnvMap.f90
   │     │  │  │  │  ├─ isocintrin
   │     │  │  │  │  │  └─ isoCtests.f90
   │     │  │  │  │  ├─ kind
   │     │  │  │  │  │  └─ foo.f90
   │     │  │  │  │  ├─ mixed
   │     │  │  │  │  │  ├─ foo.f
   │     │  │  │  │  │  ├─ foo_fixed.f90
   │     │  │  │  │  │  └─ foo_free.f90
   │     │  │  │  │  ├─ modules
   │     │  │  │  │  │  ├─ gh25337
   │     │  │  │  │  │  │  ├─ data.f90
   │     │  │  │  │  │  │  └─ use_data.f90
   │     │  │  │  │  │  ├─ gh26920
   │     │  │  │  │  │  │  ├─ two_mods_with_no_public_entities.f90
   │     │  │  │  │  │  │  └─ two_mods_with_one_public_routine.f90
   │     │  │  │  │  │  ├─ module_data_docstring.f90
   │     │  │  │  │  │  └─ use_modules.f90
   │     │  │  │  │  ├─ negative_bounds
   │     │  │  │  │  │  └─ issue_20853.f90
   │     │  │  │  │  ├─ parameter
   │     │  │  │  │  │  ├─ constant_array.f90
   │     │  │  │  │  │  ├─ constant_both.f90
   │     │  │  │  │  │  ├─ constant_compound.f90
   │     │  │  │  │  │  ├─ constant_integer.f90
   │     │  │  │  │  │  ├─ constant_non_compound.f90
   │     │  │  │  │  │  └─ constant_real.f90
   │     │  │  │  │  ├─ quoted_character
   │     │  │  │  │  │  └─ foo.f
   │     │  │  │  │  ├─ regression
   │     │  │  │  │  │  ├─ AB.inc
   │     │  │  │  │  │  ├─ assignOnlyModule.f90
   │     │  │  │  │  │  ├─ datonly.f90
   │     │  │  │  │  │  ├─ f77comments.f
   │     │  │  │  │  │  ├─ f77fixedform.f95
   │     │  │  │  │  │  ├─ f90continuation.f90
   │     │  │  │  │  │  ├─ incfile.f90
   │     │  │  │  │  │  ├─ inout.f90
   │     │  │  │  │  │  ├─ lower_f2py_fortran.f90
   │     │  │  │  │  │  └─ mod_derived_types.f90
   │     │  │  │  │  ├─ return_character
   │     │  │  │  │  │  ├─ foo77.f
   │     │  │  │  │  │  └─ foo90.f90
   │     │  │  │  │  ├─ return_complex
   │     │  │  │  │  │  ├─ foo77.f
   │     │  │  │  │  │  └─ foo90.f90
   │     │  │  │  │  ├─ return_integer
   │     │  │  │  │  │  ├─ foo77.f
   │     │  │  │  │  │  └─ foo90.f90
   │     │  │  │  │  ├─ return_logical
   │     │  │  │  │  │  ├─ foo77.f
   │     │  │  │  │  │  └─ foo90.f90
   │     │  │  │  │  ├─ return_real
   │     │  │  │  │  │  ├─ foo77.f
   │     │  │  │  │  │  └─ foo90.f90
   │     │  │  │  │  ├─ routines
   │     │  │  │  │  │  ├─ funcfortranname.f
   │     │  │  │  │  │  ├─ funcfortranname.pyf
   │     │  │  │  │  │  ├─ subrout.f
   │     │  │  │  │  │  └─ subrout.pyf
   │     │  │  │  │  ├─ size
   │     │  │  │  │  │  └─ foo.f90
   │     │  │  │  │  ├─ string
   │     │  │  │  │  │  ├─ char.f90
   │     │  │  │  │  │  ├─ fixed_string.f90
   │     │  │  │  │  │  ├─ gh24008.f
   │     │  │  │  │  │  ├─ gh24662.f90
   │     │  │  │  │  │  ├─ gh25286.f90
   │     │  │  │  │  │  ├─ gh25286.pyf
   │     │  │  │  │  │  ├─ gh25286_bc.pyf
   │     │  │  │  │  │  ├─ scalar_string.f90
   │     │  │  │  │  │  └─ string.f
   │     │  │  │  │  └─ value_attrspec
   │     │  │  │  │     └─ gh21665.f90
   │     │  │  │  ├─ test_abstract_interface.py
   │     │  │  │  ├─ test_array_from_pyobj.py
   │     │  │  │  ├─ test_assumed_shape.py
   │     │  │  │  ├─ test_block_docstring.py
   │     │  │  │  ├─ test_callback.py
   │     │  │  │  ├─ test_character.py
   │     │  │  │  ├─ test_common.py
   │     │  │  │  ├─ test_crackfortran.py
   │     │  │  │  ├─ test_data.py
   │     │  │  │  ├─ test_docs.py
   │     │  │  │  ├─ test_f2cmap.py
   │     │  │  │  ├─ test_f2py2e.py
   │     │  │  │  ├─ test_isoc.py
   │     │  │  │  ├─ test_kind.py
   │     │  │  │  ├─ test_mixed.py
   │     │  │  │  ├─ test_modules.py
   │     │  │  │  ├─ test_parameter.py
   │     │  │  │  ├─ test_pyf_src.py
   │     │  │  │  ├─ test_quoted_character.py
   │     │  │  │  ├─ test_regression.py
   │     │  │  │  ├─ test_return_character.py
   │     │  │  │  ├─ test_return_complex.py
   │     │  │  │  ├─ test_return_integer.py
   │     │  │  │  ├─ test_return_logical.py
   │     │  │  │  ├─ test_return_real.py
   │     │  │  │  ├─ test_routines.py
   │     │  │  │  ├─ test_semicolon_split.py
   │     │  │  │  ├─ test_size.py
   │     │  │  │  ├─ test_string.py
   │     │  │  │  ├─ test_symbolic.py
   │     │  │  │  ├─ test_value_attrspec.py
   │     │  │  │  ├─ util.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ test_abstract_interface.cpython-311.pyc
   │     │  │  │     ├─ test_array_from_pyobj.cpython-311.pyc
   │     │  │  │     ├─ test_assumed_shape.cpython-311.pyc
   │     │  │  │     ├─ test_block_docstring.cpython-311.pyc
   │     │  │  │     ├─ test_callback.cpython-311.pyc
   │     │  │  │     ├─ test_character.cpython-311.pyc
   │     │  │  │     ├─ test_common.cpython-311.pyc
   │     │  │  │     ├─ test_crackfortran.cpython-311.pyc
   │     │  │  │     ├─ test_data.cpython-311.pyc
   │     │  │  │     ├─ test_docs.cpython-311.pyc
   │     │  │  │     ├─ test_f2cmap.cpython-311.pyc
   │     │  │  │     ├─ test_f2py2e.cpython-311.pyc
   │     │  │  │     ├─ test_isoc.cpython-311.pyc
   │     │  │  │     ├─ test_kind.cpython-311.pyc
   │     │  │  │     ├─ test_mixed.cpython-311.pyc
   │     │  │  │     ├─ test_modules.cpython-311.pyc
   │     │  │  │     ├─ test_parameter.cpython-311.pyc
   │     │  │  │     ├─ test_pyf_src.cpython-311.pyc
   │     │  │  │     ├─ test_quoted_character.cpython-311.pyc
   │     │  │  │     ├─ test_regression.cpython-311.pyc
   │     │  │  │     ├─ test_return_character.cpython-311.pyc
   │     │  │  │     ├─ test_return_complex.cpython-311.pyc
   │     │  │  │     ├─ test_return_integer.cpython-311.pyc
   │     │  │  │     ├─ test_return_logical.cpython-311.pyc
   │     │  │  │     ├─ test_return_real.cpython-311.pyc
   │     │  │  │     ├─ test_routines.cpython-311.pyc
   │     │  │  │     ├─ test_semicolon_split.cpython-311.pyc
   │     │  │  │     ├─ test_size.cpython-311.pyc
   │     │  │  │     ├─ test_string.cpython-311.pyc
   │     │  │  │     ├─ test_symbolic.cpython-311.pyc
   │     │  │  │     ├─ test_value_attrspec.cpython-311.pyc
   │     │  │  │     ├─ util.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ use_rules.py
   │     │  │  ├─ use_rules.pyi
   │     │  │  ├─ _backends
   │     │  │  │  ├─ meson.build.template
   │     │  │  │  ├─ _backend.py
   │     │  │  │  ├─ _backend.pyi
   │     │  │  │  ├─ _distutils.py
   │     │  │  │  ├─ _distutils.pyi
   │     │  │  │  ├─ _meson.py
   │     │  │  │  ├─ _meson.pyi
   │     │  │  │  ├─ __init__.py
   │     │  │  │  ├─ __init__.pyi
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ _backend.cpython-311.pyc
   │     │  │  │     ├─ _distutils.cpython-311.pyc
   │     │  │  │     ├─ _meson.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ _isocbind.py
   │     │  │  ├─ _isocbind.pyi
   │     │  │  ├─ _src_pyf.py
   │     │  │  ├─ _src_pyf.pyi
   │     │  │  ├─ __init__.py
   │     │  │  ├─ __init__.pyi
   │     │  │  ├─ __main__.py
   │     │  │  ├─ __pycache__
   │     │  │  │  ├─ auxfuncs.cpython-311.pyc
   │     │  │  │  ├─ capi_maps.cpython-311.pyc
   │     │  │  │  ├─ cb_rules.cpython-311.pyc
   │     │  │  │  ├─ cfuncs.cpython-311.pyc
   │     │  │  │  ├─ common_rules.cpython-311.pyc
   │     │  │  │  ├─ crackfortran.cpython-311.pyc
   │     │  │  │  ├─ diagnose.cpython-311.pyc
   │     │  │  │  ├─ f2py2e.cpython-311.pyc
   │     │  │  │  ├─ f90mod_rules.cpython-311.pyc
   │     │  │  │  ├─ func2subr.cpython-311.pyc
   │     │  │  │  ├─ rules.cpython-311.pyc
   │     │  │  │  ├─ symbolic.cpython-311.pyc
   │     │  │  │  ├─ use_rules.cpython-311.pyc
   │     │  │  │  ├─ _isocbind.cpython-311.pyc
   │     │  │  │  ├─ _src_pyf.cpython-311.pyc
   │     │  │  │  ├─ __init__.cpython-311.pyc
   │     │  │  │  ├─ __main__.cpython-311.pyc
   │     │  │  │  └─ __version__.cpython-311.pyc
   │     │  │  ├─ __version__.py
   │     │  │  └─ __version__.pyi
   │     │  ├─ fft
   │     │  │  ├─ tests
   │     │  │  │  ├─ test_helper.py
   │     │  │  │  ├─ test_pocketfft.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ test_helper.cpython-311.pyc
   │     │  │  │     ├─ test_pocketfft.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ _helper.py
   │     │  │  ├─ _helper.pyi
   │     │  │  ├─ _pocketfft.py
   │     │  │  ├─ _pocketfft.pyi
   │     │  │  ├─ _pocketfft_umath.cp311-win_amd64.lib
   │     │  │  ├─ _pocketfft_umath.cp311-win_amd64.pyd
   │     │  │  ├─ __init__.py
   │     │  │  ├─ __init__.pyi
   │     │  │  └─ __pycache__
   │     │  │     ├─ _helper.cpython-311.pyc
   │     │  │     ├─ _pocketfft.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ lib
   │     │  │  ├─ array_utils.py
   │     │  │  ├─ array_utils.pyi
   │     │  │  ├─ format.py
   │     │  │  ├─ format.pyi
   │     │  │  ├─ introspect.py
   │     │  │  ├─ introspect.pyi
   │     │  │  ├─ mixins.py
   │     │  │  ├─ mixins.pyi
   │     │  │  ├─ npyio.py
   │     │  │  ├─ npyio.pyi
   │     │  │  ├─ recfunctions.py
   │     │  │  ├─ recfunctions.pyi
   │     │  │  ├─ scimath.py
   │     │  │  ├─ scimath.pyi
   │     │  │  ├─ stride_tricks.py
   │     │  │  ├─ stride_tricks.pyi
   │     │  │  ├─ tests
   │     │  │  │  ├─ data
   │     │  │  │  │  ├─ py2-np0-objarr.npy
   │     │  │  │  │  ├─ py2-objarr.npy
   │     │  │  │  │  ├─ py2-objarr.npz
   │     │  │  │  │  ├─ py3-objarr.npy
   │     │  │  │  │  ├─ py3-objarr.npz
   │     │  │  │  │  ├─ python3.npy
   │     │  │  │  │  └─ win64python2.npy
   │     │  │  │  ├─ test_arraypad.py
   │     │  │  │  ├─ test_arraysetops.py
   │     │  │  │  ├─ test_arrayterator.py
   │     │  │  │  ├─ test_array_utils.py
   │     │  │  │  ├─ test_format.py
   │     │  │  │  ├─ test_function_base.py
   │     │  │  │  ├─ test_histograms.py
   │     │  │  │  ├─ test_index_tricks.py
   │     │  │  │  ├─ test_io.py
   │     │  │  │  ├─ test_loadtxt.py
   │     │  │  │  ├─ test_mixins.py
   │     │  │  │  ├─ test_nanfunctions.py
   │     │  │  │  ├─ test_packbits.py
   │     │  │  │  ├─ test_polynomial.py
   │     │  │  │  ├─ test_recfunctions.py
   │     │  │  │  ├─ test_regression.py
   │     │  │  │  ├─ test_shape_base.py
   │     │  │  │  ├─ test_stride_tricks.py
   │     │  │  │  ├─ test_twodim_base.py
   │     │  │  │  ├─ test_type_check.py
   │     │  │  │  ├─ test_ufunclike.py
   │     │  │  │  ├─ test_utils.py
   │     │  │  │  ├─ test__datasource.py
   │     │  │  │  ├─ test__iotools.py
   │     │  │  │  ├─ test__version.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ test_arraypad.cpython-311.pyc
   │     │  │  │     ├─ test_arraysetops.cpython-311.pyc
   │     │  │  │     ├─ test_arrayterator.cpython-311.pyc
   │     │  │  │     ├─ test_array_utils.cpython-311.pyc
   │     │  │  │     ├─ test_format.cpython-311.pyc
   │     │  │  │     ├─ test_function_base.cpython-311.pyc
   │     │  │  │     ├─ test_histograms.cpython-311.pyc
   │     │  │  │     ├─ test_index_tricks.cpython-311.pyc
   │     │  │  │     ├─ test_io.cpython-311.pyc
   │     │  │  │     ├─ test_loadtxt.cpython-311.pyc
   │     │  │  │     ├─ test_mixins.cpython-311.pyc
   │     │  │  │     ├─ test_nanfunctions.cpython-311.pyc
   │     │  │  │     ├─ test_packbits.cpython-311.pyc
   │     │  │  │     ├─ test_polynomial.cpython-311.pyc
   │     │  │  │     ├─ test_recfunctions.cpython-311.pyc
   │     │  │  │     ├─ test_regression.cpython-311.pyc
   │     │  │  │     ├─ test_shape_base.cpython-311.pyc
   │     │  │  │     ├─ test_stride_tricks.cpython-311.pyc
   │     │  │  │     ├─ test_twodim_base.cpython-311.pyc
   │     │  │  │     ├─ test_type_check.cpython-311.pyc
   │     │  │  │     ├─ test_ufunclike.cpython-311.pyc
   │     │  │  │     ├─ test_utils.cpython-311.pyc
   │     │  │  │     ├─ test__datasource.cpython-311.pyc
   │     │  │  │     ├─ test__iotools.cpython-311.pyc
   │     │  │  │     ├─ test__version.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ user_array.py
   │     │  │  ├─ user_array.pyi
   │     │  │  ├─ _arraypad_impl.py
   │     │  │  ├─ _arraypad_impl.pyi
   │     │  │  ├─ _arraysetops_impl.py
   │     │  │  ├─ _arraysetops_impl.pyi
   │     │  │  ├─ _arrayterator_impl.py
   │     │  │  ├─ _arrayterator_impl.pyi
   │     │  │  ├─ _array_utils_impl.py
   │     │  │  ├─ _array_utils_impl.pyi
   │     │  │  ├─ _datasource.py
   │     │  │  ├─ _datasource.pyi
   │     │  │  ├─ _format_impl.py
   │     │  │  ├─ _format_impl.pyi
   │     │  │  ├─ _function_base_impl.py
   │     │  │  ├─ _function_base_impl.pyi
   │     │  │  ├─ _histograms_impl.py
   │     │  │  ├─ _histograms_impl.pyi
   │     │  │  ├─ _index_tricks_impl.py
   │     │  │  ├─ _index_tricks_impl.pyi
   │     │  │  ├─ _iotools.py
   │     │  │  ├─ _iotools.pyi
   │     │  │  ├─ _nanfunctions_impl.py
   │     │  │  ├─ _nanfunctions_impl.pyi
   │     │  │  ├─ _npyio_impl.py
   │     │  │  ├─ _npyio_impl.pyi
   │     │  │  ├─ _polynomial_impl.py
   │     │  │  ├─ _polynomial_impl.pyi
   │     │  │  ├─ _scimath_impl.py
   │     │  │  ├─ _scimath_impl.pyi
   │     │  │  ├─ _shape_base_impl.py
   │     │  │  ├─ _shape_base_impl.pyi
   │     │  │  ├─ _stride_tricks_impl.py
   │     │  │  ├─ _stride_tricks_impl.pyi
   │     │  │  ├─ _twodim_base_impl.py
   │     │  │  ├─ _twodim_base_impl.pyi
   │     │  │  ├─ _type_check_impl.py
   │     │  │  ├─ _type_check_impl.pyi
   │     │  │  ├─ _ufunclike_impl.py
   │     │  │  ├─ _ufunclike_impl.pyi
   │     │  │  ├─ _user_array_impl.py
   │     │  │  ├─ _user_array_impl.pyi
   │     │  │  ├─ _utils_impl.py
   │     │  │  ├─ _utils_impl.pyi
   │     │  │  ├─ _version.py
   │     │  │  ├─ _version.pyi
   │     │  │  ├─ __init__.py
   │     │  │  ├─ __init__.pyi
   │     │  │  └─ __pycache__
   │     │  │     ├─ array_utils.cpython-311.pyc
   │     │  │     ├─ format.cpython-311.pyc
   │     │  │     ├─ introspect.cpython-311.pyc
   │     │  │     ├─ mixins.cpython-311.pyc
   │     │  │     ├─ npyio.cpython-311.pyc
   │     │  │     ├─ recfunctions.cpython-311.pyc
   │     │  │     ├─ scimath.cpython-311.pyc
   │     │  │     ├─ stride_tricks.cpython-311.pyc
   │     │  │     ├─ user_array.cpython-311.pyc
   │     │  │     ├─ _arraypad_impl.cpython-311.pyc
   │     │  │     ├─ _arraysetops_impl.cpython-311.pyc
   │     │  │     ├─ _arrayterator_impl.cpython-311.pyc
   │     │  │     ├─ _array_utils_impl.cpython-311.pyc
   │     │  │     ├─ _datasource.cpython-311.pyc
   │     │  │     ├─ _format_impl.cpython-311.pyc
   │     │  │     ├─ _function_base_impl.cpython-311.pyc
   │     │  │     ├─ _histograms_impl.cpython-311.pyc
   │     │  │     ├─ _index_tricks_impl.cpython-311.pyc
   │     │  │     ├─ _iotools.cpython-311.pyc
   │     │  │     ├─ _nanfunctions_impl.cpython-311.pyc
   │     │  │     ├─ _npyio_impl.cpython-311.pyc
   │     │  │     ├─ _polynomial_impl.cpython-311.pyc
   │     │  │     ├─ _scimath_impl.cpython-311.pyc
   │     │  │     ├─ _shape_base_impl.cpython-311.pyc
   │     │  │     ├─ _stride_tricks_impl.cpython-311.pyc
   │     │  │     ├─ _twodim_base_impl.cpython-311.pyc
   │     │  │     ├─ _type_check_impl.cpython-311.pyc
   │     │  │     ├─ _ufunclike_impl.cpython-311.pyc
   │     │  │     ├─ _user_array_impl.cpython-311.pyc
   │     │  │     ├─ _utils_impl.cpython-311.pyc
   │     │  │     ├─ _version.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ linalg
   │     │  │  ├─ lapack_lite.cp311-win_amd64.lib
   │     │  │  ├─ lapack_lite.cp311-win_amd64.pyd
   │     │  │  ├─ lapack_lite.pyi
   │     │  │  ├─ tests
   │     │  │  │  ├─ test_deprecations.py
   │     │  │  │  ├─ test_linalg.py
   │     │  │  │  ├─ test_regression.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ test_deprecations.cpython-311.pyc
   │     │  │  │     ├─ test_linalg.cpython-311.pyc
   │     │  │  │     ├─ test_regression.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ _linalg.py
   │     │  │  ├─ _linalg.pyi
   │     │  │  ├─ _umath_linalg.cp311-win_amd64.lib
   │     │  │  ├─ _umath_linalg.cp311-win_amd64.pyd
   │     │  │  ├─ _umath_linalg.pyi
   │     │  │  ├─ __init__.py
   │     │  │  ├─ __init__.pyi
   │     │  │  └─ __pycache__
   │     │  │     ├─ _linalg.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ ma
   │     │  │  ├─ API_CHANGES.txt
   │     │  │  ├─ core.py
   │     │  │  ├─ core.pyi
   │     │  │  ├─ extras.py
   │     │  │  ├─ extras.pyi
   │     │  │  ├─ LICENSE
   │     │  │  ├─ mrecords.py
   │     │  │  ├─ mrecords.pyi
   │     │  │  ├─ README.rst
   │     │  │  ├─ tests
   │     │  │  │  ├─ test_arrayobject.py
   │     │  │  │  ├─ test_core.py
   │     │  │  │  ├─ test_deprecations.py
   │     │  │  │  ├─ test_extras.py
   │     │  │  │  ├─ test_mrecords.py
   │     │  │  │  ├─ test_old_ma.py
   │     │  │  │  ├─ test_regression.py
   │     │  │  │  ├─ test_subclassing.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ test_arrayobject.cpython-311.pyc
   │     │  │  │     ├─ test_core.cpython-311.pyc
   │     │  │  │     ├─ test_deprecations.cpython-311.pyc
   │     │  │  │     ├─ test_extras.cpython-311.pyc
   │     │  │  │     ├─ test_mrecords.cpython-311.pyc
   │     │  │  │     ├─ test_old_ma.cpython-311.pyc
   │     │  │  │     ├─ test_regression.cpython-311.pyc
   │     │  │  │     ├─ test_subclassing.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ testutils.py
   │     │  │  ├─ testutils.pyi
   │     │  │  ├─ __init__.py
   │     │  │  ├─ __init__.pyi
   │     │  │  └─ __pycache__
   │     │  │     ├─ core.cpython-311.pyc
   │     │  │     ├─ extras.cpython-311.pyc
   │     │  │     ├─ mrecords.cpython-311.pyc
   │     │  │     ├─ testutils.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ matlib.py
   │     │  ├─ matlib.pyi
   │     │  ├─ matrixlib
   │     │  │  ├─ defmatrix.py
   │     │  │  ├─ defmatrix.pyi
   │     │  │  ├─ tests
   │     │  │  │  ├─ test_defmatrix.py
   │     │  │  │  ├─ test_interaction.py
   │     │  │  │  ├─ test_masked_matrix.py
   │     │  │  │  ├─ test_matrix_linalg.py
   │     │  │  │  ├─ test_multiarray.py
   │     │  │  │  ├─ test_numeric.py
   │     │  │  │  ├─ test_regression.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ test_defmatrix.cpython-311.pyc
   │     │  │  │     ├─ test_interaction.cpython-311.pyc
   │     │  │  │     ├─ test_masked_matrix.cpython-311.pyc
   │     │  │  │     ├─ test_matrix_linalg.cpython-311.pyc
   │     │  │  │     ├─ test_multiarray.cpython-311.pyc
   │     │  │  │     ├─ test_numeric.cpython-311.pyc
   │     │  │  │     ├─ test_regression.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ __init__.py
   │     │  │  ├─ __init__.pyi
   │     │  │  └─ __pycache__
   │     │  │     ├─ defmatrix.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ polynomial
   │     │  │  ├─ chebyshev.py
   │     │  │  ├─ chebyshev.pyi
   │     │  │  ├─ hermite.py
   │     │  │  ├─ hermite.pyi
   │     │  │  ├─ hermite_e.py
   │     │  │  ├─ hermite_e.pyi
   │     │  │  ├─ laguerre.py
   │     │  │  ├─ laguerre.pyi
   │     │  │  ├─ legendre.py
   │     │  │  ├─ legendre.pyi
   │     │  │  ├─ polynomial.py
   │     │  │  ├─ polynomial.pyi
   │     │  │  ├─ polyutils.py
   │     │  │  ├─ polyutils.pyi
   │     │  │  ├─ tests
   │     │  │  │  ├─ test_chebyshev.py
   │     │  │  │  ├─ test_classes.py
   │     │  │  │  ├─ test_hermite.py
   │     │  │  │  ├─ test_hermite_e.py
   │     │  │  │  ├─ test_laguerre.py
   │     │  │  │  ├─ test_legendre.py
   │     │  │  │  ├─ test_polynomial.py
   │     │  │  │  ├─ test_polyutils.py
   │     │  │  │  ├─ test_printing.py
   │     │  │  │  ├─ test_symbol.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ test_chebyshev.cpython-311.pyc
   │     │  │  │     ├─ test_classes.cpython-311.pyc
   │     │  │  │     ├─ test_hermite.cpython-311.pyc
   │     │  │  │     ├─ test_hermite_e.cpython-311.pyc
   │     │  │  │     ├─ test_laguerre.cpython-311.pyc
   │     │  │  │     ├─ test_legendre.cpython-311.pyc
   │     │  │  │     ├─ test_polynomial.cpython-311.pyc
   │     │  │  │     ├─ test_polyutils.cpython-311.pyc
   │     │  │  │     ├─ test_printing.cpython-311.pyc
   │     │  │  │     ├─ test_symbol.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ _polybase.py
   │     │  │  ├─ _polybase.pyi
   │     │  │  ├─ _polytypes.pyi
   │     │  │  ├─ __init__.py
   │     │  │  ├─ __init__.pyi
   │     │  │  └─ __pycache__
   │     │  │     ├─ chebyshev.cpython-311.pyc
   │     │  │     ├─ hermite.cpython-311.pyc
   │     │  │     ├─ hermite_e.cpython-311.pyc
   │     │  │     ├─ laguerre.cpython-311.pyc
   │     │  │     ├─ legendre.cpython-311.pyc
   │     │  │     ├─ polynomial.cpython-311.pyc
   │     │  │     ├─ polyutils.cpython-311.pyc
   │     │  │     ├─ _polybase.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ py.typed
   │     │  ├─ random
   │     │  │  ├─ bit_generator.cp311-win_amd64.lib
   │     │  │  ├─ bit_generator.cp311-win_amd64.pyd
   │     │  │  ├─ bit_generator.pxd
   │     │  │  ├─ bit_generator.pyi
   │     │  │  ├─ c_distributions.pxd
   │     │  │  ├─ lib
   │     │  │  │  └─ npyrandom.lib
   │     │  │  ├─ LICENSE.md
   │     │  │  ├─ mtrand.cp311-win_amd64.lib
   │     │  │  ├─ mtrand.cp311-win_amd64.pyd
   │     │  │  ├─ mtrand.pyi
   │     │  │  ├─ tests
   │     │  │  │  ├─ data
   │     │  │  │  │  ├─ generator_pcg64_np121.pkl.gz
   │     │  │  │  │  ├─ generator_pcg64_np126.pkl.gz
   │     │  │  │  │  ├─ mt19937-testset-1.csv
   │     │  │  │  │  ├─ mt19937-testset-2.csv
   │     │  │  │  │  ├─ pcg64-testset-1.csv
   │     │  │  │  │  ├─ pcg64-testset-2.csv
   │     │  │  │  │  ├─ pcg64dxsm-testset-1.csv
   │     │  │  │  │  ├─ pcg64dxsm-testset-2.csv
   │     │  │  │  │  ├─ philox-testset-1.csv
   │     │  │  │  │  ├─ philox-testset-2.csv
   │     │  │  │  │  ├─ sfc64-testset-1.csv
   │     │  │  │  │  ├─ sfc64-testset-2.csv
   │     │  │  │  │  ├─ sfc64_np126.pkl.gz
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ test_direct.py
   │     │  │  │  ├─ test_extending.py
   │     │  │  │  ├─ test_generator_mt19937.py
   │     │  │  │  ├─ test_generator_mt19937_regressions.py
   │     │  │  │  ├─ test_random.py
   │     │  │  │  ├─ test_randomstate.py
   │     │  │  │  ├─ test_randomstate_regression.py
   │     │  │  │  ├─ test_regression.py
   │     │  │  │  ├─ test_seed_sequence.py
   │     │  │  │  ├─ test_smoke.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ test_direct.cpython-311.pyc
   │     │  │  │     ├─ test_extending.cpython-311.pyc
   │     │  │  │     ├─ test_generator_mt19937.cpython-311.pyc
   │     │  │  │     ├─ test_generator_mt19937_regressions.cpython-311.pyc
   │     │  │  │     ├─ test_random.cpython-311.pyc
   │     │  │  │     ├─ test_randomstate.cpython-311.pyc
   │     │  │  │     ├─ test_randomstate_regression.cpython-311.pyc
   │     │  │  │     ├─ test_regression.cpython-311.pyc
   │     │  │  │     ├─ test_seed_sequence.cpython-311.pyc
   │     │  │  │     ├─ test_smoke.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ _bounded_integers.cp311-win_amd64.lib
   │     │  │  ├─ _bounded_integers.cp311-win_amd64.pyd
   │     │  │  ├─ _bounded_integers.pxd
   │     │  │  ├─ _bounded_integers.pyi
   │     │  │  ├─ _common.cp311-win_amd64.lib
   │     │  │  ├─ _common.cp311-win_amd64.pyd
   │     │  │  ├─ _common.pxd
   │     │  │  ├─ _common.pyi
   │     │  │  ├─ _examples
   │     │  │  │  ├─ cffi
   │     │  │  │  │  ├─ extending.py
   │     │  │  │  │  ├─ parse.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ extending.cpython-311.pyc
   │     │  │  │  │     └─ parse.cpython-311.pyc
   │     │  │  │  ├─ cython
   │     │  │  │  │  ├─ extending.pyx
   │     │  │  │  │  ├─ extending_distributions.pyx
   │     │  │  │  │  └─ meson.build
   │     │  │  │  └─ numba
   │     │  │  │     ├─ extending.py
   │     │  │  │     ├─ extending_distributions.py
   │     │  │  │     └─ __pycache__
   │     │  │  │        ├─ extending.cpython-311.pyc
   │     │  │  │        └─ extending_distributions.cpython-311.pyc
   │     │  │  ├─ _generator.cp311-win_amd64.lib
   │     │  │  ├─ _generator.cp311-win_amd64.pyd
   │     │  │  ├─ _generator.pyi
   │     │  │  ├─ _mt19937.cp311-win_amd64.lib
   │     │  │  ├─ _mt19937.cp311-win_amd64.pyd
   │     │  │  ├─ _mt19937.pyi
   │     │  │  ├─ _pcg64.cp311-win_amd64.lib
   │     │  │  ├─ _pcg64.cp311-win_amd64.pyd
   │     │  │  ├─ _pcg64.pyi
   │     │  │  ├─ _philox.cp311-win_amd64.lib
   │     │  │  ├─ _philox.cp311-win_amd64.pyd
   │     │  │  ├─ _philox.pyi
   │     │  │  ├─ _pickle.py
   │     │  │  ├─ _pickle.pyi
   │     │  │  ├─ _sfc64.cp311-win_amd64.lib
   │     │  │  ├─ _sfc64.cp311-win_amd64.pyd
   │     │  │  ├─ _sfc64.pyi
   │     │  │  ├─ __init__.pxd
   │     │  │  ├─ __init__.py
   │     │  │  ├─ __init__.pyi
   │     │  │  └─ __pycache__
   │     │  │     ├─ _pickle.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ rec
   │     │  │  ├─ __init__.py
   │     │  │  ├─ __init__.pyi
   │     │  │  └─ __pycache__
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ strings
   │     │  │  ├─ __init__.py
   │     │  │  ├─ __init__.pyi
   │     │  │  └─ __pycache__
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ testing
   │     │  │  ├─ overrides.py
   │     │  │  ├─ overrides.pyi
   │     │  │  ├─ print_coercion_tables.py
   │     │  │  ├─ print_coercion_tables.pyi
   │     │  │  ├─ tests
   │     │  │  │  ├─ test_utils.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ test_utils.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ _private
   │     │  │  │  ├─ extbuild.py
   │     │  │  │  ├─ extbuild.pyi
   │     │  │  │  ├─ utils.py
   │     │  │  │  ├─ utils.pyi
   │     │  │  │  ├─ __init__.py
   │     │  │  │  ├─ __init__.pyi
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ extbuild.cpython-311.pyc
   │     │  │  │     ├─ utils.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ __init__.py
   │     │  │  ├─ __init__.pyi
   │     │  │  └─ __pycache__
   │     │  │     ├─ overrides.cpython-311.pyc
   │     │  │     ├─ print_coercion_tables.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ tests
   │     │  │  ├─ test_configtool.py
   │     │  │  ├─ test_ctypeslib.py
   │     │  │  ├─ test_lazyloading.py
   │     │  │  ├─ test_matlib.py
   │     │  │  ├─ test_numpy_config.py
   │     │  │  ├─ test_numpy_version.py
   │     │  │  ├─ test_public_api.py
   │     │  │  ├─ test_reloading.py
   │     │  │  ├─ test_scripts.py
   │     │  │  ├─ test_warnings.py
   │     │  │  ├─ test__all__.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ test_configtool.cpython-311.pyc
   │     │  │     ├─ test_ctypeslib.cpython-311.pyc
   │     │  │     ├─ test_lazyloading.cpython-311.pyc
   │     │  │     ├─ test_matlib.cpython-311.pyc
   │     │  │     ├─ test_numpy_config.cpython-311.pyc
   │     │  │     ├─ test_numpy_version.cpython-311.pyc
   │     │  │     ├─ test_public_api.cpython-311.pyc
   │     │  │     ├─ test_reloading.cpython-311.pyc
   │     │  │     ├─ test_scripts.cpython-311.pyc
   │     │  │     ├─ test_warnings.cpython-311.pyc
   │     │  │     ├─ test__all__.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ typing
   │     │  │  ├─ mypy_plugin.py
   │     │  │  ├─ tests
   │     │  │  │  ├─ data
   │     │  │  │  │  ├─ fail
   │     │  │  │  │  │  ├─ arithmetic.pyi
   │     │  │  │  │  │  ├─ arrayprint.pyi
   │     │  │  │  │  │  ├─ arrayterator.pyi
   │     │  │  │  │  │  ├─ array_constructors.pyi
   │     │  │  │  │  │  ├─ array_like.pyi
   │     │  │  │  │  │  ├─ array_pad.pyi
   │     │  │  │  │  │  ├─ bitwise_ops.pyi
   │     │  │  │  │  │  ├─ char.pyi
   │     │  │  │  │  │  ├─ chararray.pyi
   │     │  │  │  │  │  ├─ comparisons.pyi
   │     │  │  │  │  │  ├─ constants.pyi
   │     │  │  │  │  │  ├─ datasource.pyi
   │     │  │  │  │  │  ├─ dtype.pyi
   │     │  │  │  │  │  ├─ einsumfunc.pyi
   │     │  │  │  │  │  ├─ flatiter.pyi
   │     │  │  │  │  │  ├─ fromnumeric.pyi
   │     │  │  │  │  │  ├─ histograms.pyi
   │     │  │  │  │  │  ├─ index_tricks.pyi
   │     │  │  │  │  │  ├─ lib_function_base.pyi
   │     │  │  │  │  │  ├─ lib_polynomial.pyi
   │     │  │  │  │  │  ├─ lib_utils.pyi
   │     │  │  │  │  │  ├─ lib_version.pyi
   │     │  │  │  │  │  ├─ linalg.pyi
   │     │  │  │  │  │  ├─ ma.pyi
   │     │  │  │  │  │  ├─ memmap.pyi
   │     │  │  │  │  │  ├─ modules.pyi
   │     │  │  │  │  │  ├─ multiarray.pyi
   │     │  │  │  │  │  ├─ ndarray.pyi
   │     │  │  │  │  │  ├─ ndarray_misc.pyi
   │     │  │  │  │  │  ├─ nditer.pyi
   │     │  │  │  │  │  ├─ nested_sequence.pyi
   │     │  │  │  │  │  ├─ npyio.pyi
   │     │  │  │  │  │  ├─ numerictypes.pyi
   │     │  │  │  │  │  ├─ random.pyi
   │     │  │  │  │  │  ├─ rec.pyi
   │     │  │  │  │  │  ├─ scalars.pyi
   │     │  │  │  │  │  ├─ shape.pyi
   │     │  │  │  │  │  ├─ shape_base.pyi
   │     │  │  │  │  │  ├─ stride_tricks.pyi
   │     │  │  │  │  │  ├─ strings.pyi
   │     │  │  │  │  │  ├─ testing.pyi
   │     │  │  │  │  │  ├─ twodim_base.pyi
   │     │  │  │  │  │  ├─ type_check.pyi
   │     │  │  │  │  │  ├─ ufunclike.pyi
   │     │  │  │  │  │  ├─ ufuncs.pyi
   │     │  │  │  │  │  ├─ ufunc_config.pyi
   │     │  │  │  │  │  └─ warnings_and_errors.pyi
   │     │  │  │  │  ├─ misc
   │     │  │  │  │  │  └─ extended_precision.pyi
   │     │  │  │  │  ├─ mypy.ini
   │     │  │  │  │  ├─ pass
   │     │  │  │  │  │  ├─ arithmetic.py
   │     │  │  │  │  │  ├─ arrayprint.py
   │     │  │  │  │  │  ├─ arrayterator.py
   │     │  │  │  │  │  ├─ array_constructors.py
   │     │  │  │  │  │  ├─ array_like.py
   │     │  │  │  │  │  ├─ bitwise_ops.py
   │     │  │  │  │  │  ├─ comparisons.py
   │     │  │  │  │  │  ├─ dtype.py
   │     │  │  │  │  │  ├─ einsumfunc.py
   │     │  │  │  │  │  ├─ flatiter.py
   │     │  │  │  │  │  ├─ fromnumeric.py
   │     │  │  │  │  │  ├─ index_tricks.py
   │     │  │  │  │  │  ├─ lib_user_array.py
   │     │  │  │  │  │  ├─ lib_utils.py
   │     │  │  │  │  │  ├─ lib_version.py
   │     │  │  │  │  │  ├─ literal.py
   │     │  │  │  │  │  ├─ ma.py
   │     │  │  │  │  │  ├─ mod.py
   │     │  │  │  │  │  ├─ modules.py
   │     │  │  │  │  │  ├─ multiarray.py
   │     │  │  │  │  │  ├─ ndarray_conversion.py
   │     │  │  │  │  │  ├─ ndarray_misc.py
   │     │  │  │  │  │  ├─ ndarray_shape_manipulation.py
   │     │  │  │  │  │  ├─ nditer.py
   │     │  │  │  │  │  ├─ numeric.py
   │     │  │  │  │  │  ├─ numerictypes.py
   │     │  │  │  │  │  ├─ random.py
   │     │  │  │  │  │  ├─ recfunctions.py
   │     │  │  │  │  │  ├─ scalars.py
   │     │  │  │  │  │  ├─ shape.py
   │     │  │  │  │  │  ├─ simple.py
   │     │  │  │  │  │  ├─ ufunclike.py
   │     │  │  │  │  │  ├─ ufuncs.py
   │     │  │  │  │  │  ├─ ufunc_config.py
   │     │  │  │  │  │  ├─ warnings_and_errors.py
   │     │  │  │  │  │  └─ __pycache__
   │     │  │  │  │  │     ├─ arithmetic.cpython-311.pyc
   │     │  │  │  │  │     ├─ arrayprint.cpython-311.pyc
   │     │  │  │  │  │     ├─ arrayterator.cpython-311.pyc
   │     │  │  │  │  │     ├─ array_constructors.cpython-311.pyc
   │     │  │  │  │  │     ├─ array_like.cpython-311.pyc
   │     │  │  │  │  │     ├─ bitwise_ops.cpython-311.pyc
   │     │  │  │  │  │     ├─ comparisons.cpython-311.pyc
   │     │  │  │  │  │     ├─ dtype.cpython-311.pyc
   │     │  │  │  │  │     ├─ einsumfunc.cpython-311.pyc
   │     │  │  │  │  │     ├─ flatiter.cpython-311.pyc
   │     │  │  │  │  │     ├─ fromnumeric.cpython-311.pyc
   │     │  │  │  │  │     ├─ index_tricks.cpython-311.pyc
   │     │  │  │  │  │     ├─ lib_user_array.cpython-311.pyc
   │     │  │  │  │  │     ├─ lib_utils.cpython-311.pyc
   │     │  │  │  │  │     ├─ lib_version.cpython-311.pyc
   │     │  │  │  │  │     ├─ literal.cpython-311.pyc
   │     │  │  │  │  │     ├─ ma.cpython-311.pyc
   │     │  │  │  │  │     ├─ mod.cpython-311.pyc
   │     │  │  │  │  │     ├─ modules.cpython-311.pyc
   │     │  │  │  │  │     ├─ multiarray.cpython-311.pyc
   │     │  │  │  │  │     ├─ ndarray_conversion.cpython-311.pyc
   │     │  │  │  │  │     ├─ ndarray_misc.cpython-311.pyc
   │     │  │  │  │  │     ├─ ndarray_shape_manipulation.cpython-311.pyc
   │     │  │  │  │  │     ├─ nditer.cpython-311.pyc
   │     │  │  │  │  │     ├─ numeric.cpython-311.pyc
   │     │  │  │  │  │     ├─ numerictypes.cpython-311.pyc
   │     │  │  │  │  │     ├─ random.cpython-311.pyc
   │     │  │  │  │  │     ├─ recfunctions.cpython-311.pyc
   │     │  │  │  │  │     ├─ scalars.cpython-311.pyc
   │     │  │  │  │  │     ├─ shape.cpython-311.pyc
   │     │  │  │  │  │     ├─ simple.cpython-311.pyc
   │     │  │  │  │  │     ├─ ufunclike.cpython-311.pyc
   │     │  │  │  │  │     ├─ ufuncs.cpython-311.pyc
   │     │  │  │  │  │     ├─ ufunc_config.cpython-311.pyc
   │     │  │  │  │  │     └─ warnings_and_errors.cpython-311.pyc
   │     │  │  │  │  └─ reveal
   │     │  │  │  │     ├─ arithmetic.pyi
   │     │  │  │  │     ├─ arraypad.pyi
   │     │  │  │  │     ├─ arrayprint.pyi
   │     │  │  │  │     ├─ arraysetops.pyi
   │     │  │  │  │     ├─ arrayterator.pyi
   │     │  │  │  │     ├─ array_api_info.pyi
   │     │  │  │  │     ├─ array_constructors.pyi
   │     │  │  │  │     ├─ bitwise_ops.pyi
   │     │  │  │  │     ├─ char.pyi
   │     │  │  │  │     ├─ chararray.pyi
   │     │  │  │  │     ├─ comparisons.pyi
   │     │  │  │  │     ├─ constants.pyi
   │     │  │  │  │     ├─ ctypeslib.pyi
   │     │  │  │  │     ├─ datasource.pyi
   │     │  │  │  │     ├─ dtype.pyi
   │     │  │  │  │     ├─ einsumfunc.pyi
   │     │  │  │  │     ├─ emath.pyi
   │     │  │  │  │     ├─ fft.pyi
   │     │  │  │  │     ├─ flatiter.pyi
   │     │  │  │  │     ├─ fromnumeric.pyi
   │     │  │  │  │     ├─ getlimits.pyi
   │     │  │  │  │     ├─ histograms.pyi
   │     │  │  │  │     ├─ index_tricks.pyi
   │     │  │  │  │     ├─ lib_function_base.pyi
   │     │  │  │  │     ├─ lib_polynomial.pyi
   │     │  │  │  │     ├─ lib_utils.pyi
   │     │  │  │  │     ├─ lib_version.pyi
   │     │  │  │  │     ├─ linalg.pyi
   │     │  │  │  │     ├─ ma.pyi
   │     │  │  │  │     ├─ matrix.pyi
   │     │  │  │  │     ├─ memmap.pyi
   │     │  │  │  │     ├─ mod.pyi
   │     │  │  │  │     ├─ modules.pyi
   │     │  │  │  │     ├─ multiarray.pyi
   │     │  │  │  │     ├─ nbit_base_example.pyi
   │     │  │  │  │     ├─ ndarray_assignability.pyi
   │     │  │  │  │     ├─ ndarray_conversion.pyi
   │     │  │  │  │     ├─ ndarray_misc.pyi
   │     │  │  │  │     ├─ ndarray_shape_manipulation.pyi
   │     │  │  │  │     ├─ nditer.pyi
   │     │  │  │  │     ├─ nested_sequence.pyi
   │     │  │  │  │     ├─ npyio.pyi
   │     │  │  │  │     ├─ numeric.pyi
   │     │  │  │  │     ├─ numerictypes.pyi
   │     │  │  │  │     ├─ polynomial_polybase.pyi
   │     │  │  │  │     ├─ polynomial_polyutils.pyi
   │     │  │  │  │     ├─ polynomial_series.pyi
   │     │  │  │  │     ├─ random.pyi
   │     │  │  │  │     ├─ rec.pyi
   │     │  │  │  │     ├─ scalars.pyi
   │     │  │  │  │     ├─ shape.pyi
   │     │  │  │  │     ├─ shape_base.pyi
   │     │  │  │  │     ├─ stride_tricks.pyi
   │     │  │  │  │     ├─ strings.pyi
   │     │  │  │  │     ├─ testing.pyi
   │     │  │  │  │     ├─ twodim_base.pyi
   │     │  │  │  │     ├─ type_check.pyi
   │     │  │  │  │     ├─ ufunclike.pyi
   │     │  │  │  │     ├─ ufuncs.pyi
   │     │  │  │  │     ├─ ufunc_config.pyi
   │     │  │  │  │     └─ warnings_and_errors.pyi
   │     │  │  │  ├─ test_isfile.py
   │     │  │  │  ├─ test_runtime.py
   │     │  │  │  ├─ test_typing.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ test_isfile.cpython-311.pyc
   │     │  │  │     ├─ test_runtime.cpython-311.pyc
   │     │  │  │     ├─ test_typing.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ __init__.py
   │     │  │  ├─ __init__.pyi
   │     │  │  └─ __pycache__
   │     │  │     ├─ mypy_plugin.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ version.py
   │     │  ├─ version.pyi
   │     │  ├─ _array_api_info.py
   │     │  ├─ _array_api_info.pyi
   │     │  ├─ _configtool.py
   │     │  ├─ _configtool.pyi
   │     │  ├─ _core
   │     │  │  ├─ arrayprint.py
   │     │  │  ├─ arrayprint.pyi
   │     │  │  ├─ cversions.py
   │     │  │  ├─ defchararray.py
   │     │  │  ├─ defchararray.pyi
   │     │  │  ├─ einsumfunc.py
   │     │  │  ├─ einsumfunc.pyi
   │     │  │  ├─ fromnumeric.py
   │     │  │  ├─ fromnumeric.pyi
   │     │  │  ├─ function_base.py
   │     │  │  ├─ function_base.pyi
   │     │  │  ├─ getlimits.py
   │     │  │  ├─ getlimits.pyi
   │     │  │  ├─ include
   │     │  │  │  └─ numpy
   │     │  │  │     ├─ arrayobject.h
   │     │  │  │     ├─ arrayscalars.h
   │     │  │  │     ├─ dtype_api.h
   │     │  │  │     ├─ halffloat.h
   │     │  │  │     ├─ ndarrayobject.h
   │     │  │  │     ├─ ndarraytypes.h
   │     │  │  │     ├─ npy_2_compat.h
   │     │  │  │     ├─ npy_2_complexcompat.h
   │     │  │  │     ├─ npy_3kcompat.h
   │     │  │  │     ├─ npy_common.h
   │     │  │  │     ├─ npy_cpu.h
   │     │  │  │     ├─ npy_endian.h
   │     │  │  │     ├─ npy_math.h
   │     │  │  │     ├─ npy_no_deprecated_api.h
   │     │  │  │     ├─ npy_os.h
   │     │  │  │     ├─ numpyconfig.h
   │     │  │  │     ├─ random
   │     │  │  │     │  ├─ bitgen.h
   │     │  │  │     │  ├─ distributions.h
   │     │  │  │     │  ├─ libdivide.h
   │     │  │  │     │  └─ LICENSE.txt
   │     │  │  │     ├─ ufuncobject.h
   │     │  │  │     ├─ utils.h
   │     │  │  │     ├─ _neighborhood_iterator_imp.h
   │     │  │  │     ├─ _numpyconfig.h
   │     │  │  │     ├─ _public_dtype_api_table.h
   │     │  │  │     ├─ __multiarray_api.c
   │     │  │  │     ├─ __multiarray_api.h
   │     │  │  │     ├─ __ufunc_api.c
   │     │  │  │     └─ __ufunc_api.h
   │     │  │  ├─ lib
   │     │  │  │  ├─ npy-pkg-config
   │     │  │  │  │  ├─ mlib.ini
   │     │  │  │  │  └─ npymath.ini
   │     │  │  │  ├─ npymath.lib
   │     │  │  │  └─ pkgconfig
   │     │  │  │     └─ numpy.pc
   │     │  │  ├─ memmap.py
   │     │  │  ├─ memmap.pyi
   │     │  │  ├─ multiarray.py
   │     │  │  ├─ multiarray.pyi
   │     │  │  ├─ numeric.py
   │     │  │  ├─ numeric.pyi
   │     │  │  ├─ numerictypes.py
   │     │  │  ├─ numerictypes.pyi
   │     │  │  ├─ overrides.py
   │     │  │  ├─ overrides.pyi
   │     │  │  ├─ printoptions.py
   │     │  │  ├─ printoptions.pyi
   │     │  │  ├─ records.py
   │     │  │  ├─ records.pyi
   │     │  │  ├─ shape_base.py
   │     │  │  ├─ shape_base.pyi
   │     │  │  ├─ strings.py
   │     │  │  ├─ strings.pyi
   │     │  │  ├─ tests
   │     │  │  │  ├─ data
   │     │  │  │  │  ├─ astype_copy.pkl
   │     │  │  │  │  ├─ generate_umath_validation_data.cpp
   │     │  │  │  │  ├─ recarray_from_file.fits
   │     │  │  │  │  ├─ umath-validation-set-arccos.csv
   │     │  │  │  │  ├─ umath-validation-set-arccosh.csv
   │     │  │  │  │  ├─ umath-validation-set-arcsin.csv
   │     │  │  │  │  ├─ umath-validation-set-arcsinh.csv
   │     │  │  │  │  ├─ umath-validation-set-arctan.csv
   │     │  │  │  │  ├─ umath-validation-set-arctanh.csv
   │     │  │  │  │  ├─ umath-validation-set-cbrt.csv
   │     │  │  │  │  ├─ umath-validation-set-cos.csv
   │     │  │  │  │  ├─ umath-validation-set-cosh.csv
   │     │  │  │  │  ├─ umath-validation-set-exp.csv
   │     │  │  │  │  ├─ umath-validation-set-exp2.csv
   │     │  │  │  │  ├─ umath-validation-set-expm1.csv
   │     │  │  │  │  ├─ umath-validation-set-log.csv
   │     │  │  │  │  ├─ umath-validation-set-log10.csv
   │     │  │  │  │  ├─ umath-validation-set-log1p.csv
   │     │  │  │  │  ├─ umath-validation-set-log2.csv
   │     │  │  │  │  ├─ umath-validation-set-README.txt
   │     │  │  │  │  ├─ umath-validation-set-sin.csv
   │     │  │  │  │  ├─ umath-validation-set-sinh.csv
   │     │  │  │  │  ├─ umath-validation-set-tan.csv
   │     │  │  │  │  └─ umath-validation-set-tanh.csv
   │     │  │  │  ├─ examples
   │     │  │  │  │  ├─ cython
   │     │  │  │  │  │  ├─ checks.pyx
   │     │  │  │  │  │  ├─ meson.build
   │     │  │  │  │  │  ├─ setup.py
   │     │  │  │  │  │  └─ __pycache__
   │     │  │  │  │  │     └─ setup.cpython-311.pyc
   │     │  │  │  │  └─ limited_api
   │     │  │  │  │     ├─ limited_api1.c
   │     │  │  │  │     ├─ limited_api2.pyx
   │     │  │  │  │     ├─ limited_api_latest.c
   │     │  │  │  │     ├─ meson.build
   │     │  │  │  │     ├─ setup.py
   │     │  │  │  │     └─ __pycache__
   │     │  │  │  │        └─ setup.cpython-311.pyc
   │     │  │  │  ├─ test_abc.py
   │     │  │  │  ├─ test_api.py
   │     │  │  │  ├─ test_argparse.py
   │     │  │  │  ├─ test_arraymethod.py
   │     │  │  │  ├─ test_arrayobject.py
   │     │  │  │  ├─ test_arrayprint.py
   │     │  │  │  ├─ test_array_api_info.py
   │     │  │  │  ├─ test_array_coercion.py
   │     │  │  │  ├─ test_array_interface.py
   │     │  │  │  ├─ test_casting_floatingpoint_errors.py
   │     │  │  │  ├─ test_casting_unittests.py
   │     │  │  │  ├─ test_conversion_utils.py
   │     │  │  │  ├─ test_cpu_dispatcher.py
   │     │  │  │  ├─ test_cpu_features.py
   │     │  │  │  ├─ test_custom_dtypes.py
   │     │  │  │  ├─ test_cython.py
   │     │  │  │  ├─ test_datetime.py
   │     │  │  │  ├─ test_defchararray.py
   │     │  │  │  ├─ test_deprecations.py
   │     │  │  │  ├─ test_dlpack.py
   │     │  │  │  ├─ test_dtype.py
   │     │  │  │  ├─ test_einsum.py
   │     │  │  │  ├─ test_errstate.py
   │     │  │  │  ├─ test_extint128.py
   │     │  │  │  ├─ test_finfo.py
   │     │  │  │  ├─ test_function_base.py
   │     │  │  │  ├─ test_getlimits.py
   │     │  │  │  ├─ test_half.py
   │     │  │  │  ├─ test_hashtable.py
   │     │  │  │  ├─ test_indexerrors.py
   │     │  │  │  ├─ test_indexing.py
   │     │  │  │  ├─ test_item_selection.py
   │     │  │  │  ├─ test_limited_api.py
   │     │  │  │  ├─ test_longdouble.py
   │     │  │  │  ├─ test_memmap.py
   │     │  │  │  ├─ test_mem_overlap.py
   │     │  │  │  ├─ test_mem_policy.py
   │     │  │  │  ├─ test_multiarray.py
   │     │  │  │  ├─ test_multiprocessing.py
   │     │  │  │  ├─ test_multithreading.py
   │     │  │  │  ├─ test_nditer.py
   │     │  │  │  ├─ test_nep50_promotions.py
   │     │  │  │  ├─ test_numeric.py
   │     │  │  │  ├─ test_numerictypes.py
   │     │  │  │  ├─ test_overrides.py
   │     │  │  │  ├─ test_print.py
   │     │  │  │  ├─ test_protocols.py
   │     │  │  │  ├─ test_records.py
   │     │  │  │  ├─ test_regression.py
   │     │  │  │  ├─ test_scalarbuffer.py
   │     │  │  │  ├─ test_scalarinherit.py
   │     │  │  │  ├─ test_scalarmath.py
   │     │  │  │  ├─ test_scalarprint.py
   │     │  │  │  ├─ test_scalar_ctors.py
   │     │  │  │  ├─ test_scalar_methods.py
   │     │  │  │  ├─ test_shape_base.py
   │     │  │  │  ├─ test_simd.py
   │     │  │  │  ├─ test_simd_module.py
   │     │  │  │  ├─ test_stringdtype.py
   │     │  │  │  ├─ test_strings.py
   │     │  │  │  ├─ test_ufunc.py
   │     │  │  │  ├─ test_umath.py
   │     │  │  │  ├─ test_umath_accuracy.py
   │     │  │  │  ├─ test_umath_complex.py
   │     │  │  │  ├─ test_unicode.py
   │     │  │  │  ├─ test__exceptions.py
   │     │  │  │  ├─ _locales.py
   │     │  │  │  ├─ _natype.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ test_abc.cpython-311.pyc
   │     │  │  │     ├─ test_api.cpython-311.pyc
   │     │  │  │     ├─ test_argparse.cpython-311.pyc
   │     │  │  │     ├─ test_arraymethod.cpython-311.pyc
   │     │  │  │     ├─ test_arrayobject.cpython-311.pyc
   │     │  │  │     ├─ test_arrayprint.cpython-311.pyc
   │     │  │  │     ├─ test_array_api_info.cpython-311.pyc
   │     │  │  │     ├─ test_array_coercion.cpython-311.pyc
   │     │  │  │     ├─ test_array_interface.cpython-311.pyc
   │     │  │  │     ├─ test_casting_floatingpoint_errors.cpython-311.pyc
   │     │  │  │     ├─ test_casting_unittests.cpython-311.pyc
   │     │  │  │     ├─ test_conversion_utils.cpython-311.pyc
   │     │  │  │     ├─ test_cpu_dispatcher.cpython-311.pyc
   │     │  │  │     ├─ test_cpu_features.cpython-311.pyc
   │     │  │  │     ├─ test_custom_dtypes.cpython-311.pyc
   │     │  │  │     ├─ test_cython.cpython-311.pyc
   │     │  │  │     ├─ test_datetime.cpython-311.pyc
   │     │  │  │     ├─ test_defchararray.cpython-311.pyc
   │     │  │  │     ├─ test_deprecations.cpython-311.pyc
   │     │  │  │     ├─ test_dlpack.cpython-311.pyc
   │     │  │  │     ├─ test_dtype.cpython-311.pyc
   │     │  │  │     ├─ test_einsum.cpython-311.pyc
   │     │  │  │     ├─ test_errstate.cpython-311.pyc
   │     │  │  │     ├─ test_extint128.cpython-311.pyc
   │     │  │  │     ├─ test_finfo.cpython-311.pyc
   │     │  │  │     ├─ test_function_base.cpython-311.pyc
   │     │  │  │     ├─ test_getlimits.cpython-311.pyc
   │     │  │  │     ├─ test_half.cpython-311.pyc
   │     │  │  │     ├─ test_hashtable.cpython-311.pyc
   │     │  │  │     ├─ test_indexerrors.cpython-311.pyc
   │     │  │  │     ├─ test_indexing.cpython-311.pyc
   │     │  │  │     ├─ test_item_selection.cpython-311.pyc
   │     │  │  │     ├─ test_limited_api.cpython-311.pyc
   │     │  │  │     ├─ test_longdouble.cpython-311.pyc
   │     │  │  │     ├─ test_memmap.cpython-311.pyc
   │     │  │  │     ├─ test_mem_overlap.cpython-311.pyc
   │     │  │  │     ├─ test_mem_policy.cpython-311.pyc
   │     │  │  │     ├─ test_multiarray.cpython-311.pyc
   │     │  │  │     ├─ test_multiprocessing.cpython-311.pyc
   │     │  │  │     ├─ test_multithreading.cpython-311.pyc
   │     │  │  │     ├─ test_nditer.cpython-311.pyc
   │     │  │  │     ├─ test_nep50_promotions.cpython-311.pyc
   │     │  │  │     ├─ test_numeric.cpython-311.pyc
   │     │  │  │     ├─ test_numerictypes.cpython-311.pyc
   │     │  │  │     ├─ test_overrides.cpython-311.pyc
   │     │  │  │     ├─ test_print.cpython-311.pyc
   │     │  │  │     ├─ test_protocols.cpython-311.pyc
   │     │  │  │     ├─ test_records.cpython-311.pyc
   │     │  │  │     ├─ test_regression.cpython-311.pyc
   │     │  │  │     ├─ test_scalarbuffer.cpython-311.pyc
   │     │  │  │     ├─ test_scalarinherit.cpython-311.pyc
   │     │  │  │     ├─ test_scalarmath.cpython-311.pyc
   │     │  │  │     ├─ test_scalarprint.cpython-311.pyc
   │     │  │  │     ├─ test_scalar_ctors.cpython-311.pyc
   │     │  │  │     ├─ test_scalar_methods.cpython-311.pyc
   │     │  │  │     ├─ test_shape_base.cpython-311.pyc
   │     │  │  │     ├─ test_simd.cpython-311.pyc
   │     │  │  │     ├─ test_simd_module.cpython-311.pyc
   │     │  │  │     ├─ test_stringdtype.cpython-311.pyc
   │     │  │  │     ├─ test_strings.cpython-311.pyc
   │     │  │  │     ├─ test_ufunc.cpython-311.pyc
   │     │  │  │     ├─ test_umath.cpython-311.pyc
   │     │  │  │     ├─ test_umath_accuracy.cpython-311.pyc
   │     │  │  │     ├─ test_umath_complex.cpython-311.pyc
   │     │  │  │     ├─ test_unicode.cpython-311.pyc
   │     │  │  │     ├─ test__exceptions.cpython-311.pyc
   │     │  │  │     ├─ _locales.cpython-311.pyc
   │     │  │  │     └─ _natype.cpython-311.pyc
   │     │  │  ├─ umath.py
   │     │  │  ├─ umath.pyi
   │     │  │  ├─ _add_newdocs.py
   │     │  │  ├─ _add_newdocs.pyi
   │     │  │  ├─ _add_newdocs_scalars.py
   │     │  │  ├─ _add_newdocs_scalars.pyi
   │     │  │  ├─ _asarray.py
   │     │  │  ├─ _asarray.pyi
   │     │  │  ├─ _dtype.py
   │     │  │  ├─ _dtype.pyi
   │     │  │  ├─ _dtype_ctypes.py
   │     │  │  ├─ _dtype_ctypes.pyi
   │     │  │  ├─ _exceptions.py
   │     │  │  ├─ _exceptions.pyi
   │     │  │  ├─ _internal.py
   │     │  │  ├─ _internal.pyi
   │     │  │  ├─ _methods.py
   │     │  │  ├─ _methods.pyi
   │     │  │  ├─ _multiarray_tests.cp311-win_amd64.lib
   │     │  │  ├─ _multiarray_tests.cp311-win_amd64.pyd
   │     │  │  ├─ _multiarray_umath.cp311-win_amd64.lib
   │     │  │  ├─ _multiarray_umath.cp311-win_amd64.pyd
   │     │  │  ├─ _operand_flag_tests.cp311-win_amd64.lib
   │     │  │  ├─ _operand_flag_tests.cp311-win_amd64.pyd
   │     │  │  ├─ _rational_tests.cp311-win_amd64.lib
   │     │  │  ├─ _rational_tests.cp311-win_amd64.pyd
   │     │  │  ├─ _simd.cp311-win_amd64.lib
   │     │  │  ├─ _simd.cp311-win_amd64.pyd
   │     │  │  ├─ _simd.pyi
   │     │  │  ├─ _string_helpers.py
   │     │  │  ├─ _string_helpers.pyi
   │     │  │  ├─ _struct_ufunc_tests.cp311-win_amd64.lib
   │     │  │  ├─ _struct_ufunc_tests.cp311-win_amd64.pyd
   │     │  │  ├─ _type_aliases.py
   │     │  │  ├─ _type_aliases.pyi
   │     │  │  ├─ _ufunc_config.py
   │     │  │  ├─ _ufunc_config.pyi
   │     │  │  ├─ _umath_tests.cp311-win_amd64.lib
   │     │  │  ├─ _umath_tests.cp311-win_amd64.pyd
   │     │  │  ├─ _umath_tests.pyi
   │     │  │  ├─ __init__.py
   │     │  │  ├─ __init__.pyi
   │     │  │  └─ __pycache__
   │     │  │     ├─ arrayprint.cpython-311.pyc
   │     │  │     ├─ cversions.cpython-311.pyc
   │     │  │     ├─ defchararray.cpython-311.pyc
   │     │  │     ├─ einsumfunc.cpython-311.pyc
   │     │  │     ├─ fromnumeric.cpython-311.pyc
   │     │  │     ├─ function_base.cpython-311.pyc
   │     │  │     ├─ getlimits.cpython-311.pyc
   │     │  │     ├─ memmap.cpython-311.pyc
   │     │  │     ├─ multiarray.cpython-311.pyc
   │     │  │     ├─ numeric.cpython-311.pyc
   │     │  │     ├─ numerictypes.cpython-311.pyc
   │     │  │     ├─ overrides.cpython-311.pyc
   │     │  │     ├─ printoptions.cpython-311.pyc
   │     │  │     ├─ records.cpython-311.pyc
   │     │  │     ├─ shape_base.cpython-311.pyc
   │     │  │     ├─ strings.cpython-311.pyc
   │     │  │     ├─ umath.cpython-311.pyc
   │     │  │     ├─ _add_newdocs.cpython-311.pyc
   │     │  │     ├─ _add_newdocs_scalars.cpython-311.pyc
   │     │  │     ├─ _asarray.cpython-311.pyc
   │     │  │     ├─ _dtype.cpython-311.pyc
   │     │  │     ├─ _dtype_ctypes.cpython-311.pyc
   │     │  │     ├─ _exceptions.cpython-311.pyc
   │     │  │     ├─ _internal.cpython-311.pyc
   │     │  │     ├─ _methods.cpython-311.pyc
   │     │  │     ├─ _string_helpers.cpython-311.pyc
   │     │  │     ├─ _type_aliases.cpython-311.pyc
   │     │  │     ├─ _ufunc_config.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ _distributor_init.py
   │     │  ├─ _distributor_init.pyi
   │     │  ├─ _expired_attrs_2_0.py
   │     │  ├─ _expired_attrs_2_0.pyi
   │     │  ├─ _globals.py
   │     │  ├─ _globals.pyi
   │     │  ├─ _pyinstaller
   │     │  │  ├─ hook-numpy.py
   │     │  │  ├─ hook-numpy.pyi
   │     │  │  ├─ tests
   │     │  │  │  ├─ pyinstaller-smoke.py
   │     │  │  │  ├─ test_pyinstaller.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ pyinstaller-smoke.cpython-311.pyc
   │     │  │  │     ├─ test_pyinstaller.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ __init__.py
   │     │  │  ├─ __init__.pyi
   │     │  │  └─ __pycache__
   │     │  │     ├─ hook-numpy.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ _pytesttester.py
   │     │  ├─ _pytesttester.pyi
   │     │  ├─ _typing
   │     │  │  ├─ _add_docstring.py
   │     │  │  ├─ _array_like.py
   │     │  │  ├─ _char_codes.py
   │     │  │  ├─ _dtype_like.py
   │     │  │  ├─ _extended_precision.py
   │     │  │  ├─ _nbit.py
   │     │  │  ├─ _nbit_base.py
   │     │  │  ├─ _nbit_base.pyi
   │     │  │  ├─ _nested_sequence.py
   │     │  │  ├─ _scalars.py
   │     │  │  ├─ _shape.py
   │     │  │  ├─ _ufunc.py
   │     │  │  ├─ _ufunc.pyi
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ _add_docstring.cpython-311.pyc
   │     │  │     ├─ _array_like.cpython-311.pyc
   │     │  │     ├─ _char_codes.cpython-311.pyc
   │     │  │     ├─ _dtype_like.cpython-311.pyc
   │     │  │     ├─ _extended_precision.cpython-311.pyc
   │     │  │     ├─ _nbit.cpython-311.pyc
   │     │  │     ├─ _nbit_base.cpython-311.pyc
   │     │  │     ├─ _nested_sequence.cpython-311.pyc
   │     │  │     ├─ _scalars.cpython-311.pyc
   │     │  │     ├─ _shape.cpython-311.pyc
   │     │  │     ├─ _ufunc.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ _utils
   │     │  │  ├─ _convertions.py
   │     │  │  ├─ _convertions.pyi
   │     │  │  ├─ _inspect.py
   │     │  │  ├─ _inspect.pyi
   │     │  │  ├─ _pep440.py
   │     │  │  ├─ _pep440.pyi
   │     │  │  ├─ __init__.py
   │     │  │  ├─ __init__.pyi
   │     │  │  └─ __pycache__
   │     │  │     ├─ _convertions.cpython-311.pyc
   │     │  │     ├─ _inspect.cpython-311.pyc
   │     │  │     ├─ _pep440.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ __config__.py
   │     │  ├─ __config__.pyi
   │     │  ├─ __init__.cython-30.pxd
   │     │  ├─ __init__.pxd
   │     │  ├─ __init__.py
   │     │  ├─ __init__.pyi
   │     │  └─ __pycache__
   │     │     ├─ conftest.cpython-311.pyc
   │     │     ├─ dtypes.cpython-311.pyc
   │     │     ├─ exceptions.cpython-311.pyc
   │     │     ├─ matlib.cpython-311.pyc
   │     │     ├─ version.cpython-311.pyc
   │     │     ├─ _array_api_info.cpython-311.pyc
   │     │     ├─ _configtool.cpython-311.pyc
   │     │     ├─ _distributor_init.cpython-311.pyc
   │     │     ├─ _expired_attrs_2_0.cpython-311.pyc
   │     │     ├─ _globals.cpython-311.pyc
   │     │     ├─ _pytesttester.cpython-311.pyc
   │     │     ├─ __config__.cpython-311.pyc
   │     │     └─ __init__.cpython-311.pyc
   │     ├─ numpy-2.4.4.dist-info
   │     │  ├─ DELVEWHEEL
   │     │  ├─ entry_points.txt
   │     │  ├─ INSTALLER
   │     │  ├─ licenses
   │     │  │  ├─ LICENSE.txt
   │     │  │  └─ numpy
   │     │  │     ├─ fft
   │     │  │     │  └─ pocketfft
   │     │  │     │     └─ LICENSE.md
   │     │  │     ├─ linalg
   │     │  │     │  └─ lapack_lite
   │     │  │     │     └─ LICENSE.txt
   │     │  │     ├─ ma
   │     │  │     │  └─ LICENSE
   │     │  │     ├─ random
   │     │  │     │  ├─ LICENSE.md
   │     │  │     │  └─ src
   │     │  │     │     ├─ distributions
   │     │  │     │     │  └─ LICENSE.md
   │     │  │     │     ├─ mt19937
   │     │  │     │     │  └─ LICENSE.md
   │     │  │     │     ├─ pcg64
   │     │  │     │     │  └─ LICENSE.md
   │     │  │     │     ├─ philox
   │     │  │     │     │  └─ LICENSE.md
   │     │  │     │     ├─ sfc64
   │     │  │     │     │  └─ LICENSE.md
   │     │  │     │     └─ splitmix64
   │     │  │     │        └─ LICENSE.md
   │     │  │     └─ _core
   │     │  │        ├─ include
   │     │  │        │  └─ numpy
   │     │  │        │     └─ libdivide
   │     │  │        │        └─ LICENSE.txt
   │     │  │        └─ src
   │     │  │           ├─ common
   │     │  │           │  └─ pythoncapi-compat
   │     │  │           │     └─ COPYING
   │     │  │           ├─ highway
   │     │  │           │  └─ LICENSE
   │     │  │           ├─ multiarray
   │     │  │           │  └─ dragon4_LICENSE.txt
   │     │  │           ├─ npysort
   │     │  │           │  └─ x86-simd-sort
   │     │  │           │     └─ LICENSE.md
   │     │  │           └─ umath
   │     │  │              └─ svml
   │     │  │                 └─ LICENSE
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  └─ WHEEL
   │     ├─ numpy.libs
   │     │  ├─ libscipy_openblas64_-63c857e738469261263c764a36be9436.dll
   │     │  └─ msvcp140-a4c2229bdc2a2a630acdc095b4d86008.dll
   │     ├─ oauthlib
   │     │  ├─ common.py
   │     │  ├─ oauth1
   │     │  │  ├─ rfc5849
   │     │  │  │  ├─ endpoints
   │     │  │  │  │  ├─ access_token.py
   │     │  │  │  │  ├─ authorization.py
   │     │  │  │  │  ├─ base.py
   │     │  │  │  │  ├─ pre_configured.py
   │     │  │  │  │  ├─ request_token.py
   │     │  │  │  │  ├─ resource.py
   │     │  │  │  │  ├─ signature_only.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ access_token.cpython-311.pyc
   │     │  │  │  │     ├─ authorization.cpython-311.pyc
   │     │  │  │  │     ├─ base.cpython-311.pyc
   │     │  │  │  │     ├─ pre_configured.cpython-311.pyc
   │     │  │  │  │     ├─ request_token.cpython-311.pyc
   │     │  │  │  │     ├─ resource.cpython-311.pyc
   │     │  │  │  │     ├─ signature_only.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ errors.py
   │     │  │  │  ├─ parameters.py
   │     │  │  │  ├─ request_validator.py
   │     │  │  │  ├─ signature.py
   │     │  │  │  ├─ utils.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ errors.cpython-311.pyc
   │     │  │  │     ├─ parameters.cpython-311.pyc
   │     │  │  │     ├─ request_validator.cpython-311.pyc
   │     │  │  │     ├─ signature.cpython-311.pyc
   │     │  │  │     ├─ utils.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ oauth2
   │     │  │  ├─ rfc6749
   │     │  │  │  ├─ clients
   │     │  │  │  │  ├─ backend_application.py
   │     │  │  │  │  ├─ base.py
   │     │  │  │  │  ├─ legacy_application.py
   │     │  │  │  │  ├─ mobile_application.py
   │     │  │  │  │  ├─ service_application.py
   │     │  │  │  │  ├─ web_application.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ backend_application.cpython-311.pyc
   │     │  │  │  │     ├─ base.cpython-311.pyc
   │     │  │  │  │     ├─ legacy_application.cpython-311.pyc
   │     │  │  │  │     ├─ mobile_application.cpython-311.pyc
   │     │  │  │  │     ├─ service_application.cpython-311.pyc
   │     │  │  │  │     ├─ web_application.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ endpoints
   │     │  │  │  │  ├─ authorization.py
   │     │  │  │  │  ├─ base.py
   │     │  │  │  │  ├─ introspect.py
   │     │  │  │  │  ├─ metadata.py
   │     │  │  │  │  ├─ pre_configured.py
   │     │  │  │  │  ├─ resource.py
   │     │  │  │  │  ├─ revocation.py
   │     │  │  │  │  ├─ token.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ authorization.cpython-311.pyc
   │     │  │  │  │     ├─ base.cpython-311.pyc
   │     │  │  │  │     ├─ introspect.cpython-311.pyc
   │     │  │  │  │     ├─ metadata.cpython-311.pyc
   │     │  │  │  │     ├─ pre_configured.cpython-311.pyc
   │     │  │  │  │     ├─ resource.cpython-311.pyc
   │     │  │  │  │     ├─ revocation.cpython-311.pyc
   │     │  │  │  │     ├─ token.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ errors.py
   │     │  │  │  ├─ grant_types
   │     │  │  │  │  ├─ authorization_code.py
   │     │  │  │  │  ├─ base.py
   │     │  │  │  │  ├─ client_credentials.py
   │     │  │  │  │  ├─ implicit.py
   │     │  │  │  │  ├─ refresh_token.py
   │     │  │  │  │  ├─ resource_owner_password_credentials.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ authorization_code.cpython-311.pyc
   │     │  │  │  │     ├─ base.cpython-311.pyc
   │     │  │  │  │     ├─ client_credentials.cpython-311.pyc
   │     │  │  │  │     ├─ implicit.cpython-311.pyc
   │     │  │  │  │     ├─ refresh_token.cpython-311.pyc
   │     │  │  │  │     ├─ resource_owner_password_credentials.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ parameters.py
   │     │  │  │  ├─ request_validator.py
   │     │  │  │  ├─ tokens.py
   │     │  │  │  ├─ utils.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ errors.cpython-311.pyc
   │     │  │  │     ├─ parameters.cpython-311.pyc
   │     │  │  │     ├─ request_validator.cpython-311.pyc
   │     │  │  │     ├─ tokens.cpython-311.pyc
   │     │  │  │     ├─ utils.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ rfc8628
   │     │  │  │  ├─ clients
   │     │  │  │  │  ├─ device.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ device.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ endpoints
   │     │  │  │  │  ├─ device_authorization.py
   │     │  │  │  │  ├─ pre_configured.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ device_authorization.cpython-311.pyc
   │     │  │  │  │     ├─ pre_configured.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ errors.py
   │     │  │  │  ├─ grant_types
   │     │  │  │  │  ├─ device_code.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ device_code.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ request_validator.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ errors.cpython-311.pyc
   │     │  │  │     ├─ request_validator.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ openid
   │     │  │  ├─ connect
   │     │  │  │  ├─ core
   │     │  │  │  │  ├─ endpoints
   │     │  │  │  │  │  ├─ pre_configured.py
   │     │  │  │  │  │  ├─ userinfo.py
   │     │  │  │  │  │  ├─ __init__.py
   │     │  │  │  │  │  └─ __pycache__
   │     │  │  │  │  │     ├─ pre_configured.cpython-311.pyc
   │     │  │  │  │  │     ├─ userinfo.cpython-311.pyc
   │     │  │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  │  ├─ exceptions.py
   │     │  │  │  │  ├─ grant_types
   │     │  │  │  │  │  ├─ authorization_code.py
   │     │  │  │  │  │  ├─ base.py
   │     │  │  │  │  │  ├─ dispatchers.py
   │     │  │  │  │  │  ├─ hybrid.py
   │     │  │  │  │  │  ├─ implicit.py
   │     │  │  │  │  │  ├─ refresh_token.py
   │     │  │  │  │  │  ├─ __init__.py
   │     │  │  │  │  │  └─ __pycache__
   │     │  │  │  │  │     ├─ authorization_code.cpython-311.pyc
   │     │  │  │  │  │     ├─ base.cpython-311.pyc
   │     │  │  │  │  │     ├─ dispatchers.cpython-311.pyc
   │     │  │  │  │  │     ├─ hybrid.cpython-311.pyc
   │     │  │  │  │  │     ├─ implicit.cpython-311.pyc
   │     │  │  │  │  │     ├─ refresh_token.cpython-311.pyc
   │     │  │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  │  ├─ request_validator.py
   │     │  │  │  │  ├─ tokens.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ exceptions.cpython-311.pyc
   │     │  │  │  │     ├─ request_validator.cpython-311.pyc
   │     │  │  │  │     ├─ tokens.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ signals.py
   │     │  ├─ uri_validate.py
   │     │  ├─ __init__.py
   │     │  └─ __pycache__
   │     │     ├─ common.cpython-311.pyc
   │     │     ├─ signals.cpython-311.pyc
   │     │     ├─ uri_validate.cpython-311.pyc
   │     │     └─ __init__.cpython-311.pyc
   │     ├─ oauthlib-3.3.1.dist-info
   │     │  ├─ INSTALLER
   │     │  ├─ licenses
   │     │  │  └─ LICENSE
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  ├─ top_level.txt
   │     │  └─ WHEEL
   │     ├─ onnxruntime
   │     │  ├─ backend
   │     │  │  ├─ backend.py
   │     │  │  ├─ backend_rep.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ backend.cpython-311.pyc
   │     │  │     ├─ backend_rep.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ capi
   │     │  │  ├─ build_and_package_info.py
   │     │  │  ├─ convert_npz_to_onnx_adapter.py
   │     │  │  ├─ onnxruntime.dll
   │     │  │  ├─ onnxruntime_collect_build_info.py
   │     │  │  ├─ onnxruntime_inference_collection.py
   │     │  │  ├─ onnxruntime_providers_shared.dll
   │     │  │  ├─ onnxruntime_pybind11_state.pyd
   │     │  │  ├─ onnxruntime_validation.py
   │     │  │  ├─ version_info.py
   │     │  │  ├─ _ld_preload.py
   │     │  │  ├─ _pybind_state.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ build_and_package_info.cpython-311.pyc
   │     │  │     ├─ convert_npz_to_onnx_adapter.cpython-311.pyc
   │     │  │     ├─ onnxruntime_collect_build_info.cpython-311.pyc
   │     │  │     ├─ onnxruntime_inference_collection.cpython-311.pyc
   │     │  │     ├─ onnxruntime_validation.cpython-311.pyc
   │     │  │     ├─ version_info.cpython-311.pyc
   │     │  │     ├─ _ld_preload.cpython-311.pyc
   │     │  │     ├─ _pybind_state.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ datasets
   │     │  │  ├─ logreg_iris.onnx
   │     │  │  ├─ mul_1.onnx
   │     │  │  ├─ sigmoid.onnx
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ LICENSE
   │     │  ├─ Privacy.md
   │     │  ├─ quantization
   │     │  │  ├─ base_quantizer.py
   │     │  │  ├─ calibrate.py
   │     │  │  ├─ CalTableFlatBuffers
   │     │  │  │  ├─ KeyValue.py
   │     │  │  │  ├─ TrtTable.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ KeyValue.cpython-311.pyc
   │     │  │  │     ├─ TrtTable.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ execution_providers
   │     │  │  │  └─ qnn
   │     │  │  │     ├─ fusion_lpnorm.py
   │     │  │  │     ├─ fusion_spacetodepth.py
   │     │  │  │     ├─ mixed_precision_overrides_utils.py
   │     │  │  │     ├─ preprocess.py
   │     │  │  │     ├─ quant_config.py
   │     │  │  │     ├─ __init__.py
   │     │  │  │     └─ __pycache__
   │     │  │  │        ├─ fusion_lpnorm.cpython-311.pyc
   │     │  │  │        ├─ fusion_spacetodepth.cpython-311.pyc
   │     │  │  │        ├─ mixed_precision_overrides_utils.cpython-311.pyc
   │     │  │  │        ├─ preprocess.cpython-311.pyc
   │     │  │  │        ├─ quant_config.cpython-311.pyc
   │     │  │  │        └─ __init__.cpython-311.pyc
   │     │  │  ├─ fusions
   │     │  │  │  ├─ fusion.py
   │     │  │  │  ├─ fusion_gelu.py
   │     │  │  │  ├─ fusion_layernorm.py
   │     │  │  │  ├─ replace_upsample_with_resize.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ fusion.cpython-311.pyc
   │     │  │  │     ├─ fusion_gelu.cpython-311.pyc
   │     │  │  │     ├─ fusion_layernorm.cpython-311.pyc
   │     │  │  │     ├─ replace_upsample_with_resize.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ matmul_bnb4_quantizer.py
   │     │  │  ├─ matmul_nbits_quantizer.py
   │     │  │  ├─ neural_compressor
   │     │  │  │  ├─ onnx_model.py
   │     │  │  │  ├─ util.py
   │     │  │  │  ├─ weight_only.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ onnx_model.cpython-311.pyc
   │     │  │  │     ├─ util.cpython-311.pyc
   │     │  │  │     ├─ weight_only.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ onnx_model.py
   │     │  │  ├─ onnx_quantizer.py
   │     │  │  ├─ operators
   │     │  │  │  ├─ activation.py
   │     │  │  │  ├─ argmax.py
   │     │  │  │  ├─ attention.py
   │     │  │  │  ├─ base_operator.py
   │     │  │  │  ├─ binary_op.py
   │     │  │  │  ├─ concat.py
   │     │  │  │  ├─ conv.py
   │     │  │  │  ├─ direct_q8.py
   │     │  │  │  ├─ embed_layernorm.py
   │     │  │  │  ├─ gather.py
   │     │  │  │  ├─ gavgpool.py
   │     │  │  │  ├─ gemm.py
   │     │  │  │  ├─ lstm.py
   │     │  │  │  ├─ matmul.py
   │     │  │  │  ├─ maxpool.py
   │     │  │  │  ├─ norm.py
   │     │  │  │  ├─ pad.py
   │     │  │  │  ├─ pooling.py
   │     │  │  │  ├─ qdq_base_operator.py
   │     │  │  │  ├─ resize.py
   │     │  │  │  ├─ softmax.py
   │     │  │  │  ├─ split.py
   │     │  │  │  ├─ where.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ activation.cpython-311.pyc
   │     │  │  │     ├─ argmax.cpython-311.pyc
   │     │  │  │     ├─ attention.cpython-311.pyc
   │     │  │  │     ├─ base_operator.cpython-311.pyc
   │     │  │  │     ├─ binary_op.cpython-311.pyc
   │     │  │  │     ├─ concat.cpython-311.pyc
   │     │  │  │     ├─ conv.cpython-311.pyc
   │     │  │  │     ├─ direct_q8.cpython-311.pyc
   │     │  │  │     ├─ embed_layernorm.cpython-311.pyc
   │     │  │  │     ├─ gather.cpython-311.pyc
   │     │  │  │     ├─ gavgpool.cpython-311.pyc
   │     │  │  │     ├─ gemm.cpython-311.pyc
   │     │  │  │     ├─ lstm.cpython-311.pyc
   │     │  │  │     ├─ matmul.cpython-311.pyc
   │     │  │  │     ├─ maxpool.cpython-311.pyc
   │     │  │  │     ├─ norm.cpython-311.pyc
   │     │  │  │     ├─ pad.cpython-311.pyc
   │     │  │  │     ├─ pooling.cpython-311.pyc
   │     │  │  │     ├─ qdq_base_operator.cpython-311.pyc
   │     │  │  │     ├─ resize.cpython-311.pyc
   │     │  │  │     ├─ softmax.cpython-311.pyc
   │     │  │  │     ├─ split.cpython-311.pyc
   │     │  │  │     ├─ where.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ preprocess.py
   │     │  │  ├─ qdq_loss_debug.py
   │     │  │  ├─ qdq_quantizer.py
   │     │  │  ├─ quantize.py
   │     │  │  ├─ quant_utils.py
   │     │  │  ├─ registry.py
   │     │  │  ├─ shape_inference.py
   │     │  │  ├─ static_quantize_runner.py
   │     │  │  ├─ tensor_quant_overrides.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ base_quantizer.cpython-311.pyc
   │     │  │     ├─ calibrate.cpython-311.pyc
   │     │  │     ├─ matmul_bnb4_quantizer.cpython-311.pyc
   │     │  │     ├─ matmul_nbits_quantizer.cpython-311.pyc
   │     │  │     ├─ onnx_model.cpython-311.pyc
   │     │  │     ├─ onnx_quantizer.cpython-311.pyc
   │     │  │     ├─ preprocess.cpython-311.pyc
   │     │  │     ├─ qdq_loss_debug.cpython-311.pyc
   │     │  │     ├─ qdq_quantizer.cpython-311.pyc
   │     │  │     ├─ quantize.cpython-311.pyc
   │     │  │     ├─ quant_utils.cpython-311.pyc
   │     │  │     ├─ registry.cpython-311.pyc
   │     │  │     ├─ shape_inference.cpython-311.pyc
   │     │  │     ├─ static_quantize_runner.cpython-311.pyc
   │     │  │     ├─ tensor_quant_overrides.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ ThirdPartyNotices.txt
   │     │  ├─ tools
   │     │  │  ├─ check_onnx_model_mobile_usability.py
   │     │  │  ├─ convert_onnx_models_to_ort.py
   │     │  │  ├─ file_utils.py
   │     │  │  ├─ logger.py
   │     │  │  ├─ make_dynamic_shape_fixed.py
   │     │  │  ├─ mobile_helpers
   │     │  │  │  ├─ coreml_supported_mlprogram_ops.md
   │     │  │  │  ├─ coreml_supported_neuralnetwork_ops.md
   │     │  │  │  ├─ nnapi_supported_ops.md
   │     │  │  │  ├─ usability_checker.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ usability_checker.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ offline_tuning.py
   │     │  │  ├─ onnxruntime_test.py
   │     │  │  ├─ onnx_model_utils.py
   │     │  │  ├─ onnx_randomizer.py
   │     │  │  ├─ optimize_onnx_model.py
   │     │  │  ├─ ort_format_model
   │     │  │  │  ├─ operator_type_usage_processors.py
   │     │  │  │  ├─ ort_flatbuffers_py
   │     │  │  │  │  ├─ fbs
   │     │  │  │  │  │  ├─ ArgType.py
   │     │  │  │  │  │  ├─ ArgTypeAndIndex.py
   │     │  │  │  │  │  ├─ Attribute.py
   │     │  │  │  │  │  ├─ AttributeType.py
   │     │  │  │  │  │  ├─ Checkpoint.py
   │     │  │  │  │  │  ├─ DeprecatedKernelCreateInfos.py
   │     │  │  │  │  │  ├─ DeprecatedNodeIndexAndKernelDefHash.py
   │     │  │  │  │  │  ├─ DeprecatedSessionState.py
   │     │  │  │  │  │  ├─ DeprecatedSubGraphSessionState.py
   │     │  │  │  │  │  ├─ Dimension.py
   │     │  │  │  │  │  ├─ DimensionValue.py
   │     │  │  │  │  │  ├─ DimensionValueType.py
   │     │  │  │  │  │  ├─ EdgeEnd.py
   │     │  │  │  │  │  ├─ FloatProperty.py
   │     │  │  │  │  │  ├─ Graph.py
   │     │  │  │  │  │  ├─ InferenceSession.py
   │     │  │  │  │  │  ├─ IntProperty.py
   │     │  │  │  │  │  ├─ KernelTypeStrArgsEntry.py
   │     │  │  │  │  │  ├─ KernelTypeStrResolver.py
   │     │  │  │  │  │  ├─ MapType.py
   │     │  │  │  │  │  ├─ Model.py
   │     │  │  │  │  │  ├─ ModuleState.py
   │     │  │  │  │  │  ├─ Node.py
   │     │  │  │  │  │  ├─ NodeEdge.py
   │     │  │  │  │  │  ├─ NodesToOptimizeIndices.py
   │     │  │  │  │  │  ├─ NodeType.py
   │     │  │  │  │  │  ├─ OperatorSetId.py
   │     │  │  │  │  │  ├─ OpIdKernelTypeStrArgsEntry.py
   │     │  │  │  │  │  ├─ OptimizerGroup.py
   │     │  │  │  │  │  ├─ ParameterOptimizerState.py
   │     │  │  │  │  │  ├─ PropertyBag.py
   │     │  │  │  │  │  ├─ RuntimeOptimizationRecord.py
   │     │  │  │  │  │  ├─ RuntimeOptimizationRecordContainerEntry.py
   │     │  │  │  │  │  ├─ RuntimeOptimizations.py
   │     │  │  │  │  │  ├─ SequenceType.py
   │     │  │  │  │  │  ├─ Shape.py
   │     │  │  │  │  │  ├─ SparseTensor.py
   │     │  │  │  │  │  ├─ StringProperty.py
   │     │  │  │  │  │  ├─ StringStringEntry.py
   │     │  │  │  │  │  ├─ Tensor.py
   │     │  │  │  │  │  ├─ TensorDataType.py
   │     │  │  │  │  │  ├─ TensorTypeAndShape.py
   │     │  │  │  │  │  ├─ TypeInfo.py
   │     │  │  │  │  │  ├─ TypeInfoValue.py
   │     │  │  │  │  │  ├─ ValueInfo.py
   │     │  │  │  │  │  ├─ __init__.py
   │     │  │  │  │  │  └─ __pycache__
   │     │  │  │  │  │     ├─ ArgType.cpython-311.pyc
   │     │  │  │  │  │     ├─ ArgTypeAndIndex.cpython-311.pyc
   │     │  │  │  │  │     ├─ Attribute.cpython-311.pyc
   │     │  │  │  │  │     ├─ AttributeType.cpython-311.pyc
   │     │  │  │  │  │     ├─ Checkpoint.cpython-311.pyc
   │     │  │  │  │  │     ├─ DeprecatedKernelCreateInfos.cpython-311.pyc
   │     │  │  │  │  │     ├─ DeprecatedNodeIndexAndKernelDefHash.cpython-311.pyc
   │     │  │  │  │  │     ├─ DeprecatedSessionState.cpython-311.pyc
   │     │  │  │  │  │     ├─ DeprecatedSubGraphSessionState.cpython-311.pyc
   │     │  │  │  │  │     ├─ Dimension.cpython-311.pyc
   │     │  │  │  │  │     ├─ DimensionValue.cpython-311.pyc
   │     │  │  │  │  │     ├─ DimensionValueType.cpython-311.pyc
   │     │  │  │  │  │     ├─ EdgeEnd.cpython-311.pyc
   │     │  │  │  │  │     ├─ FloatProperty.cpython-311.pyc
   │     │  │  │  │  │     ├─ Graph.cpython-311.pyc
   │     │  │  │  │  │     ├─ InferenceSession.cpython-311.pyc
   │     │  │  │  │  │     ├─ IntProperty.cpython-311.pyc
   │     │  │  │  │  │     ├─ KernelTypeStrArgsEntry.cpython-311.pyc
   │     │  │  │  │  │     ├─ KernelTypeStrResolver.cpython-311.pyc
   │     │  │  │  │  │     ├─ MapType.cpython-311.pyc
   │     │  │  │  │  │     ├─ Model.cpython-311.pyc
   │     │  │  │  │  │     ├─ ModuleState.cpython-311.pyc
   │     │  │  │  │  │     ├─ Node.cpython-311.pyc
   │     │  │  │  │  │     ├─ NodeEdge.cpython-311.pyc
   │     │  │  │  │  │     ├─ NodesToOptimizeIndices.cpython-311.pyc
   │     │  │  │  │  │     ├─ NodeType.cpython-311.pyc
   │     │  │  │  │  │     ├─ OperatorSetId.cpython-311.pyc
   │     │  │  │  │  │     ├─ OpIdKernelTypeStrArgsEntry.cpython-311.pyc
   │     │  │  │  │  │     ├─ OptimizerGroup.cpython-311.pyc
   │     │  │  │  │  │     ├─ ParameterOptimizerState.cpython-311.pyc
   │     │  │  │  │  │     ├─ PropertyBag.cpython-311.pyc
   │     │  │  │  │  │     ├─ RuntimeOptimizationRecord.cpython-311.pyc
   │     │  │  │  │  │     ├─ RuntimeOptimizationRecordContainerEntry.cpython-311.pyc
   │     │  │  │  │  │     ├─ RuntimeOptimizations.cpython-311.pyc
   │     │  │  │  │  │     ├─ SequenceType.cpython-311.pyc
   │     │  │  │  │  │     ├─ Shape.cpython-311.pyc
   │     │  │  │  │  │     ├─ SparseTensor.cpython-311.pyc
   │     │  │  │  │  │     ├─ StringProperty.cpython-311.pyc
   │     │  │  │  │  │     ├─ StringStringEntry.cpython-311.pyc
   │     │  │  │  │  │     ├─ Tensor.cpython-311.pyc
   │     │  │  │  │  │     ├─ TensorDataType.cpython-311.pyc
   │     │  │  │  │  │     ├─ TensorTypeAndShape.cpython-311.pyc
   │     │  │  │  │  │     ├─ TypeInfo.cpython-311.pyc
   │     │  │  │  │  │     ├─ TypeInfoValue.cpython-311.pyc
   │     │  │  │  │  │     ├─ ValueInfo.cpython-311.pyc
   │     │  │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ ort_model_processor.py
   │     │  │  │  ├─ types.py
   │     │  │  │  ├─ utils.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ operator_type_usage_processors.cpython-311.pyc
   │     │  │  │     ├─ ort_model_processor.cpython-311.pyc
   │     │  │  │     ├─ types.cpython-311.pyc
   │     │  │  │     ├─ utils.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ pytorch_export_contrib_ops.py
   │     │  │  ├─ pytorch_export_helpers.py
   │     │  │  ├─ qdq_helpers
   │     │  │  │  ├─ optimize_qdq_model.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ optimize_qdq_model.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ qnn
   │     │  │  │  ├─ add_trans_cast.py
   │     │  │  │  ├─ gen_qnn_ctx_onnx_model.py
   │     │  │  │  ├─ preprocess.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ add_trans_cast.cpython-311.pyc
   │     │  │  │     ├─ gen_qnn_ctx_onnx_model.cpython-311.pyc
   │     │  │  │     └─ preprocess.cpython-311.pyc
   │     │  │  ├─ reduced_build_config_parser.py
   │     │  │  ├─ remove_initializer_from_input.py
   │     │  │  ├─ symbolic_shape_infer.py
   │     │  │  ├─ update_onnx_opset.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ check_onnx_model_mobile_usability.cpython-311.pyc
   │     │  │     ├─ convert_onnx_models_to_ort.cpython-311.pyc
   │     │  │     ├─ file_utils.cpython-311.pyc
   │     │  │     ├─ logger.cpython-311.pyc
   │     │  │     ├─ make_dynamic_shape_fixed.cpython-311.pyc
   │     │  │     ├─ offline_tuning.cpython-311.pyc
   │     │  │     ├─ onnxruntime_test.cpython-311.pyc
   │     │  │     ├─ onnx_model_utils.cpython-311.pyc
   │     │  │     ├─ onnx_randomizer.cpython-311.pyc
   │     │  │     ├─ optimize_onnx_model.cpython-311.pyc
   │     │  │     ├─ pytorch_export_contrib_ops.cpython-311.pyc
   │     │  │     ├─ pytorch_export_helpers.cpython-311.pyc
   │     │  │     ├─ reduced_build_config_parser.cpython-311.pyc
   │     │  │     ├─ remove_initializer_from_input.cpython-311.pyc
   │     │  │     ├─ symbolic_shape_infer.cpython-311.pyc
   │     │  │     ├─ update_onnx_opset.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ transformers
   │     │  │  ├─ affinity_helper.py
   │     │  │  ├─ benchmark.py
   │     │  │  ├─ benchmark_helper.py
   │     │  │  ├─ bert_perf_test.py
   │     │  │  ├─ bert_test_data.py
   │     │  │  ├─ compare_bert_results.py
   │     │  │  ├─ constants.py
   │     │  │  ├─ convert_generation.py
   │     │  │  ├─ convert_tf_models_to_pytorch.py
   │     │  │  ├─ convert_to_packing_mode.py
   │     │  │  ├─ dynamo_onnx_helper.py
   │     │  │  ├─ float16.py
   │     │  │  ├─ fusion_attention.py
   │     │  │  ├─ fusion_attention_clip.py
   │     │  │  ├─ fusion_attention_sam2.py
   │     │  │  ├─ fusion_attention_unet.py
   │     │  │  ├─ fusion_attention_vae.py
   │     │  │  ├─ fusion_bart_attention.py
   │     │  │  ├─ fusion_base.py
   │     │  │  ├─ fusion_biasgelu.py
   │     │  │  ├─ fusion_biassplitgelu.py
   │     │  │  ├─ fusion_bias_add.py
   │     │  │  ├─ fusion_conformer_attention.py
   │     │  │  ├─ fusion_constant_fold.py
   │     │  │  ├─ fusion_embedlayer.py
   │     │  │  ├─ fusion_fastgelu.py
   │     │  │  ├─ fusion_gelu.py
   │     │  │  ├─ fusion_gelu_approximation.py
   │     │  │  ├─ fusion_gemmfastgelu.py
   │     │  │  ├─ fusion_gpt_attention.py
   │     │  │  ├─ fusion_gpt_attention_megatron.py
   │     │  │  ├─ fusion_gpt_attention_no_past.py
   │     │  │  ├─ fusion_group_norm.py
   │     │  │  ├─ fusion_layernorm.py
   │     │  │  ├─ fusion_mha_mmdit.py
   │     │  │  ├─ fusion_nhwc_conv.py
   │     │  │  ├─ fusion_options.py
   │     │  │  ├─ fusion_qordered_attention.py
   │     │  │  ├─ fusion_qordered_gelu.py
   │     │  │  ├─ fusion_qordered_layernorm.py
   │     │  │  ├─ fusion_qordered_matmul.py
   │     │  │  ├─ fusion_quickgelu.py
   │     │  │  ├─ fusion_reshape.py
   │     │  │  ├─ fusion_rotary_attention.py
   │     │  │  ├─ fusion_shape.py
   │     │  │  ├─ fusion_simplified_layernorm.py
   │     │  │  ├─ fusion_skiplayernorm.py
   │     │  │  ├─ fusion_skip_group_norm.py
   │     │  │  ├─ fusion_transpose.py
   │     │  │  ├─ fusion_utils.py
   │     │  │  ├─ huggingface_models.py
   │     │  │  ├─ import_utils.py
   │     │  │  ├─ io_binding_helper.py
   │     │  │  ├─ large_model_exporter.py
   │     │  │  ├─ machine_info.py
   │     │  │  ├─ metrics.py
   │     │  │  ├─ models
   │     │  │  │  ├─ bart
   │     │  │  │  │  ├─ export.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ export.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ bert
   │     │  │  │  │  ├─ eval_squad.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ eval_squad.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ gpt2
   │     │  │  │  │  ├─ benchmark_gpt2.py
   │     │  │  │  │  ├─ convert_to_onnx.py
   │     │  │  │  │  ├─ gpt2_helper.py
   │     │  │  │  │  ├─ gpt2_parity.py
   │     │  │  │  │  ├─ gpt2_tester.py
   │     │  │  │  │  ├─ parity_check_helper.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ benchmark_gpt2.cpython-311.pyc
   │     │  │  │  │     ├─ convert_to_onnx.cpython-311.pyc
   │     │  │  │  │     ├─ gpt2_helper.cpython-311.pyc
   │     │  │  │  │     ├─ gpt2_parity.cpython-311.pyc
   │     │  │  │  │     ├─ gpt2_tester.cpython-311.pyc
   │     │  │  │  │     ├─ parity_check_helper.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ llama
   │     │  │  │  │  ├─ benchmark.py
   │     │  │  │  │  ├─ benchmark_all.py
   │     │  │  │  │  ├─ benchmark_e2e.py
   │     │  │  │  │  ├─ convert_to_onnx.py
   │     │  │  │  │  ├─ dist_settings.py
   │     │  │  │  │  ├─ llama_inputs.py
   │     │  │  │  │  ├─ llama_parity.py
   │     │  │  │  │  ├─ llama_torch.py
   │     │  │  │  │  ├─ quant_kv_dataloader.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ benchmark.cpython-311.pyc
   │     │  │  │  │     ├─ benchmark_all.cpython-311.pyc
   │     │  │  │  │     ├─ benchmark_e2e.cpython-311.pyc
   │     │  │  │  │     ├─ convert_to_onnx.cpython-311.pyc
   │     │  │  │  │     ├─ dist_settings.cpython-311.pyc
   │     │  │  │  │     ├─ llama_inputs.cpython-311.pyc
   │     │  │  │  │     ├─ llama_parity.cpython-311.pyc
   │     │  │  │  │     ├─ llama_torch.cpython-311.pyc
   │     │  │  │  │     ├─ quant_kv_dataloader.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ longformer
   │     │  │  │  │  ├─ benchmark_longformer.py
   │     │  │  │  │  ├─ convert_to_onnx.py
   │     │  │  │  │  ├─ generate_test_data.py
   │     │  │  │  │  ├─ longformer_helper.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ benchmark_longformer.cpython-311.pyc
   │     │  │  │  │     ├─ convert_to_onnx.cpython-311.pyc
   │     │  │  │  │     ├─ generate_test_data.cpython-311.pyc
   │     │  │  │  │     ├─ longformer_helper.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ phi2
   │     │  │  │  │  ├─ convert_to_onnx.py
   │     │  │  │  │  ├─ inference_example.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ convert_to_onnx.cpython-311.pyc
   │     │  │  │  │     ├─ inference_example.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ sam2
   │     │  │  │  │  ├─ benchmark_sam2.py
   │     │  │  │  │  ├─ convert_to_onnx.py
   │     │  │  │  │  ├─ image_decoder.py
   │     │  │  │  │  ├─ image_encoder.py
   │     │  │  │  │  ├─ mask_decoder.py
   │     │  │  │  │  ├─ nvtx_helper.py
   │     │  │  │  │  ├─ prompt_encoder.py
   │     │  │  │  │  ├─ sam2_demo.py
   │     │  │  │  │  ├─ sam2_image_onnx_predictor.py
   │     │  │  │  │  ├─ sam2_utils.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ benchmark_sam2.cpython-311.pyc
   │     │  │  │  │     ├─ convert_to_onnx.cpython-311.pyc
   │     │  │  │  │     ├─ image_decoder.cpython-311.pyc
   │     │  │  │  │     ├─ image_encoder.cpython-311.pyc
   │     │  │  │  │     ├─ mask_decoder.cpython-311.pyc
   │     │  │  │  │     ├─ nvtx_helper.cpython-311.pyc
   │     │  │  │  │     ├─ prompt_encoder.cpython-311.pyc
   │     │  │  │  │     ├─ sam2_demo.cpython-311.pyc
   │     │  │  │  │     ├─ sam2_image_onnx_predictor.cpython-311.pyc
   │     │  │  │  │     ├─ sam2_utils.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ stable_diffusion
   │     │  │  │  │  ├─ benchmark.py
   │     │  │  │  │  ├─ benchmark_controlnet.py
   │     │  │  │  │  ├─ demo_txt2img.py
   │     │  │  │  │  ├─ demo_txt2img_xl.py
   │     │  │  │  │  ├─ demo_utils.py
   │     │  │  │  │  ├─ diffusion_models.py
   │     │  │  │  │  ├─ diffusion_schedulers.py
   │     │  │  │  │  ├─ engine_builder.py
   │     │  │  │  │  ├─ engine_builder_ort_cuda.py
   │     │  │  │  │  ├─ engine_builder_ort_trt.py
   │     │  │  │  │  ├─ engine_builder_tensorrt.py
   │     │  │  │  │  ├─ engine_builder_torch.py
   │     │  │  │  │  ├─ optimize_pipeline.py
   │     │  │  │  │  ├─ ort_optimizer.py
   │     │  │  │  │  ├─ pipeline_stable_diffusion.py
   │     │  │  │  │  ├─ trt_utilities.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ benchmark.cpython-311.pyc
   │     │  │  │  │     ├─ benchmark_controlnet.cpython-311.pyc
   │     │  │  │  │     ├─ demo_txt2img.cpython-311.pyc
   │     │  │  │  │     ├─ demo_txt2img_xl.cpython-311.pyc
   │     │  │  │  │     ├─ demo_utils.cpython-311.pyc
   │     │  │  │  │     ├─ diffusion_models.cpython-311.pyc
   │     │  │  │  │     ├─ diffusion_schedulers.cpython-311.pyc
   │     │  │  │  │     ├─ engine_builder.cpython-311.pyc
   │     │  │  │  │     ├─ engine_builder_ort_cuda.cpython-311.pyc
   │     │  │  │  │     ├─ engine_builder_ort_trt.cpython-311.pyc
   │     │  │  │  │     ├─ engine_builder_tensorrt.cpython-311.pyc
   │     │  │  │  │     ├─ engine_builder_torch.cpython-311.pyc
   │     │  │  │  │     ├─ optimize_pipeline.cpython-311.pyc
   │     │  │  │  │     ├─ ort_optimizer.cpython-311.pyc
   │     │  │  │  │     ├─ pipeline_stable_diffusion.cpython-311.pyc
   │     │  │  │  │     ├─ trt_utilities.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ t5
   │     │  │  │  │  ├─ convert_to_onnx.py
   │     │  │  │  │  ├─ t5_decoder.py
   │     │  │  │  │  ├─ t5_encoder.py
   │     │  │  │  │  ├─ t5_encoder_decoder_init.py
   │     │  │  │  │  ├─ t5_helper.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ convert_to_onnx.cpython-311.pyc
   │     │  │  │  │     ├─ t5_decoder.cpython-311.pyc
   │     │  │  │  │     ├─ t5_encoder.cpython-311.pyc
   │     │  │  │  │     ├─ t5_encoder_decoder_init.cpython-311.pyc
   │     │  │  │  │     ├─ t5_helper.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  └─ whisper
   │     │  │  │     ├─ benchmark.py
   │     │  │  │     ├─ benchmark_all.py
   │     │  │  │     ├─ convert_to_onnx.py
   │     │  │  │     ├─ whisper_chain.py
   │     │  │  │     ├─ whisper_decoder.py
   │     │  │  │     ├─ whisper_encoder.py
   │     │  │  │     ├─ whisper_encoder_decoder_init.py
   │     │  │  │     ├─ whisper_helper.py
   │     │  │  │     ├─ whisper_inputs.py
   │     │  │  │     ├─ whisper_jump_times.py
   │     │  │  │     ├─ __init__.py
   │     │  │  │     └─ __pycache__
   │     │  │  │        ├─ benchmark.cpython-311.pyc
   │     │  │  │        ├─ benchmark_all.cpython-311.pyc
   │     │  │  │        ├─ convert_to_onnx.cpython-311.pyc
   │     │  │  │        ├─ whisper_chain.cpython-311.pyc
   │     │  │  │        ├─ whisper_decoder.cpython-311.pyc
   │     │  │  │        ├─ whisper_encoder.cpython-311.pyc
   │     │  │  │        ├─ whisper_encoder_decoder_init.cpython-311.pyc
   │     │  │  │        ├─ whisper_helper.cpython-311.pyc
   │     │  │  │        ├─ whisper_inputs.cpython-311.pyc
   │     │  │  │        ├─ whisper_jump_times.cpython-311.pyc
   │     │  │  │        └─ __init__.cpython-311.pyc
   │     │  │  ├─ onnx_exporter.py
   │     │  │  ├─ onnx_model.py
   │     │  │  ├─ onnx_model_bart.py
   │     │  │  ├─ onnx_model_bert.py
   │     │  │  ├─ onnx_model_bert_keras.py
   │     │  │  ├─ onnx_model_bert_tf.py
   │     │  │  ├─ onnx_model_clip.py
   │     │  │  ├─ onnx_model_conformer.py
   │     │  │  ├─ onnx_model_gpt2.py
   │     │  │  ├─ onnx_model_mmdit.py
   │     │  │  ├─ onnx_model_phi.py
   │     │  │  ├─ onnx_model_sam2.py
   │     │  │  ├─ onnx_model_t5.py
   │     │  │  ├─ onnx_model_tnlr.py
   │     │  │  ├─ onnx_model_unet.py
   │     │  │  ├─ onnx_model_vae.py
   │     │  │  ├─ onnx_utils.py
   │     │  │  ├─ optimizer.py
   │     │  │  ├─ past_helper.py
   │     │  │  ├─ profiler.py
   │     │  │  ├─ profile_result_processor.py
   │     │  │  ├─ quantize_helper.py
   │     │  │  ├─ shape_infer_helper.py
   │     │  │  ├─ shape_optimizer.py
   │     │  │  ├─ torch_onnx_export_helper.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ affinity_helper.cpython-311.pyc
   │     │  │     ├─ benchmark.cpython-311.pyc
   │     │  │     ├─ benchmark_helper.cpython-311.pyc
   │     │  │     ├─ bert_perf_test.cpython-311.pyc
   │     │  │     ├─ bert_test_data.cpython-311.pyc
   │     │  │     ├─ compare_bert_results.cpython-311.pyc
   │     │  │     ├─ constants.cpython-311.pyc
   │     │  │     ├─ convert_generation.cpython-311.pyc
   │     │  │     ├─ convert_tf_models_to_pytorch.cpython-311.pyc
   │     │  │     ├─ convert_to_packing_mode.cpython-311.pyc
   │     │  │     ├─ dynamo_onnx_helper.cpython-311.pyc
   │     │  │     ├─ float16.cpython-311.pyc
   │     │  │     ├─ fusion_attention.cpython-311.pyc
   │     │  │     ├─ fusion_attention_clip.cpython-311.pyc
   │     │  │     ├─ fusion_attention_sam2.cpython-311.pyc
   │     │  │     ├─ fusion_attention_unet.cpython-311.pyc
   │     │  │     ├─ fusion_attention_vae.cpython-311.pyc
   │     │  │     ├─ fusion_bart_attention.cpython-311.pyc
   │     │  │     ├─ fusion_base.cpython-311.pyc
   │     │  │     ├─ fusion_biasgelu.cpython-311.pyc
   │     │  │     ├─ fusion_biassplitgelu.cpython-311.pyc
   │     │  │     ├─ fusion_bias_add.cpython-311.pyc
   │     │  │     ├─ fusion_conformer_attention.cpython-311.pyc
   │     │  │     ├─ fusion_constant_fold.cpython-311.pyc
   │     │  │     ├─ fusion_embedlayer.cpython-311.pyc
   │     │  │     ├─ fusion_fastgelu.cpython-311.pyc
   │     │  │     ├─ fusion_gelu.cpython-311.pyc
   │     │  │     ├─ fusion_gelu_approximation.cpython-311.pyc
   │     │  │     ├─ fusion_gemmfastgelu.cpython-311.pyc
   │     │  │     ├─ fusion_gpt_attention.cpython-311.pyc
   │     │  │     ├─ fusion_gpt_attention_megatron.cpython-311.pyc
   │     │  │     ├─ fusion_gpt_attention_no_past.cpython-311.pyc
   │     │  │     ├─ fusion_group_norm.cpython-311.pyc
   │     │  │     ├─ fusion_layernorm.cpython-311.pyc
   │     │  │     ├─ fusion_mha_mmdit.cpython-311.pyc
   │     │  │     ├─ fusion_nhwc_conv.cpython-311.pyc
   │     │  │     ├─ fusion_options.cpython-311.pyc
   │     │  │     ├─ fusion_qordered_attention.cpython-311.pyc
   │     │  │     ├─ fusion_qordered_gelu.cpython-311.pyc
   │     │  │     ├─ fusion_qordered_layernorm.cpython-311.pyc
   │     │  │     ├─ fusion_qordered_matmul.cpython-311.pyc
   │     │  │     ├─ fusion_quickgelu.cpython-311.pyc
   │     │  │     ├─ fusion_reshape.cpython-311.pyc
   │     │  │     ├─ fusion_rotary_attention.cpython-311.pyc
   │     │  │     ├─ fusion_shape.cpython-311.pyc
   │     │  │     ├─ fusion_simplified_layernorm.cpython-311.pyc
   │     │  │     ├─ fusion_skiplayernorm.cpython-311.pyc
   │     │  │     ├─ fusion_skip_group_norm.cpython-311.pyc
   │     │  │     ├─ fusion_transpose.cpython-311.pyc
   │     │  │     ├─ fusion_utils.cpython-311.pyc
   │     │  │     ├─ huggingface_models.cpython-311.pyc
   │     │  │     ├─ import_utils.cpython-311.pyc
   │     │  │     ├─ io_binding_helper.cpython-311.pyc
   │     │  │     ├─ large_model_exporter.cpython-311.pyc
   │     │  │     ├─ machine_info.cpython-311.pyc
   │     │  │     ├─ metrics.cpython-311.pyc
   │     │  │     ├─ onnx_exporter.cpython-311.pyc
   │     │  │     ├─ onnx_model.cpython-311.pyc
   │     │  │     ├─ onnx_model_bart.cpython-311.pyc
   │     │  │     ├─ onnx_model_bert.cpython-311.pyc
   │     │  │     ├─ onnx_model_bert_keras.cpython-311.pyc
   │     │  │     ├─ onnx_model_bert_tf.cpython-311.pyc
   │     │  │     ├─ onnx_model_clip.cpython-311.pyc
   │     │  │     ├─ onnx_model_conformer.cpython-311.pyc
   │     │  │     ├─ onnx_model_gpt2.cpython-311.pyc
   │     │  │     ├─ onnx_model_mmdit.cpython-311.pyc
   │     │  │     ├─ onnx_model_phi.cpython-311.pyc
   │     │  │     ├─ onnx_model_sam2.cpython-311.pyc
   │     │  │     ├─ onnx_model_t5.cpython-311.pyc
   │     │  │     ├─ onnx_model_tnlr.cpython-311.pyc
   │     │  │     ├─ onnx_model_unet.cpython-311.pyc
   │     │  │     ├─ onnx_model_vae.cpython-311.pyc
   │     │  │     ├─ onnx_utils.cpython-311.pyc
   │     │  │     ├─ optimizer.cpython-311.pyc
   │     │  │     ├─ past_helper.cpython-311.pyc
   │     │  │     ├─ profiler.cpython-311.pyc
   │     │  │     ├─ profile_result_processor.cpython-311.pyc
   │     │  │     ├─ quantize_helper.cpython-311.pyc
   │     │  │     ├─ shape_infer_helper.cpython-311.pyc
   │     │  │     ├─ shape_optimizer.cpython-311.pyc
   │     │  │     ├─ torch_onnx_export_helper.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ __init__.py
   │     │  └─ __pycache__
   │     │     └─ __init__.cpython-311.pyc
   │     ├─ onnxruntime-1.24.4.dist-info
   │     │  ├─ entry_points.txt
   │     │  ├─ INSTALLER
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  ├─ top_level.txt
   │     │  └─ WHEEL
   │     ├─ opentelemetry
   │     │  ├─ attributes
   │     │  │  ├─ py.typed
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ baggage
   │     │  │  ├─ propagation
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ py.typed
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ context
   │     │  │  ├─ context.py
   │     │  │  ├─ contextvars_context.py
   │     │  │  ├─ py.typed
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ context.cpython-311.pyc
   │     │  │     ├─ contextvars_context.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ environment_variables
   │     │  │  ├─ py.typed
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ exporter
   │     │  │  └─ otlp
   │     │  │     └─ proto
   │     │  │        ├─ common
   │     │  │        │  ├─ metrics_encoder.py
   │     │  │        │  ├─ py.typed
   │     │  │        │  ├─ trace_encoder.py
   │     │  │        │  ├─ version
   │     │  │        │  │  ├─ __init__.py
   │     │  │        │  │  └─ __pycache__
   │     │  │        │  │     └─ __init__.cpython-311.pyc
   │     │  │        │  ├─ _internal
   │     │  │        │  │  ├─ metrics_encoder
   │     │  │        │  │  │  ├─ __init__.py
   │     │  │        │  │  │  └─ __pycache__
   │     │  │        │  │  │     └─ __init__.cpython-311.pyc
   │     │  │        │  │  ├─ trace_encoder
   │     │  │        │  │  │  ├─ __init__.py
   │     │  │        │  │  │  └─ __pycache__
   │     │  │        │  │  │     └─ __init__.cpython-311.pyc
   │     │  │        │  │  ├─ _log_encoder
   │     │  │        │  │  │  ├─ __init__.py
   │     │  │        │  │  │  └─ __pycache__
   │     │  │        │  │  │     └─ __init__.cpython-311.pyc
   │     │  │        │  │  ├─ __init__.py
   │     │  │        │  │  └─ __pycache__
   │     │  │        │  │     └─ __init__.cpython-311.pyc
   │     │  │        │  ├─ _log_encoder.py
   │     │  │        │  ├─ __init__.py
   │     │  │        │  └─ __pycache__
   │     │  │        │     ├─ metrics_encoder.cpython-311.pyc
   │     │  │        │     ├─ trace_encoder.cpython-311.pyc
   │     │  │        │     ├─ _log_encoder.cpython-311.pyc
   │     │  │        │     └─ __init__.cpython-311.pyc
   │     │  │        └─ grpc
   │     │  │           ├─ exporter.py
   │     │  │           ├─ metric_exporter
   │     │  │           │  ├─ __init__.py
   │     │  │           │  └─ __pycache__
   │     │  │           │     └─ __init__.cpython-311.pyc
   │     │  │           ├─ py.typed
   │     │  │           ├─ trace_exporter
   │     │  │           │  ├─ __init__.py
   │     │  │           │  └─ __pycache__
   │     │  │           │     └─ __init__.cpython-311.pyc
   │     │  │           ├─ version
   │     │  │           │  ├─ __init__.py
   │     │  │           │  └─ __pycache__
   │     │  │           │     └─ __init__.cpython-311.pyc
   │     │  │           ├─ _log_exporter
   │     │  │           │  ├─ __init__.py
   │     │  │           │  └─ __pycache__
   │     │  │           │     └─ __init__.cpython-311.pyc
   │     │  │           ├─ __init__.py
   │     │  │           └─ __pycache__
   │     │  │              ├─ exporter.cpython-311.pyc
   │     │  │              └─ __init__.cpython-311.pyc
   │     │  ├─ metrics
   │     │  │  ├─ py.typed
   │     │  │  ├─ _internal
   │     │  │  │  ├─ instrument.py
   │     │  │  │  ├─ observation.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ instrument.cpython-311.pyc
   │     │  │  │     ├─ observation.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ propagate
   │     │  │  ├─ py.typed
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ propagators
   │     │  │  ├─ composite.py
   │     │  │  ├─ py.typed
   │     │  │  ├─ textmap.py
   │     │  │  ├─ _envcarrier.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ composite.cpython-311.pyc
   │     │  │     ├─ textmap.cpython-311.pyc
   │     │  │     └─ _envcarrier.cpython-311.pyc
   │     │  ├─ proto
   │     │  │  ├─ collector
   │     │  │  │  ├─ logs
   │     │  │  │  │  └─ v1
   │     │  │  │  │     ├─ logs_service_pb2.py
   │     │  │  │  │     ├─ logs_service_pb2.pyi
   │     │  │  │  │     ├─ logs_service_pb2_grpc.py
   │     │  │  │  │     └─ __pycache__
   │     │  │  │  │        ├─ logs_service_pb2.cpython-311.pyc
   │     │  │  │  │        └─ logs_service_pb2_grpc.cpython-311.pyc
   │     │  │  │  ├─ metrics
   │     │  │  │  │  ├─ v1
   │     │  │  │  │  │  ├─ metrics_service_pb2.py
   │     │  │  │  │  │  ├─ metrics_service_pb2.pyi
   │     │  │  │  │  │  ├─ metrics_service_pb2_grpc.py
   │     │  │  │  │  │  ├─ __init__.py
   │     │  │  │  │  │  └─ __pycache__
   │     │  │  │  │  │     ├─ metrics_service_pb2.cpython-311.pyc
   │     │  │  │  │  │     ├─ metrics_service_pb2_grpc.cpython-311.pyc
   │     │  │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ profiles
   │     │  │  │  │  └─ v1development
   │     │  │  │  │     ├─ profiles_service_pb2.py
   │     │  │  │  │     ├─ profiles_service_pb2.pyi
   │     │  │  │  │     ├─ profiles_service_pb2_grpc.py
   │     │  │  │  │     └─ __pycache__
   │     │  │  │  │        ├─ profiles_service_pb2.cpython-311.pyc
   │     │  │  │  │        └─ profiles_service_pb2_grpc.cpython-311.pyc
   │     │  │  │  ├─ trace
   │     │  │  │  │  ├─ v1
   │     │  │  │  │  │  ├─ trace_service_pb2.py
   │     │  │  │  │  │  ├─ trace_service_pb2.pyi
   │     │  │  │  │  │  ├─ trace_service_pb2_grpc.py
   │     │  │  │  │  │  ├─ __init__.py
   │     │  │  │  │  │  └─ __pycache__
   │     │  │  │  │  │     ├─ trace_service_pb2.cpython-311.pyc
   │     │  │  │  │  │     ├─ trace_service_pb2_grpc.cpython-311.pyc
   │     │  │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ common
   │     │  │  │  ├─ v1
   │     │  │  │  │  ├─ common_pb2.py
   │     │  │  │  │  ├─ common_pb2.pyi
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ common_pb2.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ logs
   │     │  │  │  └─ v1
   │     │  │  │     ├─ logs_pb2.py
   │     │  │  │     ├─ logs_pb2.pyi
   │     │  │  │     └─ __pycache__
   │     │  │  │        └─ logs_pb2.cpython-311.pyc
   │     │  │  ├─ metrics
   │     │  │  │  ├─ v1
   │     │  │  │  │  ├─ metrics_pb2.py
   │     │  │  │  │  ├─ metrics_pb2.pyi
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ metrics_pb2.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ profiles
   │     │  │  │  └─ v1development
   │     │  │  │     ├─ profiles_pb2.py
   │     │  │  │     ├─ profiles_pb2.pyi
   │     │  │  │     └─ __pycache__
   │     │  │  │        └─ profiles_pb2.cpython-311.pyc
   │     │  │  ├─ py.typed
   │     │  │  ├─ resource
   │     │  │  │  ├─ v1
   │     │  │  │  │  ├─ resource_pb2.py
   │     │  │  │  │  ├─ resource_pb2.pyi
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ resource_pb2.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ trace
   │     │  │  │  ├─ v1
   │     │  │  │  │  ├─ trace_pb2.py
   │     │  │  │  │  ├─ trace_pb2.pyi
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ trace_pb2.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ version
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ py.typed
   │     │  ├─ sdk
   │     │  │  ├─ environment_variables
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ error_handler
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ metrics
   │     │  │  │  ├─ export
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ view
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ _internal
   │     │  │  │  │  ├─ aggregation.py
   │     │  │  │  │  ├─ exceptions.py
   │     │  │  │  │  ├─ exemplar
   │     │  │  │  │  │  ├─ exemplar.py
   │     │  │  │  │  │  ├─ exemplar_filter.py
   │     │  │  │  │  │  ├─ exemplar_reservoir.py
   │     │  │  │  │  │  ├─ __init__.py
   │     │  │  │  │  │  └─ __pycache__
   │     │  │  │  │  │     ├─ exemplar.cpython-311.pyc
   │     │  │  │  │  │     ├─ exemplar_filter.cpython-311.pyc
   │     │  │  │  │  │     ├─ exemplar_reservoir.cpython-311.pyc
   │     │  │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  │  ├─ exponential_histogram
   │     │  │  │  │  │  ├─ buckets.py
   │     │  │  │  │  │  ├─ mapping
   │     │  │  │  │  │  │  ├─ errors.py
   │     │  │  │  │  │  │  ├─ exponent_mapping.py
   │     │  │  │  │  │  │  ├─ ieee_754.md
   │     │  │  │  │  │  │  ├─ ieee_754.py
   │     │  │  │  │  │  │  ├─ logarithm_mapping.py
   │     │  │  │  │  │  │  ├─ __init__.py
   │     │  │  │  │  │  │  └─ __pycache__
   │     │  │  │  │  │  │     ├─ errors.cpython-311.pyc
   │     │  │  │  │  │  │     ├─ exponent_mapping.cpython-311.pyc
   │     │  │  │  │  │  │     ├─ ieee_754.cpython-311.pyc
   │     │  │  │  │  │  │     ├─ logarithm_mapping.cpython-311.pyc
   │     │  │  │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  │  │  ├─ __init__.py
   │     │  │  │  │  │  └─ __pycache__
   │     │  │  │  │  │     ├─ buckets.cpython-311.pyc
   │     │  │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  │  ├─ export
   │     │  │  │  │  │  ├─ _metric_reader_metrics.py
   │     │  │  │  │  │  ├─ __init__.py
   │     │  │  │  │  │  └─ __pycache__
   │     │  │  │  │  │     ├─ _metric_reader_metrics.cpython-311.pyc
   │     │  │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  │  ├─ instrument.py
   │     │  │  │  │  ├─ measurement.py
   │     │  │  │  │  ├─ measurement_consumer.py
   │     │  │  │  │  ├─ metric_reader_storage.py
   │     │  │  │  │  ├─ point.py
   │     │  │  │  │  ├─ sdk_configuration.py
   │     │  │  │  │  ├─ view.py
   │     │  │  │  │  ├─ _view_instrument_match.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ aggregation.cpython-311.pyc
   │     │  │  │  │     ├─ exceptions.cpython-311.pyc
   │     │  │  │  │     ├─ instrument.cpython-311.pyc
   │     │  │  │  │     ├─ measurement.cpython-311.pyc
   │     │  │  │  │     ├─ measurement_consumer.cpython-311.pyc
   │     │  │  │  │     ├─ metric_reader_storage.cpython-311.pyc
   │     │  │  │  │     ├─ point.cpython-311.pyc
   │     │  │  │  │     ├─ sdk_configuration.cpython-311.pyc
   │     │  │  │  │     ├─ view.cpython-311.pyc
   │     │  │  │  │     ├─ _view_instrument_match.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ py.typed
   │     │  │  ├─ resources
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ trace
   │     │  │  │  ├─ export
   │     │  │  │  │  ├─ in_memory_span_exporter.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ in_memory_span_exporter.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ id_generator.py
   │     │  │  │  ├─ sampling.py
   │     │  │  │  ├─ _sampling_experimental
   │     │  │  │  │  ├─ _always_off.py
   │     │  │  │  │  ├─ _always_on.py
   │     │  │  │  │  ├─ _composable.py
   │     │  │  │  │  ├─ _parent_threshold.py
   │     │  │  │  │  ├─ _rule_based.py
   │     │  │  │  │  ├─ _sampler.py
   │     │  │  │  │  ├─ _traceid_ratio.py
   │     │  │  │  │  ├─ _trace_state.py
   │     │  │  │  │  ├─ _util.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ _always_off.cpython-311.pyc
   │     │  │  │  │     ├─ _always_on.cpython-311.pyc
   │     │  │  │  │     ├─ _composable.cpython-311.pyc
   │     │  │  │  │     ├─ _parent_threshold.cpython-311.pyc
   │     │  │  │  │     ├─ _rule_based.cpython-311.pyc
   │     │  │  │  │     ├─ _sampler.cpython-311.pyc
   │     │  │  │  │     ├─ _traceid_ratio.cpython-311.pyc
   │     │  │  │  │     ├─ _trace_state.cpython-311.pyc
   │     │  │  │  │     ├─ _util.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ _tracer_metrics.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ id_generator.cpython-311.pyc
   │     │  │  │     ├─ sampling.cpython-311.pyc
   │     │  │  │     ├─ _tracer_metrics.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ util
   │     │  │  │  ├─ instrumentation.py
   │     │  │  │  ├─ _configurator.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  ├─ __init__.pyi
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ instrumentation.cpython-311.pyc
   │     │  │  │     ├─ _configurator.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ version
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ _configuration
   │     │  │  │  ├─ file
   │     │  │  │  │  ├─ _env_substitution.py
   │     │  │  │  │  ├─ _loader.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ _env_substitution.cpython-311.pyc
   │     │  │  │  │     ├─ _loader.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ models.py
   │     │  │  │  ├─ README.md
   │     │  │  │  ├─ schema.json
   │     │  │  │  ├─ _common.py
   │     │  │  │  ├─ _exceptions.py
   │     │  │  │  ├─ _meter_provider.py
   │     │  │  │  ├─ _propagator.py
   │     │  │  │  ├─ _resource.py
   │     │  │  │  ├─ _tracer_provider.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ models.cpython-311.pyc
   │     │  │  │     ├─ _common.cpython-311.pyc
   │     │  │  │     ├─ _exceptions.cpython-311.pyc
   │     │  │  │     ├─ _meter_provider.cpython-311.pyc
   │     │  │  │     ├─ _propagator.cpython-311.pyc
   │     │  │  │     ├─ _resource.cpython-311.pyc
   │     │  │  │     ├─ _tracer_provider.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ _events
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ _logs
   │     │  │  │  ├─ export
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ _internal
   │     │  │  │  │  ├─ export
   │     │  │  │  │  │  ├─ in_memory_log_exporter.py
   │     │  │  │  │  │  ├─ __init__.py
   │     │  │  │  │  │  └─ __pycache__
   │     │  │  │  │  │     ├─ in_memory_log_exporter.cpython-311.pyc
   │     │  │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  │  ├─ _logger_metrics.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ _logger_metrics.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ _shared_internal
   │     │  │  │  ├─ _processor_metrics.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ _processor_metrics.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  └─ __init__.pyi
   │     │  ├─ semconv
   │     │  │  ├─ attributes
   │     │  │  │  ├─ client_attributes.py
   │     │  │  │  ├─ code_attributes.py
   │     │  │  │  ├─ db_attributes.py
   │     │  │  │  ├─ error_attributes.py
   │     │  │  │  ├─ exception_attributes.py
   │     │  │  │  ├─ http_attributes.py
   │     │  │  │  ├─ network_attributes.py
   │     │  │  │  ├─ otel_attributes.py
   │     │  │  │  ├─ server_attributes.py
   │     │  │  │  ├─ service_attributes.py
   │     │  │  │  ├─ telemetry_attributes.py
   │     │  │  │  ├─ url_attributes.py
   │     │  │  │  ├─ user_agent_attributes.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ client_attributes.cpython-311.pyc
   │     │  │  │     ├─ code_attributes.cpython-311.pyc
   │     │  │  │     ├─ db_attributes.cpython-311.pyc
   │     │  │  │     ├─ error_attributes.cpython-311.pyc
   │     │  │  │     ├─ exception_attributes.cpython-311.pyc
   │     │  │  │     ├─ http_attributes.cpython-311.pyc
   │     │  │  │     ├─ network_attributes.cpython-311.pyc
   │     │  │  │     ├─ otel_attributes.cpython-311.pyc
   │     │  │  │     ├─ server_attributes.cpython-311.pyc
   │     │  │  │     ├─ service_attributes.cpython-311.pyc
   │     │  │  │     ├─ telemetry_attributes.cpython-311.pyc
   │     │  │  │     ├─ url_attributes.cpython-311.pyc
   │     │  │  │     ├─ user_agent_attributes.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ metrics
   │     │  │  │  ├─ db_metrics.py
   │     │  │  │  ├─ http_metrics.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ db_metrics.cpython-311.pyc
   │     │  │  │     ├─ http_metrics.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ py.typed
   │     │  │  ├─ resource
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ schemas.py
   │     │  │  ├─ trace
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ version
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ _incubating
   │     │  │  │  ├─ attributes
   │     │  │  │  │  ├─ app_attributes.py
   │     │  │  │  │  ├─ artifact_attributes.py
   │     │  │  │  │  ├─ aws_attributes.py
   │     │  │  │  │  ├─ azure_attributes.py
   │     │  │  │  │  ├─ az_attributes.py
   │     │  │  │  │  ├─ browser_attributes.py
   │     │  │  │  │  ├─ cassandra_attributes.py
   │     │  │  │  │  ├─ cicd_attributes.py
   │     │  │  │  │  ├─ client_attributes.py
   │     │  │  │  │  ├─ cloudevents_attributes.py
   │     │  │  │  │  ├─ cloudfoundry_attributes.py
   │     │  │  │  │  ├─ cloud_attributes.py
   │     │  │  │  │  ├─ code_attributes.py
   │     │  │  │  │  ├─ container_attributes.py
   │     │  │  │  │  ├─ cpu_attributes.py
   │     │  │  │  │  ├─ cpython_attributes.py
   │     │  │  │  │  ├─ db_attributes.py
   │     │  │  │  │  ├─ deployment_attributes.py
   │     │  │  │  │  ├─ destination_attributes.py
   │     │  │  │  │  ├─ device_attributes.py
   │     │  │  │  │  ├─ disk_attributes.py
   │     │  │  │  │  ├─ dns_attributes.py
   │     │  │  │  │  ├─ elasticsearch_attributes.py
   │     │  │  │  │  ├─ enduser_attributes.py
   │     │  │  │  │  ├─ error_attributes.py
   │     │  │  │  │  ├─ event_attributes.py
   │     │  │  │  │  ├─ exception_attributes.py
   │     │  │  │  │  ├─ faas_attributes.py
   │     │  │  │  │  ├─ feature_flag_attributes.py
   │     │  │  │  │  ├─ file_attributes.py
   │     │  │  │  │  ├─ gcp_attributes.py
   │     │  │  │  │  ├─ gen_ai_attributes.py
   │     │  │  │  │  ├─ geo_attributes.py
   │     │  │  │  │  ├─ graphql_attributes.py
   │     │  │  │  │  ├─ heroku_attributes.py
   │     │  │  │  │  ├─ host_attributes.py
   │     │  │  │  │  ├─ http_attributes.py
   │     │  │  │  │  ├─ hw_attributes.py
   │     │  │  │  │  ├─ jsonrpc_attributes.py
   │     │  │  │  │  ├─ k8s_attributes.py
   │     │  │  │  │  ├─ linux_attributes.py
   │     │  │  │  │  ├─ log_attributes.py
   │     │  │  │  │  ├─ mainframe_attributes.py
   │     │  │  │  │  ├─ mcp_attributes.py
   │     │  │  │  │  ├─ message_attributes.py
   │     │  │  │  │  ├─ messaging_attributes.py
   │     │  │  │  │  ├─ network_attributes.py
   │     │  │  │  │  ├─ net_attributes.py
   │     │  │  │  │  ├─ nfs_attributes.py
   │     │  │  │  │  ├─ oci_attributes.py
   │     │  │  │  │  ├─ onc_rpc_attributes.py
   │     │  │  │  │  ├─ openai_attributes.py
   │     │  │  │  │  ├─ openshift_attributes.py
   │     │  │  │  │  ├─ opentracing_attributes.py
   │     │  │  │  │  ├─ oracle_attributes.py
   │     │  │  │  │  ├─ oracle_cloud_attributes.py
   │     │  │  │  │  ├─ os_attributes.py
   │     │  │  │  │  ├─ otel_attributes.py
   │     │  │  │  │  ├─ other_attributes.py
   │     │  │  │  │  ├─ peer_attributes.py
   │     │  │  │  │  ├─ pool_attributes.py
   │     │  │  │  │  ├─ pprof_attributes.py
   │     │  │  │  │  ├─ process_attributes.py
   │     │  │  │  │  ├─ profile_attributes.py
   │     │  │  │  │  ├─ rpc_attributes.py
   │     │  │  │  │  ├─ security_rule_attributes.py
   │     │  │  │  │  ├─ server_attributes.py
   │     │  │  │  │  ├─ service_attributes.py
   │     │  │  │  │  ├─ session_attributes.py
   │     │  │  │  │  ├─ source_attributes.py
   │     │  │  │  │  ├─ system_attributes.py
   │     │  │  │  │  ├─ telemetry_attributes.py
   │     │  │  │  │  ├─ test_attributes.py
   │     │  │  │  │  ├─ thread_attributes.py
   │     │  │  │  │  ├─ tls_attributes.py
   │     │  │  │  │  ├─ url_attributes.py
   │     │  │  │  │  ├─ user_agent_attributes.py
   │     │  │  │  │  ├─ user_attributes.py
   │     │  │  │  │  ├─ vcs_attributes.py
   │     │  │  │  │  ├─ webengine_attributes.py
   │     │  │  │  │  ├─ zos_attributes.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ app_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ artifact_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ aws_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ azure_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ az_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ browser_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ cassandra_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ cicd_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ client_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ cloudevents_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ cloudfoundry_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ cloud_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ code_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ container_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ cpu_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ cpython_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ db_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ deployment_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ destination_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ device_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ disk_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ dns_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ elasticsearch_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ enduser_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ error_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ event_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ exception_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ faas_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ feature_flag_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ file_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ gcp_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ gen_ai_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ geo_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ graphql_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ heroku_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ host_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ http_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ hw_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ jsonrpc_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ k8s_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ linux_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ log_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ mainframe_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ mcp_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ message_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ messaging_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ network_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ net_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ nfs_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ oci_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ onc_rpc_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ openai_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ openshift_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ opentracing_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ oracle_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ oracle_cloud_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ os_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ otel_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ other_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ peer_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ pool_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ pprof_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ process_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ profile_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ rpc_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ security_rule_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ server_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ service_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ session_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ source_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ system_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ telemetry_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ test_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ thread_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ tls_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ url_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ user_agent_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ user_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ vcs_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ webengine_attributes.cpython-311.pyc
   │     │  │  │  │     └─ zos_attributes.cpython-311.pyc
   │     │  │  │  └─ metrics
   │     │  │  │     ├─ azure_metrics.py
   │     │  │  │     ├─ cicd_metrics.py
   │     │  │  │     ├─ container_metrics.py
   │     │  │  │     ├─ cpu_metrics.py
   │     │  │  │     ├─ cpython_metrics.py
   │     │  │  │     ├─ db_metrics.py
   │     │  │  │     ├─ dns_metrics.py
   │     │  │  │     ├─ faas_metrics.py
   │     │  │  │     ├─ gen_ai_metrics.py
   │     │  │  │     ├─ http_metrics.py
   │     │  │  │     ├─ hw_metrics.py
   │     │  │  │     ├─ k8s_metrics.py
   │     │  │  │     ├─ mcp_metrics.py
   │     │  │  │     ├─ messaging_metrics.py
   │     │  │  │     ├─ nfs_metrics.py
   │     │  │  │     ├─ openshift_metrics.py
   │     │  │  │     ├─ otel_metrics.py
   │     │  │  │     ├─ process_metrics.py
   │     │  │  │     ├─ rpc_metrics.py
   │     │  │  │     ├─ system_metrics.py
   │     │  │  │     ├─ vcs_metrics.py
   │     │  │  │     └─ __pycache__
   │     │  │  │        ├─ azure_metrics.cpython-311.pyc
   │     │  │  │        ├─ cicd_metrics.cpython-311.pyc
   │     │  │  │        ├─ container_metrics.cpython-311.pyc
   │     │  │  │        ├─ cpu_metrics.cpython-311.pyc
   │     │  │  │        ├─ cpython_metrics.cpython-311.pyc
   │     │  │  │        ├─ db_metrics.cpython-311.pyc
   │     │  │  │        ├─ dns_metrics.cpython-311.pyc
   │     │  │  │        ├─ faas_metrics.cpython-311.pyc
   │     │  │  │        ├─ gen_ai_metrics.cpython-311.pyc
   │     │  │  │        ├─ http_metrics.cpython-311.pyc
   │     │  │  │        ├─ hw_metrics.cpython-311.pyc
   │     │  │  │        ├─ k8s_metrics.cpython-311.pyc
   │     │  │  │        ├─ mcp_metrics.cpython-311.pyc
   │     │  │  │        ├─ messaging_metrics.cpython-311.pyc
   │     │  │  │        ├─ nfs_metrics.cpython-311.pyc
   │     │  │  │        ├─ openshift_metrics.cpython-311.pyc
   │     │  │  │        ├─ otel_metrics.cpython-311.pyc
   │     │  │  │        ├─ process_metrics.cpython-311.pyc
   │     │  │  │        ├─ rpc_metrics.cpython-311.pyc
   │     │  │  │        ├─ system_metrics.cpython-311.pyc
   │     │  │  │        └─ vcs_metrics.cpython-311.pyc
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ schemas.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ trace
   │     │  │  ├─ propagation
   │     │  │  │  ├─ tracecontext.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ tracecontext.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ py.typed
   │     │  │  ├─ span.py
   │     │  │  ├─ status.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ span.cpython-311.pyc
   │     │  │     ├─ status.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ util
   │     │  │  ├─ py.typed
   │     │  │  ├─ re.py
   │     │  │  ├─ types.py
   │     │  │  ├─ _decorator.py
   │     │  │  ├─ _importlib_metadata.py
   │     │  │  ├─ _once.py
   │     │  │  ├─ _providers.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ re.cpython-311.pyc
   │     │  │     ├─ types.cpython-311.pyc
   │     │  │     ├─ _decorator.cpython-311.pyc
   │     │  │     ├─ _importlib_metadata.cpython-311.pyc
   │     │  │     ├─ _once.cpython-311.pyc
   │     │  │     └─ _providers.cpython-311.pyc
   │     │  ├─ version
   │     │  │  ├─ py.typed
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ _events
   │     │  │  ├─ py.typed
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  └─ _logs
   │     │     ├─ py.typed
   │     │     ├─ severity
   │     │     │  ├─ __init__.py
   │     │     │  └─ __pycache__
   │     │     │     └─ __init__.cpython-311.pyc
   │     │     ├─ _internal
   │     │     │  ├─ __init__.py
   │     │     │  └─ __pycache__
   │     │     │     └─ __init__.cpython-311.pyc
   │     │     ├─ __init__.py
   │     │     └─ __pycache__
   │     │        └─ __init__.cpython-311.pyc
   │     ├─ opentelemetry_api-1.41.0.dist-info
   │     │  ├─ entry_points.txt
   │     │  ├─ INSTALLER
   │     │  ├─ licenses
   │     │  │  └─ LICENSE
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  └─ WHEEL
   │     ├─ opentelemetry_exporter_otlp_proto_common-1.41.0.dist-info
   │     │  ├─ INSTALLER
   │     │  ├─ licenses
   │     │  │  └─ LICENSE
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  └─ WHEEL
   │     ├─ opentelemetry_exporter_otlp_proto_grpc-1.41.0.dist-info
   │     │  ├─ entry_points.txt
   │     │  ├─ INSTALLER
   │     │  ├─ licenses
   │     │  │  └─ LICENSE
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  └─ WHEEL
   │     ├─ opentelemetry_proto-1.41.0.dist-info
   │     │  ├─ INSTALLER
   │     │  ├─ licenses
   │     │  │  └─ LICENSE
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  └─ WHEEL
   │     ├─ opentelemetry_sdk-1.41.0.dist-info
   │     │  ├─ entry_points.txt
   │     │  ├─ INSTALLER
   │     │  ├─ licenses
   │     │  │  └─ LICENSE
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  └─ WHEEL
   │     ├─ opentelemetry_semantic_conventions-0.62b0.dist-info
   │     │  ├─ INSTALLER
   │     │  ├─ licenses
   │     │  │  └─ LICENSE
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  └─ WHEEL
   │     ├─ orjson
   │     │  ├─ orjson.cp311-win_amd64.pyd
   │     │  ├─ py.typed
   │     │  ├─ __init__.py
   │     │  ├─ __init__.pyi
   │     │  └─ __pycache__
   │     │     └─ __init__.cpython-311.pyc
   │     ├─ orjson-3.11.8.dist-info
   │     │  ├─ INSTALLER
   │     │  ├─ licenses
   │     │  │  ├─ LICENSE-APACHE
   │     │  │  ├─ LICENSE-MIT
   │     │  │  └─ LICENSE-MPL-2.0
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  ├─ sboms
   │     │  │  └─ orjson.cyclonedx.json
   │     │  └─ WHEEL
   │     ├─ overrides
   │     │  ├─ enforce.py
   │     │  ├─ final.py
   │     │  ├─ overrides.py
   │     │  ├─ py.typed
   │     │  ├─ signature.py
   │     │  ├─ typing_utils.py
   │     │  ├─ __init__.py
   │     │  └─ __pycache__
   │     │     ├─ enforce.cpython-311.pyc
   │     │     ├─ final.cpython-311.pyc
   │     │     ├─ overrides.cpython-311.pyc
   │     │     ├─ signature.cpython-311.pyc
   │     │     ├─ typing_utils.cpython-311.pyc
   │     │     └─ __init__.cpython-311.pyc
   │     ├─ overrides-7.7.0.dist-info
   │     │  ├─ INSTALLER
   │     │  ├─ LICENSE
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  ├─ top_level.txt
   │     │  └─ WHEEL
   │     ├─ packaging
   │     │  ├─ licenses
   │     │  │  ├─ _spdx.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ _spdx.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ markers.py
   │     │  ├─ metadata.py
   │     │  ├─ py.typed
   │     │  ├─ pylock.py
   │     │  ├─ requirements.py
   │     │  ├─ specifiers.py
   │     │  ├─ tags.py
   │     │  ├─ utils.py
   │     │  ├─ version.py
   │     │  ├─ _elffile.py
   │     │  ├─ _manylinux.py
   │     │  ├─ _musllinux.py
   │     │  ├─ _parser.py
   │     │  ├─ _structures.py
   │     │  ├─ _tokenizer.py
   │     │  ├─ __init__.py
   │     │  └─ __pycache__
   │     │     ├─ markers.cpython-311.pyc
   │     │     ├─ metadata.cpython-311.pyc
   │     │     ├─ pylock.cpython-311.pyc
   │     │     ├─ requirements.cpython-311.pyc
   │     │     ├─ specifiers.cpython-311.pyc
   │     │     ├─ tags.cpython-311.pyc
   │     │     ├─ utils.cpython-311.pyc
   │     │     ├─ version.cpython-311.pyc
   │     │     ├─ _elffile.cpython-311.pyc
   │     │     ├─ _manylinux.cpython-311.pyc
   │     │     ├─ _musllinux.cpython-311.pyc
   │     │     ├─ _parser.cpython-311.pyc
   │     │     ├─ _structures.cpython-311.pyc
   │     │     ├─ _tokenizer.cpython-311.pyc
   │     │     └─ __init__.cpython-311.pyc
   │     ├─ packaging-26.0.dist-info
   │     │  ├─ INSTALLER
   │     │  ├─ licenses
   │     │  │  ├─ LICENSE
   │     │  │  ├─ LICENSE.APACHE
   │     │  │  └─ LICENSE.BSD
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  └─ WHEEL
   │     ├─ pandas
   │     │  ├─ api
   │     │  │  ├─ executors
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ extensions
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ indexers
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ interchange
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ internals.py
   │     │  │  ├─ types
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ typing
   │     │  │  │  ├─ aliases.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ aliases.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ internals.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ arrays
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ compat
   │     │  │  ├─ numpy
   │     │  │  │  ├─ function.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ function.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ pickle_compat.py
   │     │  │  ├─ pyarrow.py
   │     │  │  ├─ _constants.py
   │     │  │  ├─ _optional.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ pickle_compat.cpython-311.pyc
   │     │  │     ├─ pyarrow.cpython-311.pyc
   │     │  │     ├─ _constants.cpython-311.pyc
   │     │  │     ├─ _optional.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ conftest.py
   │     │  ├─ core
   │     │  │  ├─ accessor.py
   │     │  │  ├─ algorithms.py
   │     │  │  ├─ api.py
   │     │  │  ├─ apply.py
   │     │  │  ├─ arraylike.py
   │     │  │  ├─ arrays
   │     │  │  │  ├─ arrow
   │     │  │  │  │  ├─ accessors.py
   │     │  │  │  │  ├─ array.py
   │     │  │  │  │  ├─ extension_types.py
   │     │  │  │  │  ├─ _arrow_utils.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ accessors.cpython-311.pyc
   │     │  │  │  │     ├─ array.cpython-311.pyc
   │     │  │  │  │     ├─ extension_types.cpython-311.pyc
   │     │  │  │  │     ├─ _arrow_utils.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ base.py
   │     │  │  │  ├─ boolean.py
   │     │  │  │  ├─ categorical.py
   │     │  │  │  ├─ datetimelike.py
   │     │  │  │  ├─ datetimes.py
   │     │  │  │  ├─ floating.py
   │     │  │  │  ├─ integer.py
   │     │  │  │  ├─ interval.py
   │     │  │  │  ├─ masked.py
   │     │  │  │  ├─ numeric.py
   │     │  │  │  ├─ numpy_.py
   │     │  │  │  ├─ period.py
   │     │  │  │  ├─ sparse
   │     │  │  │  │  ├─ accessor.py
   │     │  │  │  │  ├─ array.py
   │     │  │  │  │  ├─ scipy_sparse.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ accessor.cpython-311.pyc
   │     │  │  │  │     ├─ array.cpython-311.pyc
   │     │  │  │  │     ├─ scipy_sparse.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ string_.py
   │     │  │  │  ├─ string_arrow.py
   │     │  │  │  ├─ timedeltas.py
   │     │  │  │  ├─ _arrow_string_mixins.py
   │     │  │  │  ├─ _mixins.py
   │     │  │  │  ├─ _ranges.py
   │     │  │  │  ├─ _utils.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ base.cpython-311.pyc
   │     │  │  │     ├─ boolean.cpython-311.pyc
   │     │  │  │     ├─ categorical.cpython-311.pyc
   │     │  │  │     ├─ datetimelike.cpython-311.pyc
   │     │  │  │     ├─ datetimes.cpython-311.pyc
   │     │  │  │     ├─ floating.cpython-311.pyc
   │     │  │  │     ├─ integer.cpython-311.pyc
   │     │  │  │     ├─ interval.cpython-311.pyc
   │     │  │  │     ├─ masked.cpython-311.pyc
   │     │  │  │     ├─ numeric.cpython-311.pyc
   │     │  │  │     ├─ numpy_.cpython-311.pyc
   │     │  │  │     ├─ period.cpython-311.pyc
   │     │  │  │     ├─ string_.cpython-311.pyc
   │     │  │  │     ├─ string_arrow.cpython-311.pyc
   │     │  │  │     ├─ timedeltas.cpython-311.pyc
   │     │  │  │     ├─ _arrow_string_mixins.cpython-311.pyc
   │     │  │  │     ├─ _mixins.cpython-311.pyc
   │     │  │  │     ├─ _ranges.cpython-311.pyc
   │     │  │  │     ├─ _utils.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ array_algos
   │     │  │  │  ├─ datetimelike_accumulations.py
   │     │  │  │  ├─ masked_accumulations.py
   │     │  │  │  ├─ masked_reductions.py
   │     │  │  │  ├─ putmask.py
   │     │  │  │  ├─ quantile.py
   │     │  │  │  ├─ replace.py
   │     │  │  │  ├─ take.py
   │     │  │  │  ├─ transforms.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ datetimelike_accumulations.cpython-311.pyc
   │     │  │  │     ├─ masked_accumulations.cpython-311.pyc
   │     │  │  │     ├─ masked_reductions.cpython-311.pyc
   │     │  │  │     ├─ putmask.cpython-311.pyc
   │     │  │  │     ├─ quantile.cpython-311.pyc
   │     │  │  │     ├─ replace.cpython-311.pyc
   │     │  │  │     ├─ take.cpython-311.pyc
   │     │  │  │     ├─ transforms.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ base.py
   │     │  │  ├─ col.py
   │     │  │  ├─ common.py
   │     │  │  ├─ computation
   │     │  │  │  ├─ align.py
   │     │  │  │  ├─ api.py
   │     │  │  │  ├─ check.py
   │     │  │  │  ├─ common.py
   │     │  │  │  ├─ engines.py
   │     │  │  │  ├─ eval.py
   │     │  │  │  ├─ expr.py
   │     │  │  │  ├─ expressions.py
   │     │  │  │  ├─ ops.py
   │     │  │  │  ├─ parsing.py
   │     │  │  │  ├─ pytables.py
   │     │  │  │  ├─ scope.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ align.cpython-311.pyc
   │     │  │  │     ├─ api.cpython-311.pyc
   │     │  │  │     ├─ check.cpython-311.pyc
   │     │  │  │     ├─ common.cpython-311.pyc
   │     │  │  │     ├─ engines.cpython-311.pyc
   │     │  │  │     ├─ eval.cpython-311.pyc
   │     │  │  │     ├─ expr.cpython-311.pyc
   │     │  │  │     ├─ expressions.cpython-311.pyc
   │     │  │  │     ├─ ops.cpython-311.pyc
   │     │  │  │     ├─ parsing.cpython-311.pyc
   │     │  │  │     ├─ pytables.cpython-311.pyc
   │     │  │  │     ├─ scope.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ config_init.py
   │     │  │  ├─ construction.py
   │     │  │  ├─ dtypes
   │     │  │  │  ├─ api.py
   │     │  │  │  ├─ astype.py
   │     │  │  │  ├─ base.py
   │     │  │  │  ├─ cast.py
   │     │  │  │  ├─ common.py
   │     │  │  │  ├─ concat.py
   │     │  │  │  ├─ dtypes.py
   │     │  │  │  ├─ generic.py
   │     │  │  │  ├─ inference.py
   │     │  │  │  ├─ missing.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ api.cpython-311.pyc
   │     │  │  │     ├─ astype.cpython-311.pyc
   │     │  │  │     ├─ base.cpython-311.pyc
   │     │  │  │     ├─ cast.cpython-311.pyc
   │     │  │  │     ├─ common.cpython-311.pyc
   │     │  │  │     ├─ concat.cpython-311.pyc
   │     │  │  │     ├─ dtypes.cpython-311.pyc
   │     │  │  │     ├─ generic.cpython-311.pyc
   │     │  │  │     ├─ inference.cpython-311.pyc
   │     │  │  │     ├─ missing.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ flags.py
   │     │  │  ├─ frame.py
   │     │  │  ├─ generic.py
   │     │  │  ├─ groupby
   │     │  │  │  ├─ base.py
   │     │  │  │  ├─ categorical.py
   │     │  │  │  ├─ generic.py
   │     │  │  │  ├─ groupby.py
   │     │  │  │  ├─ grouper.py
   │     │  │  │  ├─ indexing.py
   │     │  │  │  ├─ numba_.py
   │     │  │  │  ├─ ops.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ base.cpython-311.pyc
   │     │  │  │     ├─ categorical.cpython-311.pyc
   │     │  │  │     ├─ generic.cpython-311.pyc
   │     │  │  │     ├─ groupby.cpython-311.pyc
   │     │  │  │     ├─ grouper.cpython-311.pyc
   │     │  │  │     ├─ indexing.cpython-311.pyc
   │     │  │  │     ├─ numba_.cpython-311.pyc
   │     │  │  │     ├─ ops.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ indexers
   │     │  │  │  ├─ objects.py
   │     │  │  │  ├─ utils.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ objects.cpython-311.pyc
   │     │  │  │     ├─ utils.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ indexes
   │     │  │  │  ├─ accessors.py
   │     │  │  │  ├─ api.py
   │     │  │  │  ├─ base.py
   │     │  │  │  ├─ category.py
   │     │  │  │  ├─ datetimelike.py
   │     │  │  │  ├─ datetimes.py
   │     │  │  │  ├─ extension.py
   │     │  │  │  ├─ frozen.py
   │     │  │  │  ├─ interval.py
   │     │  │  │  ├─ multi.py
   │     │  │  │  ├─ period.py
   │     │  │  │  ├─ range.py
   │     │  │  │  ├─ timedeltas.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ accessors.cpython-311.pyc
   │     │  │  │     ├─ api.cpython-311.pyc
   │     │  │  │     ├─ base.cpython-311.pyc
   │     │  │  │     ├─ category.cpython-311.pyc
   │     │  │  │     ├─ datetimelike.cpython-311.pyc
   │     │  │  │     ├─ datetimes.cpython-311.pyc
   │     │  │  │     ├─ extension.cpython-311.pyc
   │     │  │  │     ├─ frozen.cpython-311.pyc
   │     │  │  │     ├─ interval.cpython-311.pyc
   │     │  │  │     ├─ multi.cpython-311.pyc
   │     │  │  │     ├─ period.cpython-311.pyc
   │     │  │  │     ├─ range.cpython-311.pyc
   │     │  │  │     ├─ timedeltas.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ indexing.py
   │     │  │  ├─ interchange
   │     │  │  │  ├─ buffer.py
   │     │  │  │  ├─ column.py
   │     │  │  │  ├─ dataframe.py
   │     │  │  │  ├─ dataframe_protocol.py
   │     │  │  │  ├─ from_dataframe.py
   │     │  │  │  ├─ utils.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ buffer.cpython-311.pyc
   │     │  │  │     ├─ column.cpython-311.pyc
   │     │  │  │     ├─ dataframe.cpython-311.pyc
   │     │  │  │     ├─ dataframe_protocol.cpython-311.pyc
   │     │  │  │     ├─ from_dataframe.cpython-311.pyc
   │     │  │  │     ├─ utils.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ internals
   │     │  │  │  ├─ api.py
   │     │  │  │  ├─ blocks.py
   │     │  │  │  ├─ concat.py
   │     │  │  │  ├─ construction.py
   │     │  │  │  ├─ managers.py
   │     │  │  │  ├─ ops.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ api.cpython-311.pyc
   │     │  │  │     ├─ blocks.cpython-311.pyc
   │     │  │  │     ├─ concat.cpython-311.pyc
   │     │  │  │     ├─ construction.cpython-311.pyc
   │     │  │  │     ├─ managers.cpython-311.pyc
   │     │  │  │     ├─ ops.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ methods
   │     │  │  │  ├─ describe.py
   │     │  │  │  ├─ selectn.py
   │     │  │  │  ├─ to_dict.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ describe.cpython-311.pyc
   │     │  │  │     ├─ selectn.cpython-311.pyc
   │     │  │  │     ├─ to_dict.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ missing.py
   │     │  │  ├─ nanops.py
   │     │  │  ├─ ops
   │     │  │  │  ├─ array_ops.py
   │     │  │  │  ├─ common.py
   │     │  │  │  ├─ dispatch.py
   │     │  │  │  ├─ docstrings.py
   │     │  │  │  ├─ invalid.py
   │     │  │  │  ├─ mask_ops.py
   │     │  │  │  ├─ missing.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ array_ops.cpython-311.pyc
   │     │  │  │     ├─ common.cpython-311.pyc
   │     │  │  │     ├─ dispatch.cpython-311.pyc
   │     │  │  │     ├─ docstrings.cpython-311.pyc
   │     │  │  │     ├─ invalid.cpython-311.pyc
   │     │  │  │     ├─ mask_ops.cpython-311.pyc
   │     │  │  │     ├─ missing.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ resample.py
   │     │  │  ├─ reshape
   │     │  │  │  ├─ api.py
   │     │  │  │  ├─ concat.py
   │     │  │  │  ├─ encoding.py
   │     │  │  │  ├─ melt.py
   │     │  │  │  ├─ merge.py
   │     │  │  │  ├─ pivot.py
   │     │  │  │  ├─ reshape.py
   │     │  │  │  ├─ tile.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ api.cpython-311.pyc
   │     │  │  │     ├─ concat.cpython-311.pyc
   │     │  │  │     ├─ encoding.cpython-311.pyc
   │     │  │  │     ├─ melt.cpython-311.pyc
   │     │  │  │     ├─ merge.cpython-311.pyc
   │     │  │  │     ├─ pivot.cpython-311.pyc
   │     │  │  │     ├─ reshape.cpython-311.pyc
   │     │  │  │     ├─ tile.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ roperator.py
   │     │  │  ├─ sample.py
   │     │  │  ├─ series.py
   │     │  │  ├─ shared_docs.py
   │     │  │  ├─ sorting.py
   │     │  │  ├─ sparse
   │     │  │  │  ├─ api.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ api.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ strings
   │     │  │  │  ├─ accessor.py
   │     │  │  │  ├─ object_array.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ accessor.cpython-311.pyc
   │     │  │  │     ├─ object_array.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ tools
   │     │  │  │  ├─ datetimes.py
   │     │  │  │  ├─ numeric.py
   │     │  │  │  ├─ timedeltas.py
   │     │  │  │  ├─ times.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ datetimes.cpython-311.pyc
   │     │  │  │     ├─ numeric.cpython-311.pyc
   │     │  │  │     ├─ timedeltas.cpython-311.pyc
   │     │  │  │     ├─ times.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ util
   │     │  │  │  ├─ hashing.py
   │     │  │  │  ├─ numba_.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ hashing.cpython-311.pyc
   │     │  │  │     ├─ numba_.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ window
   │     │  │  │  ├─ common.py
   │     │  │  │  ├─ doc.py
   │     │  │  │  ├─ ewm.py
   │     │  │  │  ├─ expanding.py
   │     │  │  │  ├─ numba_.py
   │     │  │  │  ├─ online.py
   │     │  │  │  ├─ rolling.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ common.cpython-311.pyc
   │     │  │  │     ├─ doc.cpython-311.pyc
   │     │  │  │     ├─ ewm.cpython-311.pyc
   │     │  │  │     ├─ expanding.cpython-311.pyc
   │     │  │  │     ├─ numba_.cpython-311.pyc
   │     │  │  │     ├─ online.cpython-311.pyc
   │     │  │  │     ├─ rolling.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ _numba
   │     │  │  │  ├─ executor.py
   │     │  │  │  ├─ extensions.py
   │     │  │  │  ├─ kernels
   │     │  │  │  │  ├─ mean_.py
   │     │  │  │  │  ├─ min_max_.py
   │     │  │  │  │  ├─ shared.py
   │     │  │  │  │  ├─ sum_.py
   │     │  │  │  │  ├─ var_.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ mean_.cpython-311.pyc
   │     │  │  │  │     ├─ min_max_.cpython-311.pyc
   │     │  │  │  │     ├─ shared.cpython-311.pyc
   │     │  │  │  │     ├─ sum_.cpython-311.pyc
   │     │  │  │  │     ├─ var_.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ executor.cpython-311.pyc
   │     │  │  │     ├─ extensions.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ accessor.cpython-311.pyc
   │     │  │     ├─ algorithms.cpython-311.pyc
   │     │  │     ├─ api.cpython-311.pyc
   │     │  │     ├─ apply.cpython-311.pyc
   │     │  │     ├─ arraylike.cpython-311.pyc
   │     │  │     ├─ base.cpython-311.pyc
   │     │  │     ├─ col.cpython-311.pyc
   │     │  │     ├─ common.cpython-311.pyc
   │     │  │     ├─ config_init.cpython-311.pyc
   │     │  │     ├─ construction.cpython-311.pyc
   │     │  │     ├─ flags.cpython-311.pyc
   │     │  │     ├─ frame.cpython-311.pyc
   │     │  │     ├─ generic.cpython-311.pyc
   │     │  │     ├─ indexing.cpython-311.pyc
   │     │  │     ├─ missing.cpython-311.pyc
   │     │  │     ├─ nanops.cpython-311.pyc
   │     │  │     ├─ resample.cpython-311.pyc
   │     │  │     ├─ roperator.cpython-311.pyc
   │     │  │     ├─ sample.cpython-311.pyc
   │     │  │     ├─ series.cpython-311.pyc
   │     │  │     ├─ shared_docs.cpython-311.pyc
   │     │  │     ├─ sorting.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ errors
   │     │  │  ├─ cow.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ cow.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ io
   │     │  │  ├─ api.py
   │     │  │  ├─ clipboard
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ clipboards.py
   │     │  │  ├─ common.py
   │     │  │  ├─ excel
   │     │  │  │  ├─ _base.py
   │     │  │  │  ├─ _calamine.py
   │     │  │  │  ├─ _odfreader.py
   │     │  │  │  ├─ _odswriter.py
   │     │  │  │  ├─ _openpyxl.py
   │     │  │  │  ├─ _pyxlsb.py
   │     │  │  │  ├─ _util.py
   │     │  │  │  ├─ _xlrd.py
   │     │  │  │  ├─ _xlsxwriter.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ _base.cpython-311.pyc
   │     │  │  │     ├─ _calamine.cpython-311.pyc
   │     │  │  │     ├─ _odfreader.cpython-311.pyc
   │     │  │  │     ├─ _odswriter.cpython-311.pyc
   │     │  │  │     ├─ _openpyxl.cpython-311.pyc
   │     │  │  │     ├─ _pyxlsb.cpython-311.pyc
   │     │  │  │     ├─ _util.cpython-311.pyc
   │     │  │  │     ├─ _xlrd.cpython-311.pyc
   │     │  │  │     ├─ _xlsxwriter.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ feather_format.py
   │     │  │  ├─ formats
   │     │  │  │  ├─ console.py
   │     │  │  │  ├─ css.py
   │     │  │  │  ├─ csvs.py
   │     │  │  │  ├─ excel.py
   │     │  │  │  ├─ format.py
   │     │  │  │  ├─ html.py
   │     │  │  │  ├─ info.py
   │     │  │  │  ├─ printing.py
   │     │  │  │  ├─ string.py
   │     │  │  │  ├─ style.py
   │     │  │  │  ├─ style_render.py
   │     │  │  │  ├─ templates
   │     │  │  │  │  ├─ html.tpl
   │     │  │  │  │  ├─ html_style.tpl
   │     │  │  │  │  ├─ html_table.tpl
   │     │  │  │  │  ├─ latex.tpl
   │     │  │  │  │  ├─ latex_longtable.tpl
   │     │  │  │  │  ├─ latex_table.tpl
   │     │  │  │  │  ├─ string.tpl
   │     │  │  │  │  └─ typst.tpl
   │     │  │  │  ├─ xml.py
   │     │  │  │  ├─ _color_data.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ console.cpython-311.pyc
   │     │  │  │     ├─ css.cpython-311.pyc
   │     │  │  │     ├─ csvs.cpython-311.pyc
   │     │  │  │     ├─ excel.cpython-311.pyc
   │     │  │  │     ├─ format.cpython-311.pyc
   │     │  │  │     ├─ html.cpython-311.pyc
   │     │  │  │     ├─ info.cpython-311.pyc
   │     │  │  │     ├─ printing.cpython-311.pyc
   │     │  │  │     ├─ string.cpython-311.pyc
   │     │  │  │     ├─ style.cpython-311.pyc
   │     │  │  │     ├─ style_render.cpython-311.pyc
   │     │  │  │     ├─ xml.cpython-311.pyc
   │     │  │  │     ├─ _color_data.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ html.py
   │     │  │  ├─ iceberg.py
   │     │  │  ├─ json
   │     │  │  │  ├─ _json.py
   │     │  │  │  ├─ _normalize.py
   │     │  │  │  ├─ _table_schema.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ _json.cpython-311.pyc
   │     │  │  │     ├─ _normalize.cpython-311.pyc
   │     │  │  │     ├─ _table_schema.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ orc.py
   │     │  │  ├─ parquet.py
   │     │  │  ├─ parsers
   │     │  │  │  ├─ arrow_parser_wrapper.py
   │     │  │  │  ├─ base_parser.py
   │     │  │  │  ├─ c_parser_wrapper.py
   │     │  │  │  ├─ python_parser.py
   │     │  │  │  ├─ readers.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ arrow_parser_wrapper.cpython-311.pyc
   │     │  │  │     ├─ base_parser.cpython-311.pyc
   │     │  │  │     ├─ c_parser_wrapper.cpython-311.pyc
   │     │  │  │     ├─ python_parser.cpython-311.pyc
   │     │  │  │     ├─ readers.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ pickle.py
   │     │  │  ├─ pytables.py
   │     │  │  ├─ sas
   │     │  │  │  ├─ sas7bdat.py
   │     │  │  │  ├─ sasreader.py
   │     │  │  │  ├─ sas_constants.py
   │     │  │  │  ├─ sas_xport.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ sas7bdat.cpython-311.pyc
   │     │  │  │     ├─ sasreader.cpython-311.pyc
   │     │  │  │     ├─ sas_constants.cpython-311.pyc
   │     │  │  │     ├─ sas_xport.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ spss.py
   │     │  │  ├─ sql.py
   │     │  │  ├─ stata.py
   │     │  │  ├─ xml.py
   │     │  │  ├─ _util.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ api.cpython-311.pyc
   │     │  │     ├─ clipboards.cpython-311.pyc
   │     │  │     ├─ common.cpython-311.pyc
   │     │  │     ├─ feather_format.cpython-311.pyc
   │     │  │     ├─ html.cpython-311.pyc
   │     │  │     ├─ iceberg.cpython-311.pyc
   │     │  │     ├─ orc.cpython-311.pyc
   │     │  │     ├─ parquet.cpython-311.pyc
   │     │  │     ├─ pickle.cpython-311.pyc
   │     │  │     ├─ pytables.cpython-311.pyc
   │     │  │     ├─ spss.cpython-311.pyc
   │     │  │     ├─ sql.cpython-311.pyc
   │     │  │     ├─ stata.cpython-311.pyc
   │     │  │     ├─ xml.cpython-311.pyc
   │     │  │     ├─ _util.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ plotting
   │     │  │  ├─ _core.py
   │     │  │  ├─ _matplotlib
   │     │  │  │  ├─ boxplot.py
   │     │  │  │  ├─ converter.py
   │     │  │  │  ├─ core.py
   │     │  │  │  ├─ groupby.py
   │     │  │  │  ├─ hist.py
   │     │  │  │  ├─ misc.py
   │     │  │  │  ├─ style.py
   │     │  │  │  ├─ timeseries.py
   │     │  │  │  ├─ tools.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ boxplot.cpython-311.pyc
   │     │  │  │     ├─ converter.cpython-311.pyc
   │     │  │  │     ├─ core.cpython-311.pyc
   │     │  │  │     ├─ groupby.cpython-311.pyc
   │     │  │  │     ├─ hist.cpython-311.pyc
   │     │  │  │     ├─ misc.cpython-311.pyc
   │     │  │  │     ├─ style.cpython-311.pyc
   │     │  │  │     ├─ timeseries.cpython-311.pyc
   │     │  │  │     ├─ tools.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ _misc.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ _core.cpython-311.pyc
   │     │  │     ├─ _misc.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ pyproject.toml
   │     │  ├─ testing.py
   │     │  ├─ tests
   │     │  │  ├─ api
   │     │  │  │  ├─ test_api.py
   │     │  │  │  ├─ test_types.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ test_api.cpython-311.pyc
   │     │  │  │     ├─ test_types.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ apply
   │     │  │  │  ├─ common.py
   │     │  │  │  ├─ conftest.py
   │     │  │  │  ├─ test_frame_apply.py
   │     │  │  │  ├─ test_frame_apply_relabeling.py
   │     │  │  │  ├─ test_frame_transform.py
   │     │  │  │  ├─ test_invalid_arg.py
   │     │  │  │  ├─ test_numba.py
   │     │  │  │  ├─ test_series_apply.py
   │     │  │  │  ├─ test_series_apply_relabeling.py
   │     │  │  │  ├─ test_series_transform.py
   │     │  │  │  ├─ test_str.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ common.cpython-311.pyc
   │     │  │  │     ├─ conftest.cpython-311.pyc
   │     │  │  │     ├─ test_frame_apply.cpython-311.pyc
   │     │  │  │     ├─ test_frame_apply_relabeling.cpython-311.pyc
   │     │  │  │     ├─ test_frame_transform.cpython-311.pyc
   │     │  │  │     ├─ test_invalid_arg.cpython-311.pyc
   │     │  │  │     ├─ test_numba.cpython-311.pyc
   │     │  │  │     ├─ test_series_apply.cpython-311.pyc
   │     │  │  │     ├─ test_series_apply_relabeling.cpython-311.pyc
   │     │  │  │     ├─ test_series_transform.cpython-311.pyc
   │     │  │  │     ├─ test_str.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ arithmetic
   │     │  │  │  ├─ common.py
   │     │  │  │  ├─ conftest.py
   │     │  │  │  ├─ test_array_ops.py
   │     │  │  │  ├─ test_bool.py
   │     │  │  │  ├─ test_categorical.py
   │     │  │  │  ├─ test_datetime64.py
   │     │  │  │  ├─ test_interval.py
   │     │  │  │  ├─ test_numeric.py
   │     │  │  │  ├─ test_object.py
   │     │  │  │  ├─ test_period.py
   │     │  │  │  ├─ test_string.py
   │     │  │  │  ├─ test_timedelta64.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ common.cpython-311.pyc
   │     │  │  │     ├─ conftest.cpython-311.pyc
   │     │  │  │     ├─ test_array_ops.cpython-311.pyc
   │     │  │  │     ├─ test_bool.cpython-311.pyc
   │     │  │  │     ├─ test_categorical.cpython-311.pyc
   │     │  │  │     ├─ test_datetime64.cpython-311.pyc
   │     │  │  │     ├─ test_interval.cpython-311.pyc
   │     │  │  │     ├─ test_numeric.cpython-311.pyc
   │     │  │  │     ├─ test_object.cpython-311.pyc
   │     │  │  │     ├─ test_period.cpython-311.pyc
   │     │  │  │     ├─ test_string.cpython-311.pyc
   │     │  │  │     ├─ test_timedelta64.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ arrays
   │     │  │  │  ├─ boolean
   │     │  │  │  │  ├─ test_arithmetic.py
   │     │  │  │  │  ├─ test_astype.py
   │     │  │  │  │  ├─ test_comparison.py
   │     │  │  │  │  ├─ test_construction.py
   │     │  │  │  │  ├─ test_function.py
   │     │  │  │  │  ├─ test_indexing.py
   │     │  │  │  │  ├─ test_logical.py
   │     │  │  │  │  ├─ test_ops.py
   │     │  │  │  │  ├─ test_reduction.py
   │     │  │  │  │  ├─ test_repr.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ test_arithmetic.cpython-311.pyc
   │     │  │  │  │     ├─ test_astype.cpython-311.pyc
   │     │  │  │  │     ├─ test_comparison.cpython-311.pyc
   │     │  │  │  │     ├─ test_construction.cpython-311.pyc
   │     │  │  │  │     ├─ test_function.cpython-311.pyc
   │     │  │  │  │     ├─ test_indexing.cpython-311.pyc
   │     │  │  │  │     ├─ test_logical.cpython-311.pyc
   │     │  │  │  │     ├─ test_ops.cpython-311.pyc
   │     │  │  │  │     ├─ test_reduction.cpython-311.pyc
   │     │  │  │  │     ├─ test_repr.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ categorical
   │     │  │  │  │  ├─ test_algos.py
   │     │  │  │  │  ├─ test_analytics.py
   │     │  │  │  │  ├─ test_api.py
   │     │  │  │  │  ├─ test_astype.py
   │     │  │  │  │  ├─ test_constructors.py
   │     │  │  │  │  ├─ test_dtypes.py
   │     │  │  │  │  ├─ test_indexing.py
   │     │  │  │  │  ├─ test_map.py
   │     │  │  │  │  ├─ test_missing.py
   │     │  │  │  │  ├─ test_operators.py
   │     │  │  │  │  ├─ test_replace.py
   │     │  │  │  │  ├─ test_repr.py
   │     │  │  │  │  ├─ test_sorting.py
   │     │  │  │  │  ├─ test_subclass.py
   │     │  │  │  │  ├─ test_take.py
   │     │  │  │  │  ├─ test_warnings.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ test_algos.cpython-311.pyc
   │     │  │  │  │     ├─ test_analytics.cpython-311.pyc
   │     │  │  │  │     ├─ test_api.cpython-311.pyc
   │     │  │  │  │     ├─ test_astype.cpython-311.pyc
   │     │  │  │  │     ├─ test_constructors.cpython-311.pyc
   │     │  │  │  │     ├─ test_dtypes.cpython-311.pyc
   │     │  │  │  │     ├─ test_indexing.cpython-311.pyc
   │     │  │  │  │     ├─ test_map.cpython-311.pyc
   │     │  │  │  │     ├─ test_missing.cpython-311.pyc
   │     │  │  │  │     ├─ test_operators.cpython-311.pyc
   │     │  │  │  │     ├─ test_replace.cpython-311.pyc
   │     │  │  │  │     ├─ test_repr.cpython-311.pyc
   │     │  │  │  │     ├─ test_sorting.cpython-311.pyc
   │     │  │  │  │     ├─ test_subclass.cpython-311.pyc
   │     │  │  │  │     ├─ test_take.cpython-311.pyc
   │     │  │  │  │     ├─ test_warnings.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ datetimes
   │     │  │  │  │  ├─ test_constructors.py
   │     │  │  │  │  ├─ test_cumulative.py
   │     │  │  │  │  ├─ test_reductions.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ test_constructors.cpython-311.pyc
   │     │  │  │  │     ├─ test_cumulative.cpython-311.pyc
   │     │  │  │  │     ├─ test_reductions.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ floating
   │     │  │  │  │  ├─ conftest.py
   │     │  │  │  │  ├─ test_arithmetic.py
   │     │  │  │  │  ├─ test_astype.py
   │     │  │  │  │  ├─ test_comparison.py
   │     │  │  │  │  ├─ test_concat.py
   │     │  │  │  │  ├─ test_construction.py
   │     │  │  │  │  ├─ test_contains.py
   │     │  │  │  │  ├─ test_function.py
   │     │  │  │  │  ├─ test_repr.py
   │     │  │  │  │  ├─ test_to_numpy.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ conftest.cpython-311.pyc
   │     │  │  │  │     ├─ test_arithmetic.cpython-311.pyc
   │     │  │  │  │     ├─ test_astype.cpython-311.pyc
   │     │  │  │  │     ├─ test_comparison.cpython-311.pyc
   │     │  │  │  │     ├─ test_concat.cpython-311.pyc
   │     │  │  │  │     ├─ test_construction.cpython-311.pyc
   │     │  │  │  │     ├─ test_contains.cpython-311.pyc
   │     │  │  │  │     ├─ test_function.cpython-311.pyc
   │     │  │  │  │     ├─ test_repr.cpython-311.pyc
   │     │  │  │  │     ├─ test_to_numpy.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ integer
   │     │  │  │  │  ├─ conftest.py
   │     │  │  │  │  ├─ test_arithmetic.py
   │     │  │  │  │  ├─ test_comparison.py
   │     │  │  │  │  ├─ test_concat.py
   │     │  │  │  │  ├─ test_construction.py
   │     │  │  │  │  ├─ test_dtypes.py
   │     │  │  │  │  ├─ test_function.py
   │     │  │  │  │  ├─ test_indexing.py
   │     │  │  │  │  ├─ test_reduction.py
   │     │  │  │  │  ├─ test_repr.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ conftest.cpython-311.pyc
   │     │  │  │  │     ├─ test_arithmetic.cpython-311.pyc
   │     │  │  │  │     ├─ test_comparison.cpython-311.pyc
   │     │  │  │  │     ├─ test_concat.cpython-311.pyc
   │     │  │  │  │     ├─ test_construction.cpython-311.pyc
   │     │  │  │  │     ├─ test_dtypes.cpython-311.pyc
   │     │  │  │  │     ├─ test_function.cpython-311.pyc
   │     │  │  │  │     ├─ test_indexing.cpython-311.pyc
   │     │  │  │  │     ├─ test_reduction.cpython-311.pyc
   │     │  │  │  │     ├─ test_repr.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ interval
   │     │  │  │  │  ├─ test_astype.py
   │     │  │  │  │  ├─ test_formats.py
   │     │  │  │  │  ├─ test_interval.py
   │     │  │  │  │  ├─ test_interval_pyarrow.py
   │     │  │  │  │  ├─ test_overlaps.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ test_astype.cpython-311.pyc
   │     │  │  │  │     ├─ test_formats.cpython-311.pyc
   │     │  │  │  │     ├─ test_interval.cpython-311.pyc
   │     │  │  │  │     ├─ test_interval_pyarrow.cpython-311.pyc
   │     │  │  │  │     ├─ test_overlaps.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ masked
   │     │  │  │  │  ├─ test_arithmetic.py
   │     │  │  │  │  ├─ test_arrow_compat.py
   │     │  │  │  │  ├─ test_function.py
   │     │  │  │  │  ├─ test_indexing.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ test_arithmetic.cpython-311.pyc
   │     │  │  │  │     ├─ test_arrow_compat.cpython-311.pyc
   │     │  │  │  │     ├─ test_function.cpython-311.pyc
   │     │  │  │  │     ├─ test_indexing.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ masked_shared.py
   │     │  │  │  ├─ numpy_
   │     │  │  │  │  ├─ test_indexing.py
   │     │  │  │  │  ├─ test_numpy.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ test_indexing.cpython-311.pyc
   │     │  │  │  │     ├─ test_numpy.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ period
   │     │  │  │  │  ├─ test_arrow_compat.py
   │     │  │  │  │  ├─ test_astype.py
   │     │  │  │  │  ├─ test_constructors.py
   │     │  │  │  │  ├─ test_reductions.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ test_arrow_compat.cpython-311.pyc
   │     │  │  │  │     ├─ test_astype.cpython-311.pyc
   │     │  │  │  │     ├─ test_constructors.cpython-311.pyc
   │     │  │  │  │     ├─ test_reductions.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ sparse
   │     │  │  │  │  ├─ test_accessor.py
   │     │  │  │  │  ├─ test_arithmetics.py
   │     │  │  │  │  ├─ test_array.py
   │     │  │  │  │  ├─ test_astype.py
   │     │  │  │  │  ├─ test_combine_concat.py
   │     │  │  │  │  ├─ test_constructors.py
   │     │  │  │  │  ├─ test_dtype.py
   │     │  │  │  │  ├─ test_indexing.py
   │     │  │  │  │  ├─ test_libsparse.py
   │     │  │  │  │  ├─ test_reductions.py
   │     │  │  │  │  ├─ test_unary.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ test_accessor.cpython-311.pyc
   │     │  │  │  │     ├─ test_arithmetics.cpython-311.pyc
   │     │  │  │  │     ├─ test_array.cpython-311.pyc
   │     │  │  │  │     ├─ test_astype.cpython-311.pyc
   │     │  │  │  │     ├─ test_combine_concat.cpython-311.pyc
   │     │  │  │  │     ├─ test_constructors.cpython-311.pyc
   │     │  │  │  │     ├─ test_dtype.cpython-311.pyc
   │     │  │  │  │     ├─ test_indexing.cpython-311.pyc
   │     │  │  │  │     ├─ test_libsparse.cpython-311.pyc
   │     │  │  │  │     ├─ test_reductions.cpython-311.pyc
   │     │  │  │  │     ├─ test_unary.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ string_
   │     │  │  │  │  ├─ test_concat.py
   │     │  │  │  │  ├─ test_string.py
   │     │  │  │  │  ├─ test_string_arrow.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ test_concat.cpython-311.pyc
   │     │  │  │  │     ├─ test_string.cpython-311.pyc
   │     │  │  │  │     ├─ test_string_arrow.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ test_array.py
   │     │  │  │  ├─ test_datetimelike.py
   │     │  │  │  ├─ test_datetimes.py
   │     │  │  │  ├─ test_ndarray_backed.py
   │     │  │  │  ├─ test_period.py
   │     │  │  │  ├─ test_timedeltas.py
   │     │  │  │  ├─ timedeltas
   │     │  │  │  │  ├─ test_constructors.py
   │     │  │  │  │  ├─ test_cumulative.py
   │     │  │  │  │  ├─ test_reductions.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ test_constructors.cpython-311.pyc
   │     │  │  │  │     ├─ test_cumulative.cpython-311.pyc
   │     │  │  │  │     ├─ test_reductions.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ masked_shared.cpython-311.pyc
   │     │  │  │     ├─ test_array.cpython-311.pyc
   │     │  │  │     ├─ test_datetimelike.cpython-311.pyc
   │     │  │  │     ├─ test_datetimes.cpython-311.pyc
   │     │  │  │     ├─ test_ndarray_backed.cpython-311.pyc
   │     │  │  │     ├─ test_period.cpython-311.pyc
   │     │  │  │     ├─ test_timedeltas.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ base
   │     │  │  │  ├─ common.py
   │     │  │  │  ├─ test_constructors.py
   │     │  │  │  ├─ test_conversion.py
   │     │  │  │  ├─ test_fillna.py
   │     │  │  │  ├─ test_misc.py
   │     │  │  │  ├─ test_transpose.py
   │     │  │  │  ├─ test_unique.py
   │     │  │  │  ├─ test_value_counts.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ common.cpython-311.pyc
   │     │  │  │     ├─ test_constructors.cpython-311.pyc
   │     │  │  │     ├─ test_conversion.cpython-311.pyc
   │     │  │  │     ├─ test_fillna.cpython-311.pyc
   │     │  │  │     ├─ test_misc.cpython-311.pyc
   │     │  │  │     ├─ test_transpose.cpython-311.pyc
   │     │  │  │     ├─ test_unique.cpython-311.pyc
   │     │  │  │     ├─ test_value_counts.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ computation
   │     │  │  │  ├─ test_compat.py
   │     │  │  │  ├─ test_eval.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ test_compat.cpython-311.pyc
   │     │  │  │     ├─ test_eval.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ config
   │     │  │  │  ├─ test_config.py
   │     │  │  │  ├─ test_localization.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ test_config.cpython-311.pyc
   │     │  │  │     ├─ test_localization.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ construction
   │     │  │  │  ├─ test_extract_array.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ test_extract_array.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ copy_view
   │     │  │  │  ├─ index
   │     │  │  │  │  ├─ test_datetimeindex.py
   │     │  │  │  │  ├─ test_index.py
   │     │  │  │  │  ├─ test_intervalindex.py
   │     │  │  │  │  ├─ test_periodindex.py
   │     │  │  │  │  ├─ test_timedeltaindex.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ test_datetimeindex.cpython-311.pyc
   │     │  │  │  │     ├─ test_index.cpython-311.pyc
   │     │  │  │  │     ├─ test_intervalindex.cpython-311.pyc
   │     │  │  │  │     ├─ test_periodindex.cpython-311.pyc
   │     │  │  │  │     ├─ test_timedeltaindex.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ test_array.py
   │     │  │  │  ├─ test_astype.py
   │     │  │  │  ├─ test_chained_assignment_deprecation.py
   │     │  │  │  ├─ test_clip.py
   │     │  │  │  ├─ test_constructors.py
   │     │  │  │  ├─ test_copy_deprecation.py
   │     │  │  │  ├─ test_core_functionalities.py
   │     │  │  │  ├─ test_functions.py
   │     │  │  │  ├─ test_indexing.py
   │     │  │  │  ├─ test_internals.py
   │     │  │  │  ├─ test_interp_fillna.py
   │     │  │  │  ├─ test_methods.py
   │     │  │  │  ├─ test_replace.py
   │     │  │  │  ├─ test_setitem.py
   │     │  │  │  ├─ test_util.py
   │     │  │  │  ├─ util.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ test_array.cpython-311.pyc
   │     │  │  │     ├─ test_astype.cpython-311.pyc
   │     │  │  │     ├─ test_chained_assignment_deprecation.cpython-311.pyc
   │     │  │  │     ├─ test_clip.cpython-311.pyc
   │     │  │  │     ├─ test_constructors.cpython-311.pyc
   │     │  │  │     ├─ test_copy_deprecation.cpython-311.pyc
   │     │  │  │     ├─ test_core_functionalities.cpython-311.pyc
   │     │  │  │     ├─ test_functions.cpython-311.pyc
   │     │  │  │     ├─ test_indexing.cpython-311.pyc
   │     │  │  │     ├─ test_internals.cpython-311.pyc
   │     │  │  │     ├─ test_interp_fillna.cpython-311.pyc
   │     │  │  │     ├─ test_methods.cpython-311.pyc
   │     │  │  │     ├─ test_replace.cpython-311.pyc
   │     │  │  │     ├─ test_setitem.cpython-311.pyc
   │     │  │  │     ├─ test_util.cpython-311.pyc
   │     │  │  │     ├─ util.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ dtypes
   │     │  │  │  ├─ cast
   │     │  │  │  │  ├─ test_box_unbox.py
   │     │  │  │  │  ├─ test_can_hold_element.py
   │     │  │  │  │  ├─ test_construct_from_scalar.py
   │     │  │  │  │  ├─ test_construct_ndarray.py
   │     │  │  │  │  ├─ test_construct_object_arr.py
   │     │  │  │  │  ├─ test_dict_compat.py
   │     │  │  │  │  ├─ test_downcast.py
   │     │  │  │  │  ├─ test_find_common_type.py
   │     │  │  │  │  ├─ test_infer_datetimelike.py
   │     │  │  │  │  ├─ test_infer_dtype.py
   │     │  │  │  │  ├─ test_promote.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ test_box_unbox.cpython-311.pyc
   │     │  │  │  │     ├─ test_can_hold_element.cpython-311.pyc
   │     │  │  │  │     ├─ test_construct_from_scalar.cpython-311.pyc
   │     │  │  │  │     ├─ test_construct_ndarray.cpython-311.pyc
   │     │  │  │  │     ├─ test_construct_object_arr.cpython-311.pyc
   │     │  │  │  │     ├─ test_dict_compat.cpython-311.pyc
   │     │  │  │  │     ├─ test_downcast.cpython-311.pyc
   │     │  │  │  │     ├─ test_find_common_type.cpython-311.pyc
   │     │  │  │  │     ├─ test_infer_datetimelike.cpython-311.pyc
   │     │  │  │  │     ├─ test_infer_dtype.cpython-311.pyc
   │     │  │  │  │     ├─ test_promote.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ test_common.py
   │     │  │  │  ├─ test_concat.py
   │     │  │  │  ├─ test_dtypes.py
   │     │  │  │  ├─ test_generic.py
   │     │  │  │  ├─ test_inference.py
   │     │  │  │  ├─ test_missing.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ test_common.cpython-311.pyc
   │     │  │  │     ├─ test_concat.cpython-311.pyc
   │     │  │  │     ├─ test_dtypes.cpython-311.pyc
   │     │  │  │     ├─ test_generic.cpython-311.pyc
   │     │  │  │     ├─ test_inference.cpython-311.pyc
   │     │  │  │     ├─ test_missing.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ extension
   │     │  │  │  ├─ array_with_attr
   │     │  │  │  │  ├─ array.py
   │     │  │  │  │  ├─ test_array_with_attr.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ array.cpython-311.pyc
   │     │  │  │  │     ├─ test_array_with_attr.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ base
   │     │  │  │  │  ├─ accumulate.py
   │     │  │  │  │  ├─ base.py
   │     │  │  │  │  ├─ casting.py
   │     │  │  │  │  ├─ constructors.py
   │     │  │  │  │  ├─ dim2.py
   │     │  │  │  │  ├─ dtype.py
   │     │  │  │  │  ├─ getitem.py
   │     │  │  │  │  ├─ groupby.py
   │     │  │  │  │  ├─ index.py
   │     │  │  │  │  ├─ interface.py
   │     │  │  │  │  ├─ io.py
   │     │  │  │  │  ├─ methods.py
   │     │  │  │  │  ├─ missing.py
   │     │  │  │  │  ├─ ops.py
   │     │  │  │  │  ├─ printing.py
   │     │  │  │  │  ├─ reduce.py
   │     │  │  │  │  ├─ reshaping.py
   │     │  │  │  │  ├─ setitem.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ accumulate.cpython-311.pyc
   │     │  │  │  │     ├─ base.cpython-311.pyc
   │     │  │  │  │     ├─ casting.cpython-311.pyc
   │     │  │  │  │     ├─ constructors.cpython-311.pyc
   │     │  │  │  │     ├─ dim2.cpython-311.pyc
   │     │  │  │  │     ├─ dtype.cpython-311.pyc
   │     │  │  │  │     ├─ getitem.cpython-311.pyc
   │     │  │  │  │     ├─ groupby.cpython-311.pyc
   │     │  │  │  │     ├─ index.cpython-311.pyc
   │     │  │  │  │     ├─ interface.cpython-311.pyc
   │     │  │  │  │     ├─ io.cpython-311.pyc
   │     │  │  │  │     ├─ methods.cpython-311.pyc
   │     │  │  │  │     ├─ missing.cpython-311.pyc
   │     │  │  │  │     ├─ ops.cpython-311.pyc
   │     │  │  │  │     ├─ printing.cpython-311.pyc
   │     │  │  │  │     ├─ reduce.cpython-311.pyc
   │     │  │  │  │     ├─ reshaping.cpython-311.pyc
   │     │  │  │  │     ├─ setitem.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ conftest.py
   │     │  │  │  ├─ date
   │     │  │  │  │  ├─ array.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ array.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ decimal
   │     │  │  │  │  ├─ array.py
   │     │  │  │  │  ├─ test_decimal.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ array.cpython-311.pyc
   │     │  │  │  │     ├─ test_decimal.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ json
   │     │  │  │  │  ├─ array.py
   │     │  │  │  │  ├─ test_json.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ array.cpython-311.pyc
   │     │  │  │  │     ├─ test_json.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ list
   │     │  │  │  │  ├─ array.py
   │     │  │  │  │  ├─ test_list.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ array.cpython-311.pyc
   │     │  │  │  │     ├─ test_list.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ test_arrow.py
   │     │  │  │  ├─ test_categorical.py
   │     │  │  │  ├─ test_common.py
   │     │  │  │  ├─ test_datetime.py
   │     │  │  │  ├─ test_extension.py
   │     │  │  │  ├─ test_interval.py
   │     │  │  │  ├─ test_masked.py
   │     │  │  │  ├─ test_numpy.py
   │     │  │  │  ├─ test_period.py
   │     │  │  │  ├─ test_sparse.py
   │     │  │  │  ├─ test_string.py
   │     │  │  │  ├─ uuid
   │     │  │  │  │  ├─ test_uuid.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ test_uuid.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ conftest.cpython-311.pyc
   │     │  │  │     ├─ test_arrow.cpython-311.pyc
   │     │  │  │     ├─ test_categorical.cpython-311.pyc
   │     │  │  │     ├─ test_common.cpython-311.pyc
   │     │  │  │     ├─ test_datetime.cpython-311.pyc
   │     │  │  │     ├─ test_extension.cpython-311.pyc
   │     │  │  │     ├─ test_interval.cpython-311.pyc
   │     │  │  │     ├─ test_masked.cpython-311.pyc
   │     │  │  │     ├─ test_numpy.cpython-311.pyc
   │     │  │  │     ├─ test_period.cpython-311.pyc
   │     │  │  │     ├─ test_sparse.cpython-311.pyc
   │     │  │  │     ├─ test_string.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ frame
   │     │  │  │  ├─ common.py
   │     │  │  │  ├─ conftest.py
   │     │  │  │  ├─ constructors
   │     │  │  │  │  ├─ test_from_dict.py
   │     │  │  │  │  ├─ test_from_records.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ test_from_dict.cpython-311.pyc
   │     │  │  │  │     ├─ test_from_records.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ indexing
   │     │  │  │  │  ├─ test_coercion.py
   │     │  │  │  │  ├─ test_delitem.py
   │     │  │  │  │  ├─ test_get.py
   │     │  │  │  │  ├─ test_getitem.py
   │     │  │  │  │  ├─ test_get_value.py
   │     │  │  │  │  ├─ test_indexing.py
   │     │  │  │  │  ├─ test_insert.py
   │     │  │  │  │  ├─ test_mask.py
   │     │  │  │  │  ├─ test_setitem.py
   │     │  │  │  │  ├─ test_set_value.py
   │     │  │  │  │  ├─ test_take.py
   │     │  │  │  │  ├─ test_where.py
   │     │  │  │  │  ├─ test_xs.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ test_coercion.cpython-311.pyc
   │     │  │  │  │     ├─ test_delitem.cpython-311.pyc
   │     │  │  │  │     ├─ test_get.cpython-311.pyc
   │     │  │  │  │     ├─ test_getitem.cpython-311.pyc
   │     │  │  │  │     ├─ test_get_value.cpython-311.pyc
   │     │  │  │  │     ├─ test_indexing.cpython-311.pyc
   │     │  │  │  │     ├─ test_insert.cpython-311.pyc
   │     │  │  │  │     ├─ test_mask.cpython-311.pyc
   │     │  │  │  │     ├─ test_setitem.cpython-311.pyc
   │     │  │  │  │     ├─ test_set_value.cpython-311.pyc
   │     │  │  │  │     ├─ test_take.cpython-311.pyc
   │     │  │  │  │     ├─ test_where.cpython-311.pyc
   │     │  │  │  │     ├─ test_xs.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ methods
   │     │  │  │  │  ├─ test_add_prefix_suffix.py
   │     │  │  │  │  ├─ test_align.py
   │     │  │  │  │  ├─ test_asfreq.py
   │     │  │  │  │  ├─ test_asof.py
   │     │  │  │  │  ├─ test_assign.py
   │     │  │  │  │  ├─ test_astype.py
   │     │  │  │  │  ├─ test_at_time.py
   │     │  │  │  │  ├─ test_between_time.py
   │     │  │  │  │  ├─ test_clip.py
   │     │  │  │  │  ├─ test_combine.py
   │     │  │  │  │  ├─ test_combine_first.py
   │     │  │  │  │  ├─ test_compare.py
   │     │  │  │  │  ├─ test_convert_dtypes.py
   │     │  │  │  │  ├─ test_copy.py
   │     │  │  │  │  ├─ test_count.py
   │     │  │  │  │  ├─ test_cov_corr.py
   │     │  │  │  │  ├─ test_describe.py
   │     │  │  │  │  ├─ test_diff.py
   │     │  │  │  │  ├─ test_dot.py
   │     │  │  │  │  ├─ test_drop.py
   │     │  │  │  │  ├─ test_droplevel.py
   │     │  │  │  │  ├─ test_dropna.py
   │     │  │  │  │  ├─ test_drop_duplicates.py
   │     │  │  │  │  ├─ test_dtypes.py
   │     │  │  │  │  ├─ test_duplicated.py
   │     │  │  │  │  ├─ test_equals.py
   │     │  │  │  │  ├─ test_explode.py
   │     │  │  │  │  ├─ test_fillna.py
   │     │  │  │  │  ├─ test_filter.py
   │     │  │  │  │  ├─ test_first_valid_index.py
   │     │  │  │  │  ├─ test_get_numeric_data.py
   │     │  │  │  │  ├─ test_head_tail.py
   │     │  │  │  │  ├─ test_infer_objects.py
   │     │  │  │  │  ├─ test_info.py
   │     │  │  │  │  ├─ test_interpolate.py
   │     │  │  │  │  ├─ test_isetitem.py
   │     │  │  │  │  ├─ test_isin.py
   │     │  │  │  │  ├─ test_is_homogeneous_dtype.py
   │     │  │  │  │  ├─ test_iterrows.py
   │     │  │  │  │  ├─ test_join.py
   │     │  │  │  │  ├─ test_map.py
   │     │  │  │  │  ├─ test_matmul.py
   │     │  │  │  │  ├─ test_nlargest.py
   │     │  │  │  │  ├─ test_pct_change.py
   │     │  │  │  │  ├─ test_pipe.py
   │     │  │  │  │  ├─ test_pop.py
   │     │  │  │  │  ├─ test_quantile.py
   │     │  │  │  │  ├─ test_rank.py
   │     │  │  │  │  ├─ test_reindex.py
   │     │  │  │  │  ├─ test_reindex_like.py
   │     │  │  │  │  ├─ test_rename.py
   │     │  │  │  │  ├─ test_rename_axis.py
   │     │  │  │  │  ├─ test_reorder_levels.py
   │     │  │  │  │  ├─ test_replace.py
   │     │  │  │  │  ├─ test_reset_index.py
   │     │  │  │  │  ├─ test_round.py
   │     │  │  │  │  ├─ test_sample.py
   │     │  │  │  │  ├─ test_select_dtypes.py
   │     │  │  │  │  ├─ test_set_axis.py
   │     │  │  │  │  ├─ test_set_index.py
   │     │  │  │  │  ├─ test_shift.py
   │     │  │  │  │  ├─ test_size.py
   │     │  │  │  │  ├─ test_sort_index.py
   │     │  │  │  │  ├─ test_sort_values.py
   │     │  │  │  │  ├─ test_swaplevel.py
   │     │  │  │  │  ├─ test_to_csv.py
   │     │  │  │  │  ├─ test_to_dict.py
   │     │  │  │  │  ├─ test_to_dict_of_blocks.py
   │     │  │  │  │  ├─ test_to_numpy.py
   │     │  │  │  │  ├─ test_to_period.py
   │     │  │  │  │  ├─ test_to_records.py
   │     │  │  │  │  ├─ test_to_timestamp.py
   │     │  │  │  │  ├─ test_transpose.py
   │     │  │  │  │  ├─ test_truncate.py
   │     │  │  │  │  ├─ test_tz_convert.py
   │     │  │  │  │  ├─ test_tz_localize.py
   │     │  │  │  │  ├─ test_update.py
   │     │  │  │  │  ├─ test_values.py
   │     │  │  │  │  ├─ test_value_counts.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ test_add_prefix_suffix.cpython-311.pyc
   │     │  │  │  │     ├─ test_align.cpython-311.pyc
   │     │  │  │  │     ├─ test_asfreq.cpython-311.pyc
   │     │  │  │  │     ├─ test_asof.cpython-311.pyc
   │     │  │  │  │     ├─ test_assign.cpython-311.pyc
   │     │  │  │  │     ├─ test_astype.cpython-311.pyc
   │     │  │  │  │     ├─ test_at_time.cpython-311.pyc
   │     │  │  │  │     ├─ test_between_time.cpython-311.pyc
   │     │  │  │  │     ├─ test_clip.cpython-311.pyc
   │     │  │  │  │     ├─ test_combine.cpython-311.pyc
   │     │  │  │  │     ├─ test_combine_first.cpython-311.pyc
   │     │  │  │  │     ├─ test_compare.cpython-311.pyc
   │     │  │  │  │     ├─ test_convert_dtypes.cpython-311.pyc
   │     │  │  │  │     ├─ test_copy.cpython-311.pyc
   │     │  │  │  │     ├─ test_count.cpython-311.pyc
   │     │  │  │  │     ├─ test_cov_corr.cpython-311.pyc
   │     │  │  │  │     ├─ test_describe.cpython-311.pyc
   │     │  │  │  │     ├─ test_diff.cpython-311.pyc
   │     │  │  │  │     ├─ test_dot.cpython-311.pyc
   │     │  │  │  │     ├─ test_drop.cpython-311.pyc
   │     │  │  │  │     ├─ test_droplevel.cpython-311.pyc
   │     │  │  │  │     ├─ test_dropna.cpython-311.pyc
   │     │  │  │  │     ├─ test_drop_duplicates.cpython-311.pyc
   │     │  │  │  │     ├─ test_dtypes.cpython-311.pyc
   │     │  │  │  │     ├─ test_duplicated.cpython-311.pyc
   │     │  │  │  │     ├─ test_equals.cpython-311.pyc
   │     │  │  │  │     ├─ test_explode.cpython-311.pyc
   │     │  │  │  │     ├─ test_fillna.cpython-311.pyc
   │     │  │  │  │     ├─ test_filter.cpython-311.pyc
   │     │  │  │  │     ├─ test_first_valid_index.cpython-311.pyc
   │     │  │  │  │     ├─ test_get_numeric_data.cpython-311.pyc
   │     │  │  │  │     ├─ test_head_tail.cpython-311.pyc
   │     │  │  │  │     ├─ test_infer_objects.cpython-311.pyc
   │     │  │  │  │     ├─ test_info.cpython-311.pyc
   │     │  │  │  │     ├─ test_interpolate.cpython-311.pyc
   │     │  │  │  │     ├─ test_isetitem.cpython-311.pyc
   │     │  │  │  │     ├─ test_isin.cpython-311.pyc
   │     │  │  │  │     ├─ test_is_homogeneous_dtype.cpython-311.pyc
   │     │  │  │  │     ├─ test_iterrows.cpython-311.pyc
   │     │  │  │  │     ├─ test_join.cpython-311.pyc
   │     │  │  │  │     ├─ test_map.cpython-311.pyc
   │     │  │  │  │     ├─ test_matmul.cpython-311.pyc
   │     │  │  │  │     ├─ test_nlargest.cpython-311.pyc
   │     │  │  │  │     ├─ test_pct_change.cpython-311.pyc
   │     │  │  │  │     ├─ test_pipe.cpython-311.pyc
   │     │  │  │  │     ├─ test_pop.cpython-311.pyc
   │     │  │  │  │     ├─ test_quantile.cpython-311.pyc
   │     │  │  │  │     ├─ test_rank.cpython-311.pyc
   │     │  │  │  │     ├─ test_reindex.cpython-311.pyc
   │     │  │  │  │     ├─ test_reindex_like.cpython-311.pyc
   │     │  │  │  │     ├─ test_rename.cpython-311.pyc
   │     │  │  │  │     ├─ test_rename_axis.cpython-311.pyc
   │     │  │  │  │     ├─ test_reorder_levels.cpython-311.pyc
   │     │  │  │  │     ├─ test_replace.cpython-311.pyc
   │     │  │  │  │     ├─ test_reset_index.cpython-311.pyc
   │     │  │  │  │     ├─ test_round.cpython-311.pyc
   │     │  │  │  │     ├─ test_sample.cpython-311.pyc
   │     │  │  │  │     ├─ test_select_dtypes.cpython-311.pyc
   │     │  │  │  │     ├─ test_set_axis.cpython-311.pyc
   │     │  │  │  │     ├─ test_set_index.cpython-311.pyc
   │     │  │  │  │     ├─ test_shift.cpython-311.pyc
   │     │  │  │  │     ├─ test_size.cpython-311.pyc
   │     │  │  │  │     ├─ test_sort_index.cpython-311.pyc
   │     │  │  │  │     ├─ test_sort_values.cpython-311.pyc
   │     │  │  │  │     ├─ test_swaplevel.cpython-311.pyc
   │     │  │  │  │     ├─ test_to_csv.cpython-311.pyc
   │     │  │  │  │     ├─ test_to_dict.cpython-311.pyc
   │     │  │  │  │     ├─ test_to_dict_of_blocks.cpython-311.pyc
   │     │  │  │  │     ├─ test_to_numpy.cpython-311.pyc
   │     │  │  │  │     ├─ test_to_period.cpython-311.pyc
   │     │  │  │  │     ├─ test_to_records.cpython-311.pyc
   │     │  │  │  │     ├─ test_to_timestamp.cpython-311.pyc
   │     │  │  │  │     ├─ test_transpose.cpython-311.pyc
   │     │  │  │  │     ├─ test_truncate.cpython-311.pyc
   │     │  │  │  │     ├─ test_tz_convert.cpython-311.pyc
   │     │  │  │  │     ├─ test_tz_localize.cpython-311.pyc
   │     │  │  │  │     ├─ test_update.cpython-311.pyc
   │     │  │  │  │     ├─ test_values.cpython-311.pyc
   │     │  │  │  │     ├─ test_value_counts.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ test_alter_axes.py
   │     │  │  │  ├─ test_api.py
   │     │  │  │  ├─ test_arithmetic.py
   │     │  │  │  ├─ test_arrow_interface.py
   │     │  │  │  ├─ test_block_internals.py
   │     │  │  │  ├─ test_constructors.py
   │     │  │  │  ├─ test_cumulative.py
   │     │  │  │  ├─ test_iteration.py
   │     │  │  │  ├─ test_logical_ops.py
   │     │  │  │  ├─ test_nonunique_indexes.py
   │     │  │  │  ├─ test_npfuncs.py
   │     │  │  │  ├─ test_query_eval.py
   │     │  │  │  ├─ test_reductions.py
   │     │  │  │  ├─ test_repr.py
   │     │  │  │  ├─ test_stack_unstack.py
   │     │  │  │  ├─ test_subclass.py
   │     │  │  │  ├─ test_ufunc.py
   │     │  │  │  ├─ test_unary.py
   │     │  │  │  ├─ test_validate.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ common.cpython-311.pyc
   │     │  │  │     ├─ conftest.cpython-311.pyc
   │     │  │  │     ├─ test_alter_axes.cpython-311.pyc
   │     │  │  │     ├─ test_api.cpython-311.pyc
   │     │  │  │     ├─ test_arithmetic.cpython-311.pyc
   │     │  │  │     ├─ test_arrow_interface.cpython-311.pyc
   │     │  │  │     ├─ test_block_internals.cpython-311.pyc
   │     │  │  │     ├─ test_constructors.cpython-311.pyc
   │     │  │  │     ├─ test_cumulative.cpython-311.pyc
   │     │  │  │     ├─ test_iteration.cpython-311.pyc
   │     │  │  │     ├─ test_logical_ops.cpython-311.pyc
   │     │  │  │     ├─ test_nonunique_indexes.cpython-311.pyc
   │     │  │  │     ├─ test_npfuncs.cpython-311.pyc
   │     │  │  │     ├─ test_query_eval.cpython-311.pyc
   │     │  │  │     ├─ test_reductions.cpython-311.pyc
   │     │  │  │     ├─ test_repr.cpython-311.pyc
   │     │  │  │     ├─ test_stack_unstack.cpython-311.pyc
   │     │  │  │     ├─ test_subclass.cpython-311.pyc
   │     │  │  │     ├─ test_ufunc.cpython-311.pyc
   │     │  │  │     ├─ test_unary.cpython-311.pyc
   │     │  │  │     ├─ test_validate.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ generic
   │     │  │  │  ├─ test_duplicate_labels.py
   │     │  │  │  ├─ test_finalize.py
   │     │  │  │  ├─ test_frame.py
   │     │  │  │  ├─ test_generic.py
   │     │  │  │  ├─ test_label_or_level_utils.py
   │     │  │  │  ├─ test_series.py
   │     │  │  │  ├─ test_to_xarray.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ test_duplicate_labels.cpython-311.pyc
   │     │  │  │     ├─ test_finalize.cpython-311.pyc
   │     │  │  │     ├─ test_frame.cpython-311.pyc
   │     │  │  │     ├─ test_generic.cpython-311.pyc
   │     │  │  │     ├─ test_label_or_level_utils.cpython-311.pyc
   │     │  │  │     ├─ test_series.cpython-311.pyc
   │     │  │  │     ├─ test_to_xarray.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ groupby
   │     │  │  │  ├─ aggregate
   │     │  │  │  │  ├─ test_aggregate.py
   │     │  │  │  │  ├─ test_cython.py
   │     │  │  │  │  ├─ test_numba.py
   │     │  │  │  │  ├─ test_other.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ test_aggregate.cpython-311.pyc
   │     │  │  │  │     ├─ test_cython.cpython-311.pyc
   │     │  │  │  │     ├─ test_numba.cpython-311.pyc
   │     │  │  │  │     ├─ test_other.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ conftest.py
   │     │  │  │  ├─ methods
   │     │  │  │  │  ├─ test_describe.py
   │     │  │  │  │  ├─ test_groupby_shift_diff.py
   │     │  │  │  │  ├─ test_is_monotonic.py
   │     │  │  │  │  ├─ test_kurt.py
   │     │  │  │  │  ├─ test_nlargest_nsmallest.py
   │     │  │  │  │  ├─ test_nth.py
   │     │  │  │  │  ├─ test_quantile.py
   │     │  │  │  │  ├─ test_rank.py
   │     │  │  │  │  ├─ test_sample.py
   │     │  │  │  │  ├─ test_size.py
   │     │  │  │  │  ├─ test_skew.py
   │     │  │  │  │  ├─ test_value_counts.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ test_describe.cpython-311.pyc
   │     │  │  │  │     ├─ test_groupby_shift_diff.cpython-311.pyc
   │     │  │  │  │     ├─ test_is_monotonic.cpython-311.pyc
   │     │  │  │  │     ├─ test_kurt.cpython-311.pyc
   │     │  │  │  │     ├─ test_nlargest_nsmallest.cpython-311.pyc
   │     │  │  │  │     ├─ test_nth.cpython-311.pyc
   │     │  │  │  │     ├─ test_quantile.cpython-311.pyc
   │     │  │  │  │     ├─ test_rank.cpython-311.pyc
   │     │  │  │  │     ├─ test_sample.cpython-311.pyc
   │     │  │  │  │     ├─ test_size.cpython-311.pyc
   │     │  │  │  │     ├─ test_skew.cpython-311.pyc
   │     │  │  │  │     ├─ test_value_counts.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ test_all_methods.py
   │     │  │  │  ├─ test_api.py
   │     │  │  │  ├─ test_apply.py
   │     │  │  │  ├─ test_bin_groupby.py
   │     │  │  │  ├─ test_categorical.py
   │     │  │  │  ├─ test_counting.py
   │     │  │  │  ├─ test_cumulative.py
   │     │  │  │  ├─ test_filters.py
   │     │  │  │  ├─ test_groupby.py
   │     │  │  │  ├─ test_groupby_dropna.py
   │     │  │  │  ├─ test_groupby_subclass.py
   │     │  │  │  ├─ test_grouping.py
   │     │  │  │  ├─ test_indexing.py
   │     │  │  │  ├─ test_index_as_string.py
   │     │  │  │  ├─ test_libgroupby.py
   │     │  │  │  ├─ test_missing.py
   │     │  │  │  ├─ test_numba.py
   │     │  │  │  ├─ test_numeric_only.py
   │     │  │  │  ├─ test_pipe.py
   │     │  │  │  ├─ test_raises.py
   │     │  │  │  ├─ test_reductions.py
   │     │  │  │  ├─ test_timegrouper.py
   │     │  │  │  ├─ transform
   │     │  │  │  │  ├─ test_numba.py
   │     │  │  │  │  ├─ test_transform.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ test_numba.cpython-311.pyc
   │     │  │  │  │     ├─ test_transform.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ conftest.cpython-311.pyc
   │     │  │  │     ├─ test_all_methods.cpython-311.pyc
   │     │  │  │     ├─ test_api.cpython-311.pyc
   │     │  │  │     ├─ test_apply.cpython-311.pyc
   │     │  │  │     ├─ test_bin_groupby.cpython-311.pyc
   │     │  │  │     ├─ test_categorical.cpython-311.pyc
   │     │  │  │     ├─ test_counting.cpython-311.pyc
   │     │  │  │     ├─ test_cumulative.cpython-311.pyc
   │     │  │  │     ├─ test_filters.cpython-311.pyc
   │     │  │  │     ├─ test_groupby.cpython-311.pyc
   │     │  │  │     ├─ test_groupby_dropna.cpython-311.pyc
   │     │  │  │     ├─ test_groupby_subclass.cpython-311.pyc
   │     │  │  │     ├─ test_grouping.cpython-311.pyc
   │     │  │  │     ├─ test_indexing.cpython-311.pyc
   │     │  │  │     ├─ test_index_as_string.cpython-311.pyc
   │     │  │  │     ├─ test_libgroupby.cpython-311.pyc
   │     │  │  │     ├─ test_missing.cpython-311.pyc
   │     │  │  │     ├─ test_numba.cpython-311.pyc
   │     │  │  │     ├─ test_numeric_only.cpython-311.pyc
   │     │  │  │     ├─ test_pipe.cpython-311.pyc
   │     │  │  │     ├─ test_raises.cpython-311.pyc
   │     │  │  │     ├─ test_reductions.cpython-311.pyc
   │     │  │  │     ├─ test_timegrouper.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ indexes
   │     │  │  │  ├─ base_class
   │     │  │  │  │  ├─ test_constructors.py
   │     │  │  │  │  ├─ test_formats.py
   │     │  │  │  │  ├─ test_indexing.py
   │     │  │  │  │  ├─ test_pickle.py
   │     │  │  │  │  ├─ test_reshape.py
   │     │  │  │  │  ├─ test_setops.py
   │     │  │  │  │  ├─ test_where.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ test_constructors.cpython-311.pyc
   │     │  │  │  │     ├─ test_formats.cpython-311.pyc
   │     │  │  │  │     ├─ test_indexing.cpython-311.pyc
   │     │  │  │  │     ├─ test_pickle.cpython-311.pyc
   │     │  │  │  │     ├─ test_reshape.cpython-311.pyc
   │     │  │  │  │     ├─ test_setops.cpython-311.pyc
   │     │  │  │  │     ├─ test_where.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ categorical
   │     │  │  │  │  ├─ test_append.py
   │     │  │  │  │  ├─ test_astype.py
   │     │  │  │  │  ├─ test_category.py
   │     │  │  │  │  ├─ test_constructors.py
   │     │  │  │  │  ├─ test_equals.py
   │     │  │  │  │  ├─ test_fillna.py
   │     │  │  │  │  ├─ test_formats.py
   │     │  │  │  │  ├─ test_indexing.py
   │     │  │  │  │  ├─ test_map.py
   │     │  │  │  │  ├─ test_reindex.py
   │     │  │  │  │  ├─ test_setops.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ test_append.cpython-311.pyc
   │     │  │  │  │     ├─ test_astype.cpython-311.pyc
   │     │  │  │  │     ├─ test_category.cpython-311.pyc
   │     │  │  │  │     ├─ test_constructors.cpython-311.pyc
   │     │  │  │  │     ├─ test_equals.cpython-311.pyc
   │     │  │  │  │     ├─ test_fillna.cpython-311.pyc
   │     │  │  │  │     ├─ test_formats.cpython-311.pyc
   │     │  │  │  │     ├─ test_indexing.cpython-311.pyc
   │     │  │  │  │     ├─ test_map.cpython-311.pyc
   │     │  │  │  │     ├─ test_reindex.cpython-311.pyc
   │     │  │  │  │     ├─ test_setops.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ conftest.py
   │     │  │  │  ├─ datetimelike_
   │     │  │  │  │  ├─ test_drop_duplicates.py
   │     │  │  │  │  ├─ test_equals.py
   │     │  │  │  │  ├─ test_indexing.py
   │     │  │  │  │  ├─ test_is_monotonic.py
   │     │  │  │  │  ├─ test_nat.py
   │     │  │  │  │  ├─ test_sort_values.py
   │     │  │  │  │  ├─ test_value_counts.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ test_drop_duplicates.cpython-311.pyc
   │     │  │  │  │     ├─ test_equals.cpython-311.pyc
   │     │  │  │  │     ├─ test_indexing.cpython-311.pyc
   │     │  │  │  │     ├─ test_is_monotonic.cpython-311.pyc
   │     │  │  │  │     ├─ test_nat.cpython-311.pyc
   │     │  │  │  │     ├─ test_sort_values.cpython-311.pyc
   │     │  │  │  │     ├─ test_value_counts.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ datetimes
   │     │  │  │  │  ├─ methods
   │     │  │  │  │  │  ├─ test_asof.py
   │     │  │  │  │  │  ├─ test_astype.py
   │     │  │  │  │  │  ├─ test_delete.py
   │     │  │  │  │  │  ├─ test_factorize.py
   │     │  │  │  │  │  ├─ test_fillna.py
   │     │  │  │  │  │  ├─ test_insert.py
   │     │  │  │  │  │  ├─ test_isocalendar.py
   │     │  │  │  │  │  ├─ test_map.py
   │     │  │  │  │  │  ├─ test_normalize.py
   │     │  │  │  │  │  ├─ test_repeat.py
   │     │  │  │  │  │  ├─ test_resolution.py
   │     │  │  │  │  │  ├─ test_round.py
   │     │  │  │  │  │  ├─ test_shift.py
   │     │  │  │  │  │  ├─ test_snap.py
   │     │  │  │  │  │  ├─ test_to_frame.py
   │     │  │  │  │  │  ├─ test_to_julian_date.py
   │     │  │  │  │  │  ├─ test_to_period.py
   │     │  │  │  │  │  ├─ test_to_pydatetime.py
   │     │  │  │  │  │  ├─ test_to_series.py
   │     │  │  │  │  │  ├─ test_tz_convert.py
   │     │  │  │  │  │  ├─ test_tz_localize.py
   │     │  │  │  │  │  ├─ test_unique.py
   │     │  │  │  │  │  ├─ __init__.py
   │     │  │  │  │  │  └─ __pycache__
   │     │  │  │  │  │     ├─ test_asof.cpython-311.pyc
   │     │  │  │  │  │     ├─ test_astype.cpython-311.pyc
   │     │  │  │  │  │     ├─ test_delete.cpython-311.pyc
   │     │  │  │  │  │     ├─ test_factorize.cpython-311.pyc
   │     │  │  │  │  │     ├─ test_fillna.cpython-311.pyc
   │     │  │  │  │  │     ├─ test_insert.cpython-311.pyc
   │     │  │  │  │  │     ├─ test_isocalendar.cpython-311.pyc
   │     │  │  │  │  │     ├─ test_map.cpython-311.pyc
   │     │  │  │  │  │     ├─ test_normalize.cpython-311.pyc
   │     │  │  │  │  │     ├─ test_repeat.cpython-311.pyc
   │     │  │  │  │  │     ├─ test_resolution.cpython-311.pyc
   │     │  │  │  │  │     ├─ test_round.cpython-311.pyc
   │     │  │  │  │  │     ├─ test_shift.cpython-311.pyc
   │     │  │  │  │  │     ├─ test_snap.cpython-311.pyc
   │     │  │  │  │  │     ├─ test_to_frame.cpython-311.pyc
   │     │  │  │  │  │     ├─ test_to_julian_date.cpython-311.pyc
   │     │  │  │  │  │     ├─ test_to_period.cpython-311.pyc
   │     │  │  │  │  │     ├─ test_to_pydatetime.cpython-311.pyc
   │     │  │  │  │  │     ├─ test_to_series.cpython-311.pyc
   │     │  │  │  │  │     ├─ test_tz_convert.cpython-311.pyc
   │     │  │  │  │  │     ├─ test_tz_localize.cpython-311.pyc
   │     │  │  │  │  │     ├─ test_unique.cpython-311.pyc
   │     │  │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  │  ├─ test_arithmetic.py
   │     │  │  │  │  ├─ test_constructors.py
   │     │  │  │  │  ├─ test_datetime.py
   │     │  │  │  │  ├─ test_date_range.py
   │     │  │  │  │  ├─ test_formats.py
   │     │  │  │  │  ├─ test_freq_attr.py
   │     │  │  │  │  ├─ test_indexing.py
   │     │  │  │  │  ├─ test_iter.py
   │     │  │  │  │  ├─ test_join.py
   │     │  │  │  │  ├─ test_npfuncs.py
   │     │  │  │  │  ├─ test_ops.py
   │     │  │  │  │  ├─ test_partial_slicing.py
   │     │  │  │  │  ├─ test_pickle.py
   │     │  │  │  │  ├─ test_reindex.py
   │     │  │  │  │  ├─ test_scalar_compat.py
   │     │  │  │  │  ├─ test_setops.py
   │     │  │  │  │  ├─ test_timezones.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ test_arithmetic.cpython-311.pyc
   │     │  │  │  │     ├─ test_constructors.cpython-311.pyc
   │     │  │  │  │     ├─ test_datetime.cpython-311.pyc
   │     │  │  │  │     ├─ test_date_range.cpython-311.pyc
   │     │  │  │  │     ├─ test_formats.cpython-311.pyc
   │     │  │  │  │     ├─ test_freq_attr.cpython-311.pyc
   │     │  │  │  │     ├─ test_indexing.cpython-311.pyc
   │     │  │  │  │     ├─ test_iter.cpython-311.pyc
   │     │  │  │  │     ├─ test_join.cpython-311.pyc
   │     │  │  │  │     ├─ test_npfuncs.cpython-311.pyc
   │     │  │  │  │     ├─ test_ops.cpython-311.pyc
   │     │  │  │  │     ├─ test_partial_slicing.cpython-311.pyc
   │     │  │  │  │     ├─ test_pickle.cpython-311.pyc
   │     │  │  │  │     ├─ test_reindex.cpython-311.pyc
   │     │  │  │  │     ├─ test_scalar_compat.cpython-311.pyc
   │     │  │  │  │     ├─ test_setops.cpython-311.pyc
   │     │  │  │  │     ├─ test_timezones.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ interval
   │     │  │  │  │  ├─ test_astype.py
   │     │  │  │  │  ├─ test_constructors.py
   │     │  │  │  │  ├─ test_equals.py
   │     │  │  │  │  ├─ test_formats.py
   │     │  │  │  │  ├─ test_indexing.py
   │     │  │  │  │  ├─ test_interval.py
   │     │  │  │  │  ├─ test_interval_range.py
   │     │  │  │  │  ├─ test_interval_tree.py
   │     │  │  │  │  ├─ test_join.py
   │     │  │  │  │  ├─ test_pickle.py
   │     │  │  │  │  ├─ test_setops.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ test_astype.cpython-311.pyc
   │     │  │  │  │     ├─ test_constructors.cpython-311.pyc
   │     │  │  │  │     ├─ test_equals.cpython-311.pyc
   │     │  │  │  │     ├─ test_formats.cpython-311.pyc
   │     │  │  │  │     ├─ test_indexing.cpython-311.pyc
   │     │  │  │  │     ├─ test_interval.cpython-311.pyc
   │     │  │  │  │     ├─ test_interval_range.cpython-311.pyc
   │     │  │  │  │     ├─ test_interval_tree.cpython-311.pyc
   │     │  │  │  │     ├─ test_join.cpython-311.pyc
   │     │  │  │  │     ├─ test_pickle.cpython-311.pyc
   │     │  │  │  │     ├─ test_setops.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ multi
   │     │  │  │  │  ├─ conftest.py
   │     │  │  │  │  ├─ test_analytics.py
   │     │  │  │  │  ├─ test_astype.py
   │     │  │  │  │  ├─ test_compat.py
   │     │  │  │  │  ├─ test_constructors.py
   │     │  │  │  │  ├─ test_conversion.py
   │     │  │  │  │  ├─ test_copy.py
   │     │  │  │  │  ├─ test_drop.py
   │     │  │  │  │  ├─ test_duplicates.py
   │     │  │  │  │  ├─ test_equivalence.py
   │     │  │  │  │  ├─ test_formats.py
   │     │  │  │  │  ├─ test_get_level_values.py
   │     │  │  │  │  ├─ test_get_set.py
   │     │  │  │  │  ├─ test_indexing.py
   │     │  │  │  │  ├─ test_integrity.py
   │     │  │  │  │  ├─ test_isin.py
   │     │  │  │  │  ├─ test_join.py
   │     │  │  │  │  ├─ test_lexsort.py
   │     │  │  │  │  ├─ test_missing.py
   │     │  │  │  │  ├─ test_monotonic.py
   │     │  │  │  │  ├─ test_names.py
   │     │  │  │  │  ├─ test_partial_indexing.py
   │     │  │  │  │  ├─ test_pickle.py
   │     │  │  │  │  ├─ test_reindex.py
   │     │  │  │  │  ├─ test_reshape.py
   │     │  │  │  │  ├─ test_setops.py
   │     │  │  │  │  ├─ test_sorting.py
   │     │  │  │  │  ├─ test_take.py
   │     │  │  │  │  ├─ test_util.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ conftest.cpython-311.pyc
   │     │  │  │  │     ├─ test_analytics.cpython-311.pyc
   │     │  │  │  │     ├─ test_astype.cpython-311.pyc
   │     │  │  │  │     ├─ test_compat.cpython-311.pyc
   │     │  │  │  │     ├─ test_constructors.cpython-311.pyc
   │     │  │  │  │     ├─ test_conversion.cpython-311.pyc
   │     │  │  │  │     ├─ test_copy.cpython-311.pyc
   │     │  │  │  │     ├─ test_drop.cpython-311.pyc
   │     │  │  │  │     ├─ test_duplicates.cpython-311.pyc
   │     │  │  │  │     ├─ test_equivalence.cpython-311.pyc
   │     │  │  │  │     ├─ test_formats.cpython-311.pyc
   │     │  │  │  │     ├─ test_get_level_values.cpython-311.pyc
   │     │  │  │  │     ├─ test_get_set.cpython-311.pyc
   │     │  │  │  │     ├─ test_indexing.cpython-311.pyc
   │     │  │  │  │     ├─ test_integrity.cpython-311.pyc
   │     │  │  │  │     ├─ test_isin.cpython-311.pyc
   │     │  │  │  │     ├─ test_join.cpython-311.pyc
   │     │  │  │  │     ├─ test_lexsort.cpython-311.pyc
   │     │  │  │  │     ├─ test_missing.cpython-311.pyc
   │     │  │  │  │     ├─ test_monotonic.cpython-311.pyc
   │     │  │  │  │     ├─ test_names.cpython-311.pyc
   │     │  │  │  │     ├─ test_partial_indexing.cpython-311.pyc
   │     │  │  │  │     ├─ test_pickle.cpython-311.pyc
   │     │  │  │  │     ├─ test_reindex.cpython-311.pyc
   │     │  │  │  │     ├─ test_reshape.cpython-311.pyc
   │     │  │  │  │     ├─ test_setops.cpython-311.pyc
   │     │  │  │  │     ├─ test_sorting.cpython-311.pyc
   │     │  │  │  │     ├─ test_take.cpython-311.pyc
   │     │  │  │  │     ├─ test_util.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ numeric
   │     │  │  │  │  ├─ test_astype.py
   │     │  │  │  │  ├─ test_indexing.py
   │     │  │  │  │  ├─ test_join.py
   │     │  │  │  │  ├─ test_numeric.py
   │     │  │  │  │  ├─ test_setops.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ test_astype.cpython-311.pyc
   │     │  │  │  │     ├─ test_indexing.cpython-311.pyc
   │     │  │  │  │     ├─ test_join.cpython-311.pyc
   │     │  │  │  │     ├─ test_numeric.cpython-311.pyc
   │     │  │  │  │     ├─ test_setops.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ object
   │     │  │  │  │  ├─ test_astype.py
   │     │  │  │  │  ├─ test_indexing.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ test_astype.cpython-311.pyc
   │     │  │  │  │     ├─ test_indexing.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ period
   │     │  │  │  │  ├─ methods
   │     │  │  │  │  │  ├─ test_asfreq.py
   │     │  │  │  │  │  ├─ test_astype.py
   │     │  │  │  │  │  ├─ test_factorize.py
   │     │  │  │  │  │  ├─ test_fillna.py
   │     │  │  │  │  │  ├─ test_insert.py
   │     │  │  │  │  │  ├─ test_is_full.py
   │     │  │  │  │  │  ├─ test_repeat.py
   │     │  │  │  │  │  ├─ test_shift.py
   │     │  │  │  │  │  ├─ test_to_timestamp.py
   │     │  │  │  │  │  ├─ __init__.py
   │     │  │  │  │  │  └─ __pycache__
   │     │  │  │  │  │     ├─ test_asfreq.cpython-311.pyc
   │     │  │  │  │  │     ├─ test_astype.cpython-311.pyc
   │     │  │  │  │  │     ├─ test_factorize.cpython-311.pyc
   │     │  │  │  │  │     ├─ test_fillna.cpython-311.pyc
   │     │  │  │  │  │     ├─ test_insert.cpython-311.pyc
   │     │  │  │  │  │     ├─ test_is_full.cpython-311.pyc
   │     │  │  │  │  │     ├─ test_repeat.cpython-311.pyc
   │     │  │  │  │  │     ├─ test_shift.cpython-311.pyc
   │     │  │  │  │  │     ├─ test_to_timestamp.cpython-311.pyc
   │     │  │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  │  ├─ test_constructors.py
   │     │  │  │  │  ├─ test_formats.py
   │     │  │  │  │  ├─ test_freq_attr.py
   │     │  │  │  │  ├─ test_indexing.py
   │     │  │  │  │  ├─ test_join.py
   │     │  │  │  │  ├─ test_monotonic.py
   │     │  │  │  │  ├─ test_partial_slicing.py
   │     │  │  │  │  ├─ test_period.py
   │     │  │  │  │  ├─ test_period_range.py
   │     │  │  │  │  ├─ test_pickle.py
   │     │  │  │  │  ├─ test_resolution.py
   │     │  │  │  │  ├─ test_scalar_compat.py
   │     │  │  │  │  ├─ test_searchsorted.py
   │     │  │  │  │  ├─ test_setops.py
   │     │  │  │  │  ├─ test_tools.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ test_constructors.cpython-311.pyc
   │     │  │  │  │     ├─ test_formats.cpython-311.pyc
   │     │  │  │  │     ├─ test_freq_attr.cpython-311.pyc
   │     │  │  │  │     ├─ test_indexing.cpython-311.pyc
   │     │  │  │  │     ├─ test_join.cpython-311.pyc
   │     │  │  │  │     ├─ test_monotonic.cpython-311.pyc
   │     │  │  │  │     ├─ test_partial_slicing.cpython-311.pyc
   │     │  │  │  │     ├─ test_period.cpython-311.pyc
   │     │  │  │  │     ├─ test_period_range.cpython-311.pyc
   │     │  │  │  │     ├─ test_pickle.cpython-311.pyc
   │     │  │  │  │     ├─ test_resolution.cpython-311.pyc
   │     │  │  │  │     ├─ test_scalar_compat.cpython-311.pyc
   │     │  │  │  │     ├─ test_searchsorted.cpython-311.pyc
   │     │  │  │  │     ├─ test_setops.cpython-311.pyc
   │     │  │  │  │     ├─ test_tools.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ ranges
   │     │  │  │  │  ├─ test_constructors.py
   │     │  │  │  │  ├─ test_indexing.py
   │     │  │  │  │  ├─ test_join.py
   │     │  │  │  │  ├─ test_range.py
   │     │  │  │  │  ├─ test_setops.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ test_constructors.cpython-311.pyc
   │     │  │  │  │     ├─ test_indexing.cpython-311.pyc
   │     │  │  │  │     ├─ test_join.cpython-311.pyc
   │     │  │  │  │     ├─ test_range.cpython-311.pyc
   │     │  │  │  │     ├─ test_setops.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ string
   │     │  │  │  │  ├─ test_astype.py
   │     │  │  │  │  ├─ test_indexing.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ test_astype.cpython-311.pyc
   │     │  │  │  │     ├─ test_indexing.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ test_any_index.py
   │     │  │  │  ├─ test_base.py
   │     │  │  │  ├─ test_common.py
   │     │  │  │  ├─ test_datetimelike.py
   │     │  │  │  ├─ test_engines.py
   │     │  │  │  ├─ test_frozen.py
   │     │  │  │  ├─ test_indexing.py
   │     │  │  │  ├─ test_index_new.py
   │     │  │  │  ├─ test_numpy_compat.py
   │     │  │  │  ├─ test_old_base.py
   │     │  │  │  ├─ test_setops.py
   │     │  │  │  ├─ test_subclass.py
   │     │  │  │  ├─ timedeltas
   │     │  │  │  │  ├─ methods
   │     │  │  │  │  │  ├─ test_astype.py
   │     │  │  │  │  │  ├─ test_factorize.py
   │     │  │  │  │  │  ├─ test_fillna.py
   │     │  │  │  │  │  ├─ test_insert.py
   │     │  │  │  │  │  ├─ test_repeat.py
   │     │  │  │  │  │  ├─ test_shift.py
   │     │  │  │  │  │  ├─ __init__.py
   │     │  │  │  │  │  └─ __pycache__
   │     │  │  │  │  │     ├─ test_astype.cpython-311.pyc
   │     │  │  │  │  │     ├─ test_factorize.cpython-311.pyc
   │     │  │  │  │  │     ├─ test_fillna.cpython-311.pyc
   │     │  │  │  │  │     ├─ test_insert.cpython-311.pyc
   │     │  │  │  │  │     ├─ test_repeat.cpython-311.pyc
   │     │  │  │  │  │     ├─ test_shift.cpython-311.pyc
   │     │  │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  │  ├─ test_arithmetic.py
   │     │  │  │  │  ├─ test_constructors.py
   │     │  │  │  │  ├─ test_delete.py
   │     │  │  │  │  ├─ test_formats.py
   │     │  │  │  │  ├─ test_freq_attr.py
   │     │  │  │  │  ├─ test_indexing.py
   │     │  │  │  │  ├─ test_join.py
   │     │  │  │  │  ├─ test_ops.py
   │     │  │  │  │  ├─ test_pickle.py
   │     │  │  │  │  ├─ test_scalar_compat.py
   │     │  │  │  │  ├─ test_searchsorted.py
   │     │  │  │  │  ├─ test_setops.py
   │     │  │  │  │  ├─ test_timedelta.py
   │     │  │  │  │  ├─ test_timedelta_range.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ test_arithmetic.cpython-311.pyc
   │     │  │  │  │     ├─ test_constructors.cpython-311.pyc
   │     │  │  │  │     ├─ test_delete.cpython-311.pyc
   │     │  │  │  │     ├─ test_formats.cpython-311.pyc
   │     │  │  │  │     ├─ test_freq_attr.cpython-311.pyc
   │     │  │  │  │     ├─ test_indexing.cpython-311.pyc
   │     │  │  │  │     ├─ test_join.cpython-311.pyc
   │     │  │  │  │     ├─ test_ops.cpython-311.pyc
   │     │  │  │  │     ├─ test_pickle.cpython-311.pyc
   │     │  │  │  │     ├─ test_scalar_compat.cpython-311.pyc
   │     │  │  │  │     ├─ test_searchsorted.cpython-311.pyc
   │     │  │  │  │     ├─ test_setops.cpython-311.pyc
   │     │  │  │  │     ├─ test_timedelta.cpython-311.pyc
   │     │  │  │  │     ├─ test_timedelta_range.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ conftest.cpython-311.pyc
   │     │  │  │     ├─ test_any_index.cpython-311.pyc
   │     │  │  │     ├─ test_base.cpython-311.pyc
   │     │  │  │     ├─ test_common.cpython-311.pyc
   │     │  │  │     ├─ test_datetimelike.cpython-311.pyc
   │     │  │  │     ├─ test_engines.cpython-311.pyc
   │     │  │  │     ├─ test_frozen.cpython-311.pyc
   │     │  │  │     ├─ test_indexing.cpython-311.pyc
   │     │  │  │     ├─ test_index_new.cpython-311.pyc
   │     │  │  │     ├─ test_numpy_compat.cpython-311.pyc
   │     │  │  │     ├─ test_old_base.cpython-311.pyc
   │     │  │  │     ├─ test_setops.cpython-311.pyc
   │     │  │  │     ├─ test_subclass.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ indexing
   │     │  │  │  ├─ common.py
   │     │  │  │  ├─ interval
   │     │  │  │  │  ├─ test_interval.py
   │     │  │  │  │  ├─ test_interval_new.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ test_interval.cpython-311.pyc
   │     │  │  │  │     ├─ test_interval_new.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ multiindex
   │     │  │  │  │  ├─ test_chaining_and_caching.py
   │     │  │  │  │  ├─ test_datetime.py
   │     │  │  │  │  ├─ test_getitem.py
   │     │  │  │  │  ├─ test_iloc.py
   │     │  │  │  │  ├─ test_indexing_slow.py
   │     │  │  │  │  ├─ test_loc.py
   │     │  │  │  │  ├─ test_multiindex.py
   │     │  │  │  │  ├─ test_partial.py
   │     │  │  │  │  ├─ test_setitem.py
   │     │  │  │  │  ├─ test_slice.py
   │     │  │  │  │  ├─ test_sorted.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ test_chaining_and_caching.cpython-311.pyc
   │     │  │  │  │     ├─ test_datetime.cpython-311.pyc
   │     │  │  │  │     ├─ test_getitem.cpython-311.pyc
   │     │  │  │  │     ├─ test_iloc.cpython-311.pyc
   │     │  │  │  │     ├─ test_indexing_slow.cpython-311.pyc
   │     │  │  │  │     ├─ test_loc.cpython-311.pyc
   │     │  │  │  │     ├─ test_multiindex.cpython-311.pyc
   │     │  │  │  │     ├─ test_partial.cpython-311.pyc
   │     │  │  │  │     ├─ test_setitem.cpython-311.pyc
   │     │  │  │  │     ├─ test_slice.cpython-311.pyc
   │     │  │  │  │     ├─ test_sorted.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ test_at.py
   │     │  │  │  ├─ test_categorical.py
   │     │  │  │  ├─ test_chaining_and_caching.py
   │     │  │  │  ├─ test_check_indexer.py
   │     │  │  │  ├─ test_coercion.py
   │     │  │  │  ├─ test_datetime.py
   │     │  │  │  ├─ test_floats.py
   │     │  │  │  ├─ test_iat.py
   │     │  │  │  ├─ test_iloc.py
   │     │  │  │  ├─ test_indexers.py
   │     │  │  │  ├─ test_indexing.py
   │     │  │  │  ├─ test_loc.py
   │     │  │  │  ├─ test_na_indexing.py
   │     │  │  │  ├─ test_partial.py
   │     │  │  │  ├─ test_scalar.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ common.cpython-311.pyc
   │     │  │  │     ├─ test_at.cpython-311.pyc
   │     │  │  │     ├─ test_categorical.cpython-311.pyc
   │     │  │  │     ├─ test_chaining_and_caching.cpython-311.pyc
   │     │  │  │     ├─ test_check_indexer.cpython-311.pyc
   │     │  │  │     ├─ test_coercion.cpython-311.pyc
   │     │  │  │     ├─ test_datetime.cpython-311.pyc
   │     │  │  │     ├─ test_floats.cpython-311.pyc
   │     │  │  │     ├─ test_iat.cpython-311.pyc
   │     │  │  │     ├─ test_iloc.cpython-311.pyc
   │     │  │  │     ├─ test_indexers.cpython-311.pyc
   │     │  │  │     ├─ test_indexing.cpython-311.pyc
   │     │  │  │     ├─ test_loc.cpython-311.pyc
   │     │  │  │     ├─ test_na_indexing.cpython-311.pyc
   │     │  │  │     ├─ test_partial.cpython-311.pyc
   │     │  │  │     ├─ test_scalar.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ interchange
   │     │  │  │  ├─ test_impl.py
   │     │  │  │  ├─ test_spec_conformance.py
   │     │  │  │  ├─ test_utils.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ test_impl.cpython-311.pyc
   │     │  │  │     ├─ test_spec_conformance.cpython-311.pyc
   │     │  │  │     ├─ test_utils.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ internals
   │     │  │  │  ├─ test_api.py
   │     │  │  │  ├─ test_internals.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ test_api.cpython-311.pyc
   │     │  │  │     ├─ test_internals.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ io
   │     │  │  │  ├─ conftest.py
   │     │  │  │  ├─ excel
   │     │  │  │  │  ├─ test_odf.py
   │     │  │  │  │  ├─ test_odswriter.py
   │     │  │  │  │  ├─ test_openpyxl.py
   │     │  │  │  │  ├─ test_readers.py
   │     │  │  │  │  ├─ test_style.py
   │     │  │  │  │  ├─ test_writers.py
   │     │  │  │  │  ├─ test_xlrd.py
   │     │  │  │  │  ├─ test_xlsxwriter.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ test_odf.cpython-311.pyc
   │     │  │  │  │     ├─ test_odswriter.cpython-311.pyc
   │     │  │  │  │     ├─ test_openpyxl.cpython-311.pyc
   │     │  │  │  │     ├─ test_readers.cpython-311.pyc
   │     │  │  │  │     ├─ test_style.cpython-311.pyc
   │     │  │  │  │     ├─ test_writers.cpython-311.pyc
   │     │  │  │  │     ├─ test_xlrd.cpython-311.pyc
   │     │  │  │  │     ├─ test_xlsxwriter.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ formats
   │     │  │  │  │  ├─ style
   │     │  │  │  │  │  ├─ test_bar.py
   │     │  │  │  │  │  ├─ test_exceptions.py
   │     │  │  │  │  │  ├─ test_format.py
   │     │  │  │  │  │  ├─ test_highlight.py
   │     │  │  │  │  │  ├─ test_html.py
   │     │  │  │  │  │  ├─ test_matplotlib.py
   │     │  │  │  │  │  ├─ test_non_unique.py
   │     │  │  │  │  │  ├─ test_style.py
   │     │  │  │  │  │  ├─ test_tooltip.py
   │     │  │  │  │  │  ├─ test_to_latex.py
   │     │  │  │  │  │  ├─ test_to_string.py
   │     │  │  │  │  │  ├─ test_to_typst.py
   │     │  │  │  │  │  ├─ __init__.py
   │     │  │  │  │  │  └─ __pycache__
   │     │  │  │  │  │     ├─ test_bar.cpython-311.pyc
   │     │  │  │  │  │     ├─ test_exceptions.cpython-311.pyc
   │     │  │  │  │  │     ├─ test_format.cpython-311.pyc
   │     │  │  │  │  │     ├─ test_highlight.cpython-311.pyc
   │     │  │  │  │  │     ├─ test_html.cpython-311.pyc
   │     │  │  │  │  │     ├─ test_matplotlib.cpython-311.pyc
   │     │  │  │  │  │     ├─ test_non_unique.cpython-311.pyc
   │     │  │  │  │  │     ├─ test_style.cpython-311.pyc
   │     │  │  │  │  │     ├─ test_tooltip.cpython-311.pyc
   │     │  │  │  │  │     ├─ test_to_latex.cpython-311.pyc
   │     │  │  │  │  │     ├─ test_to_string.cpython-311.pyc
   │     │  │  │  │  │     ├─ test_to_typst.cpython-311.pyc
   │     │  │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  │  ├─ test_console.py
   │     │  │  │  │  ├─ test_css.py
   │     │  │  │  │  ├─ test_eng_formatting.py
   │     │  │  │  │  ├─ test_format.py
   │     │  │  │  │  ├─ test_ipython_compat.py
   │     │  │  │  │  ├─ test_printing.py
   │     │  │  │  │  ├─ test_to_csv.py
   │     │  │  │  │  ├─ test_to_excel.py
   │     │  │  │  │  ├─ test_to_html.py
   │     │  │  │  │  ├─ test_to_latex.py
   │     │  │  │  │  ├─ test_to_markdown.py
   │     │  │  │  │  ├─ test_to_string.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ test_console.cpython-311.pyc
   │     │  │  │  │     ├─ test_css.cpython-311.pyc
   │     │  │  │  │     ├─ test_eng_formatting.cpython-311.pyc
   │     │  │  │  │     ├─ test_format.cpython-311.pyc
   │     │  │  │  │     ├─ test_ipython_compat.cpython-311.pyc
   │     │  │  │  │     ├─ test_printing.cpython-311.pyc
   │     │  │  │  │     ├─ test_to_csv.cpython-311.pyc
   │     │  │  │  │     ├─ test_to_excel.cpython-311.pyc
   │     │  │  │  │     ├─ test_to_html.cpython-311.pyc
   │     │  │  │  │     ├─ test_to_latex.cpython-311.pyc
   │     │  │  │  │     ├─ test_to_markdown.cpython-311.pyc
   │     │  │  │  │     ├─ test_to_string.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ generate_legacy_storage_files.py
   │     │  │  │  ├─ json
   │     │  │  │  │  ├─ conftest.py
   │     │  │  │  │  ├─ test_compression.py
   │     │  │  │  │  ├─ test_deprecated_kwargs.py
   │     │  │  │  │  ├─ test_json_table_schema.py
   │     │  │  │  │  ├─ test_json_table_schema_ext_dtype.py
   │     │  │  │  │  ├─ test_normalize.py
   │     │  │  │  │  ├─ test_pandas.py
   │     │  │  │  │  ├─ test_readlines.py
   │     │  │  │  │  ├─ test_ujson.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ conftest.cpython-311.pyc
   │     │  │  │  │     ├─ test_compression.cpython-311.pyc
   │     │  │  │  │     ├─ test_deprecated_kwargs.cpython-311.pyc
   │     │  │  │  │     ├─ test_json_table_schema.cpython-311.pyc
   │     │  │  │  │     ├─ test_json_table_schema_ext_dtype.cpython-311.pyc
   │     │  │  │  │     ├─ test_normalize.cpython-311.pyc
   │     │  │  │  │     ├─ test_pandas.cpython-311.pyc
   │     │  │  │  │     ├─ test_readlines.cpython-311.pyc
   │     │  │  │  │     ├─ test_ujson.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ parser
   │     │  │  │  │  ├─ common
   │     │  │  │  │  │  ├─ test_chunksize.py
   │     │  │  │  │  │  ├─ test_common_basic.py
   │     │  │  │  │  │  ├─ test_data_list.py
   │     │  │  │  │  │  ├─ test_decimal.py
   │     │  │  │  │  │  ├─ test_file_buffer_url.py
   │     │  │  │  │  │  ├─ test_float.py
   │     │  │  │  │  │  ├─ test_index.py
   │     │  │  │  │  │  ├─ test_inf.py
   │     │  │  │  │  │  ├─ test_ints.py
   │     │  │  │  │  │  ├─ test_iterator.py
   │     │  │  │  │  │  ├─ test_read_errors.py
   │     │  │  │  │  │  ├─ __init__.py
   │     │  │  │  │  │  └─ __pycache__
   │     │  │  │  │  │     ├─ test_chunksize.cpython-311.pyc
   │     │  │  │  │  │     ├─ test_common_basic.cpython-311.pyc
   │     │  │  │  │  │     ├─ test_data_list.cpython-311.pyc
   │     │  │  │  │  │     ├─ test_decimal.cpython-311.pyc
   │     │  │  │  │  │     ├─ test_file_buffer_url.cpython-311.pyc
   │     │  │  │  │  │     ├─ test_float.cpython-311.pyc
   │     │  │  │  │  │     ├─ test_index.cpython-311.pyc
   │     │  │  │  │  │     ├─ test_inf.cpython-311.pyc
   │     │  │  │  │  │     ├─ test_ints.cpython-311.pyc
   │     │  │  │  │  │     ├─ test_iterator.cpython-311.pyc
   │     │  │  │  │  │     ├─ test_read_errors.cpython-311.pyc
   │     │  │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  │  ├─ conftest.py
   │     │  │  │  │  ├─ dtypes
   │     │  │  │  │  │  ├─ test_categorical.py
   │     │  │  │  │  │  ├─ test_dtypes_basic.py
   │     │  │  │  │  │  ├─ test_empty.py
   │     │  │  │  │  │  ├─ __init__.py
   │     │  │  │  │  │  └─ __pycache__
   │     │  │  │  │  │     ├─ test_categorical.cpython-311.pyc
   │     │  │  │  │  │     ├─ test_dtypes_basic.cpython-311.pyc
   │     │  │  │  │  │     ├─ test_empty.cpython-311.pyc
   │     │  │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  │  ├─ test_comment.py
   │     │  │  │  │  ├─ test_compression.py
   │     │  │  │  │  ├─ test_concatenate_chunks.py
   │     │  │  │  │  ├─ test_converters.py
   │     │  │  │  │  ├─ test_c_parser_only.py
   │     │  │  │  │  ├─ test_dialect.py
   │     │  │  │  │  ├─ test_encoding.py
   │     │  │  │  │  ├─ test_header.py
   │     │  │  │  │  ├─ test_index_col.py
   │     │  │  │  │  ├─ test_mangle_dupes.py
   │     │  │  │  │  ├─ test_multi_thread.py
   │     │  │  │  │  ├─ test_na_values.py
   │     │  │  │  │  ├─ test_network.py
   │     │  │  │  │  ├─ test_parse_dates.py
   │     │  │  │  │  ├─ test_python_parser_only.py
   │     │  │  │  │  ├─ test_quoting.py
   │     │  │  │  │  ├─ test_read_fwf.py
   │     │  │  │  │  ├─ test_skiprows.py
   │     │  │  │  │  ├─ test_textreader.py
   │     │  │  │  │  ├─ test_unsupported.py
   │     │  │  │  │  ├─ test_upcast.py
   │     │  │  │  │  ├─ usecols
   │     │  │  │  │  │  ├─ test_parse_dates.py
   │     │  │  │  │  │  ├─ test_strings.py
   │     │  │  │  │  │  ├─ test_usecols_basic.py
   │     │  │  │  │  │  ├─ __init__.py
   │     │  │  │  │  │  └─ __pycache__
   │     │  │  │  │  │     ├─ test_parse_dates.cpython-311.pyc
   │     │  │  │  │  │     ├─ test_strings.cpython-311.pyc
   │     │  │  │  │  │     ├─ test_usecols_basic.cpython-311.pyc
   │     │  │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ conftest.cpython-311.pyc
   │     │  │  │  │     ├─ test_comment.cpython-311.pyc
   │     │  │  │  │     ├─ test_compression.cpython-311.pyc
   │     │  │  │  │     ├─ test_concatenate_chunks.cpython-311.pyc
   │     │  │  │  │     ├─ test_converters.cpython-311.pyc
   │     │  │  │  │     ├─ test_c_parser_only.cpython-311.pyc
   │     │  │  │  │     ├─ test_dialect.cpython-311.pyc
   │     │  │  │  │     ├─ test_encoding.cpython-311.pyc
   │     │  │  │  │     ├─ test_header.cpython-311.pyc
   │     │  │  │  │     ├─ test_index_col.cpython-311.pyc
   │     │  │  │  │     ├─ test_mangle_dupes.cpython-311.pyc
   │     │  │  │  │     ├─ test_multi_thread.cpython-311.pyc
   │     │  │  │  │     ├─ test_na_values.cpython-311.pyc
   │     │  │  │  │     ├─ test_network.cpython-311.pyc
   │     │  │  │  │     ├─ test_parse_dates.cpython-311.pyc
   │     │  │  │  │     ├─ test_python_parser_only.cpython-311.pyc
   │     │  │  │  │     ├─ test_quoting.cpython-311.pyc
   │     │  │  │  │     ├─ test_read_fwf.cpython-311.pyc
   │     │  │  │  │     ├─ test_skiprows.cpython-311.pyc
   │     │  │  │  │     ├─ test_textreader.cpython-311.pyc
   │     │  │  │  │     ├─ test_unsupported.cpython-311.pyc
   │     │  │  │  │     ├─ test_upcast.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ pytables
   │     │  │  │  │  ├─ common.py
   │     │  │  │  │  ├─ conftest.py
   │     │  │  │  │  ├─ test_append.py
   │     │  │  │  │  ├─ test_categorical.py
   │     │  │  │  │  ├─ test_compat.py
   │     │  │  │  │  ├─ test_complex.py
   │     │  │  │  │  ├─ test_errors.py
   │     │  │  │  │  ├─ test_file_handling.py
   │     │  │  │  │  ├─ test_keys.py
   │     │  │  │  │  ├─ test_put.py
   │     │  │  │  │  ├─ test_pytables_missing.py
   │     │  │  │  │  ├─ test_read.py
   │     │  │  │  │  ├─ test_retain_attributes.py
   │     │  │  │  │  ├─ test_round_trip.py
   │     │  │  │  │  ├─ test_select.py
   │     │  │  │  │  ├─ test_store.py
   │     │  │  │  │  ├─ test_subclass.py
   │     │  │  │  │  ├─ test_timezones.py
   │     │  │  │  │  ├─ test_time_series.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ common.cpython-311.pyc
   │     │  │  │  │     ├─ conftest.cpython-311.pyc
   │     │  │  │  │     ├─ test_append.cpython-311.pyc
   │     │  │  │  │     ├─ test_categorical.cpython-311.pyc
   │     │  │  │  │     ├─ test_compat.cpython-311.pyc
   │     │  │  │  │     ├─ test_complex.cpython-311.pyc
   │     │  │  │  │     ├─ test_errors.cpython-311.pyc
   │     │  │  │  │     ├─ test_file_handling.cpython-311.pyc
   │     │  │  │  │     ├─ test_keys.cpython-311.pyc
   │     │  │  │  │     ├─ test_put.cpython-311.pyc
   │     │  │  │  │     ├─ test_pytables_missing.cpython-311.pyc
   │     │  │  │  │     ├─ test_read.cpython-311.pyc
   │     │  │  │  │     ├─ test_retain_attributes.cpython-311.pyc
   │     │  │  │  │     ├─ test_round_trip.cpython-311.pyc
   │     │  │  │  │     ├─ test_select.cpython-311.pyc
   │     │  │  │  │     ├─ test_store.cpython-311.pyc
   │     │  │  │  │     ├─ test_subclass.cpython-311.pyc
   │     │  │  │  │     ├─ test_timezones.cpython-311.pyc
   │     │  │  │  │     ├─ test_time_series.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ sas
   │     │  │  │  │  ├─ test_byteswap.py
   │     │  │  │  │  ├─ test_sas.py
   │     │  │  │  │  ├─ test_sas7bdat.py
   │     │  │  │  │  ├─ test_xport.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ test_byteswap.cpython-311.pyc
   │     │  │  │  │     ├─ test_sas.cpython-311.pyc
   │     │  │  │  │     ├─ test_sas7bdat.cpython-311.pyc
   │     │  │  │  │     ├─ test_xport.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ test_clipboard.py
   │     │  │  │  ├─ test_common.py
   │     │  │  │  ├─ test_compression.py
   │     │  │  │  ├─ test_feather.py
   │     │  │  │  ├─ test_fsspec.py
   │     │  │  │  ├─ test_gcs.py
   │     │  │  │  ├─ test_html.py
   │     │  │  │  ├─ test_http_headers.py
   │     │  │  │  ├─ test_iceberg.py
   │     │  │  │  ├─ test_orc.py
   │     │  │  │  ├─ test_parquet.py
   │     │  │  │  ├─ test_pickle.py
   │     │  │  │  ├─ test_s3.py
   │     │  │  │  ├─ test_spss.py
   │     │  │  │  ├─ test_sql.py
   │     │  │  │  ├─ test_stata.py
   │     │  │  │  ├─ xml
   │     │  │  │  │  ├─ conftest.py
   │     │  │  │  │  ├─ test_to_xml.py
   │     │  │  │  │  ├─ test_xml.py
   │     │  │  │  │  ├─ test_xml_dtypes.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ conftest.cpython-311.pyc
   │     │  │  │  │     ├─ test_to_xml.cpython-311.pyc
   │     │  │  │  │     ├─ test_xml.cpython-311.pyc
   │     │  │  │  │     ├─ test_xml_dtypes.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ conftest.cpython-311.pyc
   │     │  │  │     ├─ generate_legacy_storage_files.cpython-311.pyc
   │     │  │  │     ├─ test_clipboard.cpython-311.pyc
   │     │  │  │     ├─ test_common.cpython-311.pyc
   │     │  │  │     ├─ test_compression.cpython-311.pyc
   │     │  │  │     ├─ test_feather.cpython-311.pyc
   │     │  │  │     ├─ test_fsspec.cpython-311.pyc
   │     │  │  │     ├─ test_gcs.cpython-311.pyc
   │     │  │  │     ├─ test_html.cpython-311.pyc
   │     │  │  │     ├─ test_http_headers.cpython-311.pyc
   │     │  │  │     ├─ test_iceberg.cpython-311.pyc
   │     │  │  │     ├─ test_orc.cpython-311.pyc
   │     │  │  │     ├─ test_parquet.cpython-311.pyc
   │     │  │  │     ├─ test_pickle.cpython-311.pyc
   │     │  │  │     ├─ test_s3.cpython-311.pyc
   │     │  │  │     ├─ test_spss.cpython-311.pyc
   │     │  │  │     ├─ test_sql.cpython-311.pyc
   │     │  │  │     ├─ test_stata.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ libs
   │     │  │  │  ├─ test_hashtable.py
   │     │  │  │  ├─ test_join.py
   │     │  │  │  ├─ test_lib.py
   │     │  │  │  ├─ test_libalgos.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ test_hashtable.cpython-311.pyc
   │     │  │  │     ├─ test_join.cpython-311.pyc
   │     │  │  │     ├─ test_lib.cpython-311.pyc
   │     │  │  │     ├─ test_libalgos.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ plotting
   │     │  │  │  ├─ common.py
   │     │  │  │  ├─ conftest.py
   │     │  │  │  ├─ frame
   │     │  │  │  │  ├─ test_frame.py
   │     │  │  │  │  ├─ test_frame_color.py
   │     │  │  │  │  ├─ test_frame_groupby.py
   │     │  │  │  │  ├─ test_frame_legend.py
   │     │  │  │  │  ├─ test_frame_subplots.py
   │     │  │  │  │  ├─ test_hist_box_by.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ test_frame.cpython-311.pyc
   │     │  │  │  │     ├─ test_frame_color.cpython-311.pyc
   │     │  │  │  │     ├─ test_frame_groupby.cpython-311.pyc
   │     │  │  │  │     ├─ test_frame_legend.cpython-311.pyc
   │     │  │  │  │     ├─ test_frame_subplots.cpython-311.pyc
   │     │  │  │  │     ├─ test_hist_box_by.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ test_backend.py
   │     │  │  │  ├─ test_boxplot_method.py
   │     │  │  │  ├─ test_common.py
   │     │  │  │  ├─ test_converter.py
   │     │  │  │  ├─ test_datetimelike.py
   │     │  │  │  ├─ test_groupby.py
   │     │  │  │  ├─ test_hist_method.py
   │     │  │  │  ├─ test_misc.py
   │     │  │  │  ├─ test_series.py
   │     │  │  │  ├─ test_style.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ common.cpython-311.pyc
   │     │  │  │     ├─ conftest.cpython-311.pyc
   │     │  │  │     ├─ test_backend.cpython-311.pyc
   │     │  │  │     ├─ test_boxplot_method.cpython-311.pyc
   │     │  │  │     ├─ test_common.cpython-311.pyc
   │     │  │  │     ├─ test_converter.cpython-311.pyc
   │     │  │  │     ├─ test_datetimelike.cpython-311.pyc
   │     │  │  │     ├─ test_groupby.cpython-311.pyc
   │     │  │  │     ├─ test_hist_method.cpython-311.pyc
   │     │  │  │     ├─ test_misc.cpython-311.pyc
   │     │  │  │     ├─ test_series.cpython-311.pyc
   │     │  │  │     ├─ test_style.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ reductions
   │     │  │  │  ├─ test_reductions.py
   │     │  │  │  ├─ test_stat_reductions.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ test_reductions.cpython-311.pyc
   │     │  │  │     ├─ test_stat_reductions.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ resample
   │     │  │  │  ├─ conftest.py
   │     │  │  │  ├─ test_base.py
   │     │  │  │  ├─ test_datetime_index.py
   │     │  │  │  ├─ test_period_index.py
   │     │  │  │  ├─ test_resampler_grouper.py
   │     │  │  │  ├─ test_resample_api.py
   │     │  │  │  ├─ test_timedelta.py
   │     │  │  │  ├─ test_time_grouper.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ conftest.cpython-311.pyc
   │     │  │  │     ├─ test_base.cpython-311.pyc
   │     │  │  │     ├─ test_datetime_index.cpython-311.pyc
   │     │  │  │     ├─ test_period_index.cpython-311.pyc
   │     │  │  │     ├─ test_resampler_grouper.cpython-311.pyc
   │     │  │  │     ├─ test_resample_api.cpython-311.pyc
   │     │  │  │     ├─ test_timedelta.cpython-311.pyc
   │     │  │  │     ├─ test_time_grouper.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ reshape
   │     │  │  │  ├─ concat
   │     │  │  │  │  ├─ test_append.py
   │     │  │  │  │  ├─ test_append_common.py
   │     │  │  │  │  ├─ test_categorical.py
   │     │  │  │  │  ├─ test_concat.py
   │     │  │  │  │  ├─ test_dataframe.py
   │     │  │  │  │  ├─ test_datetimes.py
   │     │  │  │  │  ├─ test_empty.py
   │     │  │  │  │  ├─ test_index.py
   │     │  │  │  │  ├─ test_invalid.py
   │     │  │  │  │  ├─ test_series.py
   │     │  │  │  │  ├─ test_sort.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ test_append.cpython-311.pyc
   │     │  │  │  │     ├─ test_append_common.cpython-311.pyc
   │     │  │  │  │     ├─ test_categorical.cpython-311.pyc
   │     │  │  │  │     ├─ test_concat.cpython-311.pyc
   │     │  │  │  │     ├─ test_dataframe.cpython-311.pyc
   │     │  │  │  │     ├─ test_datetimes.cpython-311.pyc
   │     │  │  │  │     ├─ test_empty.cpython-311.pyc
   │     │  │  │  │     ├─ test_index.cpython-311.pyc
   │     │  │  │  │     ├─ test_invalid.cpython-311.pyc
   │     │  │  │  │     ├─ test_series.cpython-311.pyc
   │     │  │  │  │     ├─ test_sort.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ merge
   │     │  │  │  │  ├─ test_join.py
   │     │  │  │  │  ├─ test_merge.py
   │     │  │  │  │  ├─ test_merge_antijoin.py
   │     │  │  │  │  ├─ test_merge_asof.py
   │     │  │  │  │  ├─ test_merge_cross.py
   │     │  │  │  │  ├─ test_merge_index_as_string.py
   │     │  │  │  │  ├─ test_merge_ordered.py
   │     │  │  │  │  ├─ test_multi.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ test_join.cpython-311.pyc
   │     │  │  │  │     ├─ test_merge.cpython-311.pyc
   │     │  │  │  │     ├─ test_merge_antijoin.cpython-311.pyc
   │     │  │  │  │     ├─ test_merge_asof.cpython-311.pyc
   │     │  │  │  │     ├─ test_merge_cross.cpython-311.pyc
   │     │  │  │  │     ├─ test_merge_index_as_string.cpython-311.pyc
   │     │  │  │  │     ├─ test_merge_ordered.cpython-311.pyc
   │     │  │  │  │     ├─ test_multi.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ test_crosstab.py
   │     │  │  │  ├─ test_cut.py
   │     │  │  │  ├─ test_from_dummies.py
   │     │  │  │  ├─ test_get_dummies.py
   │     │  │  │  ├─ test_melt.py
   │     │  │  │  ├─ test_pivot.py
   │     │  │  │  ├─ test_pivot_multilevel.py
   │     │  │  │  ├─ test_qcut.py
   │     │  │  │  ├─ test_union_categoricals.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ test_crosstab.cpython-311.pyc
   │     │  │  │     ├─ test_cut.cpython-311.pyc
   │     │  │  │     ├─ test_from_dummies.cpython-311.pyc
   │     │  │  │     ├─ test_get_dummies.cpython-311.pyc
   │     │  │  │     ├─ test_melt.cpython-311.pyc
   │     │  │  │     ├─ test_pivot.cpython-311.pyc
   │     │  │  │     ├─ test_pivot_multilevel.cpython-311.pyc
   │     │  │  │     ├─ test_qcut.cpython-311.pyc
   │     │  │  │     ├─ test_union_categoricals.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ scalar
   │     │  │  │  ├─ interval
   │     │  │  │  │  ├─ test_arithmetic.py
   │     │  │  │  │  ├─ test_constructors.py
   │     │  │  │  │  ├─ test_contains.py
   │     │  │  │  │  ├─ test_formats.py
   │     │  │  │  │  ├─ test_interval.py
   │     │  │  │  │  ├─ test_overlaps.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ test_arithmetic.cpython-311.pyc
   │     │  │  │  │     ├─ test_constructors.cpython-311.pyc
   │     │  │  │  │     ├─ test_contains.cpython-311.pyc
   │     │  │  │  │     ├─ test_formats.cpython-311.pyc
   │     │  │  │  │     ├─ test_interval.cpython-311.pyc
   │     │  │  │  │     ├─ test_overlaps.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ period
   │     │  │  │  │  ├─ test_arithmetic.py
   │     │  │  │  │  ├─ test_asfreq.py
   │     │  │  │  │  ├─ test_period.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ test_arithmetic.cpython-311.pyc
   │     │  │  │  │     ├─ test_asfreq.cpython-311.pyc
   │     │  │  │  │     ├─ test_period.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ test_nat.py
   │     │  │  │  ├─ test_na_scalar.py
   │     │  │  │  ├─ timedelta
   │     │  │  │  │  ├─ methods
   │     │  │  │  │  │  ├─ test_as_unit.py
   │     │  │  │  │  │  ├─ test_round.py
   │     │  │  │  │  │  ├─ __init__.py
   │     │  │  │  │  │  └─ __pycache__
   │     │  │  │  │  │     ├─ test_as_unit.cpython-311.pyc
   │     │  │  │  │  │     ├─ test_round.cpython-311.pyc
   │     │  │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  │  ├─ test_arithmetic.py
   │     │  │  │  │  ├─ test_constructors.py
   │     │  │  │  │  ├─ test_formats.py
   │     │  │  │  │  ├─ test_timedelta.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ test_arithmetic.cpython-311.pyc
   │     │  │  │  │     ├─ test_constructors.cpython-311.pyc
   │     │  │  │  │     ├─ test_formats.cpython-311.pyc
   │     │  │  │  │     ├─ test_timedelta.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ timestamp
   │     │  │  │  │  ├─ methods
   │     │  │  │  │  │  ├─ test_as_unit.py
   │     │  │  │  │  │  ├─ test_normalize.py
   │     │  │  │  │  │  ├─ test_replace.py
   │     │  │  │  │  │  ├─ test_round.py
   │     │  │  │  │  │  ├─ test_timestamp_method.py
   │     │  │  │  │  │  ├─ test_to_julian_date.py
   │     │  │  │  │  │  ├─ test_to_pydatetime.py
   │     │  │  │  │  │  ├─ test_tz_convert.py
   │     │  │  │  │  │  ├─ test_tz_localize.py
   │     │  │  │  │  │  ├─ __init__.py
   │     │  │  │  │  │  └─ __pycache__
   │     │  │  │  │  │     ├─ test_as_unit.cpython-311.pyc
   │     │  │  │  │  │     ├─ test_normalize.cpython-311.pyc
   │     │  │  │  │  │     ├─ test_replace.cpython-311.pyc
   │     │  │  │  │  │     ├─ test_round.cpython-311.pyc
   │     │  │  │  │  │     ├─ test_timestamp_method.cpython-311.pyc
   │     │  │  │  │  │     ├─ test_to_julian_date.cpython-311.pyc
   │     │  │  │  │  │     ├─ test_to_pydatetime.cpython-311.pyc
   │     │  │  │  │  │     ├─ test_tz_convert.cpython-311.pyc
   │     │  │  │  │  │     ├─ test_tz_localize.cpython-311.pyc
   │     │  │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  │  ├─ test_arithmetic.py
   │     │  │  │  │  ├─ test_comparisons.py
   │     │  │  │  │  ├─ test_constructors.py
   │     │  │  │  │  ├─ test_formats.py
   │     │  │  │  │  ├─ test_timestamp.py
   │     │  │  │  │  ├─ test_timezones.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ test_arithmetic.cpython-311.pyc
   │     │  │  │  │     ├─ test_comparisons.cpython-311.pyc
   │     │  │  │  │     ├─ test_constructors.cpython-311.pyc
   │     │  │  │  │     ├─ test_formats.cpython-311.pyc
   │     │  │  │  │     ├─ test_timestamp.cpython-311.pyc
   │     │  │  │  │     ├─ test_timezones.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ test_nat.cpython-311.pyc
   │     │  │  │     ├─ test_na_scalar.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ series
   │     │  │  │  ├─ accessors
   │     │  │  │  │  ├─ test_cat_accessor.py
   │     │  │  │  │  ├─ test_dt_accessor.py
   │     │  │  │  │  ├─ test_list_accessor.py
   │     │  │  │  │  ├─ test_sparse_accessor.py
   │     │  │  │  │  ├─ test_struct_accessor.py
   │     │  │  │  │  ├─ test_str_accessor.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ test_cat_accessor.cpython-311.pyc
   │     │  │  │  │     ├─ test_dt_accessor.cpython-311.pyc
   │     │  │  │  │     ├─ test_list_accessor.cpython-311.pyc
   │     │  │  │  │     ├─ test_sparse_accessor.cpython-311.pyc
   │     │  │  │  │     ├─ test_struct_accessor.cpython-311.pyc
   │     │  │  │  │     ├─ test_str_accessor.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ indexing
   │     │  │  │  │  ├─ test_datetime.py
   │     │  │  │  │  ├─ test_delitem.py
   │     │  │  │  │  ├─ test_get.py
   │     │  │  │  │  ├─ test_getitem.py
   │     │  │  │  │  ├─ test_indexing.py
   │     │  │  │  │  ├─ test_mask.py
   │     │  │  │  │  ├─ test_setitem.py
   │     │  │  │  │  ├─ test_set_value.py
   │     │  │  │  │  ├─ test_take.py
   │     │  │  │  │  ├─ test_where.py
   │     │  │  │  │  ├─ test_xs.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ test_datetime.cpython-311.pyc
   │     │  │  │  │     ├─ test_delitem.cpython-311.pyc
   │     │  │  │  │     ├─ test_get.cpython-311.pyc
   │     │  │  │  │     ├─ test_getitem.cpython-311.pyc
   │     │  │  │  │     ├─ test_indexing.cpython-311.pyc
   │     │  │  │  │     ├─ test_mask.cpython-311.pyc
   │     │  │  │  │     ├─ test_setitem.cpython-311.pyc
   │     │  │  │  │     ├─ test_set_value.cpython-311.pyc
   │     │  │  │  │     ├─ test_take.cpython-311.pyc
   │     │  │  │  │     ├─ test_where.cpython-311.pyc
   │     │  │  │  │     ├─ test_xs.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ methods
   │     │  │  │  │  ├─ test_add_prefix_suffix.py
   │     │  │  │  │  ├─ test_align.py
   │     │  │  │  │  ├─ test_argsort.py
   │     │  │  │  │  ├─ test_asof.py
   │     │  │  │  │  ├─ test_astype.py
   │     │  │  │  │  ├─ test_autocorr.py
   │     │  │  │  │  ├─ test_between.py
   │     │  │  │  │  ├─ test_case_when.py
   │     │  │  │  │  ├─ test_clip.py
   │     │  │  │  │  ├─ test_combine.py
   │     │  │  │  │  ├─ test_combine_first.py
   │     │  │  │  │  ├─ test_compare.py
   │     │  │  │  │  ├─ test_convert_dtypes.py
   │     │  │  │  │  ├─ test_copy.py
   │     │  │  │  │  ├─ test_count.py
   │     │  │  │  │  ├─ test_cov_corr.py
   │     │  │  │  │  ├─ test_describe.py
   │     │  │  │  │  ├─ test_diff.py
   │     │  │  │  │  ├─ test_drop.py
   │     │  │  │  │  ├─ test_dropna.py
   │     │  │  │  │  ├─ test_drop_duplicates.py
   │     │  │  │  │  ├─ test_dtypes.py
   │     │  │  │  │  ├─ test_duplicated.py
   │     │  │  │  │  ├─ test_equals.py
   │     │  │  │  │  ├─ test_explode.py
   │     │  │  │  │  ├─ test_fillna.py
   │     │  │  │  │  ├─ test_get_numeric_data.py
   │     │  │  │  │  ├─ test_head_tail.py
   │     │  │  │  │  ├─ test_infer_objects.py
   │     │  │  │  │  ├─ test_info.py
   │     │  │  │  │  ├─ test_interpolate.py
   │     │  │  │  │  ├─ test_isin.py
   │     │  │  │  │  ├─ test_isna.py
   │     │  │  │  │  ├─ test_is_monotonic.py
   │     │  │  │  │  ├─ test_is_unique.py
   │     │  │  │  │  ├─ test_item.py
   │     │  │  │  │  ├─ test_map.py
   │     │  │  │  │  ├─ test_matmul.py
   │     │  │  │  │  ├─ test_nlargest.py
   │     │  │  │  │  ├─ test_nunique.py
   │     │  │  │  │  ├─ test_pct_change.py
   │     │  │  │  │  ├─ test_pop.py
   │     │  │  │  │  ├─ test_quantile.py
   │     │  │  │  │  ├─ test_rank.py
   │     │  │  │  │  ├─ test_reindex.py
   │     │  │  │  │  ├─ test_reindex_like.py
   │     │  │  │  │  ├─ test_rename.py
   │     │  │  │  │  ├─ test_rename_axis.py
   │     │  │  │  │  ├─ test_repeat.py
   │     │  │  │  │  ├─ test_replace.py
   │     │  │  │  │  ├─ test_reset_index.py
   │     │  │  │  │  ├─ test_round.py
   │     │  │  │  │  ├─ test_searchsorted.py
   │     │  │  │  │  ├─ test_set_name.py
   │     │  │  │  │  ├─ test_size.py
   │     │  │  │  │  ├─ test_sort_index.py
   │     │  │  │  │  ├─ test_sort_values.py
   │     │  │  │  │  ├─ test_tolist.py
   │     │  │  │  │  ├─ test_to_csv.py
   │     │  │  │  │  ├─ test_to_dict.py
   │     │  │  │  │  ├─ test_to_frame.py
   │     │  │  │  │  ├─ test_to_numpy.py
   │     │  │  │  │  ├─ test_truncate.py
   │     │  │  │  │  ├─ test_tz_localize.py
   │     │  │  │  │  ├─ test_unique.py
   │     │  │  │  │  ├─ test_unstack.py
   │     │  │  │  │  ├─ test_update.py
   │     │  │  │  │  ├─ test_values.py
   │     │  │  │  │  ├─ test_value_counts.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ test_add_prefix_suffix.cpython-311.pyc
   │     │  │  │  │     ├─ test_align.cpython-311.pyc
   │     │  │  │  │     ├─ test_argsort.cpython-311.pyc
   │     │  │  │  │     ├─ test_asof.cpython-311.pyc
   │     │  │  │  │     ├─ test_astype.cpython-311.pyc
   │     │  │  │  │     ├─ test_autocorr.cpython-311.pyc
   │     │  │  │  │     ├─ test_between.cpython-311.pyc
   │     │  │  │  │     ├─ test_case_when.cpython-311.pyc
   │     │  │  │  │     ├─ test_clip.cpython-311.pyc
   │     │  │  │  │     ├─ test_combine.cpython-311.pyc
   │     │  │  │  │     ├─ test_combine_first.cpython-311.pyc
   │     │  │  │  │     ├─ test_compare.cpython-311.pyc
   │     │  │  │  │     ├─ test_convert_dtypes.cpython-311.pyc
   │     │  │  │  │     ├─ test_copy.cpython-311.pyc
   │     │  │  │  │     ├─ test_count.cpython-311.pyc
   │     │  │  │  │     ├─ test_cov_corr.cpython-311.pyc
   │     │  │  │  │     ├─ test_describe.cpython-311.pyc
   │     │  │  │  │     ├─ test_diff.cpython-311.pyc
   │     │  │  │  │     ├─ test_drop.cpython-311.pyc
   │     │  │  │  │     ├─ test_dropna.cpython-311.pyc
   │     │  │  │  │     ├─ test_drop_duplicates.cpython-311.pyc
   │     │  │  │  │     ├─ test_dtypes.cpython-311.pyc
   │     │  │  │  │     ├─ test_duplicated.cpython-311.pyc
   │     │  │  │  │     ├─ test_equals.cpython-311.pyc
   │     │  │  │  │     ├─ test_explode.cpython-311.pyc
   │     │  │  │  │     ├─ test_fillna.cpython-311.pyc
   │     │  │  │  │     ├─ test_get_numeric_data.cpython-311.pyc
   │     │  │  │  │     ├─ test_head_tail.cpython-311.pyc
   │     │  │  │  │     ├─ test_infer_objects.cpython-311.pyc
   │     │  │  │  │     ├─ test_info.cpython-311.pyc
   │     │  │  │  │     ├─ test_interpolate.cpython-311.pyc
   │     │  │  │  │     ├─ test_isin.cpython-311.pyc
   │     │  │  │  │     ├─ test_isna.cpython-311.pyc
   │     │  │  │  │     ├─ test_is_monotonic.cpython-311.pyc
   │     │  │  │  │     ├─ test_is_unique.cpython-311.pyc
   │     │  │  │  │     ├─ test_item.cpython-311.pyc
   │     │  │  │  │     ├─ test_map.cpython-311.pyc
   │     │  │  │  │     ├─ test_matmul.cpython-311.pyc
   │     │  │  │  │     ├─ test_nlargest.cpython-311.pyc
   │     │  │  │  │     ├─ test_nunique.cpython-311.pyc
   │     │  │  │  │     ├─ test_pct_change.cpython-311.pyc
   │     │  │  │  │     ├─ test_pop.cpython-311.pyc
   │     │  │  │  │     ├─ test_quantile.cpython-311.pyc
   │     │  │  │  │     ├─ test_rank.cpython-311.pyc
   │     │  │  │  │     ├─ test_reindex.cpython-311.pyc
   │     │  │  │  │     ├─ test_reindex_like.cpython-311.pyc
   │     │  │  │  │     ├─ test_rename.cpython-311.pyc
   │     │  │  │  │     ├─ test_rename_axis.cpython-311.pyc
   │     │  │  │  │     ├─ test_repeat.cpython-311.pyc
   │     │  │  │  │     ├─ test_replace.cpython-311.pyc
   │     │  │  │  │     ├─ test_reset_index.cpython-311.pyc
   │     │  │  │  │     ├─ test_round.cpython-311.pyc
   │     │  │  │  │     ├─ test_searchsorted.cpython-311.pyc
   │     │  │  │  │     ├─ test_set_name.cpython-311.pyc
   │     │  │  │  │     ├─ test_size.cpython-311.pyc
   │     │  │  │  │     ├─ test_sort_index.cpython-311.pyc
   │     │  │  │  │     ├─ test_sort_values.cpython-311.pyc
   │     │  │  │  │     ├─ test_tolist.cpython-311.pyc
   │     │  │  │  │     ├─ test_to_csv.cpython-311.pyc
   │     │  │  │  │     ├─ test_to_dict.cpython-311.pyc
   │     │  │  │  │     ├─ test_to_frame.cpython-311.pyc
   │     │  │  │  │     ├─ test_to_numpy.cpython-311.pyc
   │     │  │  │  │     ├─ test_truncate.cpython-311.pyc
   │     │  │  │  │     ├─ test_tz_localize.cpython-311.pyc
   │     │  │  │  │     ├─ test_unique.cpython-311.pyc
   │     │  │  │  │     ├─ test_unstack.cpython-311.pyc
   │     │  │  │  │     ├─ test_update.cpython-311.pyc
   │     │  │  │  │     ├─ test_values.cpython-311.pyc
   │     │  │  │  │     ├─ test_value_counts.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ test_api.py
   │     │  │  │  ├─ test_arithmetic.py
   │     │  │  │  ├─ test_arrow_interface.py
   │     │  │  │  ├─ test_constructors.py
   │     │  │  │  ├─ test_cumulative.py
   │     │  │  │  ├─ test_formats.py
   │     │  │  │  ├─ test_iteration.py
   │     │  │  │  ├─ test_logical_ops.py
   │     │  │  │  ├─ test_missing.py
   │     │  │  │  ├─ test_npfuncs.py
   │     │  │  │  ├─ test_reductions.py
   │     │  │  │  ├─ test_subclass.py
   │     │  │  │  ├─ test_ufunc.py
   │     │  │  │  ├─ test_unary.py
   │     │  │  │  ├─ test_validate.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ test_api.cpython-311.pyc
   │     │  │  │     ├─ test_arithmetic.cpython-311.pyc
   │     │  │  │     ├─ test_arrow_interface.cpython-311.pyc
   │     │  │  │     ├─ test_constructors.cpython-311.pyc
   │     │  │  │     ├─ test_cumulative.cpython-311.pyc
   │     │  │  │     ├─ test_formats.cpython-311.pyc
   │     │  │  │     ├─ test_iteration.cpython-311.pyc
   │     │  │  │     ├─ test_logical_ops.cpython-311.pyc
   │     │  │  │     ├─ test_missing.cpython-311.pyc
   │     │  │  │     ├─ test_npfuncs.cpython-311.pyc
   │     │  │  │     ├─ test_reductions.cpython-311.pyc
   │     │  │  │     ├─ test_subclass.cpython-311.pyc
   │     │  │  │     ├─ test_ufunc.cpython-311.pyc
   │     │  │  │     ├─ test_unary.cpython-311.pyc
   │     │  │  │     ├─ test_validate.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ strings
   │     │  │  │  ├─ conftest.py
   │     │  │  │  ├─ test_api.py
   │     │  │  │  ├─ test_case_justify.py
   │     │  │  │  ├─ test_cat.py
   │     │  │  │  ├─ test_extract.py
   │     │  │  │  ├─ test_find_replace.py
   │     │  │  │  ├─ test_get_dummies.py
   │     │  │  │  ├─ test_split_partition.py
   │     │  │  │  ├─ test_strings.py
   │     │  │  │  ├─ test_string_array.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ conftest.cpython-311.pyc
   │     │  │  │     ├─ test_api.cpython-311.pyc
   │     │  │  │     ├─ test_case_justify.cpython-311.pyc
   │     │  │  │     ├─ test_cat.cpython-311.pyc
   │     │  │  │     ├─ test_extract.cpython-311.pyc
   │     │  │  │     ├─ test_find_replace.cpython-311.pyc
   │     │  │  │     ├─ test_get_dummies.cpython-311.pyc
   │     │  │  │     ├─ test_split_partition.cpython-311.pyc
   │     │  │  │     ├─ test_strings.cpython-311.pyc
   │     │  │  │     ├─ test_string_array.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ test_aggregation.py
   │     │  │  ├─ test_algos.py
   │     │  │  ├─ test_col.py
   │     │  │  ├─ test_common.py
   │     │  │  ├─ test_downstream.py
   │     │  │  ├─ test_errors.py
   │     │  │  ├─ test_expressions.py
   │     │  │  ├─ test_flags.py
   │     │  │  ├─ test_multilevel.py
   │     │  │  ├─ test_nanops.py
   │     │  │  ├─ test_optional_dependency.py
   │     │  │  ├─ test_register_accessor.py
   │     │  │  ├─ test_sorting.py
   │     │  │  ├─ test_take.py
   │     │  │  ├─ tools
   │     │  │  │  ├─ test_to_datetime.py
   │     │  │  │  ├─ test_to_numeric.py
   │     │  │  │  ├─ test_to_time.py
   │     │  │  │  ├─ test_to_timedelta.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ test_to_datetime.cpython-311.pyc
   │     │  │  │     ├─ test_to_numeric.cpython-311.pyc
   │     │  │  │     ├─ test_to_time.cpython-311.pyc
   │     │  │  │     ├─ test_to_timedelta.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ tseries
   │     │  │  │  ├─ frequencies
   │     │  │  │  │  ├─ test_frequencies.py
   │     │  │  │  │  ├─ test_freq_code.py
   │     │  │  │  │  ├─ test_inference.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ test_frequencies.cpython-311.pyc
   │     │  │  │  │     ├─ test_freq_code.cpython-311.pyc
   │     │  │  │  │     ├─ test_inference.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ holiday
   │     │  │  │  │  ├─ test_calendar.py
   │     │  │  │  │  ├─ test_federal.py
   │     │  │  │  │  ├─ test_holiday.py
   │     │  │  │  │  ├─ test_observance.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ test_calendar.cpython-311.pyc
   │     │  │  │  │     ├─ test_federal.cpython-311.pyc
   │     │  │  │  │     ├─ test_holiday.cpython-311.pyc
   │     │  │  │  │     ├─ test_observance.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ offsets
   │     │  │  │  │  ├─ common.py
   │     │  │  │  │  ├─ test_business_day.py
   │     │  │  │  │  ├─ test_business_halfyear.py
   │     │  │  │  │  ├─ test_business_hour.py
   │     │  │  │  │  ├─ test_business_month.py
   │     │  │  │  │  ├─ test_business_quarter.py
   │     │  │  │  │  ├─ test_business_year.py
   │     │  │  │  │  ├─ test_common.py
   │     │  │  │  │  ├─ test_custom_business_day.py
   │     │  │  │  │  ├─ test_custom_business_hour.py
   │     │  │  │  │  ├─ test_custom_business_month.py
   │     │  │  │  │  ├─ test_dst.py
   │     │  │  │  │  ├─ test_easter.py
   │     │  │  │  │  ├─ test_fiscal.py
   │     │  │  │  │  ├─ test_halfyear.py
   │     │  │  │  │  ├─ test_index.py
   │     │  │  │  │  ├─ test_month.py
   │     │  │  │  │  ├─ test_offsets.py
   │     │  │  │  │  ├─ test_offsets_properties.py
   │     │  │  │  │  ├─ test_quarter.py
   │     │  │  │  │  ├─ test_ticks.py
   │     │  │  │  │  ├─ test_week.py
   │     │  │  │  │  ├─ test_year.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ common.cpython-311.pyc
   │     │  │  │  │     ├─ test_business_day.cpython-311.pyc
   │     │  │  │  │     ├─ test_business_halfyear.cpython-311.pyc
   │     │  │  │  │     ├─ test_business_hour.cpython-311.pyc
   │     │  │  │  │     ├─ test_business_month.cpython-311.pyc
   │     │  │  │  │     ├─ test_business_quarter.cpython-311.pyc
   │     │  │  │  │     ├─ test_business_year.cpython-311.pyc
   │     │  │  │  │     ├─ test_common.cpython-311.pyc
   │     │  │  │  │     ├─ test_custom_business_day.cpython-311.pyc
   │     │  │  │  │     ├─ test_custom_business_hour.cpython-311.pyc
   │     │  │  │  │     ├─ test_custom_business_month.cpython-311.pyc
   │     │  │  │  │     ├─ test_dst.cpython-311.pyc
   │     │  │  │  │     ├─ test_easter.cpython-311.pyc
   │     │  │  │  │     ├─ test_fiscal.cpython-311.pyc
   │     │  │  │  │     ├─ test_halfyear.cpython-311.pyc
   │     │  │  │  │     ├─ test_index.cpython-311.pyc
   │     │  │  │  │     ├─ test_month.cpython-311.pyc
   │     │  │  │  │     ├─ test_offsets.cpython-311.pyc
   │     │  │  │  │     ├─ test_offsets_properties.cpython-311.pyc
   │     │  │  │  │     ├─ test_quarter.cpython-311.pyc
   │     │  │  │  │     ├─ test_ticks.cpython-311.pyc
   │     │  │  │  │     ├─ test_week.cpython-311.pyc
   │     │  │  │  │     ├─ test_year.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ tslibs
   │     │  │  │  ├─ test_api.py
   │     │  │  │  ├─ test_array_to_datetime.py
   │     │  │  │  ├─ test_ccalendar.py
   │     │  │  │  ├─ test_conversion.py
   │     │  │  │  ├─ test_fields.py
   │     │  │  │  ├─ test_libfrequencies.py
   │     │  │  │  ├─ test_liboffsets.py
   │     │  │  │  ├─ test_npy_units.py
   │     │  │  │  ├─ test_np_datetime.py
   │     │  │  │  ├─ test_parse_iso8601.py
   │     │  │  │  ├─ test_parsing.py
   │     │  │  │  ├─ test_period.py
   │     │  │  │  ├─ test_resolution.py
   │     │  │  │  ├─ test_strptime.py
   │     │  │  │  ├─ test_timedeltas.py
   │     │  │  │  ├─ test_timezones.py
   │     │  │  │  ├─ test_to_offset.py
   │     │  │  │  ├─ test_tzconversion.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ test_api.cpython-311.pyc
   │     │  │  │     ├─ test_array_to_datetime.cpython-311.pyc
   │     │  │  │     ├─ test_ccalendar.cpython-311.pyc
   │     │  │  │     ├─ test_conversion.cpython-311.pyc
   │     │  │  │     ├─ test_fields.cpython-311.pyc
   │     │  │  │     ├─ test_libfrequencies.cpython-311.pyc
   │     │  │  │     ├─ test_liboffsets.cpython-311.pyc
   │     │  │  │     ├─ test_npy_units.cpython-311.pyc
   │     │  │  │     ├─ test_np_datetime.cpython-311.pyc
   │     │  │  │     ├─ test_parse_iso8601.cpython-311.pyc
   │     │  │  │     ├─ test_parsing.cpython-311.pyc
   │     │  │  │     ├─ test_period.cpython-311.pyc
   │     │  │  │     ├─ test_resolution.cpython-311.pyc
   │     │  │  │     ├─ test_strptime.cpython-311.pyc
   │     │  │  │     ├─ test_timedeltas.cpython-311.pyc
   │     │  │  │     ├─ test_timezones.cpython-311.pyc
   │     │  │  │     ├─ test_to_offset.cpython-311.pyc
   │     │  │  │     ├─ test_tzconversion.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ util
   │     │  │  │  ├─ conftest.py
   │     │  │  │  ├─ test_assert_almost_equal.py
   │     │  │  │  ├─ test_assert_attr_equal.py
   │     │  │  │  ├─ test_assert_categorical_equal.py
   │     │  │  │  ├─ test_assert_extension_array_equal.py
   │     │  │  │  ├─ test_assert_frame_equal.py
   │     │  │  │  ├─ test_assert_index_equal.py
   │     │  │  │  ├─ test_assert_interval_array_equal.py
   │     │  │  │  ├─ test_assert_numpy_array_equal.py
   │     │  │  │  ├─ test_assert_produces_warning.py
   │     │  │  │  ├─ test_assert_series_equal.py
   │     │  │  │  ├─ test_deprecate.py
   │     │  │  │  ├─ test_deprecate_kwarg.py
   │     │  │  │  ├─ test_deprecate_nonkeyword_arguments.py
   │     │  │  │  ├─ test_doc.py
   │     │  │  │  ├─ test_hashing.py
   │     │  │  │  ├─ test_numba.py
   │     │  │  │  ├─ test_rewrite_warning.py
   │     │  │  │  ├─ test_shares_memory.py
   │     │  │  │  ├─ test_show_versions.py
   │     │  │  │  ├─ test_util.py
   │     │  │  │  ├─ test_validate_args.py
   │     │  │  │  ├─ test_validate_args_and_kwargs.py
   │     │  │  │  ├─ test_validate_inclusive.py
   │     │  │  │  ├─ test_validate_kwargs.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ conftest.cpython-311.pyc
   │     │  │  │     ├─ test_assert_almost_equal.cpython-311.pyc
   │     │  │  │     ├─ test_assert_attr_equal.cpython-311.pyc
   │     │  │  │     ├─ test_assert_categorical_equal.cpython-311.pyc
   │     │  │  │     ├─ test_assert_extension_array_equal.cpython-311.pyc
   │     │  │  │     ├─ test_assert_frame_equal.cpython-311.pyc
   │     │  │  │     ├─ test_assert_index_equal.cpython-311.pyc
   │     │  │  │     ├─ test_assert_interval_array_equal.cpython-311.pyc
   │     │  │  │     ├─ test_assert_numpy_array_equal.cpython-311.pyc
   │     │  │  │     ├─ test_assert_produces_warning.cpython-311.pyc
   │     │  │  │     ├─ test_assert_series_equal.cpython-311.pyc
   │     │  │  │     ├─ test_deprecate.cpython-311.pyc
   │     │  │  │     ├─ test_deprecate_kwarg.cpython-311.pyc
   │     │  │  │     ├─ test_deprecate_nonkeyword_arguments.cpython-311.pyc
   │     │  │  │     ├─ test_doc.cpython-311.pyc
   │     │  │  │     ├─ test_hashing.cpython-311.pyc
   │     │  │  │     ├─ test_numba.cpython-311.pyc
   │     │  │  │     ├─ test_rewrite_warning.cpython-311.pyc
   │     │  │  │     ├─ test_shares_memory.cpython-311.pyc
   │     │  │  │     ├─ test_show_versions.cpython-311.pyc
   │     │  │  │     ├─ test_util.cpython-311.pyc
   │     │  │  │     ├─ test_validate_args.cpython-311.pyc
   │     │  │  │     ├─ test_validate_args_and_kwargs.cpython-311.pyc
   │     │  │  │     ├─ test_validate_inclusive.cpython-311.pyc
   │     │  │  │     ├─ test_validate_kwargs.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ window
   │     │  │  │  ├─ conftest.py
   │     │  │  │  ├─ moments
   │     │  │  │  │  ├─ conftest.py
   │     │  │  │  │  ├─ test_moments_consistency_ewm.py
   │     │  │  │  │  ├─ test_moments_consistency_expanding.py
   │     │  │  │  │  ├─ test_moments_consistency_rolling.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ conftest.cpython-311.pyc
   │     │  │  │  │     ├─ test_moments_consistency_ewm.cpython-311.pyc
   │     │  │  │  │     ├─ test_moments_consistency_expanding.cpython-311.pyc
   │     │  │  │  │     ├─ test_moments_consistency_rolling.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ test_api.py
   │     │  │  │  ├─ test_apply.py
   │     │  │  │  ├─ test_base_indexer.py
   │     │  │  │  ├─ test_cython_aggregations.py
   │     │  │  │  ├─ test_dtypes.py
   │     │  │  │  ├─ test_ewm.py
   │     │  │  │  ├─ test_expanding.py
   │     │  │  │  ├─ test_groupby.py
   │     │  │  │  ├─ test_numba.py
   │     │  │  │  ├─ test_online.py
   │     │  │  │  ├─ test_pairwise.py
   │     │  │  │  ├─ test_rolling.py
   │     │  │  │  ├─ test_rolling_functions.py
   │     │  │  │  ├─ test_rolling_quantile.py
   │     │  │  │  ├─ test_rolling_skew_kurt.py
   │     │  │  │  ├─ test_timeseries_window.py
   │     │  │  │  ├─ test_win_type.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ conftest.cpython-311.pyc
   │     │  │  │     ├─ test_api.cpython-311.pyc
   │     │  │  │     ├─ test_apply.cpython-311.pyc
   │     │  │  │     ├─ test_base_indexer.cpython-311.pyc
   │     │  │  │     ├─ test_cython_aggregations.cpython-311.pyc
   │     │  │  │     ├─ test_dtypes.cpython-311.pyc
   │     │  │  │     ├─ test_ewm.cpython-311.pyc
   │     │  │  │     ├─ test_expanding.cpython-311.pyc
   │     │  │  │     ├─ test_groupby.cpython-311.pyc
   │     │  │  │     ├─ test_numba.cpython-311.pyc
   │     │  │  │     ├─ test_online.cpython-311.pyc
   │     │  │  │     ├─ test_pairwise.cpython-311.pyc
   │     │  │  │     ├─ test_rolling.cpython-311.pyc
   │     │  │  │     ├─ test_rolling_functions.cpython-311.pyc
   │     │  │  │     ├─ test_rolling_quantile.cpython-311.pyc
   │     │  │  │     ├─ test_rolling_skew_kurt.cpython-311.pyc
   │     │  │  │     ├─ test_timeseries_window.cpython-311.pyc
   │     │  │  │     ├─ test_win_type.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ test_aggregation.cpython-311.pyc
   │     │  │     ├─ test_algos.cpython-311.pyc
   │     │  │     ├─ test_col.cpython-311.pyc
   │     │  │     ├─ test_common.cpython-311.pyc
   │     │  │     ├─ test_downstream.cpython-311.pyc
   │     │  │     ├─ test_errors.cpython-311.pyc
   │     │  │     ├─ test_expressions.cpython-311.pyc
   │     │  │     ├─ test_flags.cpython-311.pyc
   │     │  │     ├─ test_multilevel.cpython-311.pyc
   │     │  │     ├─ test_nanops.cpython-311.pyc
   │     │  │     ├─ test_optional_dependency.cpython-311.pyc
   │     │  │     ├─ test_register_accessor.cpython-311.pyc
   │     │  │     ├─ test_sorting.cpython-311.pyc
   │     │  │     ├─ test_take.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ tseries
   │     │  │  ├─ api.py
   │     │  │  ├─ frequencies.py
   │     │  │  ├─ holiday.py
   │     │  │  ├─ offsets.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ api.cpython-311.pyc
   │     │  │     ├─ frequencies.cpython-311.pyc
   │     │  │     ├─ holiday.cpython-311.pyc
   │     │  │     ├─ offsets.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ util
   │     │  │  ├─ version
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ _decorators.py
   │     │  │  ├─ _doctools.py
   │     │  │  ├─ _exceptions.py
   │     │  │  ├─ _print_versions.py
   │     │  │  ├─ _tester.py
   │     │  │  ├─ _test_decorators.py
   │     │  │  ├─ _validators.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ _decorators.cpython-311.pyc
   │     │  │     ├─ _doctools.cpython-311.pyc
   │     │  │     ├─ _exceptions.cpython-311.pyc
   │     │  │     ├─ _print_versions.cpython-311.pyc
   │     │  │     ├─ _tester.cpython-311.pyc
   │     │  │     ├─ _test_decorators.cpython-311.pyc
   │     │  │     ├─ _validators.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ _config
   │     │  │  ├─ config.py
   │     │  │  ├─ dates.py
   │     │  │  ├─ display.py
   │     │  │  ├─ localization.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ config.cpython-311.pyc
   │     │  │     ├─ dates.cpython-311.pyc
   │     │  │     ├─ display.cpython-311.pyc
   │     │  │     ├─ localization.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ _libs
   │     │  │  ├─ algos.cp311-win_amd64.lib
   │     │  │  ├─ algos.cp311-win_amd64.pyd
   │     │  │  ├─ algos.pyi
   │     │  │  ├─ arrays.cp311-win_amd64.lib
   │     │  │  ├─ arrays.cp311-win_amd64.pyd
   │     │  │  ├─ arrays.pyi
   │     │  │  ├─ byteswap.cp311-win_amd64.lib
   │     │  │  ├─ byteswap.cp311-win_amd64.pyd
   │     │  │  ├─ byteswap.pyi
   │     │  │  ├─ groupby.cp311-win_amd64.lib
   │     │  │  ├─ groupby.cp311-win_amd64.pyd
   │     │  │  ├─ groupby.pyi
   │     │  │  ├─ hashing.cp311-win_amd64.lib
   │     │  │  ├─ hashing.cp311-win_amd64.pyd
   │     │  │  ├─ hashing.pyi
   │     │  │  ├─ hashtable.cp311-win_amd64.lib
   │     │  │  ├─ hashtable.cp311-win_amd64.pyd
   │     │  │  ├─ hashtable.pyi
   │     │  │  ├─ index.cp311-win_amd64.lib
   │     │  │  ├─ index.cp311-win_amd64.pyd
   │     │  │  ├─ index.pyi
   │     │  │  ├─ indexing.cp311-win_amd64.lib
   │     │  │  ├─ indexing.cp311-win_amd64.pyd
   │     │  │  ├─ indexing.pyi
   │     │  │  ├─ internals.cp311-win_amd64.lib
   │     │  │  ├─ internals.cp311-win_amd64.pyd
   │     │  │  ├─ internals.pyi
   │     │  │  ├─ interval.cp311-win_amd64.lib
   │     │  │  ├─ interval.cp311-win_amd64.pyd
   │     │  │  ├─ interval.pyi
   │     │  │  ├─ join.cp311-win_amd64.lib
   │     │  │  ├─ join.cp311-win_amd64.pyd
   │     │  │  ├─ join.pyi
   │     │  │  ├─ json.cp311-win_amd64.lib
   │     │  │  ├─ json.cp311-win_amd64.pyd
   │     │  │  ├─ json.pyi
   │     │  │  ├─ lib.cp311-win_amd64.lib
   │     │  │  ├─ lib.cp311-win_amd64.pyd
   │     │  │  ├─ lib.pyi
   │     │  │  ├─ missing.cp311-win_amd64.lib
   │     │  │  ├─ missing.cp311-win_amd64.pyd
   │     │  │  ├─ missing.pyi
   │     │  │  ├─ ops.cp311-win_amd64.lib
   │     │  │  ├─ ops.cp311-win_amd64.pyd
   │     │  │  ├─ ops.pyi
   │     │  │  ├─ ops_dispatch.cp311-win_amd64.lib
   │     │  │  ├─ ops_dispatch.cp311-win_amd64.pyd
   │     │  │  ├─ ops_dispatch.pyi
   │     │  │  ├─ pandas_datetime.cp311-win_amd64.lib
   │     │  │  ├─ pandas_datetime.cp311-win_amd64.pyd
   │     │  │  ├─ pandas_parser.cp311-win_amd64.lib
   │     │  │  ├─ pandas_parser.cp311-win_amd64.pyd
   │     │  │  ├─ parsers.cp311-win_amd64.lib
   │     │  │  ├─ parsers.cp311-win_amd64.pyd
   │     │  │  ├─ parsers.pyi
   │     │  │  ├─ properties.cp311-win_amd64.lib
   │     │  │  ├─ properties.cp311-win_amd64.pyd
   │     │  │  ├─ properties.pyi
   │     │  │  ├─ reshape.cp311-win_amd64.lib
   │     │  │  ├─ reshape.cp311-win_amd64.pyd
   │     │  │  ├─ reshape.pyi
   │     │  │  ├─ sas.cp311-win_amd64.lib
   │     │  │  ├─ sas.cp311-win_amd64.pyd
   │     │  │  ├─ sas.pyi
   │     │  │  ├─ sparse.cp311-win_amd64.lib
   │     │  │  ├─ sparse.cp311-win_amd64.pyd
   │     │  │  ├─ sparse.pyi
   │     │  │  ├─ testing.cp311-win_amd64.lib
   │     │  │  ├─ testing.cp311-win_amd64.pyd
   │     │  │  ├─ testing.pyi
   │     │  │  ├─ tslib.cp311-win_amd64.lib
   │     │  │  ├─ tslib.cp311-win_amd64.pyd
   │     │  │  ├─ tslib.pyi
   │     │  │  ├─ tslibs
   │     │  │  │  ├─ base.cp311-win_amd64.lib
   │     │  │  │  ├─ base.cp311-win_amd64.pyd
   │     │  │  │  ├─ ccalendar.cp311-win_amd64.lib
   │     │  │  │  ├─ ccalendar.cp311-win_amd64.pyd
   │     │  │  │  ├─ ccalendar.pyi
   │     │  │  │  ├─ conversion.cp311-win_amd64.lib
   │     │  │  │  ├─ conversion.cp311-win_amd64.pyd
   │     │  │  │  ├─ conversion.pyi
   │     │  │  │  ├─ dtypes.cp311-win_amd64.lib
   │     │  │  │  ├─ dtypes.cp311-win_amd64.pyd
   │     │  │  │  ├─ dtypes.pyi
   │     │  │  │  ├─ fields.cp311-win_amd64.lib
   │     │  │  │  ├─ fields.cp311-win_amd64.pyd
   │     │  │  │  ├─ fields.pyi
   │     │  │  │  ├─ nattype.cp311-win_amd64.lib
   │     │  │  │  ├─ nattype.cp311-win_amd64.pyd
   │     │  │  │  ├─ nattype.pyi
   │     │  │  │  ├─ np_datetime.cp311-win_amd64.lib
   │     │  │  │  ├─ np_datetime.cp311-win_amd64.pyd
   │     │  │  │  ├─ np_datetime.pyi
   │     │  │  │  ├─ offsets.cp311-win_amd64.lib
   │     │  │  │  ├─ offsets.cp311-win_amd64.pyd
   │     │  │  │  ├─ offsets.pyi
   │     │  │  │  ├─ parsing.cp311-win_amd64.lib
   │     │  │  │  ├─ parsing.cp311-win_amd64.pyd
   │     │  │  │  ├─ parsing.pyi
   │     │  │  │  ├─ period.cp311-win_amd64.lib
   │     │  │  │  ├─ period.cp311-win_amd64.pyd
   │     │  │  │  ├─ period.pyi
   │     │  │  │  ├─ strptime.cp311-win_amd64.lib
   │     │  │  │  ├─ strptime.cp311-win_amd64.pyd
   │     │  │  │  ├─ strptime.pyi
   │     │  │  │  ├─ timedeltas.cp311-win_amd64.lib
   │     │  │  │  ├─ timedeltas.cp311-win_amd64.pyd
   │     │  │  │  ├─ timedeltas.pyi
   │     │  │  │  ├─ timestamps.cp311-win_amd64.lib
   │     │  │  │  ├─ timestamps.cp311-win_amd64.pyd
   │     │  │  │  ├─ timestamps.pyi
   │     │  │  │  ├─ timezones.cp311-win_amd64.lib
   │     │  │  │  ├─ timezones.cp311-win_amd64.pyd
   │     │  │  │  ├─ timezones.pyi
   │     │  │  │  ├─ tzconversion.cp311-win_amd64.lib
   │     │  │  │  ├─ tzconversion.cp311-win_amd64.pyd
   │     │  │  │  ├─ tzconversion.pyi
   │     │  │  │  ├─ vectorized.cp311-win_amd64.lib
   │     │  │  │  ├─ vectorized.cp311-win_amd64.pyd
   │     │  │  │  ├─ vectorized.pyi
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ window
   │     │  │  │  ├─ aggregations.cp311-win_amd64.lib
   │     │  │  │  ├─ aggregations.cp311-win_amd64.pyd
   │     │  │  │  ├─ aggregations.pyi
   │     │  │  │  ├─ indexers.cp311-win_amd64.lib
   │     │  │  │  ├─ indexers.cp311-win_amd64.pyd
   │     │  │  │  ├─ indexers.pyi
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ writers.cp311-win_amd64.lib
   │     │  │  ├─ writers.cp311-win_amd64.pyd
   │     │  │  ├─ writers.pyi
   │     │  │  ├─ _cyutility.cp311-win_amd64.lib
   │     │  │  ├─ _cyutility.cp311-win_amd64.pyd
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ _testing
   │     │  │  ├─ asserters.py
   │     │  │  ├─ compat.py
   │     │  │  ├─ contexts.py
   │     │  │  ├─ _hypothesis.py
   │     │  │  ├─ _io.py
   │     │  │  ├─ _warnings.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ asserters.cpython-311.pyc
   │     │  │     ├─ compat.cpython-311.pyc
   │     │  │     ├─ contexts.cpython-311.pyc
   │     │  │     ├─ _hypothesis.cpython-311.pyc
   │     │  │     ├─ _io.cpython-311.pyc
   │     │  │     ├─ _warnings.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ _typing.py
   │     │  ├─ _version.py
   │     │  ├─ _version_meson.py
   │     │  ├─ __init__.py
   │     │  └─ __pycache__
   │     │     ├─ conftest.cpython-311.pyc
   │     │     ├─ testing.cpython-311.pyc
   │     │     ├─ _typing.cpython-311.pyc
   │     │     ├─ _version.cpython-311.pyc
   │     │     ├─ _version_meson.cpython-311.pyc
   │     │     └─ __init__.cpython-311.pyc
   │     ├─ pandas-3.0.2.dist-info
   │     │  ├─ DELVEWHEEL
   │     │  ├─ entry_points.txt
   │     │  ├─ INSTALLER
   │     │  ├─ LICENSE
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  └─ WHEEL
   │     ├─ pandas.libs
   │     │  └─ msvcp140-a4c2229bdc2a2a630acdc095b4d86008.dll
   │     ├─ PIL
   │     │  ├─ AvifImagePlugin.py
   │     │  ├─ BdfFontFile.py
   │     │  ├─ BlpImagePlugin.py
   │     │  ├─ BmpImagePlugin.py
   │     │  ├─ BufrStubImagePlugin.py
   │     │  ├─ ContainerIO.py
   │     │  ├─ CurImagePlugin.py
   │     │  ├─ DcxImagePlugin.py
   │     │  ├─ DdsImagePlugin.py
   │     │  ├─ EpsImagePlugin.py
   │     │  ├─ ExifTags.py
   │     │  ├─ features.py
   │     │  ├─ FitsImagePlugin.py
   │     │  ├─ FliImagePlugin.py
   │     │  ├─ FontFile.py
   │     │  ├─ FpxImagePlugin.py
   │     │  ├─ FtexImagePlugin.py
   │     │  ├─ GbrImagePlugin.py
   │     │  ├─ GdImageFile.py
   │     │  ├─ GifImagePlugin.py
   │     │  ├─ GimpGradientFile.py
   │     │  ├─ GimpPaletteFile.py
   │     │  ├─ GribStubImagePlugin.py
   │     │  ├─ Hdf5StubImagePlugin.py
   │     │  ├─ IcnsImagePlugin.py
   │     │  ├─ IcoImagePlugin.py
   │     │  ├─ Image.py
   │     │  ├─ ImageChops.py
   │     │  ├─ ImageCms.py
   │     │  ├─ ImageColor.py
   │     │  ├─ ImageDraw.py
   │     │  ├─ ImageDraw2.py
   │     │  ├─ ImageEnhance.py
   │     │  ├─ ImageFile.py
   │     │  ├─ ImageFilter.py
   │     │  ├─ ImageFont.py
   │     │  ├─ ImageGrab.py
   │     │  ├─ ImageMath.py
   │     │  ├─ ImageMode.py
   │     │  ├─ ImageMorph.py
   │     │  ├─ ImageOps.py
   │     │  ├─ ImagePalette.py
   │     │  ├─ ImagePath.py
   │     │  ├─ ImageQt.py
   │     │  ├─ ImageSequence.py
   │     │  ├─ ImageShow.py
   │     │  ├─ ImageStat.py
   │     │  ├─ ImageText.py
   │     │  ├─ ImageTk.py
   │     │  ├─ ImageTransform.py
   │     │  ├─ ImageWin.py
   │     │  ├─ ImImagePlugin.py
   │     │  ├─ ImtImagePlugin.py
   │     │  ├─ IptcImagePlugin.py
   │     │  ├─ Jpeg2KImagePlugin.py
   │     │  ├─ JpegImagePlugin.py
   │     │  ├─ JpegPresets.py
   │     │  ├─ McIdasImagePlugin.py
   │     │  ├─ MicImagePlugin.py
   │     │  ├─ MpegImagePlugin.py
   │     │  ├─ MpoImagePlugin.py
   │     │  ├─ MspImagePlugin.py
   │     │  ├─ PaletteFile.py
   │     │  ├─ PalmImagePlugin.py
   │     │  ├─ PcdImagePlugin.py
   │     │  ├─ PcfFontFile.py
   │     │  ├─ PcxImagePlugin.py
   │     │  ├─ PdfImagePlugin.py
   │     │  ├─ PdfParser.py
   │     │  ├─ PixarImagePlugin.py
   │     │  ├─ PngImagePlugin.py
   │     │  ├─ PpmImagePlugin.py
   │     │  ├─ PsdImagePlugin.py
   │     │  ├─ PSDraw.py
   │     │  ├─ py.typed
   │     │  ├─ QoiImagePlugin.py
   │     │  ├─ report.py
   │     │  ├─ SgiImagePlugin.py
   │     │  ├─ SpiderImagePlugin.py
   │     │  ├─ SunImagePlugin.py
   │     │  ├─ TarIO.py
   │     │  ├─ TgaImagePlugin.py
   │     │  ├─ TiffImagePlugin.py
   │     │  ├─ TiffTags.py
   │     │  ├─ WalImageFile.py
   │     │  ├─ WebPImagePlugin.py
   │     │  ├─ WmfImagePlugin.py
   │     │  ├─ XbmImagePlugin.py
   │     │  ├─ XpmImagePlugin.py
   │     │  ├─ XVThumbImagePlugin.py
   │     │  ├─ _avif.cp311-win_amd64.pyd
   │     │  ├─ _avif.pyi
   │     │  ├─ _binary.py
   │     │  ├─ _deprecate.py
   │     │  ├─ _imaging.cp311-win_amd64.pyd
   │     │  ├─ _imaging.pyi
   │     │  ├─ _imagingcms.cp311-win_amd64.pyd
   │     │  ├─ _imagingcms.pyi
   │     │  ├─ _imagingft.cp311-win_amd64.pyd
   │     │  ├─ _imagingft.pyi
   │     │  ├─ _imagingmath.cp311-win_amd64.pyd
   │     │  ├─ _imagingmath.pyi
   │     │  ├─ _imagingmorph.cp311-win_amd64.pyd
   │     │  ├─ _imagingmorph.pyi
   │     │  ├─ _imagingtk.cp311-win_amd64.pyd
   │     │  ├─ _imagingtk.pyi
   │     │  ├─ _tkinter_finder.py
   │     │  ├─ _typing.py
   │     │  ├─ _util.py
   │     │  ├─ _version.py
   │     │  ├─ _webp.cp311-win_amd64.pyd
   │     │  ├─ _webp.pyi
   │     │  ├─ __init__.py
   │     │  ├─ __main__.py
   │     │  └─ __pycache__
   │     │     ├─ AvifImagePlugin.cpython-311.pyc
   │     │     ├─ BdfFontFile.cpython-311.pyc
   │     │     ├─ BlpImagePlugin.cpython-311.pyc
   │     │     ├─ BmpImagePlugin.cpython-311.pyc
   │     │     ├─ BufrStubImagePlugin.cpython-311.pyc
   │     │     ├─ ContainerIO.cpython-311.pyc
   │     │     ├─ CurImagePlugin.cpython-311.pyc
   │     │     ├─ DcxImagePlugin.cpython-311.pyc
   │     │     ├─ DdsImagePlugin.cpython-311.pyc
   │     │     ├─ EpsImagePlugin.cpython-311.pyc
   │     │     ├─ ExifTags.cpython-311.pyc
   │     │     ├─ features.cpython-311.pyc
   │     │     ├─ FitsImagePlugin.cpython-311.pyc
   │     │     ├─ FliImagePlugin.cpython-311.pyc
   │     │     ├─ FontFile.cpython-311.pyc
   │     │     ├─ FpxImagePlugin.cpython-311.pyc
   │     │     ├─ FtexImagePlugin.cpython-311.pyc
   │     │     ├─ GbrImagePlugin.cpython-311.pyc
   │     │     ├─ GdImageFile.cpython-311.pyc
   │     │     ├─ GifImagePlugin.cpython-311.pyc
   │     │     ├─ GimpGradientFile.cpython-311.pyc
   │     │     ├─ GimpPaletteFile.cpython-311.pyc
   │     │     ├─ GribStubImagePlugin.cpython-311.pyc
   │     │     ├─ Hdf5StubImagePlugin.cpython-311.pyc
   │     │     ├─ IcnsImagePlugin.cpython-311.pyc
   │     │     ├─ IcoImagePlugin.cpython-311.pyc
   │     │     ├─ Image.cpython-311.pyc
   │     │     ├─ ImageChops.cpython-311.pyc
   │     │     ├─ ImageCms.cpython-311.pyc
   │     │     ├─ ImageColor.cpython-311.pyc
   │     │     ├─ ImageDraw.cpython-311.pyc
   │     │     ├─ ImageDraw2.cpython-311.pyc
   │     │     ├─ ImageEnhance.cpython-311.pyc
   │     │     ├─ ImageFile.cpython-311.pyc
   │     │     ├─ ImageFilter.cpython-311.pyc
   │     │     ├─ ImageFont.cpython-311.pyc
   │     │     ├─ ImageGrab.cpython-311.pyc
   │     │     ├─ ImageMath.cpython-311.pyc
   │     │     ├─ ImageMode.cpython-311.pyc
   │     │     ├─ ImageMorph.cpython-311.pyc
   │     │     ├─ ImageOps.cpython-311.pyc
   │     │     ├─ ImagePalette.cpython-311.pyc
   │     │     ├─ ImagePath.cpython-311.pyc
   │     │     ├─ ImageQt.cpython-311.pyc
   │     │     ├─ ImageSequence.cpython-311.pyc
   │     │     ├─ ImageShow.cpython-311.pyc
   │     │     ├─ ImageStat.cpython-311.pyc
   │     │     ├─ ImageText.cpython-311.pyc
   │     │     ├─ ImageTk.cpython-311.pyc
   │     │     ├─ ImageTransform.cpython-311.pyc
   │     │     ├─ ImageWin.cpython-311.pyc
   │     │     ├─ ImImagePlugin.cpython-311.pyc
   │     │     ├─ ImtImagePlugin.cpython-311.pyc
   │     │     ├─ IptcImagePlugin.cpython-311.pyc
   │     │     ├─ Jpeg2KImagePlugin.cpython-311.pyc
   │     │     ├─ JpegImagePlugin.cpython-311.pyc
   │     │     ├─ JpegPresets.cpython-311.pyc
   │     │     ├─ McIdasImagePlugin.cpython-311.pyc
   │     │     ├─ MicImagePlugin.cpython-311.pyc
   │     │     ├─ MpegImagePlugin.cpython-311.pyc
   │     │     ├─ MpoImagePlugin.cpython-311.pyc
   │     │     ├─ MspImagePlugin.cpython-311.pyc
   │     │     ├─ PaletteFile.cpython-311.pyc
   │     │     ├─ PalmImagePlugin.cpython-311.pyc
   │     │     ├─ PcdImagePlugin.cpython-311.pyc
   │     │     ├─ PcfFontFile.cpython-311.pyc
   │     │     ├─ PcxImagePlugin.cpython-311.pyc
   │     │     ├─ PdfImagePlugin.cpython-311.pyc
   │     │     ├─ PdfParser.cpython-311.pyc
   │     │     ├─ PixarImagePlugin.cpython-311.pyc
   │     │     ├─ PngImagePlugin.cpython-311.pyc
   │     │     ├─ PpmImagePlugin.cpython-311.pyc
   │     │     ├─ PsdImagePlugin.cpython-311.pyc
   │     │     ├─ PSDraw.cpython-311.pyc
   │     │     ├─ QoiImagePlugin.cpython-311.pyc
   │     │     ├─ report.cpython-311.pyc
   │     │     ├─ SgiImagePlugin.cpython-311.pyc
   │     │     ├─ SpiderImagePlugin.cpython-311.pyc
   │     │     ├─ SunImagePlugin.cpython-311.pyc
   │     │     ├─ TarIO.cpython-311.pyc
   │     │     ├─ TgaImagePlugin.cpython-311.pyc
   │     │     ├─ TiffImagePlugin.cpython-311.pyc
   │     │     ├─ TiffTags.cpython-311.pyc
   │     │     ├─ WalImageFile.cpython-311.pyc
   │     │     ├─ WebPImagePlugin.cpython-311.pyc
   │     │     ├─ WmfImagePlugin.cpython-311.pyc
   │     │     ├─ XbmImagePlugin.cpython-311.pyc
   │     │     ├─ XpmImagePlugin.cpython-311.pyc
   │     │     ├─ XVThumbImagePlugin.cpython-311.pyc
   │     │     ├─ _binary.cpython-311.pyc
   │     │     ├─ _deprecate.cpython-311.pyc
   │     │     ├─ _tkinter_finder.cpython-311.pyc
   │     │     ├─ _typing.cpython-311.pyc
   │     │     ├─ _util.cpython-311.pyc
   │     │     ├─ _version.cpython-311.pyc
   │     │     ├─ __init__.cpython-311.pyc
   │     │     └─ __main__.cpython-311.pyc
   │     ├─ pillow-12.2.0.dist-info
   │     │  ├─ INSTALLER
   │     │  ├─ licenses
   │     │  │  └─ LICENSE
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  ├─ top_level.txt
   │     │  ├─ WHEEL
   │     │  └─ zip-safe
   │     ├─ pip
   │     │  ├─ py.typed
   │     │  ├─ _internal
   │     │  │  ├─ build_env.py
   │     │  │  ├─ cache.py
   │     │  │  ├─ cli
   │     │  │  │  ├─ autocompletion.py
   │     │  │  │  ├─ base_command.py
   │     │  │  │  ├─ cmdoptions.py
   │     │  │  │  ├─ command_context.py
   │     │  │  │  ├─ main.py
   │     │  │  │  ├─ main_parser.py
   │     │  │  │  ├─ parser.py
   │     │  │  │  ├─ progress_bars.py
   │     │  │  │  ├─ req_command.py
   │     │  │  │  ├─ spinners.py
   │     │  │  │  ├─ status_codes.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ autocompletion.cpython-311.pyc
   │     │  │  │     ├─ base_command.cpython-311.pyc
   │     │  │  │     ├─ cmdoptions.cpython-311.pyc
   │     │  │  │     ├─ command_context.cpython-311.pyc
   │     │  │  │     ├─ main.cpython-311.pyc
   │     │  │  │     ├─ main_parser.cpython-311.pyc
   │     │  │  │     ├─ parser.cpython-311.pyc
   │     │  │  │     ├─ progress_bars.cpython-311.pyc
   │     │  │  │     ├─ req_command.cpython-311.pyc
   │     │  │  │     ├─ spinners.cpython-311.pyc
   │     │  │  │     ├─ status_codes.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ commands
   │     │  │  │  ├─ cache.py
   │     │  │  │  ├─ check.py
   │     │  │  │  ├─ completion.py
   │     │  │  │  ├─ configuration.py
   │     │  │  │  ├─ debug.py
   │     │  │  │  ├─ download.py
   │     │  │  │  ├─ freeze.py
   │     │  │  │  ├─ hash.py
   │     │  │  │  ├─ help.py
   │     │  │  │  ├─ index.py
   │     │  │  │  ├─ inspect.py
   │     │  │  │  ├─ install.py
   │     │  │  │  ├─ list.py
   │     │  │  │  ├─ search.py
   │     │  │  │  ├─ show.py
   │     │  │  │  ├─ uninstall.py
   │     │  │  │  ├─ wheel.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ cache.cpython-311.pyc
   │     │  │  │     ├─ check.cpython-311.pyc
   │     │  │  │     ├─ completion.cpython-311.pyc
   │     │  │  │     ├─ configuration.cpython-311.pyc
   │     │  │  │     ├─ debug.cpython-311.pyc
   │     │  │  │     ├─ download.cpython-311.pyc
   │     │  │  │     ├─ freeze.cpython-311.pyc
   │     │  │  │     ├─ hash.cpython-311.pyc
   │     │  │  │     ├─ help.cpython-311.pyc
   │     │  │  │     ├─ index.cpython-311.pyc
   │     │  │  │     ├─ inspect.cpython-311.pyc
   │     │  │  │     ├─ install.cpython-311.pyc
   │     │  │  │     ├─ list.cpython-311.pyc
   │     │  │  │     ├─ search.cpython-311.pyc
   │     │  │  │     ├─ show.cpython-311.pyc
   │     │  │  │     ├─ uninstall.cpython-311.pyc
   │     │  │  │     ├─ wheel.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ configuration.py
   │     │  │  ├─ distributions
   │     │  │  │  ├─ base.py
   │     │  │  │  ├─ installed.py
   │     │  │  │  ├─ sdist.py
   │     │  │  │  ├─ wheel.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ base.cpython-311.pyc
   │     │  │  │     ├─ installed.cpython-311.pyc
   │     │  │  │     ├─ sdist.cpython-311.pyc
   │     │  │  │     ├─ wheel.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ exceptions.py
   │     │  │  ├─ index
   │     │  │  │  ├─ collector.py
   │     │  │  │  ├─ package_finder.py
   │     │  │  │  ├─ sources.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ collector.cpython-311.pyc
   │     │  │  │     ├─ package_finder.cpython-311.pyc
   │     │  │  │     ├─ sources.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ locations
   │     │  │  │  ├─ base.py
   │     │  │  │  ├─ _distutils.py
   │     │  │  │  ├─ _sysconfig.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ base.cpython-311.pyc
   │     │  │  │     ├─ _distutils.cpython-311.pyc
   │     │  │  │     ├─ _sysconfig.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ main.py
   │     │  │  ├─ metadata
   │     │  │  │  ├─ base.py
   │     │  │  │  ├─ importlib
   │     │  │  │  │  ├─ _compat.py
   │     │  │  │  │  ├─ _dists.py
   │     │  │  │  │  ├─ _envs.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ _compat.cpython-311.pyc
   │     │  │  │  │     ├─ _dists.cpython-311.pyc
   │     │  │  │  │     ├─ _envs.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ pkg_resources.py
   │     │  │  │  ├─ _json.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ base.cpython-311.pyc
   │     │  │  │     ├─ pkg_resources.cpython-311.pyc
   │     │  │  │     ├─ _json.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ models
   │     │  │  │  ├─ candidate.py
   │     │  │  │  ├─ direct_url.py
   │     │  │  │  ├─ format_control.py
   │     │  │  │  ├─ index.py
   │     │  │  │  ├─ installation_report.py
   │     │  │  │  ├─ link.py
   │     │  │  │  ├─ scheme.py
   │     │  │  │  ├─ search_scope.py
   │     │  │  │  ├─ selection_prefs.py
   │     │  │  │  ├─ target_python.py
   │     │  │  │  ├─ wheel.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ candidate.cpython-311.pyc
   │     │  │  │     ├─ direct_url.cpython-311.pyc
   │     │  │  │     ├─ format_control.cpython-311.pyc
   │     │  │  │     ├─ index.cpython-311.pyc
   │     │  │  │     ├─ installation_report.cpython-311.pyc
   │     │  │  │     ├─ link.cpython-311.pyc
   │     │  │  │     ├─ scheme.cpython-311.pyc
   │     │  │  │     ├─ search_scope.cpython-311.pyc
   │     │  │  │     ├─ selection_prefs.cpython-311.pyc
   │     │  │  │     ├─ target_python.cpython-311.pyc
   │     │  │  │     ├─ wheel.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ network
   │     │  │  │  ├─ auth.py
   │     │  │  │  ├─ cache.py
   │     │  │  │  ├─ download.py
   │     │  │  │  ├─ lazy_wheel.py
   │     │  │  │  ├─ session.py
   │     │  │  │  ├─ utils.py
   │     │  │  │  ├─ xmlrpc.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ auth.cpython-311.pyc
   │     │  │  │     ├─ cache.cpython-311.pyc
   │     │  │  │     ├─ download.cpython-311.pyc
   │     │  │  │     ├─ lazy_wheel.cpython-311.pyc
   │     │  │  │     ├─ session.cpython-311.pyc
   │     │  │  │     ├─ utils.cpython-311.pyc
   │     │  │  │     ├─ xmlrpc.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ operations
   │     │  │  │  ├─ build
   │     │  │  │  │  ├─ build_tracker.py
   │     │  │  │  │  ├─ metadata.py
   │     │  │  │  │  ├─ metadata_editable.py
   │     │  │  │  │  ├─ metadata_legacy.py
   │     │  │  │  │  ├─ wheel.py
   │     │  │  │  │  ├─ wheel_editable.py
   │     │  │  │  │  ├─ wheel_legacy.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ build_tracker.cpython-311.pyc
   │     │  │  │  │     ├─ metadata.cpython-311.pyc
   │     │  │  │  │     ├─ metadata_editable.cpython-311.pyc
   │     │  │  │  │     ├─ metadata_legacy.cpython-311.pyc
   │     │  │  │  │     ├─ wheel.cpython-311.pyc
   │     │  │  │  │     ├─ wheel_editable.cpython-311.pyc
   │     │  │  │  │     ├─ wheel_legacy.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ check.py
   │     │  │  │  ├─ freeze.py
   │     │  │  │  ├─ install
   │     │  │  │  │  ├─ editable_legacy.py
   │     │  │  │  │  ├─ wheel.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ editable_legacy.cpython-311.pyc
   │     │  │  │  │     ├─ wheel.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ prepare.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ check.cpython-311.pyc
   │     │  │  │     ├─ freeze.cpython-311.pyc
   │     │  │  │     ├─ prepare.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ pyproject.py
   │     │  │  ├─ req
   │     │  │  │  ├─ constructors.py
   │     │  │  │  ├─ req_file.py
   │     │  │  │  ├─ req_install.py
   │     │  │  │  ├─ req_set.py
   │     │  │  │  ├─ req_uninstall.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ constructors.cpython-311.pyc
   │     │  │  │     ├─ req_file.cpython-311.pyc
   │     │  │  │     ├─ req_install.cpython-311.pyc
   │     │  │  │     ├─ req_set.cpython-311.pyc
   │     │  │  │     ├─ req_uninstall.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ resolution
   │     │  │  │  ├─ base.py
   │     │  │  │  ├─ legacy
   │     │  │  │  │  ├─ resolver.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ resolver.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ resolvelib
   │     │  │  │  │  ├─ base.py
   │     │  │  │  │  ├─ candidates.py
   │     │  │  │  │  ├─ factory.py
   │     │  │  │  │  ├─ found_candidates.py
   │     │  │  │  │  ├─ provider.py
   │     │  │  │  │  ├─ reporter.py
   │     │  │  │  │  ├─ requirements.py
   │     │  │  │  │  ├─ resolver.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ base.cpython-311.pyc
   │     │  │  │  │     ├─ candidates.cpython-311.pyc
   │     │  │  │  │     ├─ factory.cpython-311.pyc
   │     │  │  │  │     ├─ found_candidates.cpython-311.pyc
   │     │  │  │  │     ├─ provider.cpython-311.pyc
   │     │  │  │  │     ├─ reporter.cpython-311.pyc
   │     │  │  │  │     ├─ requirements.cpython-311.pyc
   │     │  │  │  │     ├─ resolver.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ base.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ self_outdated_check.py
   │     │  │  ├─ utils
   │     │  │  │  ├─ appdirs.py
   │     │  │  │  ├─ compat.py
   │     │  │  │  ├─ compatibility_tags.py
   │     │  │  │  ├─ datetime.py
   │     │  │  │  ├─ deprecation.py
   │     │  │  │  ├─ direct_url_helpers.py
   │     │  │  │  ├─ egg_link.py
   │     │  │  │  ├─ encoding.py
   │     │  │  │  ├─ entrypoints.py
   │     │  │  │  ├─ filesystem.py
   │     │  │  │  ├─ filetypes.py
   │     │  │  │  ├─ glibc.py
   │     │  │  │  ├─ hashes.py
   │     │  │  │  ├─ logging.py
   │     │  │  │  ├─ misc.py
   │     │  │  │  ├─ models.py
   │     │  │  │  ├─ packaging.py
   │     │  │  │  ├─ setuptools_build.py
   │     │  │  │  ├─ subprocess.py
   │     │  │  │  ├─ temp_dir.py
   │     │  │  │  ├─ unpacking.py
   │     │  │  │  ├─ urls.py
   │     │  │  │  ├─ virtualenv.py
   │     │  │  │  ├─ wheel.py
   │     │  │  │  ├─ _jaraco_text.py
   │     │  │  │  ├─ _log.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ appdirs.cpython-311.pyc
   │     │  │  │     ├─ compat.cpython-311.pyc
   │     │  │  │     ├─ compatibility_tags.cpython-311.pyc
   │     │  │  │     ├─ datetime.cpython-311.pyc
   │     │  │  │     ├─ deprecation.cpython-311.pyc
   │     │  │  │     ├─ direct_url_helpers.cpython-311.pyc
   │     │  │  │     ├─ egg_link.cpython-311.pyc
   │     │  │  │     ├─ encoding.cpython-311.pyc
   │     │  │  │     ├─ entrypoints.cpython-311.pyc
   │     │  │  │     ├─ filesystem.cpython-311.pyc
   │     │  │  │     ├─ filetypes.cpython-311.pyc
   │     │  │  │     ├─ glibc.cpython-311.pyc
   │     │  │  │     ├─ hashes.cpython-311.pyc
   │     │  │  │     ├─ logging.cpython-311.pyc
   │     │  │  │     ├─ misc.cpython-311.pyc
   │     │  │  │     ├─ models.cpython-311.pyc
   │     │  │  │     ├─ packaging.cpython-311.pyc
   │     │  │  │     ├─ setuptools_build.cpython-311.pyc
   │     │  │  │     ├─ subprocess.cpython-311.pyc
   │     │  │  │     ├─ temp_dir.cpython-311.pyc
   │     │  │  │     ├─ unpacking.cpython-311.pyc
   │     │  │  │     ├─ urls.cpython-311.pyc
   │     │  │  │     ├─ virtualenv.cpython-311.pyc
   │     │  │  │     ├─ wheel.cpython-311.pyc
   │     │  │  │     ├─ _jaraco_text.cpython-311.pyc
   │     │  │  │     ├─ _log.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ vcs
   │     │  │  │  ├─ bazaar.py
   │     │  │  │  ├─ git.py
   │     │  │  │  ├─ mercurial.py
   │     │  │  │  ├─ subversion.py
   │     │  │  │  ├─ versioncontrol.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ bazaar.cpython-311.pyc
   │     │  │  │     ├─ git.cpython-311.pyc
   │     │  │  │     ├─ mercurial.cpython-311.pyc
   │     │  │  │     ├─ subversion.cpython-311.pyc
   │     │  │  │     ├─ versioncontrol.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ wheel_builder.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ build_env.cpython-311.pyc
   │     │  │     ├─ cache.cpython-311.pyc
   │     │  │     ├─ configuration.cpython-311.pyc
   │     │  │     ├─ exceptions.cpython-311.pyc
   │     │  │     ├─ main.cpython-311.pyc
   │     │  │     ├─ pyproject.cpython-311.pyc
   │     │  │     ├─ self_outdated_check.cpython-311.pyc
   │     │  │     ├─ wheel_builder.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ _vendor
   │     │  │  ├─ cachecontrol
   │     │  │  │  ├─ adapter.py
   │     │  │  │  ├─ cache.py
   │     │  │  │  ├─ caches
   │     │  │  │  │  ├─ file_cache.py
   │     │  │  │  │  ├─ redis_cache.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ file_cache.cpython-311.pyc
   │     │  │  │  │     ├─ redis_cache.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ controller.py
   │     │  │  │  ├─ filewrapper.py
   │     │  │  │  ├─ heuristics.py
   │     │  │  │  ├─ py.typed
   │     │  │  │  ├─ serialize.py
   │     │  │  │  ├─ wrapper.py
   │     │  │  │  ├─ _cmd.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ adapter.cpython-311.pyc
   │     │  │  │     ├─ cache.cpython-311.pyc
   │     │  │  │     ├─ controller.cpython-311.pyc
   │     │  │  │     ├─ filewrapper.cpython-311.pyc
   │     │  │  │     ├─ heuristics.cpython-311.pyc
   │     │  │  │     ├─ serialize.cpython-311.pyc
   │     │  │  │     ├─ wrapper.cpython-311.pyc
   │     │  │  │     ├─ _cmd.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ certifi
   │     │  │  │  ├─ cacert.pem
   │     │  │  │  ├─ core.py
   │     │  │  │  ├─ py.typed
   │     │  │  │  ├─ __init__.py
   │     │  │  │  ├─ __main__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ core.cpython-311.pyc
   │     │  │  │     ├─ __init__.cpython-311.pyc
   │     │  │  │     └─ __main__.cpython-311.pyc
   │     │  │  ├─ chardet
   │     │  │  │  ├─ big5freq.py
   │     │  │  │  ├─ big5prober.py
   │     │  │  │  ├─ chardistribution.py
   │     │  │  │  ├─ charsetgroupprober.py
   │     │  │  │  ├─ charsetprober.py
   │     │  │  │  ├─ cli
   │     │  │  │  │  ├─ chardetect.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ chardetect.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ codingstatemachine.py
   │     │  │  │  ├─ codingstatemachinedict.py
   │     │  │  │  ├─ cp949prober.py
   │     │  │  │  ├─ enums.py
   │     │  │  │  ├─ escprober.py
   │     │  │  │  ├─ escsm.py
   │     │  │  │  ├─ eucjpprober.py
   │     │  │  │  ├─ euckrfreq.py
   │     │  │  │  ├─ euckrprober.py
   │     │  │  │  ├─ euctwfreq.py
   │     │  │  │  ├─ euctwprober.py
   │     │  │  │  ├─ gb2312freq.py
   │     │  │  │  ├─ gb2312prober.py
   │     │  │  │  ├─ hebrewprober.py
   │     │  │  │  ├─ jisfreq.py
   │     │  │  │  ├─ johabfreq.py
   │     │  │  │  ├─ johabprober.py
   │     │  │  │  ├─ jpcntx.py
   │     │  │  │  ├─ langbulgarianmodel.py
   │     │  │  │  ├─ langgreekmodel.py
   │     │  │  │  ├─ langhebrewmodel.py
   │     │  │  │  ├─ langhungarianmodel.py
   │     │  │  │  ├─ langrussianmodel.py
   │     │  │  │  ├─ langthaimodel.py
   │     │  │  │  ├─ langturkishmodel.py
   │     │  │  │  ├─ latin1prober.py
   │     │  │  │  ├─ macromanprober.py
   │     │  │  │  ├─ mbcharsetprober.py
   │     │  │  │  ├─ mbcsgroupprober.py
   │     │  │  │  ├─ mbcssm.py
   │     │  │  │  ├─ metadata
   │     │  │  │  │  ├─ languages.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ languages.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ py.typed
   │     │  │  │  ├─ resultdict.py
   │     │  │  │  ├─ sbcharsetprober.py
   │     │  │  │  ├─ sbcsgroupprober.py
   │     │  │  │  ├─ sjisprober.py
   │     │  │  │  ├─ universaldetector.py
   │     │  │  │  ├─ utf1632prober.py
   │     │  │  │  ├─ utf8prober.py
   │     │  │  │  ├─ version.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ big5freq.cpython-311.pyc
   │     │  │  │     ├─ big5prober.cpython-311.pyc
   │     │  │  │     ├─ chardistribution.cpython-311.pyc
   │     │  │  │     ├─ charsetgroupprober.cpython-311.pyc
   │     │  │  │     ├─ charsetprober.cpython-311.pyc
   │     │  │  │     ├─ codingstatemachine.cpython-311.pyc
   │     │  │  │     ├─ codingstatemachinedict.cpython-311.pyc
   │     │  │  │     ├─ cp949prober.cpython-311.pyc
   │     │  │  │     ├─ enums.cpython-311.pyc
   │     │  │  │     ├─ escprober.cpython-311.pyc
   │     │  │  │     ├─ escsm.cpython-311.pyc
   │     │  │  │     ├─ eucjpprober.cpython-311.pyc
   │     │  │  │     ├─ euckrfreq.cpython-311.pyc
   │     │  │  │     ├─ euckrprober.cpython-311.pyc
   │     │  │  │     ├─ euctwfreq.cpython-311.pyc
   │     │  │  │     ├─ euctwprober.cpython-311.pyc
   │     │  │  │     ├─ gb2312freq.cpython-311.pyc
   │     │  │  │     ├─ gb2312prober.cpython-311.pyc
   │     │  │  │     ├─ hebrewprober.cpython-311.pyc
   │     │  │  │     ├─ jisfreq.cpython-311.pyc
   │     │  │  │     ├─ johabfreq.cpython-311.pyc
   │     │  │  │     ├─ johabprober.cpython-311.pyc
   │     │  │  │     ├─ jpcntx.cpython-311.pyc
   │     │  │  │     ├─ langbulgarianmodel.cpython-311.pyc
   │     │  │  │     ├─ langgreekmodel.cpython-311.pyc
   │     │  │  │     ├─ langhebrewmodel.cpython-311.pyc
   │     │  │  │     ├─ langhungarianmodel.cpython-311.pyc
   │     │  │  │     ├─ langrussianmodel.cpython-311.pyc
   │     │  │  │     ├─ langthaimodel.cpython-311.pyc
   │     │  │  │     ├─ langturkishmodel.cpython-311.pyc
   │     │  │  │     ├─ latin1prober.cpython-311.pyc
   │     │  │  │     ├─ macromanprober.cpython-311.pyc
   │     │  │  │     ├─ mbcharsetprober.cpython-311.pyc
   │     │  │  │     ├─ mbcsgroupprober.cpython-311.pyc
   │     │  │  │     ├─ mbcssm.cpython-311.pyc
   │     │  │  │     ├─ resultdict.cpython-311.pyc
   │     │  │  │     ├─ sbcharsetprober.cpython-311.pyc
   │     │  │  │     ├─ sbcsgroupprober.cpython-311.pyc
   │     │  │  │     ├─ sjisprober.cpython-311.pyc
   │     │  │  │     ├─ universaldetector.cpython-311.pyc
   │     │  │  │     ├─ utf1632prober.cpython-311.pyc
   │     │  │  │     ├─ utf8prober.cpython-311.pyc
   │     │  │  │     ├─ version.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ colorama
   │     │  │  │  ├─ ansi.py
   │     │  │  │  ├─ ansitowin32.py
   │     │  │  │  ├─ initialise.py
   │     │  │  │  ├─ tests
   │     │  │  │  │  ├─ ansitowin32_test.py
   │     │  │  │  │  ├─ ansi_test.py
   │     │  │  │  │  ├─ initialise_test.py
   │     │  │  │  │  ├─ isatty_test.py
   │     │  │  │  │  ├─ utils.py
   │     │  │  │  │  ├─ winterm_test.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ ansitowin32_test.cpython-311.pyc
   │     │  │  │  │     ├─ ansi_test.cpython-311.pyc
   │     │  │  │  │     ├─ initialise_test.cpython-311.pyc
   │     │  │  │  │     ├─ isatty_test.cpython-311.pyc
   │     │  │  │  │     ├─ utils.cpython-311.pyc
   │     │  │  │  │     ├─ winterm_test.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ win32.py
   │     │  │  │  ├─ winterm.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ ansi.cpython-311.pyc
   │     │  │  │     ├─ ansitowin32.cpython-311.pyc
   │     │  │  │     ├─ initialise.cpython-311.pyc
   │     │  │  │     ├─ win32.cpython-311.pyc
   │     │  │  │     ├─ winterm.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ distlib
   │     │  │  │  ├─ compat.py
   │     │  │  │  ├─ database.py
   │     │  │  │  ├─ index.py
   │     │  │  │  ├─ locators.py
   │     │  │  │  ├─ manifest.py
   │     │  │  │  ├─ markers.py
   │     │  │  │  ├─ metadata.py
   │     │  │  │  ├─ resources.py
   │     │  │  │  ├─ scripts.py
   │     │  │  │  ├─ t32.exe
   │     │  │  │  ├─ t64-arm.exe
   │     │  │  │  ├─ t64.exe
   │     │  │  │  ├─ util.py
   │     │  │  │  ├─ version.py
   │     │  │  │  ├─ w32.exe
   │     │  │  │  ├─ w64-arm.exe
   │     │  │  │  ├─ w64.exe
   │     │  │  │  ├─ wheel.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ compat.cpython-311.pyc
   │     │  │  │     ├─ database.cpython-311.pyc
   │     │  │  │     ├─ index.cpython-311.pyc
   │     │  │  │     ├─ locators.cpython-311.pyc
   │     │  │  │     ├─ manifest.cpython-311.pyc
   │     │  │  │     ├─ markers.cpython-311.pyc
   │     │  │  │     ├─ metadata.cpython-311.pyc
   │     │  │  │     ├─ resources.cpython-311.pyc
   │     │  │  │     ├─ scripts.cpython-311.pyc
   │     │  │  │     ├─ util.cpython-311.pyc
   │     │  │  │     ├─ version.cpython-311.pyc
   │     │  │  │     ├─ wheel.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ distro
   │     │  │  │  ├─ distro.py
   │     │  │  │  ├─ py.typed
   │     │  │  │  ├─ __init__.py
   │     │  │  │  ├─ __main__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ distro.cpython-311.pyc
   │     │  │  │     ├─ __init__.cpython-311.pyc
   │     │  │  │     └─ __main__.cpython-311.pyc
   │     │  │  ├─ idna
   │     │  │  │  ├─ codec.py
   │     │  │  │  ├─ compat.py
   │     │  │  │  ├─ core.py
   │     │  │  │  ├─ idnadata.py
   │     │  │  │  ├─ intranges.py
   │     │  │  │  ├─ package_data.py
   │     │  │  │  ├─ py.typed
   │     │  │  │  ├─ uts46data.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ codec.cpython-311.pyc
   │     │  │  │     ├─ compat.cpython-311.pyc
   │     │  │  │     ├─ core.cpython-311.pyc
   │     │  │  │     ├─ idnadata.cpython-311.pyc
   │     │  │  │     ├─ intranges.cpython-311.pyc
   │     │  │  │     ├─ package_data.cpython-311.pyc
   │     │  │  │     ├─ uts46data.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ msgpack
   │     │  │  │  ├─ exceptions.py
   │     │  │  │  ├─ ext.py
   │     │  │  │  ├─ fallback.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ exceptions.cpython-311.pyc
   │     │  │  │     ├─ ext.cpython-311.pyc
   │     │  │  │     ├─ fallback.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ packaging
   │     │  │  │  ├─ markers.py
   │     │  │  │  ├─ py.typed
   │     │  │  │  ├─ requirements.py
   │     │  │  │  ├─ specifiers.py
   │     │  │  │  ├─ tags.py
   │     │  │  │  ├─ utils.py
   │     │  │  │  ├─ version.py
   │     │  │  │  ├─ _manylinux.py
   │     │  │  │  ├─ _musllinux.py
   │     │  │  │  ├─ _structures.py
   │     │  │  │  ├─ __about__.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ markers.cpython-311.pyc
   │     │  │  │     ├─ requirements.cpython-311.pyc
   │     │  │  │     ├─ specifiers.cpython-311.pyc
   │     │  │  │     ├─ tags.cpython-311.pyc
   │     │  │  │     ├─ utils.cpython-311.pyc
   │     │  │  │     ├─ version.cpython-311.pyc
   │     │  │  │     ├─ _manylinux.cpython-311.pyc
   │     │  │  │     ├─ _musllinux.cpython-311.pyc
   │     │  │  │     ├─ _structures.cpython-311.pyc
   │     │  │  │     ├─ __about__.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ pkg_resources
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ platformdirs
   │     │  │  │  ├─ android.py
   │     │  │  │  ├─ api.py
   │     │  │  │  ├─ macos.py
   │     │  │  │  ├─ py.typed
   │     │  │  │  ├─ unix.py
   │     │  │  │  ├─ version.py
   │     │  │  │  ├─ windows.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  ├─ __main__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ android.cpython-311.pyc
   │     │  │  │     ├─ api.cpython-311.pyc
   │     │  │  │     ├─ macos.cpython-311.pyc
   │     │  │  │     ├─ unix.cpython-311.pyc
   │     │  │  │     ├─ version.cpython-311.pyc
   │     │  │  │     ├─ windows.cpython-311.pyc
   │     │  │  │     ├─ __init__.cpython-311.pyc
   │     │  │  │     └─ __main__.cpython-311.pyc
   │     │  │  ├─ pygments
   │     │  │  │  ├─ cmdline.py
   │     │  │  │  ├─ console.py
   │     │  │  │  ├─ filter.py
   │     │  │  │  ├─ filters
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ formatter.py
   │     │  │  │  ├─ formatters
   │     │  │  │  │  ├─ bbcode.py
   │     │  │  │  │  ├─ groff.py
   │     │  │  │  │  ├─ html.py
   │     │  │  │  │  ├─ img.py
   │     │  │  │  │  ├─ irc.py
   │     │  │  │  │  ├─ latex.py
   │     │  │  │  │  ├─ other.py
   │     │  │  │  │  ├─ pangomarkup.py
   │     │  │  │  │  ├─ rtf.py
   │     │  │  │  │  ├─ svg.py
   │     │  │  │  │  ├─ terminal.py
   │     │  │  │  │  ├─ terminal256.py
   │     │  │  │  │  ├─ _mapping.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ bbcode.cpython-311.pyc
   │     │  │  │  │     ├─ groff.cpython-311.pyc
   │     │  │  │  │     ├─ html.cpython-311.pyc
   │     │  │  │  │     ├─ img.cpython-311.pyc
   │     │  │  │  │     ├─ irc.cpython-311.pyc
   │     │  │  │  │     ├─ latex.cpython-311.pyc
   │     │  │  │  │     ├─ other.cpython-311.pyc
   │     │  │  │  │     ├─ pangomarkup.cpython-311.pyc
   │     │  │  │  │     ├─ rtf.cpython-311.pyc
   │     │  │  │  │     ├─ svg.cpython-311.pyc
   │     │  │  │  │     ├─ terminal.cpython-311.pyc
   │     │  │  │  │     ├─ terminal256.cpython-311.pyc
   │     │  │  │  │     ├─ _mapping.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ lexer.py
   │     │  │  │  ├─ lexers
   │     │  │  │  │  ├─ python.py
   │     │  │  │  │  ├─ _mapping.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ python.cpython-311.pyc
   │     │  │  │  │     ├─ _mapping.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ modeline.py
   │     │  │  │  ├─ plugin.py
   │     │  │  │  ├─ regexopt.py
   │     │  │  │  ├─ scanner.py
   │     │  │  │  ├─ sphinxext.py
   │     │  │  │  ├─ style.py
   │     │  │  │  ├─ styles
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ token.py
   │     │  │  │  ├─ unistring.py
   │     │  │  │  ├─ util.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  ├─ __main__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ cmdline.cpython-311.pyc
   │     │  │  │     ├─ console.cpython-311.pyc
   │     │  │  │     ├─ filter.cpython-311.pyc
   │     │  │  │     ├─ formatter.cpython-311.pyc
   │     │  │  │     ├─ lexer.cpython-311.pyc
   │     │  │  │     ├─ modeline.cpython-311.pyc
   │     │  │  │     ├─ plugin.cpython-311.pyc
   │     │  │  │     ├─ regexopt.cpython-311.pyc
   │     │  │  │     ├─ scanner.cpython-311.pyc
   │     │  │  │     ├─ sphinxext.cpython-311.pyc
   │     │  │  │     ├─ style.cpython-311.pyc
   │     │  │  │     ├─ token.cpython-311.pyc
   │     │  │  │     ├─ unistring.cpython-311.pyc
   │     │  │  │     ├─ util.cpython-311.pyc
   │     │  │  │     ├─ __init__.cpython-311.pyc
   │     │  │  │     └─ __main__.cpython-311.pyc
   │     │  │  ├─ pyparsing
   │     │  │  │  ├─ actions.py
   │     │  │  │  ├─ common.py
   │     │  │  │  ├─ core.py
   │     │  │  │  ├─ diagram
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ exceptions.py
   │     │  │  │  ├─ helpers.py
   │     │  │  │  ├─ py.typed
   │     │  │  │  ├─ results.py
   │     │  │  │  ├─ testing.py
   │     │  │  │  ├─ unicode.py
   │     │  │  │  ├─ util.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ actions.cpython-311.pyc
   │     │  │  │     ├─ common.cpython-311.pyc
   │     │  │  │     ├─ core.cpython-311.pyc
   │     │  │  │     ├─ exceptions.cpython-311.pyc
   │     │  │  │     ├─ helpers.cpython-311.pyc
   │     │  │  │     ├─ results.cpython-311.pyc
   │     │  │  │     ├─ testing.cpython-311.pyc
   │     │  │  │     ├─ unicode.cpython-311.pyc
   │     │  │  │     ├─ util.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ pyproject_hooks
   │     │  │  │  ├─ _compat.py
   │     │  │  │  ├─ _impl.py
   │     │  │  │  ├─ _in_process
   │     │  │  │  │  ├─ _in_process.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ _in_process.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ _compat.cpython-311.pyc
   │     │  │  │     ├─ _impl.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ requests
   │     │  │  │  ├─ adapters.py
   │     │  │  │  ├─ api.py
   │     │  │  │  ├─ auth.py
   │     │  │  │  ├─ certs.py
   │     │  │  │  ├─ compat.py
   │     │  │  │  ├─ cookies.py
   │     │  │  │  ├─ exceptions.py
   │     │  │  │  ├─ help.py
   │     │  │  │  ├─ hooks.py
   │     │  │  │  ├─ models.py
   │     │  │  │  ├─ packages.py
   │     │  │  │  ├─ sessions.py
   │     │  │  │  ├─ status_codes.py
   │     │  │  │  ├─ structures.py
   │     │  │  │  ├─ utils.py
   │     │  │  │  ├─ _internal_utils.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  ├─ __pycache__
   │     │  │  │  │  ├─ adapters.cpython-311.pyc
   │     │  │  │  │  ├─ api.cpython-311.pyc
   │     │  │  │  │  ├─ auth.cpython-311.pyc
   │     │  │  │  │  ├─ certs.cpython-311.pyc
   │     │  │  │  │  ├─ compat.cpython-311.pyc
   │     │  │  │  │  ├─ cookies.cpython-311.pyc
   │     │  │  │  │  ├─ exceptions.cpython-311.pyc
   │     │  │  │  │  ├─ help.cpython-311.pyc
   │     │  │  │  │  ├─ hooks.cpython-311.pyc
   │     │  │  │  │  ├─ models.cpython-311.pyc
   │     │  │  │  │  ├─ packages.cpython-311.pyc
   │     │  │  │  │  ├─ sessions.cpython-311.pyc
   │     │  │  │  │  ├─ status_codes.cpython-311.pyc
   │     │  │  │  │  ├─ structures.cpython-311.pyc
   │     │  │  │  │  ├─ utils.cpython-311.pyc
   │     │  │  │  │  ├─ _internal_utils.cpython-311.pyc
   │     │  │  │  │  ├─ __init__.cpython-311.pyc
   │     │  │  │  │  └─ __version__.cpython-311.pyc
   │     │  │  │  └─ __version__.py
   │     │  │  ├─ resolvelib
   │     │  │  │  ├─ compat
   │     │  │  │  │  ├─ collections_abc.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ collections_abc.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ providers.py
   │     │  │  │  ├─ py.typed
   │     │  │  │  ├─ reporters.py
   │     │  │  │  ├─ resolvers.py
   │     │  │  │  ├─ structs.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ providers.cpython-311.pyc
   │     │  │  │     ├─ reporters.cpython-311.pyc
   │     │  │  │     ├─ resolvers.cpython-311.pyc
   │     │  │  │     ├─ structs.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ rich
   │     │  │  │  ├─ abc.py
   │     │  │  │  ├─ align.py
   │     │  │  │  ├─ ansi.py
   │     │  │  │  ├─ bar.py
   │     │  │  │  ├─ box.py
   │     │  │  │  ├─ cells.py
   │     │  │  │  ├─ color.py
   │     │  │  │  ├─ color_triplet.py
   │     │  │  │  ├─ columns.py
   │     │  │  │  ├─ console.py
   │     │  │  │  ├─ constrain.py
   │     │  │  │  ├─ containers.py
   │     │  │  │  ├─ control.py
   │     │  │  │  ├─ default_styles.py
   │     │  │  │  ├─ diagnose.py
   │     │  │  │  ├─ emoji.py
   │     │  │  │  ├─ errors.py
   │     │  │  │  ├─ filesize.py
   │     │  │  │  ├─ file_proxy.py
   │     │  │  │  ├─ highlighter.py
   │     │  │  │  ├─ json.py
   │     │  │  │  ├─ jupyter.py
   │     │  │  │  ├─ layout.py
   │     │  │  │  ├─ live.py
   │     │  │  │  ├─ live_render.py
   │     │  │  │  ├─ logging.py
   │     │  │  │  ├─ markup.py
   │     │  │  │  ├─ measure.py
   │     │  │  │  ├─ padding.py
   │     │  │  │  ├─ pager.py
   │     │  │  │  ├─ palette.py
   │     │  │  │  ├─ panel.py
   │     │  │  │  ├─ pretty.py
   │     │  │  │  ├─ progress.py
   │     │  │  │  ├─ progress_bar.py
   │     │  │  │  ├─ prompt.py
   │     │  │  │  ├─ protocol.py
   │     │  │  │  ├─ py.typed
   │     │  │  │  ├─ region.py
   │     │  │  │  ├─ repr.py
   │     │  │  │  ├─ rule.py
   │     │  │  │  ├─ scope.py
   │     │  │  │  ├─ screen.py
   │     │  │  │  ├─ segment.py
   │     │  │  │  ├─ spinner.py
   │     │  │  │  ├─ status.py
   │     │  │  │  ├─ style.py
   │     │  │  │  ├─ styled.py
   │     │  │  │  ├─ syntax.py
   │     │  │  │  ├─ table.py
   │     │  │  │  ├─ terminal_theme.py
   │     │  │  │  ├─ text.py
   │     │  │  │  ├─ theme.py
   │     │  │  │  ├─ themes.py
   │     │  │  │  ├─ traceback.py
   │     │  │  │  ├─ tree.py
   │     │  │  │  ├─ _cell_widths.py
   │     │  │  │  ├─ _emoji_codes.py
   │     │  │  │  ├─ _emoji_replace.py
   │     │  │  │  ├─ _export_format.py
   │     │  │  │  ├─ _extension.py
   │     │  │  │  ├─ _fileno.py
   │     │  │  │  ├─ _inspect.py
   │     │  │  │  ├─ _log_render.py
   │     │  │  │  ├─ _loop.py
   │     │  │  │  ├─ _null_file.py
   │     │  │  │  ├─ _palettes.py
   │     │  │  │  ├─ _pick.py
   │     │  │  │  ├─ _ratio.py
   │     │  │  │  ├─ _spinners.py
   │     │  │  │  ├─ _stack.py
   │     │  │  │  ├─ _timer.py
   │     │  │  │  ├─ _win32_console.py
   │     │  │  │  ├─ _windows.py
   │     │  │  │  ├─ _windows_renderer.py
   │     │  │  │  ├─ _wrap.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  ├─ __main__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ abc.cpython-311.pyc
   │     │  │  │     ├─ align.cpython-311.pyc
   │     │  │  │     ├─ ansi.cpython-311.pyc
   │     │  │  │     ├─ bar.cpython-311.pyc
   │     │  │  │     ├─ box.cpython-311.pyc
   │     │  │  │     ├─ cells.cpython-311.pyc
   │     │  │  │     ├─ color.cpython-311.pyc
   │     │  │  │     ├─ color_triplet.cpython-311.pyc
   │     │  │  │     ├─ columns.cpython-311.pyc
   │     │  │  │     ├─ console.cpython-311.pyc
   │     │  │  │     ├─ constrain.cpython-311.pyc
   │     │  │  │     ├─ containers.cpython-311.pyc
   │     │  │  │     ├─ control.cpython-311.pyc
   │     │  │  │     ├─ default_styles.cpython-311.pyc
   │     │  │  │     ├─ diagnose.cpython-311.pyc
   │     │  │  │     ├─ emoji.cpython-311.pyc
   │     │  │  │     ├─ errors.cpython-311.pyc
   │     │  │  │     ├─ filesize.cpython-311.pyc
   │     │  │  │     ├─ file_proxy.cpython-311.pyc
   │     │  │  │     ├─ highlighter.cpython-311.pyc
   │     │  │  │     ├─ json.cpython-311.pyc
   │     │  │  │     ├─ jupyter.cpython-311.pyc
   │     │  │  │     ├─ layout.cpython-311.pyc
   │     │  │  │     ├─ live.cpython-311.pyc
   │     │  │  │     ├─ live_render.cpython-311.pyc
   │     │  │  │     ├─ logging.cpython-311.pyc
   │     │  │  │     ├─ markup.cpython-311.pyc
   │     │  │  │     ├─ measure.cpython-311.pyc
   │     │  │  │     ├─ padding.cpython-311.pyc
   │     │  │  │     ├─ pager.cpython-311.pyc
   │     │  │  │     ├─ palette.cpython-311.pyc
   │     │  │  │     ├─ panel.cpython-311.pyc
   │     │  │  │     ├─ pretty.cpython-311.pyc
   │     │  │  │     ├─ progress.cpython-311.pyc
   │     │  │  │     ├─ progress_bar.cpython-311.pyc
   │     │  │  │     ├─ prompt.cpython-311.pyc
   │     │  │  │     ├─ protocol.cpython-311.pyc
   │     │  │  │     ├─ region.cpython-311.pyc
   │     │  │  │     ├─ repr.cpython-311.pyc
   │     │  │  │     ├─ rule.cpython-311.pyc
   │     │  │  │     ├─ scope.cpython-311.pyc
   │     │  │  │     ├─ screen.cpython-311.pyc
   │     │  │  │     ├─ segment.cpython-311.pyc
   │     │  │  │     ├─ spinner.cpython-311.pyc
   │     │  │  │     ├─ status.cpython-311.pyc
   │     │  │  │     ├─ style.cpython-311.pyc
   │     │  │  │     ├─ styled.cpython-311.pyc
   │     │  │  │     ├─ syntax.cpython-311.pyc
   │     │  │  │     ├─ table.cpython-311.pyc
   │     │  │  │     ├─ terminal_theme.cpython-311.pyc
   │     │  │  │     ├─ text.cpython-311.pyc
   │     │  │  │     ├─ theme.cpython-311.pyc
   │     │  │  │     ├─ themes.cpython-311.pyc
   │     │  │  │     ├─ traceback.cpython-311.pyc
   │     │  │  │     ├─ tree.cpython-311.pyc
   │     │  │  │     ├─ _cell_widths.cpython-311.pyc
   │     │  │  │     ├─ _emoji_codes.cpython-311.pyc
   │     │  │  │     ├─ _emoji_replace.cpython-311.pyc
   │     │  │  │     ├─ _export_format.cpython-311.pyc
   │     │  │  │     ├─ _extension.cpython-311.pyc
   │     │  │  │     ├─ _fileno.cpython-311.pyc
   │     │  │  │     ├─ _inspect.cpython-311.pyc
   │     │  │  │     ├─ _log_render.cpython-311.pyc
   │     │  │  │     ├─ _loop.cpython-311.pyc
   │     │  │  │     ├─ _null_file.cpython-311.pyc
   │     │  │  │     ├─ _palettes.cpython-311.pyc
   │     │  │  │     ├─ _pick.cpython-311.pyc
   │     │  │  │     ├─ _ratio.cpython-311.pyc
   │     │  │  │     ├─ _spinners.cpython-311.pyc
   │     │  │  │     ├─ _stack.cpython-311.pyc
   │     │  │  │     ├─ _timer.cpython-311.pyc
   │     │  │  │     ├─ _win32_console.cpython-311.pyc
   │     │  │  │     ├─ _windows.cpython-311.pyc
   │     │  │  │     ├─ _windows_renderer.cpython-311.pyc
   │     │  │  │     ├─ _wrap.cpython-311.pyc
   │     │  │  │     ├─ __init__.cpython-311.pyc
   │     │  │  │     └─ __main__.cpython-311.pyc
   │     │  │  ├─ six.py
   │     │  │  ├─ tenacity
   │     │  │  │  ├─ after.py
   │     │  │  │  ├─ before.py
   │     │  │  │  ├─ before_sleep.py
   │     │  │  │  ├─ nap.py
   │     │  │  │  ├─ py.typed
   │     │  │  │  ├─ retry.py
   │     │  │  │  ├─ stop.py
   │     │  │  │  ├─ tornadoweb.py
   │     │  │  │  ├─ wait.py
   │     │  │  │  ├─ _asyncio.py
   │     │  │  │  ├─ _utils.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ after.cpython-311.pyc
   │     │  │  │     ├─ before.cpython-311.pyc
   │     │  │  │     ├─ before_sleep.cpython-311.pyc
   │     │  │  │     ├─ nap.cpython-311.pyc
   │     │  │  │     ├─ retry.cpython-311.pyc
   │     │  │  │     ├─ stop.cpython-311.pyc
   │     │  │  │     ├─ tornadoweb.cpython-311.pyc
   │     │  │  │     ├─ wait.cpython-311.pyc
   │     │  │  │     ├─ _asyncio.cpython-311.pyc
   │     │  │  │     ├─ _utils.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ tomli
   │     │  │  │  ├─ py.typed
   │     │  │  │  ├─ _parser.py
   │     │  │  │  ├─ _re.py
   │     │  │  │  ├─ _types.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ _parser.cpython-311.pyc
   │     │  │  │     ├─ _re.cpython-311.pyc
   │     │  │  │     ├─ _types.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ truststore
   │     │  │  │  ├─ py.typed
   │     │  │  │  ├─ _api.py
   │     │  │  │  ├─ _macos.py
   │     │  │  │  ├─ _openssl.py
   │     │  │  │  ├─ _ssl_constants.py
   │     │  │  │  ├─ _windows.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ _api.cpython-311.pyc
   │     │  │  │     ├─ _macos.cpython-311.pyc
   │     │  │  │     ├─ _openssl.cpython-311.pyc
   │     │  │  │     ├─ _ssl_constants.cpython-311.pyc
   │     │  │  │     ├─ _windows.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ typing_extensions.py
   │     │  │  ├─ urllib3
   │     │  │  │  ├─ connection.py
   │     │  │  │  ├─ connectionpool.py
   │     │  │  │  ├─ contrib
   │     │  │  │  │  ├─ appengine.py
   │     │  │  │  │  ├─ ntlmpool.py
   │     │  │  │  │  ├─ pyopenssl.py
   │     │  │  │  │  ├─ securetransport.py
   │     │  │  │  │  ├─ socks.py
   │     │  │  │  │  ├─ _appengine_environ.py
   │     │  │  │  │  ├─ _securetransport
   │     │  │  │  │  │  ├─ bindings.py
   │     │  │  │  │  │  ├─ low_level.py
   │     │  │  │  │  │  ├─ __init__.py
   │     │  │  │  │  │  └─ __pycache__
   │     │  │  │  │  │     ├─ bindings.cpython-311.pyc
   │     │  │  │  │  │     ├─ low_level.cpython-311.pyc
   │     │  │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ appengine.cpython-311.pyc
   │     │  │  │  │     ├─ ntlmpool.cpython-311.pyc
   │     │  │  │  │     ├─ pyopenssl.cpython-311.pyc
   │     │  │  │  │     ├─ securetransport.cpython-311.pyc
   │     │  │  │  │     ├─ socks.cpython-311.pyc
   │     │  │  │  │     ├─ _appengine_environ.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ exceptions.py
   │     │  │  │  ├─ fields.py
   │     │  │  │  ├─ filepost.py
   │     │  │  │  ├─ packages
   │     │  │  │  │  ├─ backports
   │     │  │  │  │  │  ├─ makefile.py
   │     │  │  │  │  │  ├─ weakref_finalize.py
   │     │  │  │  │  │  ├─ __init__.py
   │     │  │  │  │  │  └─ __pycache__
   │     │  │  │  │  │     ├─ makefile.cpython-311.pyc
   │     │  │  │  │  │     ├─ weakref_finalize.cpython-311.pyc
   │     │  │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  │  ├─ six.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ six.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ poolmanager.py
   │     │  │  │  ├─ request.py
   │     │  │  │  ├─ response.py
   │     │  │  │  ├─ util
   │     │  │  │  │  ├─ connection.py
   │     │  │  │  │  ├─ proxy.py
   │     │  │  │  │  ├─ queue.py
   │     │  │  │  │  ├─ request.py
   │     │  │  │  │  ├─ response.py
   │     │  │  │  │  ├─ retry.py
   │     │  │  │  │  ├─ ssltransport.py
   │     │  │  │  │  ├─ ssl_.py
   │     │  │  │  │  ├─ ssl_match_hostname.py
   │     │  │  │  │  ├─ timeout.py
   │     │  │  │  │  ├─ url.py
   │     │  │  │  │  ├─ wait.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ connection.cpython-311.pyc
   │     │  │  │  │     ├─ proxy.cpython-311.pyc
   │     │  │  │  │     ├─ queue.cpython-311.pyc
   │     │  │  │  │     ├─ request.cpython-311.pyc
   │     │  │  │  │     ├─ response.cpython-311.pyc
   │     │  │  │  │     ├─ retry.cpython-311.pyc
   │     │  │  │  │     ├─ ssltransport.cpython-311.pyc
   │     │  │  │  │     ├─ ssl_.cpython-311.pyc
   │     │  │  │  │     ├─ ssl_match_hostname.cpython-311.pyc
   │     │  │  │  │     ├─ timeout.cpython-311.pyc
   │     │  │  │  │     ├─ url.cpython-311.pyc
   │     │  │  │  │     ├─ wait.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ _collections.py
   │     │  │  │  ├─ _version.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ connection.cpython-311.pyc
   │     │  │  │     ├─ connectionpool.cpython-311.pyc
   │     │  │  │     ├─ exceptions.cpython-311.pyc
   │     │  │  │     ├─ fields.cpython-311.pyc
   │     │  │  │     ├─ filepost.cpython-311.pyc
   │     │  │  │     ├─ poolmanager.cpython-311.pyc
   │     │  │  │     ├─ request.cpython-311.pyc
   │     │  │  │     ├─ response.cpython-311.pyc
   │     │  │  │     ├─ _collections.cpython-311.pyc
   │     │  │  │     ├─ _version.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ vendor.txt
   │     │  │  ├─ webencodings
   │     │  │  │  ├─ labels.py
   │     │  │  │  ├─ mklabels.py
   │     │  │  │  ├─ tests.py
   │     │  │  │  ├─ x_user_defined.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ labels.cpython-311.pyc
   │     │  │  │     ├─ mklabels.cpython-311.pyc
   │     │  │  │     ├─ tests.cpython-311.pyc
   │     │  │  │     ├─ x_user_defined.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ six.cpython-311.pyc
   │     │  │     ├─ typing_extensions.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ __init__.py
   │     │  ├─ __main__.py
   │     │  ├─ __pip-runner__.py
   │     │  └─ __pycache__
   │     │     ├─ __init__.cpython-311.pyc
   │     │     ├─ __main__.cpython-311.pyc
   │     │     └─ __pip-runner__.cpython-311.pyc
   │     ├─ pip-24.0.dist-info
   │     │  ├─ AUTHORS.txt
   │     │  ├─ entry_points.txt
   │     │  ├─ INSTALLER
   │     │  ├─ LICENSE.txt
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  ├─ REQUESTED
   │     │  ├─ top_level.txt
   │     │  └─ WHEEL
   │     ├─ pkg_resources
   │     │  ├─ extern
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ _vendor
   │     │  │  ├─ appdirs.py
   │     │  │  ├─ importlib_resources
   │     │  │  │  ├─ abc.py
   │     │  │  │  ├─ readers.py
   │     │  │  │  ├─ simple.py
   │     │  │  │  ├─ _adapters.py
   │     │  │  │  ├─ _common.py
   │     │  │  │  ├─ _compat.py
   │     │  │  │  ├─ _itertools.py
   │     │  │  │  ├─ _legacy.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ abc.cpython-311.pyc
   │     │  │  │     ├─ readers.cpython-311.pyc
   │     │  │  │     ├─ simple.cpython-311.pyc
   │     │  │  │     ├─ _adapters.cpython-311.pyc
   │     │  │  │     ├─ _common.cpython-311.pyc
   │     │  │  │     ├─ _compat.cpython-311.pyc
   │     │  │  │     ├─ _itertools.cpython-311.pyc
   │     │  │  │     ├─ _legacy.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ jaraco
   │     │  │  │  ├─ context.py
   │     │  │  │  ├─ functools.py
   │     │  │  │  ├─ text
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ context.cpython-311.pyc
   │     │  │  │     ├─ functools.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ more_itertools
   │     │  │  │  ├─ more.py
   │     │  │  │  ├─ recipes.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ more.cpython-311.pyc
   │     │  │  │     ├─ recipes.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ packaging
   │     │  │  │  ├─ markers.py
   │     │  │  │  ├─ requirements.py
   │     │  │  │  ├─ specifiers.py
   │     │  │  │  ├─ tags.py
   │     │  │  │  ├─ utils.py
   │     │  │  │  ├─ version.py
   │     │  │  │  ├─ _manylinux.py
   │     │  │  │  ├─ _musllinux.py
   │     │  │  │  ├─ _structures.py
   │     │  │  │  ├─ __about__.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ markers.cpython-311.pyc
   │     │  │  │     ├─ requirements.cpython-311.pyc
   │     │  │  │     ├─ specifiers.cpython-311.pyc
   │     │  │  │     ├─ tags.cpython-311.pyc
   │     │  │  │     ├─ utils.cpython-311.pyc
   │     │  │  │     ├─ version.cpython-311.pyc
   │     │  │  │     ├─ _manylinux.cpython-311.pyc
   │     │  │  │     ├─ _musllinux.cpython-311.pyc
   │     │  │  │     ├─ _structures.cpython-311.pyc
   │     │  │  │     ├─ __about__.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ pyparsing
   │     │  │  │  ├─ actions.py
   │     │  │  │  ├─ common.py
   │     │  │  │  ├─ core.py
   │     │  │  │  ├─ diagram
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ exceptions.py
   │     │  │  │  ├─ helpers.py
   │     │  │  │  ├─ results.py
   │     │  │  │  ├─ testing.py
   │     │  │  │  ├─ unicode.py
   │     │  │  │  ├─ util.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ actions.cpython-311.pyc
   │     │  │  │     ├─ common.cpython-311.pyc
   │     │  │  │     ├─ core.cpython-311.pyc
   │     │  │  │     ├─ exceptions.cpython-311.pyc
   │     │  │  │     ├─ helpers.cpython-311.pyc
   │     │  │  │     ├─ results.cpython-311.pyc
   │     │  │  │     ├─ testing.cpython-311.pyc
   │     │  │  │     ├─ unicode.cpython-311.pyc
   │     │  │  │     ├─ util.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ zipp.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ appdirs.cpython-311.pyc
   │     │  │     ├─ zipp.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ __init__.py
   │     │  └─ __pycache__
   │     │     └─ __init__.cpython-311.pyc
   │     ├─ protobuf-6.33.6.dist-info
   │     │  ├─ INSTALLER
   │     │  ├─ LICENSE
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  └─ WHEEL
   │     ├─ pyarrow
   │     │  ├─ acero.py
   │     │  ├─ array.pxi
   │     │  ├─ arrow.dll
   │     │  ├─ arrow.lib
   │     │  ├─ arrow_acero.dll
   │     │  ├─ arrow_acero.lib
   │     │  ├─ arrow_compute.dll
   │     │  ├─ arrow_compute.lib
   │     │  ├─ arrow_dataset.dll
   │     │  ├─ arrow_dataset.lib
   │     │  ├─ arrow_flight.dll
   │     │  ├─ arrow_flight.lib
   │     │  ├─ arrow_python.dll
   │     │  ├─ arrow_python.lib
   │     │  ├─ arrow_python_flight.dll
   │     │  ├─ arrow_python_flight.lib
   │     │  ├─ arrow_python_parquet_encryption.dll
   │     │  ├─ arrow_python_parquet_encryption.lib
   │     │  ├─ arrow_substrait.dll
   │     │  ├─ arrow_substrait.lib
   │     │  ├─ benchmark.pxi
   │     │  ├─ benchmark.py
   │     │  ├─ builder.pxi
   │     │  ├─ cffi.py
   │     │  ├─ compat.pxi
   │     │  ├─ compute.py
   │     │  ├─ config.pxi
   │     │  ├─ conftest.py
   │     │  ├─ csv.py
   │     │  ├─ cuda.py
   │     │  ├─ dataset.py
   │     │  ├─ device.pxi
   │     │  ├─ error.pxi
   │     │  ├─ feather.py
   │     │  ├─ flight.py
   │     │  ├─ fs.py
   │     │  ├─ gandiva.pyx
   │     │  ├─ include
   │     │  │  ├─ arrow
   │     │  │  │  ├─ acero
   │     │  │  │  │  ├─ accumulation_queue.h
   │     │  │  │  │  ├─ aggregate_node.h
   │     │  │  │  │  ├─ api.h
   │     │  │  │  │  ├─ asof_join_node.h
   │     │  │  │  │  ├─ backpressure_handler.h
   │     │  │  │  │  ├─ benchmark_util.h
   │     │  │  │  │  ├─ bloom_filter.h
   │     │  │  │  │  ├─ exec_plan.h
   │     │  │  │  │  ├─ hash_join.h
   │     │  │  │  │  ├─ hash_join_dict.h
   │     │  │  │  │  ├─ hash_join_node.h
   │     │  │  │  │  ├─ map_node.h
   │     │  │  │  │  ├─ options.h
   │     │  │  │  │  ├─ order_by_impl.h
   │     │  │  │  │  ├─ partition_util.h
   │     │  │  │  │  ├─ query_context.h
   │     │  │  │  │  ├─ schema_util.h
   │     │  │  │  │  ├─ task_util.h
   │     │  │  │  │  ├─ test_nodes.h
   │     │  │  │  │  ├─ time_series_util.h
   │     │  │  │  │  ├─ tpch_node.h
   │     │  │  │  │  ├─ type_fwd.h
   │     │  │  │  │  ├─ util.h
   │     │  │  │  │  └─ visibility.h
   │     │  │  │  ├─ adapters
   │     │  │  │  │  ├─ orc
   │     │  │  │  │  │  ├─ adapter.h
   │     │  │  │  │  │  └─ options.h
   │     │  │  │  │  └─ tensorflow
   │     │  │  │  │     └─ convert.h
   │     │  │  │  ├─ api.h
   │     │  │  │  ├─ array
   │     │  │  │  │  ├─ array_base.h
   │     │  │  │  │  ├─ array_binary.h
   │     │  │  │  │  ├─ array_decimal.h
   │     │  │  │  │  ├─ array_dict.h
   │     │  │  │  │  ├─ array_nested.h
   │     │  │  │  │  ├─ array_primitive.h
   │     │  │  │  │  ├─ array_run_end.h
   │     │  │  │  │  ├─ builder_adaptive.h
   │     │  │  │  │  ├─ builder_base.h
   │     │  │  │  │  ├─ builder_binary.h
   │     │  │  │  │  ├─ builder_decimal.h
   │     │  │  │  │  ├─ builder_dict.h
   │     │  │  │  │  ├─ builder_nested.h
   │     │  │  │  │  ├─ builder_primitive.h
   │     │  │  │  │  ├─ builder_run_end.h
   │     │  │  │  │  ├─ builder_time.h
   │     │  │  │  │  ├─ builder_union.h
   │     │  │  │  │  ├─ concatenate.h
   │     │  │  │  │  ├─ data.h
   │     │  │  │  │  ├─ diff.h
   │     │  │  │  │  ├─ statistics.h
   │     │  │  │  │  ├─ util.h
   │     │  │  │  │  └─ validate.h
   │     │  │  │  ├─ array.h
   │     │  │  │  ├─ buffer.h
   │     │  │  │  ├─ buffer_builder.h
   │     │  │  │  ├─ builder.h
   │     │  │  │  ├─ c
   │     │  │  │  │  ├─ abi.h
   │     │  │  │  │  ├─ bridge.h
   │     │  │  │  │  ├─ dlpack.h
   │     │  │  │  │  ├─ dlpack_abi.h
   │     │  │  │  │  └─ helpers.h
   │     │  │  │  ├─ chunked_array.h
   │     │  │  │  ├─ chunk_resolver.h
   │     │  │  │  ├─ compare.h
   │     │  │  │  ├─ compute
   │     │  │  │  │  ├─ api.h
   │     │  │  │  │  ├─ api_aggregate.h
   │     │  │  │  │  ├─ api_scalar.h
   │     │  │  │  │  ├─ api_vector.h
   │     │  │  │  │  ├─ cast.h
   │     │  │  │  │  ├─ exec.h
   │     │  │  │  │  ├─ expression.h
   │     │  │  │  │  ├─ function.h
   │     │  │  │  │  ├─ function_options.h
   │     │  │  │  │  ├─ initialize.h
   │     │  │  │  │  ├─ kernel.h
   │     │  │  │  │  ├─ ordering.h
   │     │  │  │  │  ├─ registry.h
   │     │  │  │  │  ├─ row
   │     │  │  │  │  │  └─ grouper.h
   │     │  │  │  │  ├─ type_fwd.h
   │     │  │  │  │  ├─ util.h
   │     │  │  │  │  └─ visibility.h
   │     │  │  │  ├─ config.h
   │     │  │  │  ├─ csv
   │     │  │  │  │  ├─ api.h
   │     │  │  │  │  ├─ chunker.h
   │     │  │  │  │  ├─ column_builder.h
   │     │  │  │  │  ├─ column_decoder.h
   │     │  │  │  │  ├─ converter.h
   │     │  │  │  │  ├─ invalid_row.h
   │     │  │  │  │  ├─ options.h
   │     │  │  │  │  ├─ parser.h
   │     │  │  │  │  ├─ reader.h
   │     │  │  │  │  ├─ test_common.h
   │     │  │  │  │  ├─ type_fwd.h
   │     │  │  │  │  └─ writer.h
   │     │  │  │  ├─ dataset
   │     │  │  │  │  ├─ api.h
   │     │  │  │  │  ├─ dataset.h
   │     │  │  │  │  ├─ dataset_writer.h
   │     │  │  │  │  ├─ discovery.h
   │     │  │  │  │  ├─ file_base.h
   │     │  │  │  │  ├─ file_csv.h
   │     │  │  │  │  ├─ file_ipc.h
   │     │  │  │  │  ├─ file_json.h
   │     │  │  │  │  ├─ file_orc.h
   │     │  │  │  │  ├─ file_parquet.h
   │     │  │  │  │  ├─ parquet_encryption_config.h
   │     │  │  │  │  ├─ partition.h
   │     │  │  │  │  ├─ plan.h
   │     │  │  │  │  ├─ projector.h
   │     │  │  │  │  ├─ scanner.h
   │     │  │  │  │  ├─ type_fwd.h
   │     │  │  │  │  └─ visibility.h
   │     │  │  │  ├─ datum.h
   │     │  │  │  ├─ device.h
   │     │  │  │  ├─ device_allocation_type_set.h
   │     │  │  │  ├─ engine
   │     │  │  │  │  ├─ api.h
   │     │  │  │  │  └─ substrait
   │     │  │  │  │     ├─ api.h
   │     │  │  │  │     ├─ extension_set.h
   │     │  │  │  │     ├─ extension_types.h
   │     │  │  │  │     ├─ options.h
   │     │  │  │  │     ├─ relation.h
   │     │  │  │  │     ├─ serde.h
   │     │  │  │  │     ├─ test_plan_builder.h
   │     │  │  │  │     ├─ test_util.h
   │     │  │  │  │     ├─ type_fwd.h
   │     │  │  │  │     ├─ util.h
   │     │  │  │  │     └─ visibility.h
   │     │  │  │  ├─ extension
   │     │  │  │  │  ├─ bool8.h
   │     │  │  │  │  ├─ fixed_shape_tensor.h
   │     │  │  │  │  ├─ json.h
   │     │  │  │  │  ├─ opaque.h
   │     │  │  │  │  └─ uuid.h
   │     │  │  │  ├─ extension_type.h
   │     │  │  │  ├─ filesystem
   │     │  │  │  │  ├─ api.h
   │     │  │  │  │  ├─ azurefs.h
   │     │  │  │  │  ├─ filesystem.h
   │     │  │  │  │  ├─ filesystem_library.h
   │     │  │  │  │  ├─ gcsfs.h
   │     │  │  │  │  ├─ hdfs.h
   │     │  │  │  │  ├─ localfs.h
   │     │  │  │  │  ├─ mockfs.h
   │     │  │  │  │  ├─ path_util.h
   │     │  │  │  │  ├─ s3fs.h
   │     │  │  │  │  ├─ s3_test_util.h
   │     │  │  │  │  ├─ test_util.h
   │     │  │  │  │  └─ type_fwd.h
   │     │  │  │  ├─ flight
   │     │  │  │  │  ├─ api.h
   │     │  │  │  │  ├─ client.h
   │     │  │  │  │  ├─ client_auth.h
   │     │  │  │  │  ├─ client_cookie_middleware.h
   │     │  │  │  │  ├─ client_middleware.h
   │     │  │  │  │  ├─ client_tracing_middleware.h
   │     │  │  │  │  ├─ middleware.h
   │     │  │  │  │  ├─ otel_logging.h
   │     │  │  │  │  ├─ platform.h
   │     │  │  │  │  ├─ server.h
   │     │  │  │  │  ├─ server_auth.h
   │     │  │  │  │  ├─ server_middleware.h
   │     │  │  │  │  ├─ server_tracing_middleware.h
   │     │  │  │  │  ├─ test_auth_handlers.h
   │     │  │  │  │  ├─ test_definitions.h
   │     │  │  │  │  ├─ test_flight_server.h
   │     │  │  │  │  ├─ test_util.h
   │     │  │  │  │  ├─ transport.h
   │     │  │  │  │  ├─ transport_server.h
   │     │  │  │  │  ├─ types.h
   │     │  │  │  │  ├─ types_async.h
   │     │  │  │  │  ├─ type_fwd.h
   │     │  │  │  │  └─ visibility.h
   │     │  │  │  ├─ io
   │     │  │  │  │  ├─ api.h
   │     │  │  │  │  ├─ buffered.h
   │     │  │  │  │  ├─ caching.h
   │     │  │  │  │  ├─ compressed.h
   │     │  │  │  │  ├─ concurrency.h
   │     │  │  │  │  ├─ file.h
   │     │  │  │  │  ├─ hdfs.h
   │     │  │  │  │  ├─ interfaces.h
   │     │  │  │  │  ├─ memory.h
   │     │  │  │  │  ├─ mman.h
   │     │  │  │  │  ├─ slow.h
   │     │  │  │  │  ├─ stdio.h
   │     │  │  │  │  ├─ test_common.h
   │     │  │  │  │  ├─ transform.h
   │     │  │  │  │  └─ type_fwd.h
   │     │  │  │  ├─ ipc
   │     │  │  │  │  ├─ api.h
   │     │  │  │  │  ├─ dictionary.h
   │     │  │  │  │  ├─ feather.h
   │     │  │  │  │  ├─ message.h
   │     │  │  │  │  ├─ options.h
   │     │  │  │  │  ├─ reader.h
   │     │  │  │  │  ├─ test_common.h
   │     │  │  │  │  ├─ type_fwd.h
   │     │  │  │  │  ├─ util.h
   │     │  │  │  │  └─ writer.h
   │     │  │  │  ├─ json
   │     │  │  │  │  ├─ api.h
   │     │  │  │  │  ├─ chunked_builder.h
   │     │  │  │  │  ├─ chunker.h
   │     │  │  │  │  ├─ converter.h
   │     │  │  │  │  ├─ from_string.h
   │     │  │  │  │  ├─ object_parser.h
   │     │  │  │  │  ├─ object_writer.h
   │     │  │  │  │  ├─ options.h
   │     │  │  │  │  ├─ parser.h
   │     │  │  │  │  ├─ rapidjson_defs.h
   │     │  │  │  │  ├─ reader.h
   │     │  │  │  │  ├─ test_common.h
   │     │  │  │  │  └─ type_fwd.h
   │     │  │  │  ├─ memory_pool.h
   │     │  │  │  ├─ memory_pool_test.h
   │     │  │  │  ├─ pretty_print.h
   │     │  │  │  ├─ python
   │     │  │  │  │  ├─ api.h
   │     │  │  │  │  ├─ arrow_to_pandas.h
   │     │  │  │  │  ├─ async.h
   │     │  │  │  │  ├─ benchmark.h
   │     │  │  │  │  ├─ common.h
   │     │  │  │  │  ├─ config.h
   │     │  │  │  │  ├─ csv.h
   │     │  │  │  │  ├─ datetime.h
   │     │  │  │  │  ├─ decimal.h
   │     │  │  │  │  ├─ extension_type.h
   │     │  │  │  │  ├─ filesystem.h
   │     │  │  │  │  ├─ flight.h
   │     │  │  │  │  ├─ gdb.h
   │     │  │  │  │  ├─ helpers.h
   │     │  │  │  │  ├─ inference.h
   │     │  │  │  │  ├─ io.h
   │     │  │  │  │  ├─ ipc.h
   │     │  │  │  │  ├─ iterators.h
   │     │  │  │  │  ├─ lib.h
   │     │  │  │  │  ├─ lib_api.h
   │     │  │  │  │  ├─ numpy_convert.h
   │     │  │  │  │  ├─ numpy_init.h
   │     │  │  │  │  ├─ numpy_interop.h
   │     │  │  │  │  ├─ numpy_to_arrow.h
   │     │  │  │  │  ├─ parquet_encryption.h
   │     │  │  │  │  ├─ platform.h
   │     │  │  │  │  ├─ pyarrow.h
   │     │  │  │  │  ├─ pyarrow_api.h
   │     │  │  │  │  ├─ pyarrow_lib.h
   │     │  │  │  │  ├─ python_test.h
   │     │  │  │  │  ├─ python_to_arrow.h
   │     │  │  │  │  ├─ type_traits.h
   │     │  │  │  │  ├─ udf.h
   │     │  │  │  │  ├─ util.h
   │     │  │  │  │  ├─ vendored
   │     │  │  │  │  │  └─ pythoncapi_compat.h
   │     │  │  │  │  └─ visibility.h
   │     │  │  │  ├─ record_batch.h
   │     │  │  │  ├─ result.h
   │     │  │  │  ├─ scalar.h
   │     │  │  │  ├─ sparse_tensor.h
   │     │  │  │  ├─ status.h
   │     │  │  │  ├─ stl.h
   │     │  │  │  ├─ stl_allocator.h
   │     │  │  │  ├─ stl_iterator.h
   │     │  │  │  ├─ table.h
   │     │  │  │  ├─ table_builder.h
   │     │  │  │  ├─ tensor
   │     │  │  │  │  └─ converter.h
   │     │  │  │  ├─ tensor.h
   │     │  │  │  ├─ testing
   │     │  │  │  │  ├─ async_test_util.h
   │     │  │  │  │  ├─ builder.h
   │     │  │  │  │  ├─ executor_util.h
   │     │  │  │  │  ├─ extension_type.h
   │     │  │  │  │  ├─ fixed_width_test_util.h
   │     │  │  │  │  ├─ future_util.h
   │     │  │  │  │  ├─ generator.h
   │     │  │  │  │  ├─ gtest_compat.h
   │     │  │  │  │  ├─ gtest_util.h
   │     │  │  │  │  ├─ matchers.h
   │     │  │  │  │  ├─ math.h
   │     │  │  │  │  ├─ process.h
   │     │  │  │  │  ├─ random.h
   │     │  │  │  │  ├─ uniform_real.h
   │     │  │  │  │  ├─ util.h
   │     │  │  │  │  └─ visibility.h
   │     │  │  │  ├─ type.h
   │     │  │  │  ├─ type_fwd.h
   │     │  │  │  ├─ type_traits.h
   │     │  │  │  ├─ util
   │     │  │  │  │  ├─ algorithm.h
   │     │  │  │  │  ├─ aligned_storage.h
   │     │  │  │  │  ├─ align_util.h
   │     │  │  │  │  ├─ async_generator.h
   │     │  │  │  │  ├─ async_generator_fwd.h
   │     │  │  │  │  ├─ async_util.h
   │     │  │  │  │  ├─ base64.h
   │     │  │  │  │  ├─ basic_decimal.h
   │     │  │  │  │  ├─ benchmark_util.h
   │     │  │  │  │  ├─ binary_view_util.h
   │     │  │  │  │  ├─ bitmap.h
   │     │  │  │  │  ├─ bitmap_builders.h
   │     │  │  │  │  ├─ bitmap_generate.h
   │     │  │  │  │  ├─ bitmap_ops.h
   │     │  │  │  │  ├─ bitmap_reader.h
   │     │  │  │  │  ├─ bitmap_visit.h
   │     │  │  │  │  ├─ bitmap_writer.h
   │     │  │  │  │  ├─ bit_block_counter.h
   │     │  │  │  │  ├─ bit_run_reader.h
   │     │  │  │  │  ├─ bit_util.h
   │     │  │  │  │  ├─ byte_size.h
   │     │  │  │  │  ├─ cancel.h
   │     │  │  │  │  ├─ checked_cast.h
   │     │  │  │  │  ├─ compare.h
   │     │  │  │  │  ├─ compression.h
   │     │  │  │  │  ├─ concurrent_map.h
   │     │  │  │  │  ├─ config.h
   │     │  │  │  │  ├─ converter.h
   │     │  │  │  │  ├─ cpu_info.h
   │     │  │  │  │  ├─ crc32.h
   │     │  │  │  │  ├─ debug.h
   │     │  │  │  │  ├─ decimal.h
   │     │  │  │  │  ├─ delimiting.h
   │     │  │  │  │  ├─ endian.h
   │     │  │  │  │  ├─ float16.h
   │     │  │  │  │  ├─ formatting.h
   │     │  │  │  │  ├─ functional.h
   │     │  │  │  │  ├─ future.h
   │     │  │  │  │  ├─ hashing.h
   │     │  │  │  │  ├─ hash_util.h
   │     │  │  │  │  ├─ int_util.h
   │     │  │  │  │  ├─ int_util_overflow.h
   │     │  │  │  │  ├─ io_util.h
   │     │  │  │  │  ├─ iterator.h
   │     │  │  │  │  ├─ key_value_metadata.h
   │     │  │  │  │  ├─ launder.h
   │     │  │  │  │  ├─ list_util.h
   │     │  │  │  │  ├─ logger.h
   │     │  │  │  │  ├─ logging.h
   │     │  │  │  │  ├─ macros.h
   │     │  │  │  │  ├─ math_constants.h
   │     │  │  │  │  ├─ mutex.h
   │     │  │  │  │  ├─ parallel.h
   │     │  │  │  │  ├─ pcg_random.h
   │     │  │  │  │  ├─ prefetch.h
   │     │  │  │  │  ├─ queue.h
   │     │  │  │  │  ├─ range.h
   │     │  │  │  │  ├─ ree_util.h
   │     │  │  │  │  ├─ regex.h
   │     │  │  │  │  ├─ rows_to_batches.h
   │     │  │  │  │  ├─ secure_string.h
   │     │  │  │  │  ├─ simd.h
   │     │  │  │  │  ├─ small_vector.h
   │     │  │  │  │  ├─ span.h
   │     │  │  │  │  ├─ string.h
   │     │  │  │  │  ├─ string_util.h
   │     │  │  │  │  ├─ task_group.h
   │     │  │  │  │  ├─ test_common.h
   │     │  │  │  │  ├─ thread_pool.h
   │     │  │  │  │  ├─ time.h
   │     │  │  │  │  ├─ tracing.h
   │     │  │  │  │  ├─ type_fwd.h
   │     │  │  │  │  ├─ type_traits.h
   │     │  │  │  │  ├─ ubsan.h
   │     │  │  │  │  ├─ union_util.h
   │     │  │  │  │  ├─ unreachable.h
   │     │  │  │  │  ├─ uri.h
   │     │  │  │  │  ├─ utf8.h
   │     │  │  │  │  ├─ value_parsing.h
   │     │  │  │  │  ├─ vector.h
   │     │  │  │  │  ├─ visibility.h
   │     │  │  │  │  ├─ windows_compatibility.h
   │     │  │  │  │  └─ windows_fixup.h
   │     │  │  │  ├─ vendored
   │     │  │  │  │  ├─ datetime
   │     │  │  │  │  │  ├─ date.h
   │     │  │  │  │  │  ├─ ios.h
   │     │  │  │  │  │  ├─ tz.h
   │     │  │  │  │  │  ├─ tz_private.h
   │     │  │  │  │  │  └─ visibility.h
   │     │  │  │  │  ├─ datetime.h
   │     │  │  │  │  ├─ double-conversion
   │     │  │  │  │  │  ├─ bignum-dtoa.h
   │     │  │  │  │  │  ├─ bignum.h
   │     │  │  │  │  │  ├─ cached-powers.h
   │     │  │  │  │  │  ├─ diy-fp.h
   │     │  │  │  │  │  ├─ double-conversion.h
   │     │  │  │  │  │  ├─ double-to-string.h
   │     │  │  │  │  │  ├─ fast-dtoa.h
   │     │  │  │  │  │  ├─ fixed-dtoa.h
   │     │  │  │  │  │  ├─ ieee.h
   │     │  │  │  │  │  ├─ string-to-double.h
   │     │  │  │  │  │  ├─ strtod.h
   │     │  │  │  │  │  └─ utils.h
   │     │  │  │  │  ├─ pcg
   │     │  │  │  │  │  ├─ pcg_extras.hpp
   │     │  │  │  │  │  ├─ pcg_random.hpp
   │     │  │  │  │  │  └─ pcg_uint128.hpp
   │     │  │  │  │  ├─ portable-snippets
   │     │  │  │  │  │  └─ debug-trap.h
   │     │  │  │  │  ├─ ProducerConsumerQueue.h
   │     │  │  │  │  ├─ safeint
   │     │  │  │  │  │  ├─ safe_math.h
   │     │  │  │  │  │  └─ safe_math_impl.h
   │     │  │  │  │  ├─ strptime.h
   │     │  │  │  │  ├─ xxhash
   │     │  │  │  │  │  └─ xxhash.h
   │     │  │  │  │  └─ xxhash.h
   │     │  │  │  ├─ visitor.h
   │     │  │  │  ├─ visitor_generate.h
   │     │  │  │  ├─ visit_array_inline.h
   │     │  │  │  ├─ visit_data_inline.h
   │     │  │  │  ├─ visit_scalar_inline.h
   │     │  │  │  └─ visit_type_inline.h
   │     │  │  └─ parquet
   │     │  │     ├─ api
   │     │  │     │  ├─ io.h
   │     │  │     │  ├─ reader.h
   │     │  │     │  ├─ schema.h
   │     │  │     │  └─ writer.h
   │     │  │     ├─ arrow
   │     │  │     │  ├─ reader.h
   │     │  │     │  ├─ schema.h
   │     │  │     │  ├─ test_util.h
   │     │  │     │  └─ writer.h
   │     │  │     ├─ benchmark_util.h
   │     │  │     ├─ bloom_filter.h
   │     │  │     ├─ bloom_filter_reader.h
   │     │  │     ├─ column_page.h
   │     │  │     ├─ column_reader.h
   │     │  │     ├─ column_scanner.h
   │     │  │     ├─ column_writer.h
   │     │  │     ├─ encoding.h
   │     │  │     ├─ encryption
   │     │  │     │  ├─ crypto_factory.h
   │     │  │     │  ├─ encryption.h
   │     │  │     │  ├─ file_key_material_store.h
   │     │  │     │  ├─ file_key_unwrapper.h
   │     │  │     │  ├─ file_key_wrapper.h
   │     │  │     │  ├─ file_system_key_material_store.h
   │     │  │     │  ├─ key_encryption_key.h
   │     │  │     │  ├─ key_material.h
   │     │  │     │  ├─ key_metadata.h
   │     │  │     │  ├─ key_toolkit.h
   │     │  │     │  ├─ kms_client.h
   │     │  │     │  ├─ kms_client_factory.h
   │     │  │     │  ├─ local_wrap_kms_client.h
   │     │  │     │  ├─ test_encryption_util.h
   │     │  │     │  ├─ test_in_memory_kms.h
   │     │  │     │  ├─ two_level_cache_with_expiration.h
   │     │  │     │  └─ type_fwd.h
   │     │  │     ├─ exception.h
   │     │  │     ├─ file_reader.h
   │     │  │     ├─ file_writer.h
   │     │  │     ├─ geospatial
   │     │  │     │  └─ statistics.h
   │     │  │     ├─ hasher.h
   │     │  │     ├─ level_comparison.h
   │     │  │     ├─ level_comparison_inc.h
   │     │  │     ├─ level_conversion.h
   │     │  │     ├─ level_conversion_inc.h
   │     │  │     ├─ metadata.h
   │     │  │     ├─ page_index.h
   │     │  │     ├─ parquet_version.h
   │     │  │     ├─ platform.h
   │     │  │     ├─ printer.h
   │     │  │     ├─ properties.h
   │     │  │     ├─ schema.h
   │     │  │     ├─ size_statistics.h
   │     │  │     ├─ statistics.h
   │     │  │     ├─ stream_reader.h
   │     │  │     ├─ stream_writer.h
   │     │  │     ├─ test_util.h
   │     │  │     ├─ types.h
   │     │  │     ├─ type_fwd.h
   │     │  │     ├─ windows_compatibility.h
   │     │  │     ├─ windows_fixup.h
   │     │  │     └─ xxhasher.h
   │     │  ├─ includes
   │     │  │  ├─ common.pxd
   │     │  │  ├─ libarrow.pxd
   │     │  │  ├─ libarrow_acero.pxd
   │     │  │  ├─ libarrow_cuda.pxd
   │     │  │  ├─ libarrow_dataset.pxd
   │     │  │  ├─ libarrow_dataset_parquet.pxd
   │     │  │  ├─ libarrow_feather.pxd
   │     │  │  ├─ libarrow_flight.pxd
   │     │  │  ├─ libarrow_fs.pxd
   │     │  │  ├─ libarrow_python.pxd
   │     │  │  ├─ libarrow_substrait.pxd
   │     │  │  ├─ libgandiva.pxd
   │     │  │  ├─ libparquet.pxd
   │     │  │  ├─ libparquet_encryption.pxd
   │     │  │  └─ __init__.pxd
   │     │  ├─ interchange
   │     │  │  ├─ buffer.py
   │     │  │  ├─ column.py
   │     │  │  ├─ dataframe.py
   │     │  │  ├─ from_dataframe.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ buffer.cpython-311.pyc
   │     │  │     ├─ column.cpython-311.pyc
   │     │  │     ├─ dataframe.cpython-311.pyc
   │     │  │     ├─ from_dataframe.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ io.pxi
   │     │  ├─ ipc.pxi
   │     │  ├─ ipc.py
   │     │  ├─ json.py
   │     │  ├─ jvm.py
   │     │  ├─ lib.cp311-win_amd64.pyd
   │     │  ├─ lib.h
   │     │  ├─ lib.pxd
   │     │  ├─ lib.pyx
   │     │  ├─ lib_api.h
   │     │  ├─ memory.pxi
   │     │  ├─ orc.py
   │     │  ├─ pandas-shim.pxi
   │     │  ├─ pandas_compat.py
   │     │  ├─ parquet
   │     │  │  ├─ core.py
   │     │  │  ├─ encryption.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ core.cpython-311.pyc
   │     │  │     ├─ encryption.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ parquet.dll
   │     │  ├─ parquet.lib
   │     │  ├─ public-api.pxi
   │     │  ├─ scalar.pxi
   │     │  ├─ src
   │     │  │  └─ arrow
   │     │  │     └─ python
   │     │  │        ├─ api.h
   │     │  │        ├─ arrow_to_pandas.cc
   │     │  │        ├─ arrow_to_pandas.h
   │     │  │        ├─ arrow_to_python_internal.h
   │     │  │        ├─ async.h
   │     │  │        ├─ benchmark.cc
   │     │  │        ├─ benchmark.h
   │     │  │        ├─ CMakeLists.txt
   │     │  │        ├─ common.cc
   │     │  │        ├─ common.h
   │     │  │        ├─ config.cc
   │     │  │        ├─ config.h
   │     │  │        ├─ config_internal.h.cmake
   │     │  │        ├─ csv.cc
   │     │  │        ├─ csv.h
   │     │  │        ├─ datetime.cc
   │     │  │        ├─ datetime.h
   │     │  │        ├─ decimal.cc
   │     │  │        ├─ decimal.h
   │     │  │        ├─ extension_type.cc
   │     │  │        ├─ extension_type.h
   │     │  │        ├─ filesystem.cc
   │     │  │        ├─ filesystem.h
   │     │  │        ├─ flight.cc
   │     │  │        ├─ flight.h
   │     │  │        ├─ gdb.cc
   │     │  │        ├─ gdb.h
   │     │  │        ├─ helpers.cc
   │     │  │        ├─ helpers.h
   │     │  │        ├─ inference.cc
   │     │  │        ├─ inference.h
   │     │  │        ├─ io.cc
   │     │  │        ├─ io.h
   │     │  │        ├─ ipc.cc
   │     │  │        ├─ ipc.h
   │     │  │        ├─ iterators.h
   │     │  │        ├─ numpy_convert.cc
   │     │  │        ├─ numpy_convert.h
   │     │  │        ├─ numpy_init.cc
   │     │  │        ├─ numpy_init.h
   │     │  │        ├─ numpy_internal.h
   │     │  │        ├─ numpy_interop.h
   │     │  │        ├─ numpy_to_arrow.cc
   │     │  │        ├─ numpy_to_arrow.h
   │     │  │        ├─ parquet_encryption.cc
   │     │  │        ├─ parquet_encryption.h
   │     │  │        ├─ platform.h
   │     │  │        ├─ pyarrow.cc
   │     │  │        ├─ pyarrow.h
   │     │  │        ├─ pyarrow_api.h
   │     │  │        ├─ pyarrow_lib.h
   │     │  │        ├─ python_test.cc
   │     │  │        ├─ python_test.h
   │     │  │        ├─ python_to_arrow.cc
   │     │  │        ├─ python_to_arrow.h
   │     │  │        ├─ type_traits.h
   │     │  │        ├─ udf.cc
   │     │  │        ├─ udf.h
   │     │  │        ├─ util.cc
   │     │  │        ├─ util.h
   │     │  │        ├─ vendored
   │     │  │        │  ├─ CMakeLists.txt
   │     │  │        │  └─ pythoncapi_compat.h
   │     │  │        └─ visibility.h
   │     │  ├─ substrait.py
   │     │  ├─ table.pxi
   │     │  ├─ tensor.pxi
   │     │  ├─ tests
   │     │  │  ├─ arrow_16597.py
   │     │  │  ├─ arrow_39313.py
   │     │  │  ├─ arrow_7980.py
   │     │  │  ├─ bound_function_visit_strings.pyx
   │     │  │  ├─ conftest.py
   │     │  │  ├─ data
   │     │  │  │  ├─ feather
   │     │  │  │  │  └─ v0.17.0.version.2-compression.lz4.feather
   │     │  │  │  ├─ orc
   │     │  │  │  │  ├─ decimal.jsn.gz
   │     │  │  │  │  ├─ decimal.orc
   │     │  │  │  │  ├─ README.md
   │     │  │  │  │  ├─ TestOrcFile.emptyFile.jsn.gz
   │     │  │  │  │  ├─ TestOrcFile.emptyFile.orc
   │     │  │  │  │  ├─ TestOrcFile.test1.jsn.gz
   │     │  │  │  │  ├─ TestOrcFile.test1.orc
   │     │  │  │  │  ├─ TestOrcFile.testDate1900.jsn.gz
   │     │  │  │  │  └─ TestOrcFile.testDate1900.orc
   │     │  │  │  └─ parquet
   │     │  │  │     ├─ v0.7.1.all-named-index.parquet
   │     │  │  │     ├─ v0.7.1.column-metadata-handling.parquet
   │     │  │  │     ├─ v0.7.1.parquet
   │     │  │  │     └─ v0.7.1.some-named-index.parquet
   │     │  │  ├─ extensions.pyx
   │     │  │  ├─ interchange
   │     │  │  │  ├─ test_conversion.py
   │     │  │  │  ├─ test_interchange_spec.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ test_conversion.cpython-311.pyc
   │     │  │  │     ├─ test_interchange_spec.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ pandas_examples.py
   │     │  │  ├─ pandas_threaded_import.py
   │     │  │  ├─ parquet
   │     │  │  │  ├─ common.py
   │     │  │  │  ├─ conftest.py
   │     │  │  │  ├─ encryption.py
   │     │  │  │  ├─ test_basic.py
   │     │  │  │  ├─ test_compliant_nested_type.py
   │     │  │  │  ├─ test_dataset.py
   │     │  │  │  ├─ test_data_types.py
   │     │  │  │  ├─ test_datetime.py
   │     │  │  │  ├─ test_encryption.py
   │     │  │  │  ├─ test_metadata.py
   │     │  │  │  ├─ test_pandas.py
   │     │  │  │  ├─ test_parquet_file.py
   │     │  │  │  ├─ test_parquet_writer.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ common.cpython-311.pyc
   │     │  │  │     ├─ conftest.cpython-311.pyc
   │     │  │  │     ├─ encryption.cpython-311.pyc
   │     │  │  │     ├─ test_basic.cpython-311.pyc
   │     │  │  │     ├─ test_compliant_nested_type.cpython-311.pyc
   │     │  │  │     ├─ test_dataset.cpython-311.pyc
   │     │  │  │     ├─ test_data_types.cpython-311.pyc
   │     │  │  │     ├─ test_datetime.cpython-311.pyc
   │     │  │  │     ├─ test_encryption.cpython-311.pyc
   │     │  │  │     ├─ test_metadata.cpython-311.pyc
   │     │  │  │     ├─ test_pandas.cpython-311.pyc
   │     │  │  │     ├─ test_parquet_file.cpython-311.pyc
   │     │  │  │     ├─ test_parquet_writer.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ pyarrow_cython_example.pyx
   │     │  │  ├─ read_record_batch.py
   │     │  │  ├─ strategies.py
   │     │  │  ├─ test_acero.py
   │     │  │  ├─ test_adhoc_memory_leak.py
   │     │  │  ├─ test_array.py
   │     │  │  ├─ test_builder.py
   │     │  │  ├─ test_cffi.py
   │     │  │  ├─ test_compute.py
   │     │  │  ├─ test_convert_builtin.py
   │     │  │  ├─ test_cpp_internals.py
   │     │  │  ├─ test_csv.py
   │     │  │  ├─ test_cuda.py
   │     │  │  ├─ test_cuda_numba_interop.py
   │     │  │  ├─ test_cython.py
   │     │  │  ├─ test_dataset.py
   │     │  │  ├─ test_dataset_encryption.py
   │     │  │  ├─ test_deprecations.py
   │     │  │  ├─ test_device.py
   │     │  │  ├─ test_dlpack.py
   │     │  │  ├─ test_exec_plan.py
   │     │  │  ├─ test_extension_type.py
   │     │  │  ├─ test_feather.py
   │     │  │  ├─ test_flight.py
   │     │  │  ├─ test_flight_async.py
   │     │  │  ├─ test_fs.py
   │     │  │  ├─ test_gandiva.py
   │     │  │  ├─ test_gdb.py
   │     │  │  ├─ test_io.py
   │     │  │  ├─ test_ipc.py
   │     │  │  ├─ test_json.py
   │     │  │  ├─ test_jvm.py
   │     │  │  ├─ test_memory.py
   │     │  │  ├─ test_misc.py
   │     │  │  ├─ test_orc.py
   │     │  │  ├─ test_pandas.py
   │     │  │  ├─ test_scalars.py
   │     │  │  ├─ test_schema.py
   │     │  │  ├─ test_sparse_tensor.py
   │     │  │  ├─ test_strategies.py
   │     │  │  ├─ test_substrait.py
   │     │  │  ├─ test_table.py
   │     │  │  ├─ test_tensor.py
   │     │  │  ├─ test_types.py
   │     │  │  ├─ test_udf.py
   │     │  │  ├─ test_util.py
   │     │  │  ├─ test_without_numpy.py
   │     │  │  ├─ util.py
   │     │  │  ├─ wsgi_examples.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ arrow_16597.cpython-311.pyc
   │     │  │     ├─ arrow_39313.cpython-311.pyc
   │     │  │     ├─ arrow_7980.cpython-311.pyc
   │     │  │     ├─ conftest.cpython-311.pyc
   │     │  │     ├─ pandas_examples.cpython-311.pyc
   │     │  │     ├─ pandas_threaded_import.cpython-311.pyc
   │     │  │     ├─ read_record_batch.cpython-311.pyc
   │     │  │     ├─ strategies.cpython-311.pyc
   │     │  │     ├─ test_acero.cpython-311.pyc
   │     │  │     ├─ test_adhoc_memory_leak.cpython-311.pyc
   │     │  │     ├─ test_array.cpython-311.pyc
   │     │  │     ├─ test_builder.cpython-311.pyc
   │     │  │     ├─ test_cffi.cpython-311.pyc
   │     │  │     ├─ test_compute.cpython-311.pyc
   │     │  │     ├─ test_convert_builtin.cpython-311.pyc
   │     │  │     ├─ test_cpp_internals.cpython-311.pyc
   │     │  │     ├─ test_csv.cpython-311.pyc
   │     │  │     ├─ test_cuda.cpython-311.pyc
   │     │  │     ├─ test_cuda_numba_interop.cpython-311.pyc
   │     │  │     ├─ test_cython.cpython-311.pyc
   │     │  │     ├─ test_dataset.cpython-311.pyc
   │     │  │     ├─ test_dataset_encryption.cpython-311.pyc
   │     │  │     ├─ test_deprecations.cpython-311.pyc
   │     │  │     ├─ test_device.cpython-311.pyc
   │     │  │     ├─ test_dlpack.cpython-311.pyc
   │     │  │     ├─ test_exec_plan.cpython-311.pyc
   │     │  │     ├─ test_extension_type.cpython-311.pyc
   │     │  │     ├─ test_feather.cpython-311.pyc
   │     │  │     ├─ test_flight.cpython-311.pyc
   │     │  │     ├─ test_flight_async.cpython-311.pyc
   │     │  │     ├─ test_fs.cpython-311.pyc
   │     │  │     ├─ test_gandiva.cpython-311.pyc
   │     │  │     ├─ test_gdb.cpython-311.pyc
   │     │  │     ├─ test_io.cpython-311.pyc
   │     │  │     ├─ test_ipc.cpython-311.pyc
   │     │  │     ├─ test_json.cpython-311.pyc
   │     │  │     ├─ test_jvm.cpython-311.pyc
   │     │  │     ├─ test_memory.cpython-311.pyc
   │     │  │     ├─ test_misc.cpython-311.pyc
   │     │  │     ├─ test_orc.cpython-311.pyc
   │     │  │     ├─ test_pandas.cpython-311.pyc
   │     │  │     ├─ test_scalars.cpython-311.pyc
   │     │  │     ├─ test_schema.cpython-311.pyc
   │     │  │     ├─ test_sparse_tensor.cpython-311.pyc
   │     │  │     ├─ test_strategies.cpython-311.pyc
   │     │  │     ├─ test_substrait.cpython-311.pyc
   │     │  │     ├─ test_table.cpython-311.pyc
   │     │  │     ├─ test_tensor.cpython-311.pyc
   │     │  │     ├─ test_types.cpython-311.pyc
   │     │  │     ├─ test_udf.cpython-311.pyc
   │     │  │     ├─ test_util.cpython-311.pyc
   │     │  │     ├─ test_without_numpy.cpython-311.pyc
   │     │  │     ├─ util.cpython-311.pyc
   │     │  │     ├─ wsgi_examples.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ types.pxi
   │     │  ├─ types.py
   │     │  ├─ util.py
   │     │  ├─ vendored
   │     │  │  ├─ docscrape.py
   │     │  │  ├─ version.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ docscrape.cpython-311.pyc
   │     │  │     ├─ version.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ _acero.cp311-win_amd64.pyd
   │     │  ├─ _acero.pxd
   │     │  ├─ _acero.pyx
   │     │  ├─ _azurefs.pyx
   │     │  ├─ _compute.cp311-win_amd64.pyd
   │     │  ├─ _compute.pxd
   │     │  ├─ _compute.pyx
   │     │  ├─ _compute_docstrings.py
   │     │  ├─ _csv.cp311-win_amd64.pyd
   │     │  ├─ _csv.pxd
   │     │  ├─ _csv.pyx
   │     │  ├─ _cuda.pxd
   │     │  ├─ _cuda.pyx
   │     │  ├─ _dataset.cp311-win_amd64.pyd
   │     │  ├─ _dataset.pxd
   │     │  ├─ _dataset.pyx
   │     │  ├─ _dataset_orc.cp311-win_amd64.pyd
   │     │  ├─ _dataset_orc.pyx
   │     │  ├─ _dataset_parquet.cp311-win_amd64.pyd
   │     │  ├─ _dataset_parquet.pxd
   │     │  ├─ _dataset_parquet.pyx
   │     │  ├─ _dataset_parquet_encryption.cp311-win_amd64.pyd
   │     │  ├─ _dataset_parquet_encryption.pyx
   │     │  ├─ _dlpack.pxi
   │     │  ├─ _feather.cp311-win_amd64.pyd
   │     │  ├─ _feather.pyx
   │     │  ├─ _flight.cp311-win_amd64.pyd
   │     │  ├─ _flight.pyx
   │     │  ├─ _fs.cp311-win_amd64.pyd
   │     │  ├─ _fs.pxd
   │     │  ├─ _fs.pyx
   │     │  ├─ _gcsfs.cp311-win_amd64.pyd
   │     │  ├─ _gcsfs.pyx
   │     │  ├─ _generated_version.py
   │     │  ├─ _hdfs.cp311-win_amd64.pyd
   │     │  ├─ _hdfs.pyx
   │     │  ├─ _json.cp311-win_amd64.pyd
   │     │  ├─ _json.pxd
   │     │  ├─ _json.pyx
   │     │  ├─ _orc.cp311-win_amd64.pyd
   │     │  ├─ _orc.pxd
   │     │  ├─ _orc.pyx
   │     │  ├─ _parquet.cp311-win_amd64.pyd
   │     │  ├─ _parquet.pxd
   │     │  ├─ _parquet.pyx
   │     │  ├─ _parquet_encryption.cp311-win_amd64.pyd
   │     │  ├─ _parquet_encryption.pxd
   │     │  ├─ _parquet_encryption.pyx
   │     │  ├─ _pyarrow_cpp_tests.cp311-win_amd64.pyd
   │     │  ├─ _pyarrow_cpp_tests.pxd
   │     │  ├─ _pyarrow_cpp_tests.pyx
   │     │  ├─ _s3fs.cp311-win_amd64.pyd
   │     │  ├─ _s3fs.pyx
   │     │  ├─ _substrait.cp311-win_amd64.pyd
   │     │  ├─ _substrait.pyx
   │     │  ├─ __init__.pxd
   │     │  ├─ __init__.py
   │     │  └─ __pycache__
   │     │     ├─ acero.cpython-311.pyc
   │     │     ├─ benchmark.cpython-311.pyc
   │     │     ├─ cffi.cpython-311.pyc
   │     │     ├─ compute.cpython-311.pyc
   │     │     ├─ conftest.cpython-311.pyc
   │     │     ├─ csv.cpython-311.pyc
   │     │     ├─ cuda.cpython-311.pyc
   │     │     ├─ dataset.cpython-311.pyc
   │     │     ├─ feather.cpython-311.pyc
   │     │     ├─ flight.cpython-311.pyc
   │     │     ├─ fs.cpython-311.pyc
   │     │     ├─ ipc.cpython-311.pyc
   │     │     ├─ json.cpython-311.pyc
   │     │     ├─ jvm.cpython-311.pyc
   │     │     ├─ orc.cpython-311.pyc
   │     │     ├─ pandas_compat.cpython-311.pyc
   │     │     ├─ substrait.cpython-311.pyc
   │     │     ├─ types.cpython-311.pyc
   │     │     ├─ util.cpython-311.pyc
   │     │     ├─ _compute_docstrings.cpython-311.pyc
   │     │     ├─ _generated_version.cpython-311.pyc
   │     │     └─ __init__.cpython-311.pyc
   │     ├─ pyarrow-23.0.1.dist-info
   │     │  ├─ DELVEWHEEL
   │     │  ├─ INSTALLER
   │     │  ├─ licenses
   │     │  │  ├─ LICENSE.txt
   │     │  │  └─ NOTICE.txt
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  ├─ top_level.txt
   │     │  └─ WHEEL
   │     ├─ pyarrow.libs
   │     │  └─ msvcp140-2a7008da6f9aae43c7a434835dcaf31e.dll
   │     ├─ pybase64
   │     │  ├─ py.typed
   │     │  ├─ _fallback.py
   │     │  ├─ _license.py
   │     │  ├─ _license.pyi
   │     │  ├─ _pybase64.cp311-win_amd64.pyd
   │     │  ├─ _pybase64.pyi
   │     │  ├─ _typing.py
   │     │  ├─ _version.py
   │     │  ├─ __init__.py
   │     │  ├─ __main__.py
   │     │  └─ __pycache__
   │     │     ├─ _fallback.cpython-311.pyc
   │     │     ├─ _license.cpython-311.pyc
   │     │     ├─ _typing.cpython-311.pyc
   │     │     ├─ _version.cpython-311.pyc
   │     │     ├─ __init__.cpython-311.pyc
   │     │     └─ __main__.cpython-311.pyc
   │     ├─ pybase64-1.4.3.dist-info
   │     │  ├─ entry_points.txt
   │     │  ├─ INSTALLER
   │     │  ├─ licenses
   │     │  │  └─ LICENSE
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  ├─ top_level.txt
   │     │  └─ WHEEL
   │     ├─ pydantic
   │     │  ├─ aliases.py
   │     │  ├─ alias_generators.py
   │     │  ├─ annotated_handlers.py
   │     │  ├─ class_validators.py
   │     │  ├─ color.py
   │     │  ├─ config.py
   │     │  ├─ dataclasses.py
   │     │  ├─ datetime_parse.py
   │     │  ├─ decorator.py
   │     │  ├─ deprecated
   │     │  │  ├─ class_validators.py
   │     │  │  ├─ config.py
   │     │  │  ├─ copy_internals.py
   │     │  │  ├─ decorator.py
   │     │  │  ├─ json.py
   │     │  │  ├─ parse.py
   │     │  │  ├─ tools.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ class_validators.cpython-311.pyc
   │     │  │     ├─ config.cpython-311.pyc
   │     │  │     ├─ copy_internals.cpython-311.pyc
   │     │  │     ├─ decorator.cpython-311.pyc
   │     │  │     ├─ json.cpython-311.pyc
   │     │  │     ├─ parse.cpython-311.pyc
   │     │  │     ├─ tools.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ env_settings.py
   │     │  ├─ errors.py
   │     │  ├─ error_wrappers.py
   │     │  ├─ experimental
   │     │  │  ├─ arguments_schema.py
   │     │  │  ├─ missing_sentinel.py
   │     │  │  ├─ pipeline.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ arguments_schema.cpython-311.pyc
   │     │  │     ├─ missing_sentinel.cpython-311.pyc
   │     │  │     ├─ pipeline.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ fields.py
   │     │  ├─ functional_serializers.py
   │     │  ├─ functional_validators.py
   │     │  ├─ generics.py
   │     │  ├─ json.py
   │     │  ├─ json_schema.py
   │     │  ├─ main.py
   │     │  ├─ mypy.py
   │     │  ├─ networks.py
   │     │  ├─ parse.py
   │     │  ├─ plugin
   │     │  │  ├─ _loader.py
   │     │  │  ├─ _schema_validator.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ _loader.cpython-311.pyc
   │     │  │     ├─ _schema_validator.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ py.typed
   │     │  ├─ root_model.py
   │     │  ├─ schema.py
   │     │  ├─ tools.py
   │     │  ├─ types.py
   │     │  ├─ type_adapter.py
   │     │  ├─ typing.py
   │     │  ├─ utils.py
   │     │  ├─ v1
   │     │  │  ├─ annotated_types.py
   │     │  │  ├─ class_validators.py
   │     │  │  ├─ color.py
   │     │  │  ├─ config.py
   │     │  │  ├─ dataclasses.py
   │     │  │  ├─ datetime_parse.py
   │     │  │  ├─ decorator.py
   │     │  │  ├─ env_settings.py
   │     │  │  ├─ errors.py
   │     │  │  ├─ error_wrappers.py
   │     │  │  ├─ fields.py
   │     │  │  ├─ generics.py
   │     │  │  ├─ json.py
   │     │  │  ├─ main.py
   │     │  │  ├─ mypy.py
   │     │  │  ├─ networks.py
   │     │  │  ├─ parse.py
   │     │  │  ├─ py.typed
   │     │  │  ├─ schema.py
   │     │  │  ├─ tools.py
   │     │  │  ├─ types.py
   │     │  │  ├─ typing.py
   │     │  │  ├─ utils.py
   │     │  │  ├─ validators.py
   │     │  │  ├─ version.py
   │     │  │  ├─ _hypothesis_plugin.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ annotated_types.cpython-311.pyc
   │     │  │     ├─ class_validators.cpython-311.pyc
   │     │  │     ├─ color.cpython-311.pyc
   │     │  │     ├─ config.cpython-311.pyc
   │     │  │     ├─ dataclasses.cpython-311.pyc
   │     │  │     ├─ datetime_parse.cpython-311.pyc
   │     │  │     ├─ decorator.cpython-311.pyc
   │     │  │     ├─ env_settings.cpython-311.pyc
   │     │  │     ├─ errors.cpython-311.pyc
   │     │  │     ├─ error_wrappers.cpython-311.pyc
   │     │  │     ├─ fields.cpython-311.pyc
   │     │  │     ├─ generics.cpython-311.pyc
   │     │  │     ├─ json.cpython-311.pyc
   │     │  │     ├─ main.cpython-311.pyc
   │     │  │     ├─ mypy.cpython-311.pyc
   │     │  │     ├─ networks.cpython-311.pyc
   │     │  │     ├─ parse.cpython-311.pyc
   │     │  │     ├─ schema.cpython-311.pyc
   │     │  │     ├─ tools.cpython-311.pyc
   │     │  │     ├─ types.cpython-311.pyc
   │     │  │     ├─ typing.cpython-311.pyc
   │     │  │     ├─ utils.cpython-311.pyc
   │     │  │     ├─ validators.cpython-311.pyc
   │     │  │     ├─ version.cpython-311.pyc
   │     │  │     ├─ _hypothesis_plugin.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ validate_call_decorator.py
   │     │  ├─ validators.py
   │     │  ├─ version.py
   │     │  ├─ warnings.py
   │     │  ├─ _internal
   │     │  │  ├─ _config.py
   │     │  │  ├─ _core_metadata.py
   │     │  │  ├─ _core_utils.py
   │     │  │  ├─ _dataclasses.py
   │     │  │  ├─ _decorators.py
   │     │  │  ├─ _decorators_v1.py
   │     │  │  ├─ _discriminated_union.py
   │     │  │  ├─ _docs_extraction.py
   │     │  │  ├─ _fields.py
   │     │  │  ├─ _forward_ref.py
   │     │  │  ├─ _generate_schema.py
   │     │  │  ├─ _generics.py
   │     │  │  ├─ _git.py
   │     │  │  ├─ _import_utils.py
   │     │  │  ├─ _internal_dataclass.py
   │     │  │  ├─ _known_annotated_metadata.py
   │     │  │  ├─ _mock_val_ser.py
   │     │  │  ├─ _model_construction.py
   │     │  │  ├─ _namespace_utils.py
   │     │  │  ├─ _repr.py
   │     │  │  ├─ _schema_gather.py
   │     │  │  ├─ _schema_generation_shared.py
   │     │  │  ├─ _serializers.py
   │     │  │  ├─ _signature.py
   │     │  │  ├─ _typing_extra.py
   │     │  │  ├─ _utils.py
   │     │  │  ├─ _validate_call.py
   │     │  │  ├─ _validators.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ _config.cpython-311.pyc
   │     │  │     ├─ _core_metadata.cpython-311.pyc
   │     │  │     ├─ _core_utils.cpython-311.pyc
   │     │  │     ├─ _dataclasses.cpython-311.pyc
   │     │  │     ├─ _decorators.cpython-311.pyc
   │     │  │     ├─ _decorators_v1.cpython-311.pyc
   │     │  │     ├─ _discriminated_union.cpython-311.pyc
   │     │  │     ├─ _docs_extraction.cpython-311.pyc
   │     │  │     ├─ _fields.cpython-311.pyc
   │     │  │     ├─ _forward_ref.cpython-311.pyc
   │     │  │     ├─ _generate_schema.cpython-311.pyc
   │     │  │     ├─ _generics.cpython-311.pyc
   │     │  │     ├─ _git.cpython-311.pyc
   │     │  │     ├─ _import_utils.cpython-311.pyc
   │     │  │     ├─ _internal_dataclass.cpython-311.pyc
   │     │  │     ├─ _known_annotated_metadata.cpython-311.pyc
   │     │  │     ├─ _mock_val_ser.cpython-311.pyc
   │     │  │     ├─ _model_construction.cpython-311.pyc
   │     │  │     ├─ _namespace_utils.cpython-311.pyc
   │     │  │     ├─ _repr.cpython-311.pyc
   │     │  │     ├─ _schema_gather.cpython-311.pyc
   │     │  │     ├─ _schema_generation_shared.cpython-311.pyc
   │     │  │     ├─ _serializers.cpython-311.pyc
   │     │  │     ├─ _signature.cpython-311.pyc
   │     │  │     ├─ _typing_extra.cpython-311.pyc
   │     │  │     ├─ _utils.cpython-311.pyc
   │     │  │     ├─ _validate_call.cpython-311.pyc
   │     │  │     ├─ _validators.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ _migration.py
   │     │  ├─ __init__.py
   │     │  └─ __pycache__
   │     │     ├─ aliases.cpython-311.pyc
   │     │     ├─ alias_generators.cpython-311.pyc
   │     │     ├─ annotated_handlers.cpython-311.pyc
   │     │     ├─ class_validators.cpython-311.pyc
   │     │     ├─ color.cpython-311.pyc
   │     │     ├─ config.cpython-311.pyc
   │     │     ├─ dataclasses.cpython-311.pyc
   │     │     ├─ datetime_parse.cpython-311.pyc
   │     │     ├─ decorator.cpython-311.pyc
   │     │     ├─ env_settings.cpython-311.pyc
   │     │     ├─ errors.cpython-311.pyc
   │     │     ├─ error_wrappers.cpython-311.pyc
   │     │     ├─ fields.cpython-311.pyc
   │     │     ├─ functional_serializers.cpython-311.pyc
   │     │     ├─ functional_validators.cpython-311.pyc
   │     │     ├─ generics.cpython-311.pyc
   │     │     ├─ json.cpython-311.pyc
   │     │     ├─ json_schema.cpython-311.pyc
   │     │     ├─ main.cpython-311.pyc
   │     │     ├─ mypy.cpython-311.pyc
   │     │     ├─ networks.cpython-311.pyc
   │     │     ├─ parse.cpython-311.pyc
   │     │     ├─ root_model.cpython-311.pyc
   │     │     ├─ schema.cpython-311.pyc
   │     │     ├─ tools.cpython-311.pyc
   │     │     ├─ types.cpython-311.pyc
   │     │     ├─ type_adapter.cpython-311.pyc
   │     │     ├─ typing.cpython-311.pyc
   │     │     ├─ utils.cpython-311.pyc
   │     │     ├─ validate_call_decorator.cpython-311.pyc
   │     │     ├─ validators.cpython-311.pyc
   │     │     ├─ version.cpython-311.pyc
   │     │     ├─ warnings.cpython-311.pyc
   │     │     ├─ _migration.cpython-311.pyc
   │     │     └─ __init__.cpython-311.pyc
   │     ├─ pydantic-2.12.5.dist-info
   │     │  ├─ INSTALLER
   │     │  ├─ licenses
   │     │  │  └─ LICENSE
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  ├─ REQUESTED
   │     │  └─ WHEEL
   │     ├─ pydantic_core
   │     │  ├─ core_schema.py
   │     │  ├─ py.typed
   │     │  ├─ _pydantic_core.cp311-win_amd64.pyd
   │     │  ├─ _pydantic_core.pyi
   │     │  ├─ __init__.py
   │     │  └─ __pycache__
   │     │     ├─ core_schema.cpython-311.pyc
   │     │     └─ __init__.cpython-311.pyc
   │     ├─ pydantic_core-2.41.5.dist-info
   │     │  ├─ INSTALLER
   │     │  ├─ licenses
   │     │  │  └─ LICENSE
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  └─ WHEEL
   │     ├─ pydantic_settings
   │     │  ├─ exceptions.py
   │     │  ├─ main.py
   │     │  ├─ py.typed
   │     │  ├─ sources
   │     │  │  ├─ base.py
   │     │  │  ├─ providers
   │     │  │  │  ├─ aws.py
   │     │  │  │  ├─ azure.py
   │     │  │  │  ├─ cli.py
   │     │  │  │  ├─ dotenv.py
   │     │  │  │  ├─ env.py
   │     │  │  │  ├─ gcp.py
   │     │  │  │  ├─ json.py
   │     │  │  │  ├─ nested_secrets.py
   │     │  │  │  ├─ pyproject.py
   │     │  │  │  ├─ secrets.py
   │     │  │  │  ├─ toml.py
   │     │  │  │  ├─ yaml.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ aws.cpython-311.pyc
   │     │  │  │     ├─ azure.cpython-311.pyc
   │     │  │  │     ├─ cli.cpython-311.pyc
   │     │  │  │     ├─ dotenv.cpython-311.pyc
   │     │  │  │     ├─ env.cpython-311.pyc
   │     │  │  │     ├─ gcp.cpython-311.pyc
   │     │  │  │     ├─ json.cpython-311.pyc
   │     │  │  │     ├─ nested_secrets.cpython-311.pyc
   │     │  │  │     ├─ pyproject.cpython-311.pyc
   │     │  │  │     ├─ secrets.cpython-311.pyc
   │     │  │  │     ├─ toml.cpython-311.pyc
   │     │  │  │     ├─ yaml.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ types.py
   │     │  │  ├─ utils.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ base.cpython-311.pyc
   │     │  │     ├─ types.cpython-311.pyc
   │     │  │     ├─ utils.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ utils.py
   │     │  ├─ version.py
   │     │  ├─ __init__.py
   │     │  └─ __pycache__
   │     │     ├─ exceptions.cpython-311.pyc
   │     │     ├─ main.cpython-311.pyc
   │     │     ├─ utils.cpython-311.pyc
   │     │     ├─ version.cpython-311.pyc
   │     │     └─ __init__.cpython-311.pyc
   │     ├─ pydantic_settings-2.13.1.dist-info
   │     │  ├─ INSTALLER
   │     │  ├─ licenses
   │     │  │  └─ LICENSE
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  ├─ REQUESTED
   │     │  └─ WHEEL
   │     ├─ pydeck
   │     │  ├─ .DS_Store
   │     │  ├─ bindings
   │     │  │  ├─ base_map_provider.py
   │     │  │  ├─ deck.py
   │     │  │  ├─ json_tools.py
   │     │  │  ├─ layer.py
   │     │  │  ├─ light_settings.py
   │     │  │  ├─ map_styles.py
   │     │  │  ├─ view.py
   │     │  │  ├─ view_state.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ base_map_provider.cpython-311.pyc
   │     │  │     ├─ deck.cpython-311.pyc
   │     │  │     ├─ json_tools.cpython-311.pyc
   │     │  │     ├─ layer.cpython-311.pyc
   │     │  │     ├─ light_settings.cpython-311.pyc
   │     │  │     ├─ map_styles.cpython-311.pyc
   │     │  │     ├─ view.cpython-311.pyc
   │     │  │     ├─ view_state.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ data_utils
   │     │  │  ├─ binary_transfer.py
   │     │  │  ├─ color_scales.py
   │     │  │  ├─ type_checking.py
   │     │  │  ├─ viewport_helpers.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ binary_transfer.cpython-311.pyc
   │     │  │     ├─ color_scales.cpython-311.pyc
   │     │  │     ├─ type_checking.cpython-311.pyc
   │     │  │     ├─ viewport_helpers.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ exceptions
   │     │  │  ├─ exceptions.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ exceptions.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ frontend_semver.py
   │     │  ├─ io
   │     │  │  ├─ .DS_Store
   │     │  │  ├─ html.py
   │     │  │  ├─ templates
   │     │  │  │  ├─ index.j2
   │     │  │  │  └─ style.j2
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ html.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ nbextension
   │     │  │  ├─ .DS_Store
   │     │  │  ├─ static
   │     │  │  │  ├─ .DS_Store
   │     │  │  │  ├─ extensionRequires.js
   │     │  │  │  ├─ index.js
   │     │  │  │  └─ index.js.map
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ settings.py
   │     │  ├─ types
   │     │  │  ├─ base.py
   │     │  │  ├─ function.py
   │     │  │  ├─ image.py
   │     │  │  ├─ string.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ base.cpython-311.pyc
   │     │  │     ├─ function.cpython-311.pyc
   │     │  │     ├─ image.cpython-311.pyc
   │     │  │     ├─ string.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ widget
   │     │  │  ├─ debounce.py
   │     │  │  ├─ widget.py
   │     │  │  ├─ _frontend.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ debounce.cpython-311.pyc
   │     │  │     ├─ widget.cpython-311.pyc
   │     │  │     ├─ _frontend.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ _version.py
   │     │  ├─ __init__.py
   │     │  └─ __pycache__
   │     │     ├─ frontend_semver.cpython-311.pyc
   │     │     ├─ settings.cpython-311.pyc
   │     │     ├─ _version.cpython-311.pyc
   │     │     └─ __init__.cpython-311.pyc
   │     ├─ pydeck-0.9.1.dist-info
   │     │  ├─ INSTALLER
   │     │  ├─ LICENSE.txt
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  ├─ top_level.txt
   │     │  └─ WHEEL
   │     ├─ pygments
   │     │  ├─ cmdline.py
   │     │  ├─ console.py
   │     │  ├─ filter.py
   │     │  ├─ filters
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ formatter.py
   │     │  ├─ formatters
   │     │  │  ├─ bbcode.py
   │     │  │  ├─ groff.py
   │     │  │  ├─ html.py
   │     │  │  ├─ img.py
   │     │  │  ├─ irc.py
   │     │  │  ├─ latex.py
   │     │  │  ├─ other.py
   │     │  │  ├─ pangomarkup.py
   │     │  │  ├─ rtf.py
   │     │  │  ├─ svg.py
   │     │  │  ├─ terminal.py
   │     │  │  ├─ terminal256.py
   │     │  │  ├─ _mapping.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ bbcode.cpython-311.pyc
   │     │  │     ├─ groff.cpython-311.pyc
   │     │  │     ├─ html.cpython-311.pyc
   │     │  │     ├─ img.cpython-311.pyc
   │     │  │     ├─ irc.cpython-311.pyc
   │     │  │     ├─ latex.cpython-311.pyc
   │     │  │     ├─ other.cpython-311.pyc
   │     │  │     ├─ pangomarkup.cpython-311.pyc
   │     │  │     ├─ rtf.cpython-311.pyc
   │     │  │     ├─ svg.cpython-311.pyc
   │     │  │     ├─ terminal.cpython-311.pyc
   │     │  │     ├─ terminal256.cpython-311.pyc
   │     │  │     ├─ _mapping.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ lexer.py
   │     │  ├─ lexers
   │     │  │  ├─ actionscript.py
   │     │  │  ├─ ada.py
   │     │  │  ├─ agile.py
   │     │  │  ├─ algebra.py
   │     │  │  ├─ ambient.py
   │     │  │  ├─ amdgpu.py
   │     │  │  ├─ ampl.py
   │     │  │  ├─ apdlexer.py
   │     │  │  ├─ apl.py
   │     │  │  ├─ archetype.py
   │     │  │  ├─ arrow.py
   │     │  │  ├─ arturo.py
   │     │  │  ├─ asc.py
   │     │  │  ├─ asm.py
   │     │  │  ├─ asn1.py
   │     │  │  ├─ automation.py
   │     │  │  ├─ bare.py
   │     │  │  ├─ basic.py
   │     │  │  ├─ bdd.py
   │     │  │  ├─ berry.py
   │     │  │  ├─ bibtex.py
   │     │  │  ├─ blueprint.py
   │     │  │  ├─ boa.py
   │     │  │  ├─ bqn.py
   │     │  │  ├─ business.py
   │     │  │  ├─ capnproto.py
   │     │  │  ├─ carbon.py
   │     │  │  ├─ cddl.py
   │     │  │  ├─ chapel.py
   │     │  │  ├─ clean.py
   │     │  │  ├─ codeql.py
   │     │  │  ├─ comal.py
   │     │  │  ├─ compiled.py
   │     │  │  ├─ configs.py
   │     │  │  ├─ console.py
   │     │  │  ├─ cplint.py
   │     │  │  ├─ crystal.py
   │     │  │  ├─ csound.py
   │     │  │  ├─ css.py
   │     │  │  ├─ c_cpp.py
   │     │  │  ├─ c_like.py
   │     │  │  ├─ d.py
   │     │  │  ├─ dalvik.py
   │     │  │  ├─ data.py
   │     │  │  ├─ dax.py
   │     │  │  ├─ devicetree.py
   │     │  │  ├─ diff.py
   │     │  │  ├─ dns.py
   │     │  │  ├─ dotnet.py
   │     │  │  ├─ dsls.py
   │     │  │  ├─ dylan.py
   │     │  │  ├─ ecl.py
   │     │  │  ├─ eiffel.py
   │     │  │  ├─ elm.py
   │     │  │  ├─ elpi.py
   │     │  │  ├─ email.py
   │     │  │  ├─ erlang.py
   │     │  │  ├─ esoteric.py
   │     │  │  ├─ ezhil.py
   │     │  │  ├─ factor.py
   │     │  │  ├─ fantom.py
   │     │  │  ├─ felix.py
   │     │  │  ├─ fift.py
   │     │  │  ├─ floscript.py
   │     │  │  ├─ forth.py
   │     │  │  ├─ fortran.py
   │     │  │  ├─ foxpro.py
   │     │  │  ├─ freefem.py
   │     │  │  ├─ func.py
   │     │  │  ├─ functional.py
   │     │  │  ├─ futhark.py
   │     │  │  ├─ gcodelexer.py
   │     │  │  ├─ gdscript.py
   │     │  │  ├─ gleam.py
   │     │  │  ├─ go.py
   │     │  │  ├─ grammar_notation.py
   │     │  │  ├─ graph.py
   │     │  │  ├─ graphics.py
   │     │  │  ├─ graphql.py
   │     │  │  ├─ graphviz.py
   │     │  │  ├─ gsql.py
   │     │  │  ├─ hare.py
   │     │  │  ├─ haskell.py
   │     │  │  ├─ haxe.py
   │     │  │  ├─ hdl.py
   │     │  │  ├─ hexdump.py
   │     │  │  ├─ html.py
   │     │  │  ├─ idl.py
   │     │  │  ├─ igor.py
   │     │  │  ├─ inferno.py
   │     │  │  ├─ installers.py
   │     │  │  ├─ int_fiction.py
   │     │  │  ├─ iolang.py
   │     │  │  ├─ j.py
   │     │  │  ├─ javascript.py
   │     │  │  ├─ jmespath.py
   │     │  │  ├─ jslt.py
   │     │  │  ├─ json5.py
   │     │  │  ├─ jsonnet.py
   │     │  │  ├─ jsx.py
   │     │  │  ├─ julia.py
   │     │  │  ├─ jvm.py
   │     │  │  ├─ kuin.py
   │     │  │  ├─ kusto.py
   │     │  │  ├─ ldap.py
   │     │  │  ├─ lean.py
   │     │  │  ├─ lilypond.py
   │     │  │  ├─ lisp.py
   │     │  │  ├─ macaulay2.py
   │     │  │  ├─ make.py
   │     │  │  ├─ maple.py
   │     │  │  ├─ markup.py
   │     │  │  ├─ math.py
   │     │  │  ├─ matlab.py
   │     │  │  ├─ maxima.py
   │     │  │  ├─ meson.py
   │     │  │  ├─ mime.py
   │     │  │  ├─ minecraft.py
   │     │  │  ├─ mips.py
   │     │  │  ├─ ml.py
   │     │  │  ├─ modeling.py
   │     │  │  ├─ modula2.py
   │     │  │  ├─ mojo.py
   │     │  │  ├─ monte.py
   │     │  │  ├─ mosel.py
   │     │  │  ├─ ncl.py
   │     │  │  ├─ nimrod.py
   │     │  │  ├─ nit.py
   │     │  │  ├─ nix.py
   │     │  │  ├─ numbair.py
   │     │  │  ├─ oberon.py
   │     │  │  ├─ objective.py
   │     │  │  ├─ ooc.py
   │     │  │  ├─ openscad.py
   │     │  │  ├─ other.py
   │     │  │  ├─ parasail.py
   │     │  │  ├─ parsers.py
   │     │  │  ├─ pascal.py
   │     │  │  ├─ pawn.py
   │     │  │  ├─ pddl.py
   │     │  │  ├─ perl.py
   │     │  │  ├─ phix.py
   │     │  │  ├─ php.py
   │     │  │  ├─ pointless.py
   │     │  │  ├─ pony.py
   │     │  │  ├─ praat.py
   │     │  │  ├─ procfile.py
   │     │  │  ├─ prolog.py
   │     │  │  ├─ promql.py
   │     │  │  ├─ prql.py
   │     │  │  ├─ ptx.py
   │     │  │  ├─ python.py
   │     │  │  ├─ q.py
   │     │  │  ├─ qlik.py
   │     │  │  ├─ qvt.py
   │     │  │  ├─ r.py
   │     │  │  ├─ rdf.py
   │     │  │  ├─ rebol.py
   │     │  │  ├─ rego.py
   │     │  │  ├─ rell.py
   │     │  │  ├─ resource.py
   │     │  │  ├─ ride.py
   │     │  │  ├─ rita.py
   │     │  │  ├─ rnc.py
   │     │  │  ├─ roboconf.py
   │     │  │  ├─ robotframework.py
   │     │  │  ├─ ruby.py
   │     │  │  ├─ rust.py
   │     │  │  ├─ sas.py
   │     │  │  ├─ savi.py
   │     │  │  ├─ scdoc.py
   │     │  │  ├─ scripting.py
   │     │  │  ├─ sgf.py
   │     │  │  ├─ shell.py
   │     │  │  ├─ sieve.py
   │     │  │  ├─ slash.py
   │     │  │  ├─ smalltalk.py
   │     │  │  ├─ smithy.py
   │     │  │  ├─ smv.py
   │     │  │  ├─ snobol.py
   │     │  │  ├─ solidity.py
   │     │  │  ├─ soong.py
   │     │  │  ├─ sophia.py
   │     │  │  ├─ special.py
   │     │  │  ├─ spice.py
   │     │  │  ├─ sql.py
   │     │  │  ├─ srcinfo.py
   │     │  │  ├─ stata.py
   │     │  │  ├─ supercollider.py
   │     │  │  ├─ tablegen.py
   │     │  │  ├─ tact.py
   │     │  │  ├─ tal.py
   │     │  │  ├─ tcl.py
   │     │  │  ├─ teal.py
   │     │  │  ├─ templates.py
   │     │  │  ├─ teraterm.py
   │     │  │  ├─ testing.py
   │     │  │  ├─ text.py
   │     │  │  ├─ textedit.py
   │     │  │  ├─ textfmts.py
   │     │  │  ├─ theorem.py
   │     │  │  ├─ thingsdb.py
   │     │  │  ├─ tlb.py
   │     │  │  ├─ tls.py
   │     │  │  ├─ tnt.py
   │     │  │  ├─ trafficscript.py
   │     │  │  ├─ typoscript.py
   │     │  │  ├─ typst.py
   │     │  │  ├─ ul4.py
   │     │  │  ├─ unicon.py
   │     │  │  ├─ urbi.py
   │     │  │  ├─ usd.py
   │     │  │  ├─ varnish.py
   │     │  │  ├─ verification.py
   │     │  │  ├─ verifpal.py
   │     │  │  ├─ vip.py
   │     │  │  ├─ vyper.py
   │     │  │  ├─ web.py
   │     │  │  ├─ webassembly.py
   │     │  │  ├─ webidl.py
   │     │  │  ├─ webmisc.py
   │     │  │  ├─ wgsl.py
   │     │  │  ├─ whiley.py
   │     │  │  ├─ wowtoc.py
   │     │  │  ├─ wren.py
   │     │  │  ├─ x10.py
   │     │  │  ├─ xorg.py
   │     │  │  ├─ yang.py
   │     │  │  ├─ yara.py
   │     │  │  ├─ zig.py
   │     │  │  ├─ _ada_builtins.py
   │     │  │  ├─ _asy_builtins.py
   │     │  │  ├─ _cl_builtins.py
   │     │  │  ├─ _cocoa_builtins.py
   │     │  │  ├─ _csound_builtins.py
   │     │  │  ├─ _css_builtins.py
   │     │  │  ├─ _googlesql_builtins.py
   │     │  │  ├─ _julia_builtins.py
   │     │  │  ├─ _lasso_builtins.py
   │     │  │  ├─ _lilypond_builtins.py
   │     │  │  ├─ _luau_builtins.py
   │     │  │  ├─ _lua_builtins.py
   │     │  │  ├─ _mapping.py
   │     │  │  ├─ _mql_builtins.py
   │     │  │  ├─ _mysql_builtins.py
   │     │  │  ├─ _openedge_builtins.py
   │     │  │  ├─ _php_builtins.py
   │     │  │  ├─ _postgres_builtins.py
   │     │  │  ├─ _qlik_builtins.py
   │     │  │  ├─ _scheme_builtins.py
   │     │  │  ├─ _scilab_builtins.py
   │     │  │  ├─ _sourcemod_builtins.py
   │     │  │  ├─ _sql_builtins.py
   │     │  │  ├─ _stan_builtins.py
   │     │  │  ├─ _stata_builtins.py
   │     │  │  ├─ _tsql_builtins.py
   │     │  │  ├─ _usd_builtins.py
   │     │  │  ├─ _vbscript_builtins.py
   │     │  │  ├─ _vim_builtins.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ actionscript.cpython-311.pyc
   │     │  │     ├─ ada.cpython-311.pyc
   │     │  │     ├─ agile.cpython-311.pyc
   │     │  │     ├─ algebra.cpython-311.pyc
   │     │  │     ├─ ambient.cpython-311.pyc
   │     │  │     ├─ amdgpu.cpython-311.pyc
   │     │  │     ├─ ampl.cpython-311.pyc
   │     │  │     ├─ apdlexer.cpython-311.pyc
   │     │  │     ├─ apl.cpython-311.pyc
   │     │  │     ├─ archetype.cpython-311.pyc
   │     │  │     ├─ arrow.cpython-311.pyc
   │     │  │     ├─ arturo.cpython-311.pyc
   │     │  │     ├─ asc.cpython-311.pyc
   │     │  │     ├─ asm.cpython-311.pyc
   │     │  │     ├─ asn1.cpython-311.pyc
   │     │  │     ├─ automation.cpython-311.pyc
   │     │  │     ├─ bare.cpython-311.pyc
   │     │  │     ├─ basic.cpython-311.pyc
   │     │  │     ├─ bdd.cpython-311.pyc
   │     │  │     ├─ berry.cpython-311.pyc
   │     │  │     ├─ bibtex.cpython-311.pyc
   │     │  │     ├─ blueprint.cpython-311.pyc
   │     │  │     ├─ boa.cpython-311.pyc
   │     │  │     ├─ bqn.cpython-311.pyc
   │     │  │     ├─ business.cpython-311.pyc
   │     │  │     ├─ capnproto.cpython-311.pyc
   │     │  │     ├─ carbon.cpython-311.pyc
   │     │  │     ├─ cddl.cpython-311.pyc
   │     │  │     ├─ chapel.cpython-311.pyc
   │     │  │     ├─ clean.cpython-311.pyc
   │     │  │     ├─ codeql.cpython-311.pyc
   │     │  │     ├─ comal.cpython-311.pyc
   │     │  │     ├─ compiled.cpython-311.pyc
   │     │  │     ├─ configs.cpython-311.pyc
   │     │  │     ├─ console.cpython-311.pyc
   │     │  │     ├─ cplint.cpython-311.pyc
   │     │  │     ├─ crystal.cpython-311.pyc
   │     │  │     ├─ csound.cpython-311.pyc
   │     │  │     ├─ css.cpython-311.pyc
   │     │  │     ├─ c_cpp.cpython-311.pyc
   │     │  │     ├─ c_like.cpython-311.pyc
   │     │  │     ├─ d.cpython-311.pyc
   │     │  │     ├─ dalvik.cpython-311.pyc
   │     │  │     ├─ data.cpython-311.pyc
   │     │  │     ├─ dax.cpython-311.pyc
   │     │  │     ├─ devicetree.cpython-311.pyc
   │     │  │     ├─ diff.cpython-311.pyc
   │     │  │     ├─ dns.cpython-311.pyc
   │     │  │     ├─ dotnet.cpython-311.pyc
   │     │  │     ├─ dsls.cpython-311.pyc
   │     │  │     ├─ dylan.cpython-311.pyc
   │     │  │     ├─ ecl.cpython-311.pyc
   │     │  │     ├─ eiffel.cpython-311.pyc
   │     │  │     ├─ elm.cpython-311.pyc
   │     │  │     ├─ elpi.cpython-311.pyc
   │     │  │     ├─ email.cpython-311.pyc
   │     │  │     ├─ erlang.cpython-311.pyc
   │     │  │     ├─ esoteric.cpython-311.pyc
   │     │  │     ├─ ezhil.cpython-311.pyc
   │     │  │     ├─ factor.cpython-311.pyc
   │     │  │     ├─ fantom.cpython-311.pyc
   │     │  │     ├─ felix.cpython-311.pyc
   │     │  │     ├─ fift.cpython-311.pyc
   │     │  │     ├─ floscript.cpython-311.pyc
   │     │  │     ├─ forth.cpython-311.pyc
   │     │  │     ├─ fortran.cpython-311.pyc
   │     │  │     ├─ foxpro.cpython-311.pyc
   │     │  │     ├─ freefem.cpython-311.pyc
   │     │  │     ├─ func.cpython-311.pyc
   │     │  │     ├─ functional.cpython-311.pyc
   │     │  │     ├─ futhark.cpython-311.pyc
   │     │  │     ├─ gcodelexer.cpython-311.pyc
   │     │  │     ├─ gdscript.cpython-311.pyc
   │     │  │     ├─ gleam.cpython-311.pyc
   │     │  │     ├─ go.cpython-311.pyc
   │     │  │     ├─ grammar_notation.cpython-311.pyc
   │     │  │     ├─ graph.cpython-311.pyc
   │     │  │     ├─ graphics.cpython-311.pyc
   │     │  │     ├─ graphql.cpython-311.pyc
   │     │  │     ├─ graphviz.cpython-311.pyc
   │     │  │     ├─ gsql.cpython-311.pyc
   │     │  │     ├─ hare.cpython-311.pyc
   │     │  │     ├─ haskell.cpython-311.pyc
   │     │  │     ├─ haxe.cpython-311.pyc
   │     │  │     ├─ hdl.cpython-311.pyc
   │     │  │     ├─ hexdump.cpython-311.pyc
   │     │  │     ├─ html.cpython-311.pyc
   │     │  │     ├─ idl.cpython-311.pyc
   │     │  │     ├─ igor.cpython-311.pyc
   │     │  │     ├─ inferno.cpython-311.pyc
   │     │  │     ├─ installers.cpython-311.pyc
   │     │  │     ├─ int_fiction.cpython-311.pyc
   │     │  │     ├─ iolang.cpython-311.pyc
   │     │  │     ├─ j.cpython-311.pyc
   │     │  │     ├─ javascript.cpython-311.pyc
   │     │  │     ├─ jmespath.cpython-311.pyc
   │     │  │     ├─ jslt.cpython-311.pyc
   │     │  │     ├─ json5.cpython-311.pyc
   │     │  │     ├─ jsonnet.cpython-311.pyc
   │     │  │     ├─ jsx.cpython-311.pyc
   │     │  │     ├─ julia.cpython-311.pyc
   │     │  │     ├─ jvm.cpython-311.pyc
   │     │  │     ├─ kuin.cpython-311.pyc
   │     │  │     ├─ kusto.cpython-311.pyc
   │     │  │     ├─ ldap.cpython-311.pyc
   │     │  │     ├─ lean.cpython-311.pyc
   │     │  │     ├─ lilypond.cpython-311.pyc
   │     │  │     ├─ lisp.cpython-311.pyc
   │     │  │     ├─ macaulay2.cpython-311.pyc
   │     │  │     ├─ make.cpython-311.pyc
   │     │  │     ├─ maple.cpython-311.pyc
   │     │  │     ├─ markup.cpython-311.pyc
   │     │  │     ├─ math.cpython-311.pyc
   │     │  │     ├─ matlab.cpython-311.pyc
   │     │  │     ├─ maxima.cpython-311.pyc
   │     │  │     ├─ meson.cpython-311.pyc
   │     │  │     ├─ mime.cpython-311.pyc
   │     │  │     ├─ minecraft.cpython-311.pyc
   │     │  │     ├─ mips.cpython-311.pyc
   │     │  │     ├─ ml.cpython-311.pyc
   │     │  │     ├─ modeling.cpython-311.pyc
   │     │  │     ├─ modula2.cpython-311.pyc
   │     │  │     ├─ mojo.cpython-311.pyc
   │     │  │     ├─ monte.cpython-311.pyc
   │     │  │     ├─ mosel.cpython-311.pyc
   │     │  │     ├─ ncl.cpython-311.pyc
   │     │  │     ├─ nimrod.cpython-311.pyc
   │     │  │     ├─ nit.cpython-311.pyc
   │     │  │     ├─ nix.cpython-311.pyc
   │     │  │     ├─ numbair.cpython-311.pyc
   │     │  │     ├─ oberon.cpython-311.pyc
   │     │  │     ├─ objective.cpython-311.pyc
   │     │  │     ├─ ooc.cpython-311.pyc
   │     │  │     ├─ openscad.cpython-311.pyc
   │     │  │     ├─ other.cpython-311.pyc
   │     │  │     ├─ parasail.cpython-311.pyc
   │     │  │     ├─ parsers.cpython-311.pyc
   │     │  │     ├─ pascal.cpython-311.pyc
   │     │  │     ├─ pawn.cpython-311.pyc
   │     │  │     ├─ pddl.cpython-311.pyc
   │     │  │     ├─ perl.cpython-311.pyc
   │     │  │     ├─ phix.cpython-311.pyc
   │     │  │     ├─ php.cpython-311.pyc
   │     │  │     ├─ pointless.cpython-311.pyc
   │     │  │     ├─ pony.cpython-311.pyc
   │     │  │     ├─ praat.cpython-311.pyc
   │     │  │     ├─ procfile.cpython-311.pyc
   │     │  │     ├─ prolog.cpython-311.pyc
   │     │  │     ├─ promql.cpython-311.pyc
   │     │  │     ├─ prql.cpython-311.pyc
   │     │  │     ├─ ptx.cpython-311.pyc
   │     │  │     ├─ python.cpython-311.pyc
   │     │  │     ├─ q.cpython-311.pyc
   │     │  │     ├─ qlik.cpython-311.pyc
   │     │  │     ├─ qvt.cpython-311.pyc
   │     │  │     ├─ r.cpython-311.pyc
   │     │  │     ├─ rdf.cpython-311.pyc
   │     │  │     ├─ rebol.cpython-311.pyc
   │     │  │     ├─ rego.cpython-311.pyc
   │     │  │     ├─ rell.cpython-311.pyc
   │     │  │     ├─ resource.cpython-311.pyc
   │     │  │     ├─ ride.cpython-311.pyc
   │     │  │     ├─ rita.cpython-311.pyc
   │     │  │     ├─ rnc.cpython-311.pyc
   │     │  │     ├─ roboconf.cpython-311.pyc
   │     │  │     ├─ robotframework.cpython-311.pyc
   │     │  │     ├─ ruby.cpython-311.pyc
   │     │  │     ├─ rust.cpython-311.pyc
   │     │  │     ├─ sas.cpython-311.pyc
   │     │  │     ├─ savi.cpython-311.pyc
   │     │  │     ├─ scdoc.cpython-311.pyc
   │     │  │     ├─ scripting.cpython-311.pyc
   │     │  │     ├─ sgf.cpython-311.pyc
   │     │  │     ├─ shell.cpython-311.pyc
   │     │  │     ├─ sieve.cpython-311.pyc
   │     │  │     ├─ slash.cpython-311.pyc
   │     │  │     ├─ smalltalk.cpython-311.pyc
   │     │  │     ├─ smithy.cpython-311.pyc
   │     │  │     ├─ smv.cpython-311.pyc
   │     │  │     ├─ snobol.cpython-311.pyc
   │     │  │     ├─ solidity.cpython-311.pyc
   │     │  │     ├─ soong.cpython-311.pyc
   │     │  │     ├─ sophia.cpython-311.pyc
   │     │  │     ├─ special.cpython-311.pyc
   │     │  │     ├─ spice.cpython-311.pyc
   │     │  │     ├─ sql.cpython-311.pyc
   │     │  │     ├─ srcinfo.cpython-311.pyc
   │     │  │     ├─ stata.cpython-311.pyc
   │     │  │     ├─ supercollider.cpython-311.pyc
   │     │  │     ├─ tablegen.cpython-311.pyc
   │     │  │     ├─ tact.cpython-311.pyc
   │     │  │     ├─ tal.cpython-311.pyc
   │     │  │     ├─ tcl.cpython-311.pyc
   │     │  │     ├─ teal.cpython-311.pyc
   │     │  │     ├─ templates.cpython-311.pyc
   │     │  │     ├─ teraterm.cpython-311.pyc
   │     │  │     ├─ testing.cpython-311.pyc
   │     │  │     ├─ text.cpython-311.pyc
   │     │  │     ├─ textedit.cpython-311.pyc
   │     │  │     ├─ textfmts.cpython-311.pyc
   │     │  │     ├─ theorem.cpython-311.pyc
   │     │  │     ├─ thingsdb.cpython-311.pyc
   │     │  │     ├─ tlb.cpython-311.pyc
   │     │  │     ├─ tls.cpython-311.pyc
   │     │  │     ├─ tnt.cpython-311.pyc
   │     │  │     ├─ trafficscript.cpython-311.pyc
   │     │  │     ├─ typoscript.cpython-311.pyc
   │     │  │     ├─ typst.cpython-311.pyc
   │     │  │     ├─ ul4.cpython-311.pyc
   │     │  │     ├─ unicon.cpython-311.pyc
   │     │  │     ├─ urbi.cpython-311.pyc
   │     │  │     ├─ usd.cpython-311.pyc
   │     │  │     ├─ varnish.cpython-311.pyc
   │     │  │     ├─ verification.cpython-311.pyc
   │     │  │     ├─ verifpal.cpython-311.pyc
   │     │  │     ├─ vip.cpython-311.pyc
   │     │  │     ├─ vyper.cpython-311.pyc
   │     │  │     ├─ web.cpython-311.pyc
   │     │  │     ├─ webassembly.cpython-311.pyc
   │     │  │     ├─ webidl.cpython-311.pyc
   │     │  │     ├─ webmisc.cpython-311.pyc
   │     │  │     ├─ wgsl.cpython-311.pyc
   │     │  │     ├─ whiley.cpython-311.pyc
   │     │  │     ├─ wowtoc.cpython-311.pyc
   │     │  │     ├─ wren.cpython-311.pyc
   │     │  │     ├─ x10.cpython-311.pyc
   │     │  │     ├─ xorg.cpython-311.pyc
   │     │  │     ├─ yang.cpython-311.pyc
   │     │  │     ├─ yara.cpython-311.pyc
   │     │  │     ├─ zig.cpython-311.pyc
   │     │  │     ├─ _ada_builtins.cpython-311.pyc
   │     │  │     ├─ _asy_builtins.cpython-311.pyc
   │     │  │     ├─ _cl_builtins.cpython-311.pyc
   │     │  │     ├─ _cocoa_builtins.cpython-311.pyc
   │     │  │     ├─ _csound_builtins.cpython-311.pyc
   │     │  │     ├─ _css_builtins.cpython-311.pyc
   │     │  │     ├─ _googlesql_builtins.cpython-311.pyc
   │     │  │     ├─ _julia_builtins.cpython-311.pyc
   │     │  │     ├─ _lasso_builtins.cpython-311.pyc
   │     │  │     ├─ _lilypond_builtins.cpython-311.pyc
   │     │  │     ├─ _luau_builtins.cpython-311.pyc
   │     │  │     ├─ _lua_builtins.cpython-311.pyc
   │     │  │     ├─ _mapping.cpython-311.pyc
   │     │  │     ├─ _mql_builtins.cpython-311.pyc
   │     │  │     ├─ _mysql_builtins.cpython-311.pyc
   │     │  │     ├─ _openedge_builtins.cpython-311.pyc
   │     │  │     ├─ _php_builtins.cpython-311.pyc
   │     │  │     ├─ _postgres_builtins.cpython-311.pyc
   │     │  │     ├─ _qlik_builtins.cpython-311.pyc
   │     │  │     ├─ _scheme_builtins.cpython-311.pyc
   │     │  │     ├─ _scilab_builtins.cpython-311.pyc
   │     │  │     ├─ _sourcemod_builtins.cpython-311.pyc
   │     │  │     ├─ _sql_builtins.cpython-311.pyc
   │     │  │     ├─ _stan_builtins.cpython-311.pyc
   │     │  │     ├─ _stata_builtins.cpython-311.pyc
   │     │  │     ├─ _tsql_builtins.cpython-311.pyc
   │     │  │     ├─ _usd_builtins.cpython-311.pyc
   │     │  │     ├─ _vbscript_builtins.cpython-311.pyc
   │     │  │     ├─ _vim_builtins.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ modeline.py
   │     │  ├─ plugin.py
   │     │  ├─ regexopt.py
   │     │  ├─ scanner.py
   │     │  ├─ sphinxext.py
   │     │  ├─ style.py
   │     │  ├─ styles
   │     │  │  ├─ abap.py
   │     │  │  ├─ algol.py
   │     │  │  ├─ algol_nu.py
   │     │  │  ├─ arduino.py
   │     │  │  ├─ autumn.py
   │     │  │  ├─ borland.py
   │     │  │  ├─ bw.py
   │     │  │  ├─ coffee.py
   │     │  │  ├─ colorful.py
   │     │  │  ├─ default.py
   │     │  │  ├─ dracula.py
   │     │  │  ├─ emacs.py
   │     │  │  ├─ friendly.py
   │     │  │  ├─ friendly_grayscale.py
   │     │  │  ├─ fruity.py
   │     │  │  ├─ gh_dark.py
   │     │  │  ├─ gruvbox.py
   │     │  │  ├─ igor.py
   │     │  │  ├─ inkpot.py
   │     │  │  ├─ lightbulb.py
   │     │  │  ├─ lilypond.py
   │     │  │  ├─ lovelace.py
   │     │  │  ├─ manni.py
   │     │  │  ├─ material.py
   │     │  │  ├─ monokai.py
   │     │  │  ├─ murphy.py
   │     │  │  ├─ native.py
   │     │  │  ├─ nord.py
   │     │  │  ├─ onedark.py
   │     │  │  ├─ paraiso_dark.py
   │     │  │  ├─ paraiso_light.py
   │     │  │  ├─ pastie.py
   │     │  │  ├─ perldoc.py
   │     │  │  ├─ rainbow_dash.py
   │     │  │  ├─ rrt.py
   │     │  │  ├─ sas.py
   │     │  │  ├─ solarized.py
   │     │  │  ├─ staroffice.py
   │     │  │  ├─ stata_dark.py
   │     │  │  ├─ stata_light.py
   │     │  │  ├─ tango.py
   │     │  │  ├─ trac.py
   │     │  │  ├─ vim.py
   │     │  │  ├─ vs.py
   │     │  │  ├─ xcode.py
   │     │  │  ├─ zenburn.py
   │     │  │  ├─ _mapping.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ abap.cpython-311.pyc
   │     │  │     ├─ algol.cpython-311.pyc
   │     │  │     ├─ algol_nu.cpython-311.pyc
   │     │  │     ├─ arduino.cpython-311.pyc
   │     │  │     ├─ autumn.cpython-311.pyc
   │     │  │     ├─ borland.cpython-311.pyc
   │     │  │     ├─ bw.cpython-311.pyc
   │     │  │     ├─ coffee.cpython-311.pyc
   │     │  │     ├─ colorful.cpython-311.pyc
   │     │  │     ├─ default.cpython-311.pyc
   │     │  │     ├─ dracula.cpython-311.pyc
   │     │  │     ├─ emacs.cpython-311.pyc
   │     │  │     ├─ friendly.cpython-311.pyc
   │     │  │     ├─ friendly_grayscale.cpython-311.pyc
   │     │  │     ├─ fruity.cpython-311.pyc
   │     │  │     ├─ gh_dark.cpython-311.pyc
   │     │  │     ├─ gruvbox.cpython-311.pyc
   │     │  │     ├─ igor.cpython-311.pyc
   │     │  │     ├─ inkpot.cpython-311.pyc
   │     │  │     ├─ lightbulb.cpython-311.pyc
   │     │  │     ├─ lilypond.cpython-311.pyc
   │     │  │     ├─ lovelace.cpython-311.pyc
   │     │  │     ├─ manni.cpython-311.pyc
   │     │  │     ├─ material.cpython-311.pyc
   │     │  │     ├─ monokai.cpython-311.pyc
   │     │  │     ├─ murphy.cpython-311.pyc
   │     │  │     ├─ native.cpython-311.pyc
   │     │  │     ├─ nord.cpython-311.pyc
   │     │  │     ├─ onedark.cpython-311.pyc
   │     │  │     ├─ paraiso_dark.cpython-311.pyc
   │     │  │     ├─ paraiso_light.cpython-311.pyc
   │     │  │     ├─ pastie.cpython-311.pyc
   │     │  │     ├─ perldoc.cpython-311.pyc
   │     │  │     ├─ rainbow_dash.cpython-311.pyc
   │     │  │     ├─ rrt.cpython-311.pyc
   │     │  │     ├─ sas.cpython-311.pyc
   │     │  │     ├─ solarized.cpython-311.pyc
   │     │  │     ├─ staroffice.cpython-311.pyc
   │     │  │     ├─ stata_dark.cpython-311.pyc
   │     │  │     ├─ stata_light.cpython-311.pyc
   │     │  │     ├─ tango.cpython-311.pyc
   │     │  │     ├─ trac.cpython-311.pyc
   │     │  │     ├─ vim.cpython-311.pyc
   │     │  │     ├─ vs.cpython-311.pyc
   │     │  │     ├─ xcode.cpython-311.pyc
   │     │  │     ├─ zenburn.cpython-311.pyc
   │     │  │     ├─ _mapping.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ token.py
   │     │  ├─ unistring.py
   │     │  ├─ util.py
   │     │  ├─ __init__.py
   │     │  ├─ __main__.py
   │     │  └─ __pycache__
   │     │     ├─ cmdline.cpython-311.pyc
   │     │     ├─ console.cpython-311.pyc
   │     │     ├─ filter.cpython-311.pyc
   │     │     ├─ formatter.cpython-311.pyc
   │     │     ├─ lexer.cpython-311.pyc
   │     │     ├─ modeline.cpython-311.pyc
   │     │     ├─ plugin.cpython-311.pyc
   │     │     ├─ regexopt.cpython-311.pyc
   │     │     ├─ scanner.cpython-311.pyc
   │     │     ├─ sphinxext.cpython-311.pyc
   │     │     ├─ style.cpython-311.pyc
   │     │     ├─ token.cpython-311.pyc
   │     │     ├─ unistring.cpython-311.pyc
   │     │     ├─ util.cpython-311.pyc
   │     │     ├─ __init__.cpython-311.pyc
   │     │     └─ __main__.cpython-311.pyc
   │     ├─ pygments-2.20.0.dist-info
   │     │  ├─ entry_points.txt
   │     │  ├─ INSTALLER
   │     │  ├─ licenses
   │     │  │  ├─ AUTHORS
   │     │  │  └─ LICENSE
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  └─ WHEEL
   │     ├─ pypika
   │     │  ├─ analytics.py
   │     │  ├─ clickhouse
   │     │  │  ├─ array.py
   │     │  │  ├─ condition.py
   │     │  │  ├─ dates_and_times.py
   │     │  │  ├─ nullable_arg.py
   │     │  │  ├─ search_string.py
   │     │  │  ├─ type_conversion.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ array.cpython-311.pyc
   │     │  │     ├─ condition.cpython-311.pyc
   │     │  │     ├─ dates_and_times.cpython-311.pyc
   │     │  │     ├─ nullable_arg.cpython-311.pyc
   │     │  │     ├─ search_string.cpython-311.pyc
   │     │  │     ├─ type_conversion.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ dialects.py
   │     │  ├─ enums.py
   │     │  ├─ functions.py
   │     │  ├─ pseudocolumns.py
   │     │  ├─ py.typed
   │     │  ├─ queries.py
   │     │  ├─ terms.py
   │     │  ├─ utils.py
   │     │  ├─ __init__.py
   │     │  └─ __pycache__
   │     │     ├─ analytics.cpython-311.pyc
   │     │     ├─ dialects.cpython-311.pyc
   │     │     ├─ enums.cpython-311.pyc
   │     │     ├─ functions.cpython-311.pyc
   │     │     ├─ pseudocolumns.cpython-311.pyc
   │     │     ├─ queries.cpython-311.pyc
   │     │     ├─ terms.cpython-311.pyc
   │     │     ├─ utils.cpython-311.pyc
   │     │     └─ __init__.cpython-311.pyc
   │     ├─ pypika-0.51.1.dist-info
   │     │  ├─ INSTALLER
   │     │  ├─ licenses
   │     │  │  └─ LICENSE.txt
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  ├─ top_level.txt
   │     │  └─ WHEEL
   │     ├─ pyproject_hooks
   │     │  ├─ py.typed
   │     │  ├─ _impl.py
   │     │  ├─ _in_process
   │     │  │  ├─ _in_process.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ _in_process.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ __init__.py
   │     │  └─ __pycache__
   │     │     ├─ _impl.cpython-311.pyc
   │     │     └─ __init__.cpython-311.pyc
   │     ├─ pyproject_hooks-1.2.0.dist-info
   │     │  ├─ INSTALLER
   │     │  ├─ LICENSE
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  └─ WHEEL
   │     ├─ python_dateutil-2.9.0.post0.dist-info
   │     │  ├─ INSTALLER
   │     │  ├─ LICENSE
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  ├─ top_level.txt
   │     │  ├─ WHEEL
   │     │  └─ zip-safe
   │     ├─ python_dotenv-1.2.2.dist-info
   │     │  ├─ entry_points.txt
   │     │  ├─ INSTALLER
   │     │  ├─ licenses
   │     │  │  └─ LICENSE
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  ├─ REQUESTED
   │     │  ├─ top_level.txt
   │     │  └─ WHEEL
   │     ├─ pyyaml-6.0.3.dist-info
   │     │  ├─ INSTALLER
   │     │  ├─ licenses
   │     │  │  └─ LICENSE
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  ├─ top_level.txt
   │     │  └─ WHEEL
   │     ├─ referencing
   │     │  ├─ exceptions.py
   │     │  ├─ jsonschema.py
   │     │  ├─ py.typed
   │     │  ├─ retrieval.py
   │     │  ├─ tests
   │     │  │  ├─ test_core.py
   │     │  │  ├─ test_exceptions.py
   │     │  │  ├─ test_jsonschema.py
   │     │  │  ├─ test_referencing_suite.py
   │     │  │  ├─ test_retrieval.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ test_core.cpython-311.pyc
   │     │  │     ├─ test_exceptions.cpython-311.pyc
   │     │  │     ├─ test_jsonschema.cpython-311.pyc
   │     │  │     ├─ test_referencing_suite.cpython-311.pyc
   │     │  │     ├─ test_retrieval.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ typing.py
   │     │  ├─ _attrs.py
   │     │  ├─ _attrs.pyi
   │     │  ├─ _core.py
   │     │  ├─ __init__.py
   │     │  └─ __pycache__
   │     │     ├─ exceptions.cpython-311.pyc
   │     │     ├─ jsonschema.cpython-311.pyc
   │     │     ├─ retrieval.cpython-311.pyc
   │     │     ├─ typing.cpython-311.pyc
   │     │     ├─ _attrs.cpython-311.pyc
   │     │     ├─ _core.cpython-311.pyc
   │     │     └─ __init__.cpython-311.pyc
   │     ├─ referencing-0.37.0.dist-info
   │     │  ├─ INSTALLER
   │     │  ├─ licenses
   │     │  │  └─ COPYING
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  └─ WHEEL
   │     ├─ requests
   │     │  ├─ adapters.py
   │     │  ├─ api.py
   │     │  ├─ auth.py
   │     │  ├─ certs.py
   │     │  ├─ compat.py
   │     │  ├─ cookies.py
   │     │  ├─ exceptions.py
   │     │  ├─ help.py
   │     │  ├─ hooks.py
   │     │  ├─ models.py
   │     │  ├─ packages.py
   │     │  ├─ sessions.py
   │     │  ├─ status_codes.py
   │     │  ├─ structures.py
   │     │  ├─ utils.py
   │     │  ├─ _internal_utils.py
   │     │  ├─ __init__.py
   │     │  ├─ __pycache__
   │     │  │  ├─ adapters.cpython-311.pyc
   │     │  │  ├─ api.cpython-311.pyc
   │     │  │  ├─ auth.cpython-311.pyc
   │     │  │  ├─ certs.cpython-311.pyc
   │     │  │  ├─ compat.cpython-311.pyc
   │     │  │  ├─ cookies.cpython-311.pyc
   │     │  │  ├─ exceptions.cpython-311.pyc
   │     │  │  ├─ help.cpython-311.pyc
   │     │  │  ├─ hooks.cpython-311.pyc
   │     │  │  ├─ models.cpython-311.pyc
   │     │  │  ├─ packages.cpython-311.pyc
   │     │  │  ├─ sessions.cpython-311.pyc
   │     │  │  ├─ status_codes.cpython-311.pyc
   │     │  │  ├─ structures.cpython-311.pyc
   │     │  │  ├─ utils.cpython-311.pyc
   │     │  │  ├─ _internal_utils.cpython-311.pyc
   │     │  │  ├─ __init__.cpython-311.pyc
   │     │  │  └─ __version__.cpython-311.pyc
   │     │  └─ __version__.py
   │     ├─ requests-2.33.1.dist-info
   │     │  ├─ INSTALLER
   │     │  ├─ licenses
   │     │  │  ├─ LICENSE
   │     │  │  └─ NOTICE
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  ├─ top_level.txt
   │     │  └─ WHEEL
   │     ├─ requests_oauthlib
   │     │  ├─ compliance_fixes
   │     │  │  ├─ douban.py
   │     │  │  ├─ ebay.py
   │     │  │  ├─ facebook.py
   │     │  │  ├─ fitbit.py
   │     │  │  ├─ instagram.py
   │     │  │  ├─ mailchimp.py
   │     │  │  ├─ plentymarkets.py
   │     │  │  ├─ slack.py
   │     │  │  ├─ weibo.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ douban.cpython-311.pyc
   │     │  │     ├─ ebay.cpython-311.pyc
   │     │  │     ├─ facebook.cpython-311.pyc
   │     │  │     ├─ fitbit.cpython-311.pyc
   │     │  │     ├─ instagram.cpython-311.pyc
   │     │  │     ├─ mailchimp.cpython-311.pyc
   │     │  │     ├─ plentymarkets.cpython-311.pyc
   │     │  │     ├─ slack.cpython-311.pyc
   │     │  │     ├─ weibo.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ oauth1_auth.py
   │     │  ├─ oauth1_session.py
   │     │  ├─ oauth2_auth.py
   │     │  ├─ oauth2_session.py
   │     │  ├─ __init__.py
   │     │  └─ __pycache__
   │     │     ├─ oauth1_auth.cpython-311.pyc
   │     │     ├─ oauth1_session.cpython-311.pyc
   │     │     ├─ oauth2_auth.cpython-311.pyc
   │     │     ├─ oauth2_session.cpython-311.pyc
   │     │     └─ __init__.cpython-311.pyc
   │     ├─ requests_oauthlib-2.0.0.dist-info
   │     │  ├─ INSTALLER
   │     │  ├─ LICENSE
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  ├─ top_level.txt
   │     │  └─ WHEEL
   │     ├─ rich
   │     │  ├─ abc.py
   │     │  ├─ align.py
   │     │  ├─ ansi.py
   │     │  ├─ bar.py
   │     │  ├─ box.py
   │     │  ├─ cells.py
   │     │  ├─ color.py
   │     │  ├─ color_triplet.py
   │     │  ├─ columns.py
   │     │  ├─ console.py
   │     │  ├─ constrain.py
   │     │  ├─ containers.py
   │     │  ├─ control.py
   │     │  ├─ default_styles.py
   │     │  ├─ diagnose.py
   │     │  ├─ emoji.py
   │     │  ├─ errors.py
   │     │  ├─ filesize.py
   │     │  ├─ file_proxy.py
   │     │  ├─ highlighter.py
   │     │  ├─ json.py
   │     │  ├─ jupyter.py
   │     │  ├─ layout.py
   │     │  ├─ live.py
   │     │  ├─ live_render.py
   │     │  ├─ logging.py
   │     │  ├─ markdown.py
   │     │  ├─ markup.py
   │     │  ├─ measure.py
   │     │  ├─ padding.py
   │     │  ├─ pager.py
   │     │  ├─ palette.py
   │     │  ├─ panel.py
   │     │  ├─ pretty.py
   │     │  ├─ progress.py
   │     │  ├─ progress_bar.py
   │     │  ├─ prompt.py
   │     │  ├─ protocol.py
   │     │  ├─ py.typed
   │     │  ├─ region.py
   │     │  ├─ repr.py
   │     │  ├─ rule.py
   │     │  ├─ scope.py
   │     │  ├─ screen.py
   │     │  ├─ segment.py
   │     │  ├─ spinner.py
   │     │  ├─ status.py
   │     │  ├─ style.py
   │     │  ├─ styled.py
   │     │  ├─ syntax.py
   │     │  ├─ table.py
   │     │  ├─ terminal_theme.py
   │     │  ├─ text.py
   │     │  ├─ theme.py
   │     │  ├─ themes.py
   │     │  ├─ traceback.py
   │     │  ├─ tree.py
   │     │  ├─ _emoji_codes.py
   │     │  ├─ _emoji_replace.py
   │     │  ├─ _export_format.py
   │     │  ├─ _extension.py
   │     │  ├─ _fileno.py
   │     │  ├─ _inspect.py
   │     │  ├─ _log_render.py
   │     │  ├─ _loop.py
   │     │  ├─ _null_file.py
   │     │  ├─ _palettes.py
   │     │  ├─ _pick.py
   │     │  ├─ _ratio.py
   │     │  ├─ _spinners.py
   │     │  ├─ _stack.py
   │     │  ├─ _timer.py
   │     │  ├─ _unicode_data
   │     │  │  ├─ unicode10-0-0.py
   │     │  │  ├─ unicode11-0-0.py
   │     │  │  ├─ unicode12-0-0.py
   │     │  │  ├─ unicode12-1-0.py
   │     │  │  ├─ unicode13-0-0.py
   │     │  │  ├─ unicode14-0-0.py
   │     │  │  ├─ unicode15-0-0.py
   │     │  │  ├─ unicode15-1-0.py
   │     │  │  ├─ unicode16-0-0.py
   │     │  │  ├─ unicode17-0-0.py
   │     │  │  ├─ unicode4-1-0.py
   │     │  │  ├─ unicode5-0-0.py
   │     │  │  ├─ unicode5-1-0.py
   │     │  │  ├─ unicode5-2-0.py
   │     │  │  ├─ unicode6-0-0.py
   │     │  │  ├─ unicode6-1-0.py
   │     │  │  ├─ unicode6-2-0.py
   │     │  │  ├─ unicode6-3-0.py
   │     │  │  ├─ unicode7-0-0.py
   │     │  │  ├─ unicode8-0-0.py
   │     │  │  ├─ unicode9-0-0.py
   │     │  │  ├─ _versions.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ unicode10-0-0.cpython-311.pyc
   │     │  │     ├─ unicode11-0-0.cpython-311.pyc
   │     │  │     ├─ unicode12-0-0.cpython-311.pyc
   │     │  │     ├─ unicode12-1-0.cpython-311.pyc
   │     │  │     ├─ unicode13-0-0.cpython-311.pyc
   │     │  │     ├─ unicode14-0-0.cpython-311.pyc
   │     │  │     ├─ unicode15-0-0.cpython-311.pyc
   │     │  │     ├─ unicode15-1-0.cpython-311.pyc
   │     │  │     ├─ unicode16-0-0.cpython-311.pyc
   │     │  │     ├─ unicode17-0-0.cpython-311.pyc
   │     │  │     ├─ unicode4-1-0.cpython-311.pyc
   │     │  │     ├─ unicode5-0-0.cpython-311.pyc
   │     │  │     ├─ unicode5-1-0.cpython-311.pyc
   │     │  │     ├─ unicode5-2-0.cpython-311.pyc
   │     │  │     ├─ unicode6-0-0.cpython-311.pyc
   │     │  │     ├─ unicode6-1-0.cpython-311.pyc
   │     │  │     ├─ unicode6-2-0.cpython-311.pyc
   │     │  │     ├─ unicode6-3-0.cpython-311.pyc
   │     │  │     ├─ unicode7-0-0.cpython-311.pyc
   │     │  │     ├─ unicode8-0-0.cpython-311.pyc
   │     │  │     ├─ unicode9-0-0.cpython-311.pyc
   │     │  │     ├─ _versions.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ _win32_console.py
   │     │  ├─ _windows.py
   │     │  ├─ _windows_renderer.py
   │     │  ├─ _wrap.py
   │     │  ├─ __init__.py
   │     │  ├─ __main__.py
   │     │  └─ __pycache__
   │     │     ├─ abc.cpython-311.pyc
   │     │     ├─ align.cpython-311.pyc
   │     │     ├─ ansi.cpython-311.pyc
   │     │     ├─ bar.cpython-311.pyc
   │     │     ├─ box.cpython-311.pyc
   │     │     ├─ cells.cpython-311.pyc
   │     │     ├─ color.cpython-311.pyc
   │     │     ├─ color_triplet.cpython-311.pyc
   │     │     ├─ columns.cpython-311.pyc
   │     │     ├─ console.cpython-311.pyc
   │     │     ├─ constrain.cpython-311.pyc
   │     │     ├─ containers.cpython-311.pyc
   │     │     ├─ control.cpython-311.pyc
   │     │     ├─ default_styles.cpython-311.pyc
   │     │     ├─ diagnose.cpython-311.pyc
   │     │     ├─ emoji.cpython-311.pyc
   │     │     ├─ errors.cpython-311.pyc
   │     │     ├─ filesize.cpython-311.pyc
   │     │     ├─ file_proxy.cpython-311.pyc
   │     │     ├─ highlighter.cpython-311.pyc
   │     │     ├─ json.cpython-311.pyc
   │     │     ├─ jupyter.cpython-311.pyc
   │     │     ├─ layout.cpython-311.pyc
   │     │     ├─ live.cpython-311.pyc
   │     │     ├─ live_render.cpython-311.pyc
   │     │     ├─ logging.cpython-311.pyc
   │     │     ├─ markdown.cpython-311.pyc
   │     │     ├─ markup.cpython-311.pyc
   │     │     ├─ measure.cpython-311.pyc
   │     │     ├─ padding.cpython-311.pyc
   │     │     ├─ pager.cpython-311.pyc
   │     │     ├─ palette.cpython-311.pyc
   │     │     ├─ panel.cpython-311.pyc
   │     │     ├─ pretty.cpython-311.pyc
   │     │     ├─ progress.cpython-311.pyc
   │     │     ├─ progress_bar.cpython-311.pyc
   │     │     ├─ prompt.cpython-311.pyc
   │     │     ├─ protocol.cpython-311.pyc
   │     │     ├─ region.cpython-311.pyc
   │     │     ├─ repr.cpython-311.pyc
   │     │     ├─ rule.cpython-311.pyc
   │     │     ├─ scope.cpython-311.pyc
   │     │     ├─ screen.cpython-311.pyc
   │     │     ├─ segment.cpython-311.pyc
   │     │     ├─ spinner.cpython-311.pyc
   │     │     ├─ status.cpython-311.pyc
   │     │     ├─ style.cpython-311.pyc
   │     │     ├─ styled.cpython-311.pyc
   │     │     ├─ syntax.cpython-311.pyc
   │     │     ├─ table.cpython-311.pyc
   │     │     ├─ terminal_theme.cpython-311.pyc
   │     │     ├─ text.cpython-311.pyc
   │     │     ├─ theme.cpython-311.pyc
   │     │     ├─ themes.cpython-311.pyc
   │     │     ├─ traceback.cpython-311.pyc
   │     │     ├─ tree.cpython-311.pyc
   │     │     ├─ _emoji_codes.cpython-311.pyc
   │     │     ├─ _emoji_replace.cpython-311.pyc
   │     │     ├─ _export_format.cpython-311.pyc
   │     │     ├─ _extension.cpython-311.pyc
   │     │     ├─ _fileno.cpython-311.pyc
   │     │     ├─ _inspect.cpython-311.pyc
   │     │     ├─ _log_render.cpython-311.pyc
   │     │     ├─ _loop.cpython-311.pyc
   │     │     ├─ _null_file.cpython-311.pyc
   │     │     ├─ _palettes.cpython-311.pyc
   │     │     ├─ _pick.cpython-311.pyc
   │     │     ├─ _ratio.cpython-311.pyc
   │     │     ├─ _spinners.cpython-311.pyc
   │     │     ├─ _stack.cpython-311.pyc
   │     │     ├─ _timer.cpython-311.pyc
   │     │     ├─ _win32_console.cpython-311.pyc
   │     │     ├─ _windows.cpython-311.pyc
   │     │     ├─ _windows_renderer.cpython-311.pyc
   │     │     ├─ _wrap.cpython-311.pyc
   │     │     ├─ __init__.cpython-311.pyc
   │     │     └─ __main__.cpython-311.pyc
   │     ├─ rich-14.3.3.dist-info
   │     │  ├─ INSTALLER
   │     │  ├─ licenses
   │     │  │  └─ LICENSE
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  └─ WHEEL
   │     ├─ rpds
   │     │  ├─ py.typed
   │     │  ├─ rpds.cp311-win_amd64.pyd
   │     │  ├─ __init__.py
   │     │  ├─ __init__.pyi
   │     │  └─ __pycache__
   │     │     └─ __init__.cpython-311.pyc
   │     ├─ rpds_py-0.30.0.dist-info
   │     │  ├─ INSTALLER
   │     │  ├─ licenses
   │     │  │  └─ LICENSE
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  └─ WHEEL
   │     ├─ schemas
   │     │  └─ embedding_functions
   │     │     ├─ amazon_bedrock.json
   │     │     ├─ baseten.json
   │     │     ├─ base_schema.json
   │     │     ├─ bm25.json
   │     │     ├─ chroma-cloud-qwen.json
   │     │     ├─ chroma-cloud-splade.json
   │     │     ├─ chroma_bm25.json
   │     │     ├─ chroma_langchain.json
   │     │     ├─ cloudflare_workers_ai.json
   │     │     ├─ cohere.json
   │     │     ├─ default.json
   │     │     ├─ fastembed_sparse.json
   │     │     ├─ google_gemini.json
   │     │     ├─ google_genai.json
   │     │     ├─ google_generative_ai.json
   │     │     ├─ google_palm.json
   │     │     ├─ google_vertex.json
   │     │     ├─ huggingface.json
   │     │     ├─ huggingface_server.json
   │     │     ├─ huggingface_sparse.json
   │     │     ├─ instructor.json
   │     │     ├─ jina.json
   │     │     ├─ mistral.json
   │     │     ├─ morph.json
   │     │     ├─ nomic.json
   │     │     ├─ ollama.json
   │     │     ├─ onnx_mini_lm_l6_v2.json
   │     │     ├─ openai.json
   │     │     ├─ open_clip.json
   │     │     ├─ perplexity.json
   │     │     ├─ README.md
   │     │     ├─ roboflow.json
   │     │     ├─ sentence_transformer.json
   │     │     ├─ text2vec.json
   │     │     ├─ together_ai.json
   │     │     ├─ transformers.json
   │     │     └─ voyageai.json
   │     ├─ setuptools
   │     │  ├─ archive_util.py
   │     │  ├─ build_meta.py
   │     │  ├─ cli-32.exe
   │     │  ├─ cli-64.exe
   │     │  ├─ cli-arm64.exe
   │     │  ├─ cli.exe
   │     │  ├─ command
   │     │  │  ├─ alias.py
   │     │  │  ├─ bdist_egg.py
   │     │  │  ├─ bdist_rpm.py
   │     │  │  ├─ build.py
   │     │  │  ├─ build_clib.py
   │     │  │  ├─ build_ext.py
   │     │  │  ├─ build_py.py
   │     │  │  ├─ develop.py
   │     │  │  ├─ dist_info.py
   │     │  │  ├─ easy_install.py
   │     │  │  ├─ editable_wheel.py
   │     │  │  ├─ egg_info.py
   │     │  │  ├─ install.py
   │     │  │  ├─ install_egg_info.py
   │     │  │  ├─ install_lib.py
   │     │  │  ├─ install_scripts.py
   │     │  │  ├─ launcher manifest.xml
   │     │  │  ├─ py36compat.py
   │     │  │  ├─ register.py
   │     │  │  ├─ rotate.py
   │     │  │  ├─ saveopts.py
   │     │  │  ├─ sdist.py
   │     │  │  ├─ setopt.py
   │     │  │  ├─ test.py
   │     │  │  ├─ upload.py
   │     │  │  ├─ upload_docs.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ alias.cpython-311.pyc
   │     │  │     ├─ bdist_egg.cpython-311.pyc
   │     │  │     ├─ bdist_rpm.cpython-311.pyc
   │     │  │     ├─ build.cpython-311.pyc
   │     │  │     ├─ build_clib.cpython-311.pyc
   │     │  │     ├─ build_ext.cpython-311.pyc
   │     │  │     ├─ build_py.cpython-311.pyc
   │     │  │     ├─ develop.cpython-311.pyc
   │     │  │     ├─ dist_info.cpython-311.pyc
   │     │  │     ├─ easy_install.cpython-311.pyc
   │     │  │     ├─ editable_wheel.cpython-311.pyc
   │     │  │     ├─ egg_info.cpython-311.pyc
   │     │  │     ├─ install.cpython-311.pyc
   │     │  │     ├─ install_egg_info.cpython-311.pyc
   │     │  │     ├─ install_lib.cpython-311.pyc
   │     │  │     ├─ install_scripts.cpython-311.pyc
   │     │  │     ├─ py36compat.cpython-311.pyc
   │     │  │     ├─ register.cpython-311.pyc
   │     │  │     ├─ rotate.cpython-311.pyc
   │     │  │     ├─ saveopts.cpython-311.pyc
   │     │  │     ├─ sdist.cpython-311.pyc
   │     │  │     ├─ setopt.cpython-311.pyc
   │     │  │     ├─ test.cpython-311.pyc
   │     │  │     ├─ upload.cpython-311.pyc
   │     │  │     ├─ upload_docs.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ config
   │     │  │  ├─ expand.py
   │     │  │  ├─ pyprojecttoml.py
   │     │  │  ├─ setupcfg.py
   │     │  │  ├─ _apply_pyprojecttoml.py
   │     │  │  ├─ _validate_pyproject
   │     │  │  │  ├─ error_reporting.py
   │     │  │  │  ├─ extra_validations.py
   │     │  │  │  ├─ fastjsonschema_exceptions.py
   │     │  │  │  ├─ fastjsonschema_validations.py
   │     │  │  │  ├─ formats.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ error_reporting.cpython-311.pyc
   │     │  │  │     ├─ extra_validations.cpython-311.pyc
   │     │  │  │     ├─ fastjsonschema_exceptions.cpython-311.pyc
   │     │  │  │     ├─ fastjsonschema_validations.cpython-311.pyc
   │     │  │  │     ├─ formats.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ expand.cpython-311.pyc
   │     │  │     ├─ pyprojecttoml.cpython-311.pyc
   │     │  │     ├─ setupcfg.cpython-311.pyc
   │     │  │     ├─ _apply_pyprojecttoml.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ depends.py
   │     │  ├─ dep_util.py
   │     │  ├─ discovery.py
   │     │  ├─ dist.py
   │     │  ├─ errors.py
   │     │  ├─ extension.py
   │     │  ├─ extern
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ glob.py
   │     │  ├─ gui-32.exe
   │     │  ├─ gui-64.exe
   │     │  ├─ gui-arm64.exe
   │     │  ├─ gui.exe
   │     │  ├─ installer.py
   │     │  ├─ launch.py
   │     │  ├─ logging.py
   │     │  ├─ monkey.py
   │     │  ├─ msvc.py
   │     │  ├─ namespaces.py
   │     │  ├─ package_index.py
   │     │  ├─ py34compat.py
   │     │  ├─ sandbox.py
   │     │  ├─ script (dev).tmpl
   │     │  ├─ script.tmpl
   │     │  ├─ unicode_utils.py
   │     │  ├─ version.py
   │     │  ├─ wheel.py
   │     │  ├─ windows_support.py
   │     │  ├─ _deprecation_warning.py
   │     │  ├─ _distutils
   │     │  │  ├─ archive_util.py
   │     │  │  ├─ bcppcompiler.py
   │     │  │  ├─ ccompiler.py
   │     │  │  ├─ cmd.py
   │     │  │  ├─ command
   │     │  │  │  ├─ bdist.py
   │     │  │  │  ├─ bdist_dumb.py
   │     │  │  │  ├─ bdist_rpm.py
   │     │  │  │  ├─ build.py
   │     │  │  │  ├─ build_clib.py
   │     │  │  │  ├─ build_ext.py
   │     │  │  │  ├─ build_py.py
   │     │  │  │  ├─ build_scripts.py
   │     │  │  │  ├─ check.py
   │     │  │  │  ├─ clean.py
   │     │  │  │  ├─ config.py
   │     │  │  │  ├─ install.py
   │     │  │  │  ├─ install_data.py
   │     │  │  │  ├─ install_egg_info.py
   │     │  │  │  ├─ install_headers.py
   │     │  │  │  ├─ install_lib.py
   │     │  │  │  ├─ install_scripts.py
   │     │  │  │  ├─ py37compat.py
   │     │  │  │  ├─ register.py
   │     │  │  │  ├─ sdist.py
   │     │  │  │  ├─ upload.py
   │     │  │  │  ├─ _framework_compat.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ bdist.cpython-311.pyc
   │     │  │  │     ├─ bdist_dumb.cpython-311.pyc
   │     │  │  │     ├─ bdist_rpm.cpython-311.pyc
   │     │  │  │     ├─ build.cpython-311.pyc
   │     │  │  │     ├─ build_clib.cpython-311.pyc
   │     │  │  │     ├─ build_ext.cpython-311.pyc
   │     │  │  │     ├─ build_py.cpython-311.pyc
   │     │  │  │     ├─ build_scripts.cpython-311.pyc
   │     │  │  │     ├─ check.cpython-311.pyc
   │     │  │  │     ├─ clean.cpython-311.pyc
   │     │  │  │     ├─ config.cpython-311.pyc
   │     │  │  │     ├─ install.cpython-311.pyc
   │     │  │  │     ├─ install_data.cpython-311.pyc
   │     │  │  │     ├─ install_egg_info.cpython-311.pyc
   │     │  │  │     ├─ install_headers.cpython-311.pyc
   │     │  │  │     ├─ install_lib.cpython-311.pyc
   │     │  │  │     ├─ install_scripts.cpython-311.pyc
   │     │  │  │     ├─ py37compat.cpython-311.pyc
   │     │  │  │     ├─ register.cpython-311.pyc
   │     │  │  │     ├─ sdist.cpython-311.pyc
   │     │  │  │     ├─ upload.cpython-311.pyc
   │     │  │  │     ├─ _framework_compat.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ config.py
   │     │  │  ├─ core.py
   │     │  │  ├─ cygwinccompiler.py
   │     │  │  ├─ debug.py
   │     │  │  ├─ dep_util.py
   │     │  │  ├─ dir_util.py
   │     │  │  ├─ dist.py
   │     │  │  ├─ errors.py
   │     │  │  ├─ extension.py
   │     │  │  ├─ fancy_getopt.py
   │     │  │  ├─ filelist.py
   │     │  │  ├─ file_util.py
   │     │  │  ├─ log.py
   │     │  │  ├─ msvc9compiler.py
   │     │  │  ├─ msvccompiler.py
   │     │  │  ├─ py38compat.py
   │     │  │  ├─ py39compat.py
   │     │  │  ├─ spawn.py
   │     │  │  ├─ sysconfig.py
   │     │  │  ├─ text_file.py
   │     │  │  ├─ unixccompiler.py
   │     │  │  ├─ util.py
   │     │  │  ├─ version.py
   │     │  │  ├─ versionpredicate.py
   │     │  │  ├─ _collections.py
   │     │  │  ├─ _functools.py
   │     │  │  ├─ _macos_compat.py
   │     │  │  ├─ _msvccompiler.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ archive_util.cpython-311.pyc
   │     │  │     ├─ bcppcompiler.cpython-311.pyc
   │     │  │     ├─ ccompiler.cpython-311.pyc
   │     │  │     ├─ cmd.cpython-311.pyc
   │     │  │     ├─ config.cpython-311.pyc
   │     │  │     ├─ core.cpython-311.pyc
   │     │  │     ├─ cygwinccompiler.cpython-311.pyc
   │     │  │     ├─ debug.cpython-311.pyc
   │     │  │     ├─ dep_util.cpython-311.pyc
   │     │  │     ├─ dir_util.cpython-311.pyc
   │     │  │     ├─ dist.cpython-311.pyc
   │     │  │     ├─ errors.cpython-311.pyc
   │     │  │     ├─ extension.cpython-311.pyc
   │     │  │     ├─ fancy_getopt.cpython-311.pyc
   │     │  │     ├─ filelist.cpython-311.pyc
   │     │  │     ├─ file_util.cpython-311.pyc
   │     │  │     ├─ log.cpython-311.pyc
   │     │  │     ├─ msvc9compiler.cpython-311.pyc
   │     │  │     ├─ msvccompiler.cpython-311.pyc
   │     │  │     ├─ py38compat.cpython-311.pyc
   │     │  │     ├─ py39compat.cpython-311.pyc
   │     │  │     ├─ spawn.cpython-311.pyc
   │     │  │     ├─ sysconfig.cpython-311.pyc
   │     │  │     ├─ text_file.cpython-311.pyc
   │     │  │     ├─ unixccompiler.cpython-311.pyc
   │     │  │     ├─ util.cpython-311.pyc
   │     │  │     ├─ version.cpython-311.pyc
   │     │  │     ├─ versionpredicate.cpython-311.pyc
   │     │  │     ├─ _collections.cpython-311.pyc
   │     │  │     ├─ _functools.cpython-311.pyc
   │     │  │     ├─ _macos_compat.cpython-311.pyc
   │     │  │     ├─ _msvccompiler.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ _entry_points.py
   │     │  ├─ _imp.py
   │     │  ├─ _importlib.py
   │     │  ├─ _itertools.py
   │     │  ├─ _path.py
   │     │  ├─ _reqs.py
   │     │  ├─ _vendor
   │     │  │  ├─ importlib_metadata
   │     │  │  │  ├─ _adapters.py
   │     │  │  │  ├─ _collections.py
   │     │  │  │  ├─ _compat.py
   │     │  │  │  ├─ _functools.py
   │     │  │  │  ├─ _itertools.py
   │     │  │  │  ├─ _meta.py
   │     │  │  │  ├─ _text.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ _adapters.cpython-311.pyc
   │     │  │  │     ├─ _collections.cpython-311.pyc
   │     │  │  │     ├─ _compat.cpython-311.pyc
   │     │  │  │     ├─ _functools.cpython-311.pyc
   │     │  │  │     ├─ _itertools.cpython-311.pyc
   │     │  │  │     ├─ _meta.cpython-311.pyc
   │     │  │  │     ├─ _text.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ importlib_resources
   │     │  │  │  ├─ abc.py
   │     │  │  │  ├─ readers.py
   │     │  │  │  ├─ simple.py
   │     │  │  │  ├─ _adapters.py
   │     │  │  │  ├─ _common.py
   │     │  │  │  ├─ _compat.py
   │     │  │  │  ├─ _itertools.py
   │     │  │  │  ├─ _legacy.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ abc.cpython-311.pyc
   │     │  │  │     ├─ readers.cpython-311.pyc
   │     │  │  │     ├─ simple.cpython-311.pyc
   │     │  │  │     ├─ _adapters.cpython-311.pyc
   │     │  │  │     ├─ _common.cpython-311.pyc
   │     │  │  │     ├─ _compat.cpython-311.pyc
   │     │  │  │     ├─ _itertools.cpython-311.pyc
   │     │  │  │     ├─ _legacy.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ jaraco
   │     │  │  │  ├─ context.py
   │     │  │  │  ├─ functools.py
   │     │  │  │  ├─ text
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ context.cpython-311.pyc
   │     │  │  │     ├─ functools.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ more_itertools
   │     │  │  │  ├─ more.py
   │     │  │  │  ├─ recipes.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ more.cpython-311.pyc
   │     │  │  │     ├─ recipes.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ ordered_set.py
   │     │  │  ├─ packaging
   │     │  │  │  ├─ markers.py
   │     │  │  │  ├─ requirements.py
   │     │  │  │  ├─ specifiers.py
   │     │  │  │  ├─ tags.py
   │     │  │  │  ├─ utils.py
   │     │  │  │  ├─ version.py
   │     │  │  │  ├─ _manylinux.py
   │     │  │  │  ├─ _musllinux.py
   │     │  │  │  ├─ _structures.py
   │     │  │  │  ├─ __about__.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ markers.cpython-311.pyc
   │     │  │  │     ├─ requirements.cpython-311.pyc
   │     │  │  │     ├─ specifiers.cpython-311.pyc
   │     │  │  │     ├─ tags.cpython-311.pyc
   │     │  │  │     ├─ utils.cpython-311.pyc
   │     │  │  │     ├─ version.cpython-311.pyc
   │     │  │  │     ├─ _manylinux.cpython-311.pyc
   │     │  │  │     ├─ _musllinux.cpython-311.pyc
   │     │  │  │     ├─ _structures.cpython-311.pyc
   │     │  │  │     ├─ __about__.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ pyparsing
   │     │  │  │  ├─ actions.py
   │     │  │  │  ├─ common.py
   │     │  │  │  ├─ core.py
   │     │  │  │  ├─ diagram
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ exceptions.py
   │     │  │  │  ├─ helpers.py
   │     │  │  │  ├─ results.py
   │     │  │  │  ├─ testing.py
   │     │  │  │  ├─ unicode.py
   │     │  │  │  ├─ util.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ actions.cpython-311.pyc
   │     │  │  │     ├─ common.cpython-311.pyc
   │     │  │  │     ├─ core.cpython-311.pyc
   │     │  │  │     ├─ exceptions.cpython-311.pyc
   │     │  │  │     ├─ helpers.cpython-311.pyc
   │     │  │  │     ├─ results.cpython-311.pyc
   │     │  │  │     ├─ testing.cpython-311.pyc
   │     │  │  │     ├─ unicode.cpython-311.pyc
   │     │  │  │     ├─ util.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ tomli
   │     │  │  │  ├─ _parser.py
   │     │  │  │  ├─ _re.py
   │     │  │  │  ├─ _types.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ _parser.cpython-311.pyc
   │     │  │  │     ├─ _re.cpython-311.pyc
   │     │  │  │     ├─ _types.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ typing_extensions.py
   │     │  │  ├─ zipp.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ ordered_set.cpython-311.pyc
   │     │  │     ├─ typing_extensions.cpython-311.pyc
   │     │  │     ├─ zipp.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ __init__.py
   │     │  └─ __pycache__
   │     │     ├─ archive_util.cpython-311.pyc
   │     │     ├─ build_meta.cpython-311.pyc
   │     │     ├─ depends.cpython-311.pyc
   │     │     ├─ dep_util.cpython-311.pyc
   │     │     ├─ discovery.cpython-311.pyc
   │     │     ├─ dist.cpython-311.pyc
   │     │     ├─ errors.cpython-311.pyc
   │     │     ├─ extension.cpython-311.pyc
   │     │     ├─ glob.cpython-311.pyc
   │     │     ├─ installer.cpython-311.pyc
   │     │     ├─ launch.cpython-311.pyc
   │     │     ├─ logging.cpython-311.pyc
   │     │     ├─ monkey.cpython-311.pyc
   │     │     ├─ msvc.cpython-311.pyc
   │     │     ├─ namespaces.cpython-311.pyc
   │     │     ├─ package_index.cpython-311.pyc
   │     │     ├─ py34compat.cpython-311.pyc
   │     │     ├─ sandbox.cpython-311.pyc
   │     │     ├─ unicode_utils.cpython-311.pyc
   │     │     ├─ version.cpython-311.pyc
   │     │     ├─ wheel.cpython-311.pyc
   │     │     ├─ windows_support.cpython-311.pyc
   │     │     ├─ _deprecation_warning.cpython-311.pyc
   │     │     ├─ _entry_points.cpython-311.pyc
   │     │     ├─ _imp.cpython-311.pyc
   │     │     ├─ _importlib.cpython-311.pyc
   │     │     ├─ _itertools.cpython-311.pyc
   │     │     ├─ _path.cpython-311.pyc
   │     │     ├─ _reqs.cpython-311.pyc
   │     │     └─ __init__.cpython-311.pyc
   │     ├─ setuptools-65.5.0.dist-info
   │     │  ├─ entry_points.txt
   │     │  ├─ INSTALLER
   │     │  ├─ LICENSE
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  ├─ REQUESTED
   │     │  ├─ top_level.txt
   │     │  └─ WHEEL
   │     ├─ shellingham
   │     │  ├─ nt.py
   │     │  ├─ posix
   │     │  │  ├─ proc.py
   │     │  │  ├─ ps.py
   │     │  │  ├─ _core.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ proc.cpython-311.pyc
   │     │  │     ├─ ps.cpython-311.pyc
   │     │  │     ├─ _core.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ _core.py
   │     │  ├─ __init__.py
   │     │  └─ __pycache__
   │     │     ├─ nt.cpython-311.pyc
   │     │     ├─ _core.cpython-311.pyc
   │     │     └─ __init__.cpython-311.pyc
   │     ├─ shellingham-1.5.4.dist-info
   │     │  ├─ INSTALLER
   │     │  ├─ LICENSE
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  ├─ top_level.txt
   │     │  ├─ WHEEL
   │     │  └─ zip-safe
   │     ├─ six-1.17.0.dist-info
   │     │  ├─ INSTALLER
   │     │  ├─ LICENSE
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  ├─ top_level.txt
   │     │  └─ WHEEL
   │     ├─ six.py
   │     ├─ smmap
   │     │  ├─ buf.py
   │     │  ├─ mman.py
   │     │  ├─ test
   │     │  │  ├─ lib.py
   │     │  │  ├─ test_buf.py
   │     │  │  ├─ test_mman.py
   │     │  │  ├─ test_tutorial.py
   │     │  │  ├─ test_util.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ lib.cpython-311.pyc
   │     │  │     ├─ test_buf.cpython-311.pyc
   │     │  │     ├─ test_mman.cpython-311.pyc
   │     │  │     ├─ test_tutorial.cpython-311.pyc
   │     │  │     ├─ test_util.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ util.py
   │     │  ├─ __init__.py
   │     │  └─ __pycache__
   │     │     ├─ buf.cpython-311.pyc
   │     │     ├─ mman.cpython-311.pyc
   │     │     ├─ util.cpython-311.pyc
   │     │     └─ __init__.cpython-311.pyc
   │     ├─ smmap-5.0.3.dist-info
   │     │  ├─ INSTALLER
   │     │  ├─ licenses
   │     │  │  └─ LICENSE
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  ├─ top_level.txt
   │     │  ├─ WHEEL
   │     │  └─ zip-safe
   │     ├─ sniffio
   │     │  ├─ py.typed
   │     │  ├─ _impl.py
   │     │  ├─ _tests
   │     │  │  ├─ test_sniffio.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ test_sniffio.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ _version.py
   │     │  ├─ __init__.py
   │     │  └─ __pycache__
   │     │     ├─ _impl.cpython-311.pyc
   │     │     ├─ _version.cpython-311.pyc
   │     │     └─ __init__.cpython-311.pyc
   │     ├─ sniffio-1.3.1.dist-info
   │     │  ├─ INSTALLER
   │     │  ├─ LICENSE
   │     │  ├─ LICENSE.APACHE2
   │     │  ├─ LICENSE.MIT
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  ├─ top_level.txt
   │     │  └─ WHEEL
   │     ├─ streamlit
   │     │  ├─ auth_util.py
   │     │  ├─ cli_util.py
   │     │  ├─ column_config.py
   │     │  ├─ commands
   │     │  │  ├─ echo.py
   │     │  │  ├─ execution_control.py
   │     │  │  ├─ logo.py
   │     │  │  ├─ navigation.py
   │     │  │  ├─ page_config.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ echo.cpython-311.pyc
   │     │  │     ├─ execution_control.cpython-311.pyc
   │     │  │     ├─ logo.cpython-311.pyc
   │     │  │     ├─ navigation.cpython-311.pyc
   │     │  │     ├─ page_config.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ components
   │     │  │  ├─ lib
   │     │  │  │  ├─ local_component_registry.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ local_component_registry.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ types
   │     │  │  │  ├─ base_component_registry.py
   │     │  │  │  ├─ base_custom_component.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ base_component_registry.cpython-311.pyc
   │     │  │  │     ├─ base_custom_component.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ v1
   │     │  │  │  ├─ components.py
   │     │  │  │  ├─ component_arrow.py
   │     │  │  │  ├─ component_registry.py
   │     │  │  │  ├─ custom_component.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ components.cpython-311.pyc
   │     │  │  │     ├─ component_arrow.cpython-311.pyc
   │     │  │  │     ├─ component_registry.cpython-311.pyc
   │     │  │  │     ├─ custom_component.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ v2
   │     │  │  │  ├─ bidi_component
   │     │  │  │  │  ├─ constants.py
   │     │  │  │  │  ├─ main.py
   │     │  │  │  │  ├─ serialization.py
   │     │  │  │  │  ├─ state.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ constants.cpython-311.pyc
   │     │  │  │  │     ├─ main.cpython-311.pyc
   │     │  │  │  │     ├─ serialization.cpython-311.pyc
   │     │  │  │  │     ├─ state.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ component_definition_resolver.py
   │     │  │  │  ├─ component_file_watcher.py
   │     │  │  │  ├─ component_manager.py
   │     │  │  │  ├─ component_manifest_handler.py
   │     │  │  │  ├─ component_path_utils.py
   │     │  │  │  ├─ component_registry.py
   │     │  │  │  ├─ get_bidi_component_manager.py
   │     │  │  │  ├─ manifest_scanner.py
   │     │  │  │  ├─ presentation.py
   │     │  │  │  ├─ types.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ component_definition_resolver.cpython-311.pyc
   │     │  │  │     ├─ component_file_watcher.cpython-311.pyc
   │     │  │  │     ├─ component_manager.cpython-311.pyc
   │     │  │  │     ├─ component_manifest_handler.cpython-311.pyc
   │     │  │  │     ├─ component_path_utils.cpython-311.pyc
   │     │  │  │     ├─ component_registry.cpython-311.pyc
   │     │  │  │     ├─ get_bidi_component_manager.cpython-311.pyc
   │     │  │  │     ├─ manifest_scanner.cpython-311.pyc
   │     │  │  │     ├─ presentation.cpython-311.pyc
   │     │  │  │     ├─ types.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ config.py
   │     │  ├─ config_option.py
   │     │  ├─ config_util.py
   │     │  ├─ connections
   │     │  │  ├─ base_connection.py
   │     │  │  ├─ snowflake_connection.py
   │     │  │  ├─ snowpark_connection.py
   │     │  │  ├─ sql_connection.py
   │     │  │  ├─ util.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ base_connection.cpython-311.pyc
   │     │  │     ├─ snowflake_connection.cpython-311.pyc
   │     │  │     ├─ snowpark_connection.cpython-311.pyc
   │     │  │     ├─ sql_connection.cpython-311.pyc
   │     │  │     ├─ util.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ cursor.py
   │     │  ├─ dataframe_util.py
   │     │  ├─ delta_generator.py
   │     │  ├─ delta_generator_singletons.py
   │     │  ├─ deprecation_util.py
   │     │  ├─ development.py
   │     │  ├─ elements
   │     │  │  ├─ alert.py
   │     │  │  ├─ arrow.py
   │     │  │  ├─ balloons.py
   │     │  │  ├─ bokeh_chart.py
   │     │  │  ├─ code.py
   │     │  │  ├─ deck_gl_json_chart.py
   │     │  │  ├─ dialog_decorator.py
   │     │  │  ├─ empty.py
   │     │  │  ├─ exception.py
   │     │  │  ├─ form.py
   │     │  │  ├─ graphviz_chart.py
   │     │  │  ├─ heading.py
   │     │  │  ├─ help.py
   │     │  │  ├─ html.py
   │     │  │  ├─ iframe.py
   │     │  │  ├─ image.py
   │     │  │  ├─ json.py
   │     │  │  ├─ layouts.py
   │     │  │  ├─ lib
   │     │  │  │  ├─ built_in_chart_utils.py
   │     │  │  │  ├─ color_util.py
   │     │  │  │  ├─ column_config_utils.py
   │     │  │  │  ├─ column_types.py
   │     │  │  │  ├─ dialog.py
   │     │  │  │  ├─ dicttools.py
   │     │  │  │  ├─ file_uploader_utils.py
   │     │  │  │  ├─ form_utils.py
   │     │  │  │  ├─ image_utils.py
   │     │  │  │  ├─ js_number.py
   │     │  │  │  ├─ layout_utils.py
   │     │  │  │  ├─ mutable_expander_container.py
   │     │  │  │  ├─ mutable_popover_container.py
   │     │  │  │  ├─ mutable_status_container.py
   │     │  │  │  ├─ mutable_tab_container.py
   │     │  │  │  ├─ options_selector_utils.py
   │     │  │  │  ├─ pandas_styler_utils.py
   │     │  │  │  ├─ policies.py
   │     │  │  │  ├─ shortcut_utils.py
   │     │  │  │  ├─ streamlit_plotly_theme.py
   │     │  │  │  ├─ subtitle_utils.py
   │     │  │  │  ├─ utils.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ built_in_chart_utils.cpython-311.pyc
   │     │  │  │     ├─ color_util.cpython-311.pyc
   │     │  │  │     ├─ column_config_utils.cpython-311.pyc
   │     │  │  │     ├─ column_types.cpython-311.pyc
   │     │  │  │     ├─ dialog.cpython-311.pyc
   │     │  │  │     ├─ dicttools.cpython-311.pyc
   │     │  │  │     ├─ file_uploader_utils.cpython-311.pyc
   │     │  │  │     ├─ form_utils.cpython-311.pyc
   │     │  │  │     ├─ image_utils.cpython-311.pyc
   │     │  │  │     ├─ js_number.cpython-311.pyc
   │     │  │  │     ├─ layout_utils.cpython-311.pyc
   │     │  │  │     ├─ mutable_expander_container.cpython-311.pyc
   │     │  │  │     ├─ mutable_popover_container.cpython-311.pyc
   │     │  │  │     ├─ mutable_status_container.cpython-311.pyc
   │     │  │  │     ├─ mutable_tab_container.cpython-311.pyc
   │     │  │  │     ├─ options_selector_utils.cpython-311.pyc
   │     │  │  │     ├─ pandas_styler_utils.cpython-311.pyc
   │     │  │  │     ├─ policies.cpython-311.pyc
   │     │  │  │     ├─ shortcut_utils.cpython-311.pyc
   │     │  │  │     ├─ streamlit_plotly_theme.cpython-311.pyc
   │     │  │  │     ├─ subtitle_utils.cpython-311.pyc
   │     │  │  │     ├─ utils.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ map.py
   │     │  │  ├─ markdown.py
   │     │  │  ├─ media.py
   │     │  │  ├─ metric.py
   │     │  │  ├─ pdf.py
   │     │  │  ├─ plotly_chart.py
   │     │  │  ├─ progress.py
   │     │  │  ├─ pyplot.py
   │     │  │  ├─ snow.py
   │     │  │  ├─ space.py
   │     │  │  ├─ spinner.py
   │     │  │  ├─ table.py
   │     │  │  ├─ text.py
   │     │  │  ├─ toast.py
   │     │  │  ├─ vega_charts.py
   │     │  │  ├─ widgets
   │     │  │  │  ├─ audio_input.py
   │     │  │  │  ├─ button.py
   │     │  │  │  ├─ button_group.py
   │     │  │  │  ├─ camera_input.py
   │     │  │  │  ├─ chat.py
   │     │  │  │  ├─ checkbox.py
   │     │  │  │  ├─ color_picker.py
   │     │  │  │  ├─ data_editor.py
   │     │  │  │  ├─ feedback.py
   │     │  │  │  ├─ file_uploader.py
   │     │  │  │  ├─ menu_button.py
   │     │  │  │  ├─ multiselect.py
   │     │  │  │  ├─ number_input.py
   │     │  │  │  ├─ radio.py
   │     │  │  │  ├─ selectbox.py
   │     │  │  │  ├─ select_slider.py
   │     │  │  │  ├─ slider.py
   │     │  │  │  ├─ text_widgets.py
   │     │  │  │  ├─ time_widgets.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ audio_input.cpython-311.pyc
   │     │  │  │     ├─ button.cpython-311.pyc
   │     │  │  │     ├─ button_group.cpython-311.pyc
   │     │  │  │     ├─ camera_input.cpython-311.pyc
   │     │  │  │     ├─ chat.cpython-311.pyc
   │     │  │  │     ├─ checkbox.cpython-311.pyc
   │     │  │  │     ├─ color_picker.cpython-311.pyc
   │     │  │  │     ├─ data_editor.cpython-311.pyc
   │     │  │  │     ├─ feedback.cpython-311.pyc
   │     │  │  │     ├─ file_uploader.cpython-311.pyc
   │     │  │  │     ├─ menu_button.cpython-311.pyc
   │     │  │  │     ├─ multiselect.cpython-311.pyc
   │     │  │  │     ├─ number_input.cpython-311.pyc
   │     │  │  │     ├─ radio.cpython-311.pyc
   │     │  │  │     ├─ selectbox.cpython-311.pyc
   │     │  │  │     ├─ select_slider.cpython-311.pyc
   │     │  │  │     ├─ slider.cpython-311.pyc
   │     │  │  │     ├─ text_widgets.cpython-311.pyc
   │     │  │  │     ├─ time_widgets.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ write.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ alert.cpython-311.pyc
   │     │  │     ├─ arrow.cpython-311.pyc
   │     │  │     ├─ balloons.cpython-311.pyc
   │     │  │     ├─ bokeh_chart.cpython-311.pyc
   │     │  │     ├─ code.cpython-311.pyc
   │     │  │     ├─ deck_gl_json_chart.cpython-311.pyc
   │     │  │     ├─ dialog_decorator.cpython-311.pyc
   │     │  │     ├─ empty.cpython-311.pyc
   │     │  │     ├─ exception.cpython-311.pyc
   │     │  │     ├─ form.cpython-311.pyc
   │     │  │     ├─ graphviz_chart.cpython-311.pyc
   │     │  │     ├─ heading.cpython-311.pyc
   │     │  │     ├─ help.cpython-311.pyc
   │     │  │     ├─ html.cpython-311.pyc
   │     │  │     ├─ iframe.cpython-311.pyc
   │     │  │     ├─ image.cpython-311.pyc
   │     │  │     ├─ json.cpython-311.pyc
   │     │  │     ├─ layouts.cpython-311.pyc
   │     │  │     ├─ map.cpython-311.pyc
   │     │  │     ├─ markdown.cpython-311.pyc
   │     │  │     ├─ media.cpython-311.pyc
   │     │  │     ├─ metric.cpython-311.pyc
   │     │  │     ├─ pdf.cpython-311.pyc
   │     │  │     ├─ plotly_chart.cpython-311.pyc
   │     │  │     ├─ progress.cpython-311.pyc
   │     │  │     ├─ pyplot.cpython-311.pyc
   │     │  │     ├─ snow.cpython-311.pyc
   │     │  │     ├─ space.cpython-311.pyc
   │     │  │     ├─ spinner.cpython-311.pyc
   │     │  │     ├─ table.cpython-311.pyc
   │     │  │     ├─ text.cpython-311.pyc
   │     │  │     ├─ toast.cpython-311.pyc
   │     │  │     ├─ vega_charts.cpython-311.pyc
   │     │  │     ├─ write.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ emojis.py
   │     │  ├─ env_util.py
   │     │  ├─ errors.py
   │     │  ├─ error_util.py
   │     │  ├─ external
   │     │  │  ├─ langchain
   │     │  │  │  ├─ streamlit_callback_handler.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ streamlit_callback_handler.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ file_util.py
   │     │  ├─ git_util.py
   │     │  ├─ hello
   │     │  │  ├─ animation_demo.py
   │     │  │  ├─ dataframe_demo.py
   │     │  │  ├─ hello.py
   │     │  │  ├─ mapping_demo.py
   │     │  │  ├─ plotting_demo.py
   │     │  │  ├─ streamlit_app.py
   │     │  │  ├─ utils.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ animation_demo.cpython-311.pyc
   │     │  │     ├─ dataframe_demo.cpython-311.pyc
   │     │  │     ├─ hello.cpython-311.pyc
   │     │  │     ├─ mapping_demo.cpython-311.pyc
   │     │  │     ├─ plotting_demo.cpython-311.pyc
   │     │  │     ├─ streamlit_app.cpython-311.pyc
   │     │  │     ├─ utils.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ logger.py
   │     │  ├─ material_icon_names.py
   │     │  ├─ navigation
   │     │  │  ├─ page.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ page.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ net_util.py
   │     │  ├─ path_security.py
   │     │  ├─ platform.py
   │     │  ├─ proto
   │     │  │  ├─ Alert_pb2.py
   │     │  │  ├─ Alert_pb2.pyi
   │     │  │  ├─ AppPage_pb2.py
   │     │  │  ├─ AppPage_pb2.pyi
   │     │  │  ├─ ArrowData_pb2.py
   │     │  │  ├─ ArrowData_pb2.pyi
   │     │  │  ├─ ArrowNamedDataSet_pb2.py
   │     │  │  ├─ ArrowNamedDataSet_pb2.pyi
   │     │  │  ├─ AudioInput_pb2.py
   │     │  │  ├─ AudioInput_pb2.pyi
   │     │  │  ├─ Audio_pb2.py
   │     │  │  ├─ Audio_pb2.pyi
   │     │  │  ├─ AuthRedirect_pb2.py
   │     │  │  ├─ AuthRedirect_pb2.pyi
   │     │  │  ├─ AutoRerun_pb2.py
   │     │  │  ├─ AutoRerun_pb2.pyi
   │     │  │  ├─ BackMsg_pb2.py
   │     │  │  ├─ BackMsg_pb2.pyi
   │     │  │  ├─ Balloons_pb2.py
   │     │  │  ├─ Balloons_pb2.pyi
   │     │  │  ├─ BidiComponent_pb2.py
   │     │  │  ├─ BidiComponent_pb2.pyi
   │     │  │  ├─ Block_pb2.py
   │     │  │  ├─ Block_pb2.pyi
   │     │  │  ├─ ButtonGroup_pb2.py
   │     │  │  ├─ ButtonGroup_pb2.pyi
   │     │  │  ├─ ButtonLikeIconPosition_pb2.py
   │     │  │  ├─ ButtonLikeIconPosition_pb2.pyi
   │     │  │  ├─ Button_pb2.py
   │     │  │  ├─ Button_pb2.pyi
   │     │  │  ├─ CameraInput_pb2.py
   │     │  │  ├─ CameraInput_pb2.pyi
   │     │  │  ├─ ChatInput_pb2.py
   │     │  │  ├─ ChatInput_pb2.pyi
   │     │  │  ├─ Checkbox_pb2.py
   │     │  │  ├─ Checkbox_pb2.pyi
   │     │  │  ├─ ClientState_pb2.py
   │     │  │  ├─ ClientState_pb2.pyi
   │     │  │  ├─ Code_pb2.py
   │     │  │  ├─ Code_pb2.pyi
   │     │  │  ├─ ColorPicker_pb2.py
   │     │  │  ├─ ColorPicker_pb2.pyi
   │     │  │  ├─ Common_pb2.py
   │     │  │  ├─ Common_pb2.pyi
   │     │  │  ├─ Components_pb2.py
   │     │  │  ├─ Components_pb2.pyi
   │     │  │  ├─ Dataframe_pb2.py
   │     │  │  ├─ Dataframe_pb2.pyi
   │     │  │  ├─ DateInput_pb2.py
   │     │  │  ├─ DateInput_pb2.pyi
   │     │  │  ├─ DateTimeInput_pb2.py
   │     │  │  ├─ DateTimeInput_pb2.pyi
   │     │  │  ├─ DeckGlJsonChart_pb2.py
   │     │  │  ├─ DeckGlJsonChart_pb2.pyi
   │     │  │  ├─ Delta_pb2.py
   │     │  │  ├─ Delta_pb2.pyi
   │     │  │  ├─ DownloadButton_pb2.py
   │     │  │  ├─ DownloadButton_pb2.pyi
   │     │  │  ├─ Element_pb2.py
   │     │  │  ├─ Element_pb2.pyi
   │     │  │  ├─ Empty_pb2.py
   │     │  │  ├─ Empty_pb2.pyi
   │     │  │  ├─ Exception_pb2.py
   │     │  │  ├─ Exception_pb2.pyi
   │     │  │  ├─ Favicon_pb2.py
   │     │  │  ├─ Favicon_pb2.pyi
   │     │  │  ├─ Feedback_pb2.py
   │     │  │  ├─ Feedback_pb2.pyi
   │     │  │  ├─ FileUploader_pb2.py
   │     │  │  ├─ FileUploader_pb2.pyi
   │     │  │  ├─ ForwardMsg_pb2.py
   │     │  │  ├─ ForwardMsg_pb2.pyi
   │     │  │  ├─ GapSize_pb2.py
   │     │  │  ├─ GapSize_pb2.pyi
   │     │  │  ├─ GitInfo_pb2.py
   │     │  │  ├─ GitInfo_pb2.pyi
   │     │  │  ├─ GraphVizChart_pb2.py
   │     │  │  ├─ GraphVizChart_pb2.pyi
   │     │  │  ├─ Heading_pb2.py
   │     │  │  ├─ Heading_pb2.pyi
   │     │  │  ├─ HeightConfig_pb2.py
   │     │  │  ├─ HeightConfig_pb2.pyi
   │     │  │  ├─ Help_pb2.py
   │     │  │  ├─ Help_pb2.pyi
   │     │  │  ├─ Html_pb2.py
   │     │  │  ├─ Html_pb2.pyi
   │     │  │  ├─ IFrame_pb2.py
   │     │  │  ├─ IFrame_pb2.pyi
   │     │  │  ├─ Image_pb2.py
   │     │  │  ├─ Image_pb2.pyi
   │     │  │  ├─ Json_pb2.py
   │     │  │  ├─ Json_pb2.pyi
   │     │  │  ├─ LabelVisibility_pb2.py
   │     │  │  ├─ LabelVisibility_pb2.pyi
   │     │  │  ├─ LinkButton_pb2.py
   │     │  │  ├─ LinkButton_pb2.pyi
   │     │  │  ├─ Logo_pb2.py
   │     │  │  ├─ Logo_pb2.pyi
   │     │  │  ├─ Markdown_pb2.py
   │     │  │  ├─ Markdown_pb2.pyi
   │     │  │  ├─ MenuButton_pb2.py
   │     │  │  ├─ MenuButton_pb2.pyi
   │     │  │  ├─ MetricsEvent_pb2.py
   │     │  │  ├─ MetricsEvent_pb2.pyi
   │     │  │  ├─ Metric_pb2.py
   │     │  │  ├─ Metric_pb2.pyi
   │     │  │  ├─ MultiSelect_pb2.py
   │     │  │  ├─ MultiSelect_pb2.pyi
   │     │  │  ├─ Navigation_pb2.py
   │     │  │  ├─ Navigation_pb2.pyi
   │     │  │  ├─ NewSession_pb2.py
   │     │  │  ├─ NewSession_pb2.pyi
   │     │  │  ├─ NumberInput_pb2.py
   │     │  │  ├─ NumberInput_pb2.pyi
   │     │  │  ├─ openmetrics_data_model_pb2.py
   │     │  │  ├─ openmetrics_data_model_pb2.pyi
   │     │  │  ├─ PageConfig_pb2.py
   │     │  │  ├─ PageConfig_pb2.pyi
   │     │  │  ├─ PageInfo_pb2.py
   │     │  │  ├─ PageInfo_pb2.pyi
   │     │  │  ├─ PageLink_pb2.py
   │     │  │  ├─ PageLink_pb2.pyi
   │     │  │  ├─ PageNotFound_pb2.py
   │     │  │  ├─ PageNotFound_pb2.pyi
   │     │  │  ├─ PageProfile_pb2.py
   │     │  │  ├─ PageProfile_pb2.pyi
   │     │  │  ├─ ParentMessage_pb2.py
   │     │  │  ├─ ParentMessage_pb2.pyi
   │     │  │  ├─ PlotlyChart_pb2.py
   │     │  │  ├─ PlotlyChart_pb2.pyi
   │     │  │  ├─ Progress_pb2.py
   │     │  │  ├─ Progress_pb2.pyi
   │     │  │  ├─ Radio_pb2.py
   │     │  │  ├─ Radio_pb2.pyi
   │     │  │  ├─ RootContainer_pb2.py
   │     │  │  ├─ RootContainer_pb2.pyi
   │     │  │  ├─ Selectbox_pb2.py
   │     │  │  ├─ Selectbox_pb2.pyi
   │     │  │  ├─ SelectWidgetFilterMode_pb2.py
   │     │  │  ├─ SelectWidgetFilterMode_pb2.pyi
   │     │  │  ├─ SessionEvent_pb2.py
   │     │  │  ├─ SessionEvent_pb2.pyi
   │     │  │  ├─ SessionStatus_pb2.py
   │     │  │  ├─ SessionStatus_pb2.pyi
   │     │  │  ├─ Skeleton_pb2.py
   │     │  │  ├─ Skeleton_pb2.pyi
   │     │  │  ├─ Slider_pb2.py
   │     │  │  ├─ Slider_pb2.pyi
   │     │  │  ├─ Snow_pb2.py
   │     │  │  ├─ Snow_pb2.pyi
   │     │  │  ├─ Space_pb2.py
   │     │  │  ├─ Space_pb2.pyi
   │     │  │  ├─ Spinner_pb2.py
   │     │  │  ├─ Spinner_pb2.pyi
   │     │  │  ├─ Table_pb2.py
   │     │  │  ├─ Table_pb2.pyi
   │     │  │  ├─ TextAlignmentConfig_pb2.py
   │     │  │  ├─ TextAlignmentConfig_pb2.pyi
   │     │  │  ├─ TextArea_pb2.py
   │     │  │  ├─ TextArea_pb2.pyi
   │     │  │  ├─ TextInput_pb2.py
   │     │  │  ├─ TextInput_pb2.pyi
   │     │  │  ├─ Text_pb2.py
   │     │  │  ├─ Text_pb2.pyi
   │     │  │  ├─ TimeInput_pb2.py
   │     │  │  ├─ TimeInput_pb2.pyi
   │     │  │  ├─ Toast_pb2.py
   │     │  │  ├─ Toast_pb2.pyi
   │     │  │  ├─ Transient_pb2.py
   │     │  │  ├─ Transient_pb2.pyi
   │     │  │  ├─ VegaLiteChart_pb2.py
   │     │  │  ├─ VegaLiteChart_pb2.pyi
   │     │  │  ├─ Video_pb2.py
   │     │  │  ├─ Video_pb2.pyi
   │     │  │  ├─ WidgetStates_pb2.py
   │     │  │  ├─ WidgetStates_pb2.pyi
   │     │  │  ├─ WidthConfig_pb2.py
   │     │  │  ├─ WidthConfig_pb2.pyi
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ Alert_pb2.cpython-311.pyc
   │     │  │     ├─ AppPage_pb2.cpython-311.pyc
   │     │  │     ├─ ArrowData_pb2.cpython-311.pyc
   │     │  │     ├─ ArrowNamedDataSet_pb2.cpython-311.pyc
   │     │  │     ├─ AudioInput_pb2.cpython-311.pyc
   │     │  │     ├─ Audio_pb2.cpython-311.pyc
   │     │  │     ├─ AuthRedirect_pb2.cpython-311.pyc
   │     │  │     ├─ AutoRerun_pb2.cpython-311.pyc
   │     │  │     ├─ BackMsg_pb2.cpython-311.pyc
   │     │  │     ├─ Balloons_pb2.cpython-311.pyc
   │     │  │     ├─ BidiComponent_pb2.cpython-311.pyc
   │     │  │     ├─ Block_pb2.cpython-311.pyc
   │     │  │     ├─ ButtonGroup_pb2.cpython-311.pyc
   │     │  │     ├─ ButtonLikeIconPosition_pb2.cpython-311.pyc
   │     │  │     ├─ Button_pb2.cpython-311.pyc
   │     │  │     ├─ CameraInput_pb2.cpython-311.pyc
   │     │  │     ├─ ChatInput_pb2.cpython-311.pyc
   │     │  │     ├─ Checkbox_pb2.cpython-311.pyc
   │     │  │     ├─ ClientState_pb2.cpython-311.pyc
   │     │  │     ├─ Code_pb2.cpython-311.pyc
   │     │  │     ├─ ColorPicker_pb2.cpython-311.pyc
   │     │  │     ├─ Common_pb2.cpython-311.pyc
   │     │  │     ├─ Components_pb2.cpython-311.pyc
   │     │  │     ├─ Dataframe_pb2.cpython-311.pyc
   │     │  │     ├─ DateInput_pb2.cpython-311.pyc
   │     │  │     ├─ DateTimeInput_pb2.cpython-311.pyc
   │     │  │     ├─ DeckGlJsonChart_pb2.cpython-311.pyc
   │     │  │     ├─ Delta_pb2.cpython-311.pyc
   │     │  │     ├─ DownloadButton_pb2.cpython-311.pyc
   │     │  │     ├─ Element_pb2.cpython-311.pyc
   │     │  │     ├─ Empty_pb2.cpython-311.pyc
   │     │  │     ├─ Exception_pb2.cpython-311.pyc
   │     │  │     ├─ Favicon_pb2.cpython-311.pyc
   │     │  │     ├─ Feedback_pb2.cpython-311.pyc
   │     │  │     ├─ FileUploader_pb2.cpython-311.pyc
   │     │  │     ├─ ForwardMsg_pb2.cpython-311.pyc
   │     │  │     ├─ GapSize_pb2.cpython-311.pyc
   │     │  │     ├─ GitInfo_pb2.cpython-311.pyc
   │     │  │     ├─ GraphVizChart_pb2.cpython-311.pyc
   │     │  │     ├─ Heading_pb2.cpython-311.pyc
   │     │  │     ├─ HeightConfig_pb2.cpython-311.pyc
   │     │  │     ├─ Help_pb2.cpython-311.pyc
   │     │  │     ├─ Html_pb2.cpython-311.pyc
   │     │  │     ├─ IFrame_pb2.cpython-311.pyc
   │     │  │     ├─ Image_pb2.cpython-311.pyc
   │     │  │     ├─ Json_pb2.cpython-311.pyc
   │     │  │     ├─ LabelVisibility_pb2.cpython-311.pyc
   │     │  │     ├─ LinkButton_pb2.cpython-311.pyc
   │     │  │     ├─ Logo_pb2.cpython-311.pyc
   │     │  │     ├─ Markdown_pb2.cpython-311.pyc
   │     │  │     ├─ MenuButton_pb2.cpython-311.pyc
   │     │  │     ├─ MetricsEvent_pb2.cpython-311.pyc
   │     │  │     ├─ Metric_pb2.cpython-311.pyc
   │     │  │     ├─ MultiSelect_pb2.cpython-311.pyc
   │     │  │     ├─ Navigation_pb2.cpython-311.pyc
   │     │  │     ├─ NewSession_pb2.cpython-311.pyc
   │     │  │     ├─ NumberInput_pb2.cpython-311.pyc
   │     │  │     ├─ openmetrics_data_model_pb2.cpython-311.pyc
   │     │  │     ├─ PageConfig_pb2.cpython-311.pyc
   │     │  │     ├─ PageInfo_pb2.cpython-311.pyc
   │     │  │     ├─ PageLink_pb2.cpython-311.pyc
   │     │  │     ├─ PageNotFound_pb2.cpython-311.pyc
   │     │  │     ├─ PageProfile_pb2.cpython-311.pyc
   │     │  │     ├─ ParentMessage_pb2.cpython-311.pyc
   │     │  │     ├─ PlotlyChart_pb2.cpython-311.pyc
   │     │  │     ├─ Progress_pb2.cpython-311.pyc
   │     │  │     ├─ Radio_pb2.cpython-311.pyc
   │     │  │     ├─ RootContainer_pb2.cpython-311.pyc
   │     │  │     ├─ Selectbox_pb2.cpython-311.pyc
   │     │  │     ├─ SelectWidgetFilterMode_pb2.cpython-311.pyc
   │     │  │     ├─ SessionEvent_pb2.cpython-311.pyc
   │     │  │     ├─ SessionStatus_pb2.cpython-311.pyc
   │     │  │     ├─ Skeleton_pb2.cpython-311.pyc
   │     │  │     ├─ Slider_pb2.cpython-311.pyc
   │     │  │     ├─ Snow_pb2.cpython-311.pyc
   │     │  │     ├─ Space_pb2.cpython-311.pyc
   │     │  │     ├─ Spinner_pb2.cpython-311.pyc
   │     │  │     ├─ Table_pb2.cpython-311.pyc
   │     │  │     ├─ TextAlignmentConfig_pb2.cpython-311.pyc
   │     │  │     ├─ TextArea_pb2.cpython-311.pyc
   │     │  │     ├─ TextInput_pb2.cpython-311.pyc
   │     │  │     ├─ Text_pb2.cpython-311.pyc
   │     │  │     ├─ TimeInput_pb2.cpython-311.pyc
   │     │  │     ├─ Toast_pb2.cpython-311.pyc
   │     │  │     ├─ Transient_pb2.cpython-311.pyc
   │     │  │     ├─ VegaLiteChart_pb2.cpython-311.pyc
   │     │  │     ├─ Video_pb2.cpython-311.pyc
   │     │  │     ├─ WidgetStates_pb2.cpython-311.pyc
   │     │  │     ├─ WidthConfig_pb2.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ py.typed
   │     │  ├─ runtime
   │     │  │  ├─ app_session.py
   │     │  │  ├─ caching
   │     │  │  │  ├─ cached_message_replay.py
   │     │  │  │  ├─ cache_data_api.py
   │     │  │  │  ├─ cache_errors.py
   │     │  │  │  ├─ cache_resource_api.py
   │     │  │  │  ├─ cache_type.py
   │     │  │  │  ├─ cache_utils.py
   │     │  │  │  ├─ hashing.py
   │     │  │  │  ├─ legacy_cache_api.py
   │     │  │  │  ├─ storage
   │     │  │  │  │  ├─ cache_storage_protocol.py
   │     │  │  │  │  ├─ dummy_cache_storage.py
   │     │  │  │  │  ├─ in_memory_cache_storage_wrapper.py
   │     │  │  │  │  ├─ local_disk_cache_storage.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ cache_storage_protocol.cpython-311.pyc
   │     │  │  │  │     ├─ dummy_cache_storage.cpython-311.pyc
   │     │  │  │  │     ├─ in_memory_cache_storage_wrapper.cpython-311.pyc
   │     │  │  │  │     ├─ local_disk_cache_storage.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ ttl_cleanup_cache.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ cached_message_replay.cpython-311.pyc
   │     │  │  │     ├─ cache_data_api.cpython-311.pyc
   │     │  │  │     ├─ cache_errors.cpython-311.pyc
   │     │  │  │     ├─ cache_resource_api.cpython-311.pyc
   │     │  │  │     ├─ cache_type.cpython-311.pyc
   │     │  │  │     ├─ cache_utils.cpython-311.pyc
   │     │  │  │     ├─ hashing.cpython-311.pyc
   │     │  │  │     ├─ legacy_cache_api.cpython-311.pyc
   │     │  │  │     ├─ ttl_cleanup_cache.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ connection_factory.py
   │     │  │  ├─ context.py
   │     │  │  ├─ context_util.py
   │     │  │  ├─ credentials.py
   │     │  │  ├─ download_data_util.py
   │     │  │  ├─ forward_msg_cache.py
   │     │  │  ├─ forward_msg_queue.py
   │     │  │  ├─ fragment.py
   │     │  │  ├─ media_file_manager.py
   │     │  │  ├─ media_file_storage.py
   │     │  │  ├─ memory_media_file_storage.py
   │     │  │  ├─ memory_session_storage.py
   │     │  │  ├─ memory_uploaded_file_manager.py
   │     │  │  ├─ metrics_util.py
   │     │  │  ├─ pages_manager.py
   │     │  │  ├─ runtime.py
   │     │  │  ├─ runtime_util.py
   │     │  │  ├─ scriptrunner
   │     │  │  │  ├─ exec_code.py
   │     │  │  │  ├─ magic.py
   │     │  │  │  ├─ magic_funcs.py
   │     │  │  │  ├─ script_cache.py
   │     │  │  │  ├─ script_runner.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ exec_code.cpython-311.pyc
   │     │  │  │     ├─ magic.cpython-311.pyc
   │     │  │  │     ├─ magic_funcs.cpython-311.pyc
   │     │  │  │     ├─ script_cache.cpython-311.pyc
   │     │  │  │     ├─ script_runner.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ scriptrunner_utils
   │     │  │  │  ├─ exceptions.py
   │     │  │  │  ├─ script_requests.py
   │     │  │  │  ├─ script_run_context.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ exceptions.cpython-311.pyc
   │     │  │  │     ├─ script_requests.cpython-311.pyc
   │     │  │  │     ├─ script_run_context.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ script_data.py
   │     │  │  ├─ secrets.py
   │     │  │  ├─ session_manager.py
   │     │  │  ├─ state
   │     │  │  │  ├─ common.py
   │     │  │  │  ├─ presentation.py
   │     │  │  │  ├─ query_params.py
   │     │  │  │  ├─ query_params_proxy.py
   │     │  │  │  ├─ safe_session_state.py
   │     │  │  │  ├─ session_state.py
   │     │  │  │  ├─ session_state_proxy.py
   │     │  │  │  ├─ widgets.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ common.cpython-311.pyc
   │     │  │  │     ├─ presentation.cpython-311.pyc
   │     │  │  │     ├─ query_params.cpython-311.pyc
   │     │  │  │     ├─ query_params_proxy.cpython-311.pyc
   │     │  │  │     ├─ safe_session_state.cpython-311.pyc
   │     │  │  │     ├─ session_state.cpython-311.pyc
   │     │  │  │     ├─ session_state_proxy.cpython-311.pyc
   │     │  │  │     ├─ widgets.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ stats.py
   │     │  │  ├─ theme_util.py
   │     │  │  ├─ uploaded_file_manager.py
   │     │  │  ├─ websocket_session_manager.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ app_session.cpython-311.pyc
   │     │  │     ├─ connection_factory.cpython-311.pyc
   │     │  │     ├─ context.cpython-311.pyc
   │     │  │     ├─ context_util.cpython-311.pyc
   │     │  │     ├─ credentials.cpython-311.pyc
   │     │  │     ├─ download_data_util.cpython-311.pyc
   │     │  │     ├─ forward_msg_cache.cpython-311.pyc
   │     │  │     ├─ forward_msg_queue.cpython-311.pyc
   │     │  │     ├─ fragment.cpython-311.pyc
   │     │  │     ├─ media_file_manager.cpython-311.pyc
   │     │  │     ├─ media_file_storage.cpython-311.pyc
   │     │  │     ├─ memory_media_file_storage.cpython-311.pyc
   │     │  │     ├─ memory_session_storage.cpython-311.pyc
   │     │  │     ├─ memory_uploaded_file_manager.cpython-311.pyc
   │     │  │     ├─ metrics_util.cpython-311.pyc
   │     │  │     ├─ pages_manager.cpython-311.pyc
   │     │  │     ├─ runtime.cpython-311.pyc
   │     │  │     ├─ runtime_util.cpython-311.pyc
   │     │  │     ├─ script_data.cpython-311.pyc
   │     │  │     ├─ secrets.cpython-311.pyc
   │     │  │     ├─ session_manager.cpython-311.pyc
   │     │  │     ├─ stats.cpython-311.pyc
   │     │  │     ├─ theme_util.cpython-311.pyc
   │     │  │     ├─ uploaded_file_manager.cpython-311.pyc
   │     │  │     ├─ websocket_session_manager.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ source_util.py
   │     │  ├─ starlette.py
   │     │  ├─ static
   │     │  │  ├─ favicon.png
   │     │  │  ├─ index.html
   │     │  │  ├─ manifest.json
   │     │  │  └─ static
   │     │  │     ├─ css
   │     │  │     │  ├─ DataFrame.DUkanX9_.css
   │     │  │     │  ├─ DeckGlJsonChart.s6LXjV0D.css
   │     │  │     │  ├─ index.D5HInCXB.css
   │     │  │     │  └─ katex.B5r0Qy_s.css
   │     │  │     ├─ js
   │     │  │     │  ├─ ArrowVegaLiteChart.BgaFuvXj.js
   │     │  │     │  ├─ assertNever.mU6MN8YK.js
   │     │  │     │  ├─ Audio.DVdpy7BU.js
   │     │  │     │  ├─ AudioInput.TfAPbJRC.js
   │     │  │     │  ├─ axios.BPGFmyVv.js
   │     │  │     │  ├─ Balloons.JTmp0dzs.js
   │     │  │     │  ├─ base-input.BCpWsOz-.js
   │     │  │     │  ├─ BidiComponent.3S0iM8vz.js
   │     │  │     │  ├─ Button.Hj_dGHW6.js
   │     │  │     │  ├─ ButtonGroup.BXeBtkCq.js
   │     │  │     │  ├─ CameraInput.uIuk6ccb.js
   │     │  │     │  ├─ ChatInput.B3lt_SJW.js
   │     │  │     │  ├─ checkbox.BKzSOQIB.js
   │     │  │     │  ├─ Checkbox.Czpn5mOz.js
   │     │  │     │  ├─ chunk.DuxOD-Sk.js
   │     │  │     │  ├─ click-outside-container.D4IIXuyx.js
   │     │  │     │  ├─ ColorPicker.B4HXakbQ.js
   │     │  │     │  ├─ ComponentInstance.BRYZ-p_b.js
   │     │  │     │  ├─ config.DACbyDxu.js
   │     │  │     │  ├─ createDownloadLinkElement.B-T6Vdep.js
   │     │  │     │  ├─ data-grid-overlay-editor.D6LzjOmD.js
   │     │  │     │  ├─ DataFrame.B0wXvMOP.js
   │     │  │     │  ├─ DataFrame.BgahE5yf.js
   │     │  │     │  ├─ DateInput.C2LzvXf1.js
   │     │  │     │  ├─ DateTimeInput.WrWXWIMp.js
   │     │  │     │  ├─ DeckGlJsonChart.DputmGud.js
   │     │  │     │  ├─ dist.A11CXetj.js
   │     │  │     │  ├─ dist.DdsunV6A.js
   │     │  │     │  ├─ DownloadButton.BQoUqc_h.js
   │     │  │     │  ├─ downloader.BV1UiReQ.js
   │     │  │     │  ├─ DynamicIcon.D2luRNwf.js
   │     │  │     │  ├─ embed.BwU7eQR9.js
   │     │  │     │  ├─ emotion-is-prop-valid.esm.DV_OErv-.js
   │     │  │     │  ├─ emotion-styled.browser.esm.j1V2KkYw.js
   │     │  │     │  ├─ eq.BGqw_fW_.js
   │     │  │     │  ├─ ErrorElement.xCwUz6pJ.js
   │     │  │     │  ├─ ErrorOutline.esm.Cxx-qceN.js
   │     │  │     │  ├─ es6.BTMf8SGQ.js
   │     │  │     │  ├─ Feedback.DtOndIfL.js
   │     │  │     │  ├─ FileDownload.esm.BdW3jFEZ.js
   │     │  │     │  ├─ FileSystemDirectoryHandle.BKJzl0Bz.js
   │     │  │     │  ├─ FileSystemFileHandle.CQgtHVCp.js
   │     │  │     │  ├─ FileSystemHandle._FKvy7zP.js
   │     │  │     │  ├─ FileUploader.B5S2eV1g.js
   │     │  │     │  ├─ formatMoment.Dc51VdnH.js
   │     │  │     │  ├─ formatNumber.DnA3ZyCB.js
   │     │  │     │  ├─ FormClearHelper.DN2kTD-G.js
   │     │  │     │  ├─ FormSubmitContent.CetWAxjW.js
   │     │  │     │  ├─ getColors.BEaEwBzZ.js
   │     │  │     │  ├─ GraphVizChart.DB7xGpeO.js
   │     │  │     │  ├─ hastscript.DafCiGgE.js
   │     │  │     │  ├─ Html.Clzed01O.js
   │     │  │     │  ├─ iconPosition.CdmCI0sD.js
   │     │  │     │  ├─ IFrame.XAqDW6_G.js
   │     │  │     │  ├─ iframeResizer.contentWindow.DWzQ-oz2.js
   │     │  │     │  ├─ IFrameUtil.CiJyrZfZ.js
   │     │  │     │  ├─ ImageList.B79aWf7B.js
   │     │  │     │  ├─ index.k-9rUdPI.js
   │     │  │     │  ├─ input.DBFWi917.js
   │     │  │     │  ├─ InputInstructions.PWNfQco1.js
   │     │  │     │  ├─ inputUtils.Byd2SrPo.js
   │     │  │     │  ├─ isArguments.CEs-JkNn.js
   │     │  │     │  ├─ isLength.Dot76Eow.js
   │     │  │     │  ├─ isSymbol.CDgzX1Rm.js
   │     │  │     │  ├─ Json.-8FfjBFP.js
   │     │  │     │  ├─ katex.min.YR_J8GMy.js
   │     │  │     │  ├─ lib.B_Qh5M3c.js
   │     │  │     │  ├─ lib.CBj_K-OS.js
   │     │  │     │  ├─ lib.CsmfjxBh.js
   │     │  │     │  ├─ lib.Cv6eTW_C.js
   │     │  │     │  ├─ LinkButton.CUlfWtZm.js
   │     │  │     │  ├─ loglevel.H4SN4KQm.js
   │     │  │     │  ├─ memory.BVqsnNa9.js
   │     │  │     │  ├─ MenuButton.CkrUQxUV.js
   │     │  │     │  ├─ Metric.DF8T1EpJ.js
   │     │  │     │  ├─ moment.DPazYqn3.js
   │     │  │     │  ├─ Multiselect.CCXI2AlG.js
   │     │  │     │  ├─ number-overlay-editor.CZ2WpGgL.js
   │     │  │     │  ├─ NumberInput.AsqciBnX.js
   │     │  │     │  ├─ numbro.C2rdNegt.js
   │     │  │     │  ├─ PageLink.Hz0BEV_T.js
   │     │  │     │  ├─ pandasStylerUtils.GZKmwX22.js
   │     │  │     │  ├─ Particles.Dqljt1pN.js
   │     │  │     │  ├─ PlotlyChart.CBOrhmVc.js
   │     │  │     │  ├─ PortalContext.Bg1T10mv.js
   │     │  │     │  ├─ possibleConstructorReturn.VpVYTsiS.js
   │     │  │     │  ├─ preload-helper.CoWfPq16.js
   │     │  │     │  ├─ Progress.DKhnyE6H.js
   │     │  │     │  ├─ ProgressBar.C73530Ij.js
   │     │  │     │  ├─ protobuf.DYxUUxb3.js
   │     │  │     │  ├─ Radio.C0JFcs8M.js
   │     │  │     │  ├─ reactJsonViewCompat.C6CTzcn3.js
   │     │  │     │  ├─ record.DUa-llRd.js
   │     │  │     │  ├─ rehype-katex.DVT-WRwH.js
   │     │  │     │  ├─ rehype-raw.Dgaibtrn.js
   │     │  │     │  ├─ remark-emoji.DuJHwH0n.js
   │     │  │     │  ├─ resolveDefaultExport.DPeOhot3.js
   │     │  │     │  ├─ sandbox.BBGM6nH4.js
   │     │  │     │  ├─ Selectbox.BXbl2es5.js
   │     │  │     │  ├─ Slider.BrkNAuxL.js
   │     │  │     │  ├─ Snow.a4omAiaI.js
   │     │  │     │  ├─ space-separated-tokens.DQiA2tSI.js
   │     │  │     │  ├─ Spinner.BlF8qQwd.js
   │     │  │     │  ├─ sprintfjs.BY72gOw3.js
   │     │  │     │  ├─ src.BE12mjIH.js
   │     │  │     │  ├─ src.BnXM6qiK.js
   │     │  │     │  ├─ StreamlitSyntaxHighlighter.DH2RtWai.js
   │     │  │     │  ├─ styled-components.ShTfqeM5.js
   │     │  │     │  ├─ Table.B0sRe7km.js
   │     │  │     │  ├─ TableChart.esm.Bcz_qI55.js
   │     │  │     │  ├─ TextArea.BLSs-yzT.js
   │     │  │     │  ├─ TextInput.BR_ERkRL.js
   │     │  │     │  ├─ threshold.CMPFSu_V.js
   │     │  │     │  ├─ TimeInput.xjeK4dwL.js
   │     │  │     │  ├─ timepicker.Cq_RyggO.js
   │     │  │     │  ├─ timer.C1LL4d3i.js
   │     │  │     │  ├─ Toast.Bzt5VJpT.js
   │     │  │     │  ├─ toConsumableArray.CMlzSAzJ.js
   │     │  │     │  ├─ toString.BkSzPhlJ.js
   │     │  │     │  ├─ UploadFileInfo.Cf3tZVPo.js
   │     │  │     │  ├─ UriUtil.iHepHDsL.js
   │     │  │     │  ├─ urls.EQJ-7zG1.js
   │     │  │     │  ├─ useBasicWidgetState.eEcmgPXG.js
   │     │  │     │  ├─ useCopyToClipboard.qxi5xnmv.js
   │     │  │     │  ├─ useCrossOriginAttribute.CgfxJ_46.js
   │     │  │     │  ├─ useEmotionTheme.C795Rarg.js
   │     │  │     │  ├─ useIntlLocale.D0-u8iwM.js
   │     │  │     │  ├─ useRequiredContext.C6MAk7EW.js
   │     │  │     │  ├─ useTextInputAutoExpand.CtVDXTc2.js
   │     │  │     │  ├─ useTimeout.Bx6_cYZk.js
   │     │  │     │  ├─ useUpdateUiValue.4BpllAT6.js
   │     │  │     │  ├─ useWaveformController.BeQueWNP.js
   │     │  │     │  ├─ useWindowDimensionsContext.-OfdvZoJ.js
   │     │  │     │  ├─ util.B0Prp0qp.js
   │     │  │     │  ├─ utils.CU17Veq9.js
   │     │  │     │  ├─ utils.DOkIMtzG.js
   │     │  │     │  ├─ utils.DyQFaQ9q.js
   │     │  │     │  ├─ utils2.W7NPIKaJ.js
   │     │  │     │  ├─ v4.Dwn3ecIa.js
   │     │  │     │  ├─ Video.C6ajvIyH.js
   │     │  │     │  ├─ wavesurfer.esm.DYRfx2Vs.js
   │     │  │     │  ├─ web-namespaces.aHXsjywx.js
   │     │  │     │  ├─ webgl-device.Dfp4sxhf.js
   │     │  │     │  ├─ withCalculatedWidth.C7Q8zdoQ.js
   │     │  │     │  ├─ withFullScreenWrapper.B4kf8iv-.js
   │     │  │     │  ├─ _arrayIncludesWith.C7He3_lH.js
   │     │  │     │  ├─ _baseIndexOf.DmzSbCrC.js
   │     │  │     │  ├─ _hasPath.DerTBTUd.js
   │     │  │     │  ├─ _isIterateeCall.B_kjaL0b.js
   │     │  │     │  └─ _toKey.IZoVG-B2.js
   │     │  │     ├─ media
   │     │  │     │  ├─ balloon-0.Czj7AKwE.png
   │     │  │     │  ├─ balloon-1.CNvFFrND.png
   │     │  │     │  ├─ balloon-2.DTvC6B1t.png
   │     │  │     │  ├─ balloon-3.CgSk4tbL.png
   │     │  │     │  ├─ balloon-4.mbtFrzxf.png
   │     │  │     │  ├─ balloon-5.CSwkUfRA.png
   │     │  │     │  ├─ fireworks.B4d-_KUe.gif
   │     │  │     │  ├─ flake-0.DgWaVvm5.png
   │     │  │     │  ├─ flake-1.B2r5AHMK.png
   │     │  │     │  ├─ flake-2.BnWSExPC.png
   │     │  │     │  ├─ KaTeX_AMS-Regular.BQhdFMY1.woff2
   │     │  │     │  ├─ KaTeX_AMS-Regular.DMm9YOAa.woff
   │     │  │     │  ├─ KaTeX_AMS-Regular.DRggAlZN.ttf
   │     │  │     │  ├─ KaTeX_Caligraphic-Bold.ATXxdsX0.ttf
   │     │  │     │  ├─ KaTeX_Caligraphic-Bold.BEiXGLvX.woff
   │     │  │     │  ├─ KaTeX_Caligraphic-Bold.Dq_IR9rO.woff2
   │     │  │     │  ├─ KaTeX_Caligraphic-Regular.CTRA-rTL.woff
   │     │  │     │  ├─ KaTeX_Caligraphic-Regular.Di6jR-x-.woff2
   │     │  │     │  ├─ KaTeX_Caligraphic-Regular.wX97UBjC.ttf
   │     │  │     │  ├─ KaTeX_Fraktur-Bold.BdnERNNW.ttf
   │     │  │     │  ├─ KaTeX_Fraktur-Bold.BsDP51OF.woff
   │     │  │     │  ├─ KaTeX_Fraktur-Bold.CL6g_b3V.woff2
   │     │  │     │  ├─ KaTeX_Fraktur-Regular.CB_wures.ttf
   │     │  │     │  ├─ KaTeX_Fraktur-Regular.CTYiF6lA.woff2
   │     │  │     │  ├─ KaTeX_Fraktur-Regular.Dxdc4cR9.woff
   │     │  │     │  ├─ KaTeX_Main-Bold.Cx986IdX.woff2
   │     │  │     │  ├─ KaTeX_Main-Bold.Jm3AIy58.woff
   │     │  │     │  ├─ KaTeX_Main-Bold.waoOVXN0.ttf
   │     │  │     │  ├─ KaTeX_Main-BoldItalic.DxDJ3AOS.woff2
   │     │  │     │  ├─ KaTeX_Main-BoldItalic.DzxPMmG6.ttf
   │     │  │     │  ├─ KaTeX_Main-BoldItalic.SpSLRI95.woff
   │     │  │     │  ├─ KaTeX_Main-Italic.3WenGoN9.ttf
   │     │  │     │  ├─ KaTeX_Main-Italic.BMLOBm91.woff
   │     │  │     │  ├─ KaTeX_Main-Italic.NWA7e6Wa.woff2
   │     │  │     │  ├─ KaTeX_Main-Regular.B22Nviop.woff2
   │     │  │     │  ├─ KaTeX_Main-Regular.Dr94JaBh.woff
   │     │  │     │  ├─ KaTeX_Main-Regular.ypZvNtVU.ttf
   │     │  │     │  ├─ KaTeX_Math-BoldItalic.B3XSjfu4.ttf
   │     │  │     │  ├─ KaTeX_Math-BoldItalic.CZnvNsCZ.woff2
   │     │  │     │  ├─ KaTeX_Math-BoldItalic.iY-2wyZ7.woff
   │     │  │     │  ├─ KaTeX_Math-Italic.DA0__PXp.woff
   │     │  │     │  ├─ KaTeX_Math-Italic.flOr_0UB.ttf
   │     │  │     │  ├─ KaTeX_Math-Italic.t53AETM-.woff2
   │     │  │     │  ├─ KaTeX_SansSerif-Bold.CFMepnvq.ttf
   │     │  │     │  ├─ KaTeX_SansSerif-Bold.D1sUS0GD.woff2
   │     │  │     │  ├─ KaTeX_SansSerif-Bold.DbIhKOiC.woff
   │     │  │     │  ├─ KaTeX_SansSerif-Italic.C3H0VqGB.woff2
   │     │  │     │  ├─ KaTeX_SansSerif-Italic.DN2j7dab.woff
   │     │  │     │  ├─ KaTeX_SansSerif-Italic.YYjJ1zSn.ttf
   │     │  │     │  ├─ KaTeX_SansSerif-Regular.BNo7hRIc.ttf
   │     │  │     │  ├─ KaTeX_SansSerif-Regular.CS6fqUqJ.woff
   │     │  │     │  ├─ KaTeX_SansSerif-Regular.DDBCnlJ7.woff2
   │     │  │     │  ├─ KaTeX_Script-Regular.C5JkGWo-.ttf
   │     │  │     │  ├─ KaTeX_Script-Regular.D3wIWfF6.woff2
   │     │  │     │  ├─ KaTeX_Script-Regular.D5yQViql.woff
   │     │  │     │  ├─ KaTeX_Size1-Regular.C195tn64.woff
   │     │  │     │  ├─ KaTeX_Size1-Regular.Dbsnue_I.ttf
   │     │  │     │  ├─ KaTeX_Size1-Regular.mCD8mA8B.woff2
   │     │  │     │  ├─ KaTeX_Size2-Regular.B7gKUWhC.ttf
   │     │  │     │  ├─ KaTeX_Size2-Regular.Dy4dx90m.woff2
   │     │  │     │  ├─ KaTeX_Size2-Regular.oD1tc_U0.woff
   │     │  │     │  ├─ KaTeX_Size3-Regular.CTq5MqoE.woff
   │     │  │     │  ├─ KaTeX_Size3-Regular.DgpXs0kz.ttf
   │     │  │     │  ├─ KaTeX_Size4-Regular.BF-4gkZK.woff
   │     │  │     │  ├─ KaTeX_Size4-Regular.Dl5lxZxV.woff2
   │     │  │     │  ├─ KaTeX_Size4-Regular.DWFBv043.ttf
   │     │  │     │  ├─ KaTeX_Typewriter-Regular.C0xS9mPB.woff
   │     │  │     │  ├─ KaTeX_Typewriter-Regular.CO6r4hn1.woff2
   │     │  │     │  ├─ KaTeX_Typewriter-Regular.D3Ib7_Hf.ttf
   │     │  │     │  ├─ MaterialSymbols-Rounded.BK8hQpFn.woff2
   │     │  │     │  ├─ snowflake.JU2jBHL8.svg
   │     │  │     │  ├─ SourceCodeVF-Italic.ttf.Ba1oaZG1.woff2
   │     │  │     │  ├─ SourceCodeVF-Upright.ttf.BjWn63N-.woff2
   │     │  │     │  ├─ SourceSansVF-Italic.ttf.Bt9VkdQ3.woff2
   │     │  │     │  ├─ SourceSansVF-Upright.ttf.BsWL4Kly.woff2
   │     │  │     │  ├─ SourceSerifVariable-Italic.ttf.CVdzAtxO.woff2
   │     │  │     │  └─ SourceSerifVariable-Roman.ttf.mdpVL9bi.woff2
   │     │  │     └─ worker-DD5bG58f.js
   │     │  ├─ string_util.py
   │     │  ├─ temporary_directory.py
   │     │  ├─ testing
   │     │  │  ├─ v1
   │     │  │  │  ├─ app_test.py
   │     │  │  │  ├─ element_tree.py
   │     │  │  │  ├─ local_script_runner.py
   │     │  │  │  ├─ util.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ app_test.cpython-311.pyc
   │     │  │  │     ├─ element_tree.cpython-311.pyc
   │     │  │  │     ├─ local_script_runner.cpython-311.pyc
   │     │  │  │     ├─ util.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ time_util.py
   │     │  ├─ type_util.py
   │     │  ├─ url_util.py
   │     │  ├─ user_info.py
   │     │  ├─ util.py
   │     │  ├─ vendor
   │     │  │  ├─ pympler
   │     │  │  │  ├─ asizeof.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ asizeof.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ version.py
   │     │  ├─ watcher
   │     │  │  ├─ event_based_path_watcher.py
   │     │  │  ├─ folder_black_list.py
   │     │  │  ├─ local_sources_watcher.py
   │     │  │  ├─ path_watcher.py
   │     │  │  ├─ polling_path_watcher.py
   │     │  │  ├─ util.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ event_based_path_watcher.cpython-311.pyc
   │     │  │     ├─ folder_black_list.cpython-311.pyc
   │     │  │     ├─ local_sources_watcher.cpython-311.pyc
   │     │  │     ├─ path_watcher.cpython-311.pyc
   │     │  │     ├─ polling_path_watcher.cpython-311.pyc
   │     │  │     ├─ util.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ web
   │     │  │  ├─ bootstrap.py
   │     │  │  ├─ cache_storage_manager_config.py
   │     │  │  ├─ cli.py
   │     │  │  ├─ server
   │     │  │  │  ├─ app_discovery.py
   │     │  │  │  ├─ app_static_file_handler.py
   │     │  │  │  ├─ authlib_tornado_integration.py
   │     │  │  │  ├─ bidi_component_request_handler.py
   │     │  │  │  ├─ browser_websocket_handler.py
   │     │  │  │  ├─ component_file_utils.py
   │     │  │  │  ├─ component_request_handler.py
   │     │  │  │  ├─ media_file_handler.py
   │     │  │  │  ├─ oauth_authlib_routes.py
   │     │  │  │  ├─ oidc_mixin.py
   │     │  │  │  ├─ routes.py
   │     │  │  │  ├─ server.py
   │     │  │  │  ├─ server_util.py
   │     │  │  │  ├─ starlette
   │     │  │  │  │  ├─ starlette_app.py
   │     │  │  │  │  ├─ starlette_app_utils.py
   │     │  │  │  │  ├─ starlette_auth_routes.py
   │     │  │  │  │  ├─ starlette_gzip_middleware.py
   │     │  │  │  │  ├─ starlette_path_security_middleware.py
   │     │  │  │  │  ├─ starlette_routes.py
   │     │  │  │  │  ├─ starlette_server.py
   │     │  │  │  │  ├─ starlette_server_config.py
   │     │  │  │  │  ├─ starlette_static_routes.py
   │     │  │  │  │  ├─ starlette_websocket.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ starlette_app.cpython-311.pyc
   │     │  │  │  │     ├─ starlette_app_utils.cpython-311.pyc
   │     │  │  │  │     ├─ starlette_auth_routes.cpython-311.pyc
   │     │  │  │  │     ├─ starlette_gzip_middleware.cpython-311.pyc
   │     │  │  │  │     ├─ starlette_path_security_middleware.cpython-311.pyc
   │     │  │  │  │     ├─ starlette_routes.cpython-311.pyc
   │     │  │  │  │     ├─ starlette_server.cpython-311.pyc
   │     │  │  │  │     ├─ starlette_server_config.cpython-311.pyc
   │     │  │  │  │     ├─ starlette_static_routes.cpython-311.pyc
   │     │  │  │  │     ├─ starlette_websocket.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ stats_request_handler.py
   │     │  │  │  ├─ upload_file_request_handler.py
   │     │  │  │  ├─ websocket_headers.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ app_discovery.cpython-311.pyc
   │     │  │  │     ├─ app_static_file_handler.cpython-311.pyc
   │     │  │  │     ├─ authlib_tornado_integration.cpython-311.pyc
   │     │  │  │     ├─ bidi_component_request_handler.cpython-311.pyc
   │     │  │  │     ├─ browser_websocket_handler.cpython-311.pyc
   │     │  │  │     ├─ component_file_utils.cpython-311.pyc
   │     │  │  │     ├─ component_request_handler.cpython-311.pyc
   │     │  │  │     ├─ media_file_handler.cpython-311.pyc
   │     │  │  │     ├─ oauth_authlib_routes.cpython-311.pyc
   │     │  │  │     ├─ oidc_mixin.cpython-311.pyc
   │     │  │  │     ├─ routes.cpython-311.pyc
   │     │  │  │     ├─ server.cpython-311.pyc
   │     │  │  │     ├─ server_util.cpython-311.pyc
   │     │  │  │     ├─ stats_request_handler.cpython-311.pyc
   │     │  │  │     ├─ upload_file_request_handler.cpython-311.pyc
   │     │  │  │     ├─ websocket_headers.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ bootstrap.cpython-311.pyc
   │     │  │     ├─ cache_storage_manager_config.cpython-311.pyc
   │     │  │     ├─ cli.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ __init__.py
   │     │  ├─ __main__.py
   │     │  └─ __pycache__
   │     │     ├─ auth_util.cpython-311.pyc
   │     │     ├─ cli_util.cpython-311.pyc
   │     │     ├─ column_config.cpython-311.pyc
   │     │     ├─ config.cpython-311.pyc
   │     │     ├─ config_option.cpython-311.pyc
   │     │     ├─ config_util.cpython-311.pyc
   │     │     ├─ cursor.cpython-311.pyc
   │     │     ├─ dataframe_util.cpython-311.pyc
   │     │     ├─ delta_generator.cpython-311.pyc
   │     │     ├─ delta_generator_singletons.cpython-311.pyc
   │     │     ├─ deprecation_util.cpython-311.pyc
   │     │     ├─ development.cpython-311.pyc
   │     │     ├─ emojis.cpython-311.pyc
   │     │     ├─ env_util.cpython-311.pyc
   │     │     ├─ errors.cpython-311.pyc
   │     │     ├─ error_util.cpython-311.pyc
   │     │     ├─ file_util.cpython-311.pyc
   │     │     ├─ git_util.cpython-311.pyc
   │     │     ├─ logger.cpython-311.pyc
   │     │     ├─ material_icon_names.cpython-311.pyc
   │     │     ├─ net_util.cpython-311.pyc
   │     │     ├─ path_security.cpython-311.pyc
   │     │     ├─ platform.cpython-311.pyc
   │     │     ├─ source_util.cpython-311.pyc
   │     │     ├─ starlette.cpython-311.pyc
   │     │     ├─ string_util.cpython-311.pyc
   │     │     ├─ temporary_directory.cpython-311.pyc
   │     │     ├─ time_util.cpython-311.pyc
   │     │     ├─ type_util.cpython-311.pyc
   │     │     ├─ url_util.cpython-311.pyc
   │     │     ├─ user_info.cpython-311.pyc
   │     │     ├─ util.cpython-311.pyc
   │     │     ├─ version.cpython-311.pyc
   │     │     ├─ __init__.cpython-311.pyc
   │     │     └─ __main__.cpython-311.pyc
   │     ├─ streamlit-1.56.0.dist-info
   │     │  ├─ entry_points.txt
   │     │  ├─ INSTALLER
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  ├─ REQUESTED
   │     │  ├─ top_level.txt
   │     │  └─ WHEEL
   │     ├─ sympy
   │     │  ├─ abc.py
   │     │  ├─ algebras
   │     │  │  ├─ quaternion.py
   │     │  │  ├─ tests
   │     │  │  │  ├─ test_quaternion.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ test_quaternion.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ quaternion.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ assumptions
   │     │  │  ├─ ask.py
   │     │  │  ├─ ask_generated.py
   │     │  │  ├─ assume.py
   │     │  │  ├─ cnf.py
   │     │  │  ├─ facts.py
   │     │  │  ├─ handlers
   │     │  │  │  ├─ calculus.py
   │     │  │  │  ├─ common.py
   │     │  │  │  ├─ matrices.py
   │     │  │  │  ├─ ntheory.py
   │     │  │  │  ├─ order.py
   │     │  │  │  ├─ sets.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ calculus.cpython-311.pyc
   │     │  │  │     ├─ common.cpython-311.pyc
   │     │  │  │     ├─ matrices.cpython-311.pyc
   │     │  │  │     ├─ ntheory.cpython-311.pyc
   │     │  │  │     ├─ order.cpython-311.pyc
   │     │  │  │     ├─ sets.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ lra_satask.py
   │     │  │  ├─ predicates
   │     │  │  │  ├─ calculus.py
   │     │  │  │  ├─ common.py
   │     │  │  │  ├─ matrices.py
   │     │  │  │  ├─ ntheory.py
   │     │  │  │  ├─ order.py
   │     │  │  │  ├─ sets.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ calculus.cpython-311.pyc
   │     │  │  │     ├─ common.cpython-311.pyc
   │     │  │  │     ├─ matrices.cpython-311.pyc
   │     │  │  │     ├─ ntheory.cpython-311.pyc
   │     │  │  │     ├─ order.cpython-311.pyc
   │     │  │  │     ├─ sets.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ refine.py
   │     │  │  ├─ relation
   │     │  │  │  ├─ binrel.py
   │     │  │  │  ├─ equality.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ binrel.cpython-311.pyc
   │     │  │  │     ├─ equality.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ satask.py
   │     │  │  ├─ sathandlers.py
   │     │  │  ├─ tests
   │     │  │  │  ├─ test_assumptions_2.py
   │     │  │  │  ├─ test_context.py
   │     │  │  │  ├─ test_matrices.py
   │     │  │  │  ├─ test_query.py
   │     │  │  │  ├─ test_refine.py
   │     │  │  │  ├─ test_rel_queries.py
   │     │  │  │  ├─ test_satask.py
   │     │  │  │  ├─ test_sathandlers.py
   │     │  │  │  ├─ test_wrapper.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ test_assumptions_2.cpython-311.pyc
   │     │  │  │     ├─ test_context.cpython-311.pyc
   │     │  │  │     ├─ test_matrices.cpython-311.pyc
   │     │  │  │     ├─ test_query.cpython-311.pyc
   │     │  │  │     ├─ test_refine.cpython-311.pyc
   │     │  │  │     ├─ test_rel_queries.cpython-311.pyc
   │     │  │  │     ├─ test_satask.cpython-311.pyc
   │     │  │  │     ├─ test_sathandlers.cpython-311.pyc
   │     │  │  │     ├─ test_wrapper.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ wrapper.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ ask.cpython-311.pyc
   │     │  │     ├─ ask_generated.cpython-311.pyc
   │     │  │     ├─ assume.cpython-311.pyc
   │     │  │     ├─ cnf.cpython-311.pyc
   │     │  │     ├─ facts.cpython-311.pyc
   │     │  │     ├─ lra_satask.cpython-311.pyc
   │     │  │     ├─ refine.cpython-311.pyc
   │     │  │     ├─ satask.cpython-311.pyc
   │     │  │     ├─ sathandlers.cpython-311.pyc
   │     │  │     ├─ wrapper.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ benchmarks
   │     │  │  ├─ bench_discrete_log.py
   │     │  │  ├─ bench_meijerint.py
   │     │  │  ├─ bench_symbench.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ bench_discrete_log.cpython-311.pyc
   │     │  │     ├─ bench_meijerint.cpython-311.pyc
   │     │  │     ├─ bench_symbench.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ calculus
   │     │  │  ├─ accumulationbounds.py
   │     │  │  ├─ euler.py
   │     │  │  ├─ finite_diff.py
   │     │  │  ├─ singularities.py
   │     │  │  ├─ tests
   │     │  │  │  ├─ test_accumulationbounds.py
   │     │  │  │  ├─ test_euler.py
   │     │  │  │  ├─ test_finite_diff.py
   │     │  │  │  ├─ test_singularities.py
   │     │  │  │  ├─ test_util.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ test_accumulationbounds.cpython-311.pyc
   │     │  │  │     ├─ test_euler.cpython-311.pyc
   │     │  │  │     ├─ test_finite_diff.cpython-311.pyc
   │     │  │  │     ├─ test_singularities.cpython-311.pyc
   │     │  │  │     ├─ test_util.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ util.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ accumulationbounds.cpython-311.pyc
   │     │  │     ├─ euler.cpython-311.pyc
   │     │  │     ├─ finite_diff.cpython-311.pyc
   │     │  │     ├─ singularities.cpython-311.pyc
   │     │  │     ├─ util.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ categories
   │     │  │  ├─ baseclasses.py
   │     │  │  ├─ diagram_drawing.py
   │     │  │  ├─ tests
   │     │  │  │  ├─ test_baseclasses.py
   │     │  │  │  ├─ test_drawing.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ test_baseclasses.cpython-311.pyc
   │     │  │  │     ├─ test_drawing.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ baseclasses.cpython-311.pyc
   │     │  │     ├─ diagram_drawing.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ codegen
   │     │  │  ├─ abstract_nodes.py
   │     │  │  ├─ algorithms.py
   │     │  │  ├─ approximations.py
   │     │  │  ├─ ast.py
   │     │  │  ├─ cfunctions.py
   │     │  │  ├─ cnodes.py
   │     │  │  ├─ cutils.py
   │     │  │  ├─ cxxnodes.py
   │     │  │  ├─ fnodes.py
   │     │  │  ├─ futils.py
   │     │  │  ├─ matrix_nodes.py
   │     │  │  ├─ numpy_nodes.py
   │     │  │  ├─ pynodes.py
   │     │  │  ├─ pyutils.py
   │     │  │  ├─ rewriting.py
   │     │  │  ├─ scipy_nodes.py
   │     │  │  ├─ tests
   │     │  │  │  ├─ test_abstract_nodes.py
   │     │  │  │  ├─ test_algorithms.py
   │     │  │  │  ├─ test_applications.py
   │     │  │  │  ├─ test_approximations.py
   │     │  │  │  ├─ test_ast.py
   │     │  │  │  ├─ test_cfunctions.py
   │     │  │  │  ├─ test_cnodes.py
   │     │  │  │  ├─ test_cxxnodes.py
   │     │  │  │  ├─ test_fnodes.py
   │     │  │  │  ├─ test_matrix_nodes.py
   │     │  │  │  ├─ test_numpy_nodes.py
   │     │  │  │  ├─ test_pynodes.py
   │     │  │  │  ├─ test_pyutils.py
   │     │  │  │  ├─ test_rewriting.py
   │     │  │  │  ├─ test_scipy_nodes.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ test_abstract_nodes.cpython-311.pyc
   │     │  │  │     ├─ test_algorithms.cpython-311.pyc
   │     │  │  │     ├─ test_applications.cpython-311.pyc
   │     │  │  │     ├─ test_approximations.cpython-311.pyc
   │     │  │  │     ├─ test_ast.cpython-311.pyc
   │     │  │  │     ├─ test_cfunctions.cpython-311.pyc
   │     │  │  │     ├─ test_cnodes.cpython-311.pyc
   │     │  │  │     ├─ test_cxxnodes.cpython-311.pyc
   │     │  │  │     ├─ test_fnodes.cpython-311.pyc
   │     │  │  │     ├─ test_matrix_nodes.cpython-311.pyc
   │     │  │  │     ├─ test_numpy_nodes.cpython-311.pyc
   │     │  │  │     ├─ test_pynodes.cpython-311.pyc
   │     │  │  │     ├─ test_pyutils.cpython-311.pyc
   │     │  │  │     ├─ test_rewriting.cpython-311.pyc
   │     │  │  │     ├─ test_scipy_nodes.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ abstract_nodes.cpython-311.pyc
   │     │  │     ├─ algorithms.cpython-311.pyc
   │     │  │     ├─ approximations.cpython-311.pyc
   │     │  │     ├─ ast.cpython-311.pyc
   │     │  │     ├─ cfunctions.cpython-311.pyc
   │     │  │     ├─ cnodes.cpython-311.pyc
   │     │  │     ├─ cutils.cpython-311.pyc
   │     │  │     ├─ cxxnodes.cpython-311.pyc
   │     │  │     ├─ fnodes.cpython-311.pyc
   │     │  │     ├─ futils.cpython-311.pyc
   │     │  │     ├─ matrix_nodes.cpython-311.pyc
   │     │  │     ├─ numpy_nodes.cpython-311.pyc
   │     │  │     ├─ pynodes.cpython-311.pyc
   │     │  │     ├─ pyutils.cpython-311.pyc
   │     │  │     ├─ rewriting.cpython-311.pyc
   │     │  │     ├─ scipy_nodes.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ combinatorics
   │     │  │  ├─ coset_table.py
   │     │  │  ├─ fp_groups.py
   │     │  │  ├─ free_groups.py
   │     │  │  ├─ galois.py
   │     │  │  ├─ generators.py
   │     │  │  ├─ graycode.py
   │     │  │  ├─ group_constructs.py
   │     │  │  ├─ group_numbers.py
   │     │  │  ├─ homomorphisms.py
   │     │  │  ├─ named_groups.py
   │     │  │  ├─ partitions.py
   │     │  │  ├─ pc_groups.py
   │     │  │  ├─ permutations.py
   │     │  │  ├─ perm_groups.py
   │     │  │  ├─ polyhedron.py
   │     │  │  ├─ prufer.py
   │     │  │  ├─ rewritingsystem.py
   │     │  │  ├─ rewritingsystem_fsm.py
   │     │  │  ├─ schur_number.py
   │     │  │  ├─ subsets.py
   │     │  │  ├─ tensor_can.py
   │     │  │  ├─ tests
   │     │  │  │  ├─ test_coset_table.py
   │     │  │  │  ├─ test_fp_groups.py
   │     │  │  │  ├─ test_free_groups.py
   │     │  │  │  ├─ test_galois.py
   │     │  │  │  ├─ test_generators.py
   │     │  │  │  ├─ test_graycode.py
   │     │  │  │  ├─ test_group_constructs.py
   │     │  │  │  ├─ test_group_numbers.py
   │     │  │  │  ├─ test_homomorphisms.py
   │     │  │  │  ├─ test_named_groups.py
   │     │  │  │  ├─ test_partitions.py
   │     │  │  │  ├─ test_pc_groups.py
   │     │  │  │  ├─ test_permutations.py
   │     │  │  │  ├─ test_perm_groups.py
   │     │  │  │  ├─ test_polyhedron.py
   │     │  │  │  ├─ test_prufer.py
   │     │  │  │  ├─ test_rewriting.py
   │     │  │  │  ├─ test_schur_number.py
   │     │  │  │  ├─ test_subsets.py
   │     │  │  │  ├─ test_tensor_can.py
   │     │  │  │  ├─ test_testutil.py
   │     │  │  │  ├─ test_util.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ test_coset_table.cpython-311.pyc
   │     │  │  │     ├─ test_fp_groups.cpython-311.pyc
   │     │  │  │     ├─ test_free_groups.cpython-311.pyc
   │     │  │  │     ├─ test_galois.cpython-311.pyc
   │     │  │  │     ├─ test_generators.cpython-311.pyc
   │     │  │  │     ├─ test_graycode.cpython-311.pyc
   │     │  │  │     ├─ test_group_constructs.cpython-311.pyc
   │     │  │  │     ├─ test_group_numbers.cpython-311.pyc
   │     │  │  │     ├─ test_homomorphisms.cpython-311.pyc
   │     │  │  │     ├─ test_named_groups.cpython-311.pyc
   │     │  │  │     ├─ test_partitions.cpython-311.pyc
   │     │  │  │     ├─ test_pc_groups.cpython-311.pyc
   │     │  │  │     ├─ test_permutations.cpython-311.pyc
   │     │  │  │     ├─ test_perm_groups.cpython-311.pyc
   │     │  │  │     ├─ test_polyhedron.cpython-311.pyc
   │     │  │  │     ├─ test_prufer.cpython-311.pyc
   │     │  │  │     ├─ test_rewriting.cpython-311.pyc
   │     │  │  │     ├─ test_schur_number.cpython-311.pyc
   │     │  │  │     ├─ test_subsets.cpython-311.pyc
   │     │  │  │     ├─ test_tensor_can.cpython-311.pyc
   │     │  │  │     ├─ test_testutil.cpython-311.pyc
   │     │  │  │     ├─ test_util.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ testutil.py
   │     │  │  ├─ util.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ coset_table.cpython-311.pyc
   │     │  │     ├─ fp_groups.cpython-311.pyc
   │     │  │     ├─ free_groups.cpython-311.pyc
   │     │  │     ├─ galois.cpython-311.pyc
   │     │  │     ├─ generators.cpython-311.pyc
   │     │  │     ├─ graycode.cpython-311.pyc
   │     │  │     ├─ group_constructs.cpython-311.pyc
   │     │  │     ├─ group_numbers.cpython-311.pyc
   │     │  │     ├─ homomorphisms.cpython-311.pyc
   │     │  │     ├─ named_groups.cpython-311.pyc
   │     │  │     ├─ partitions.cpython-311.pyc
   │     │  │     ├─ pc_groups.cpython-311.pyc
   │     │  │     ├─ permutations.cpython-311.pyc
   │     │  │     ├─ perm_groups.cpython-311.pyc
   │     │  │     ├─ polyhedron.cpython-311.pyc
   │     │  │     ├─ prufer.cpython-311.pyc
   │     │  │     ├─ rewritingsystem.cpython-311.pyc
   │     │  │     ├─ rewritingsystem_fsm.cpython-311.pyc
   │     │  │     ├─ schur_number.cpython-311.pyc
   │     │  │     ├─ subsets.cpython-311.pyc
   │     │  │     ├─ tensor_can.cpython-311.pyc
   │     │  │     ├─ testutil.cpython-311.pyc
   │     │  │     ├─ util.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ concrete
   │     │  │  ├─ delta.py
   │     │  │  ├─ expr_with_intlimits.py
   │     │  │  ├─ expr_with_limits.py
   │     │  │  ├─ gosper.py
   │     │  │  ├─ guess.py
   │     │  │  ├─ products.py
   │     │  │  ├─ summations.py
   │     │  │  ├─ tests
   │     │  │  │  ├─ test_delta.py
   │     │  │  │  ├─ test_gosper.py
   │     │  │  │  ├─ test_guess.py
   │     │  │  │  ├─ test_products.py
   │     │  │  │  ├─ test_sums_products.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ test_delta.cpython-311.pyc
   │     │  │  │     ├─ test_gosper.cpython-311.pyc
   │     │  │  │     ├─ test_guess.cpython-311.pyc
   │     │  │  │     ├─ test_products.cpython-311.pyc
   │     │  │  │     ├─ test_sums_products.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ delta.cpython-311.pyc
   │     │  │     ├─ expr_with_intlimits.cpython-311.pyc
   │     │  │     ├─ expr_with_limits.cpython-311.pyc
   │     │  │     ├─ gosper.cpython-311.pyc
   │     │  │     ├─ guess.cpython-311.pyc
   │     │  │     ├─ products.cpython-311.pyc
   │     │  │     ├─ summations.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ conftest.py
   │     │  ├─ core
   │     │  │  ├─ add.py
   │     │  │  ├─ alphabets.py
   │     │  │  ├─ assumptions.py
   │     │  │  ├─ assumptions_generated.py
   │     │  │  ├─ backend.py
   │     │  │  ├─ basic.py
   │     │  │  ├─ benchmarks
   │     │  │  │  ├─ bench_arit.py
   │     │  │  │  ├─ bench_assumptions.py
   │     │  │  │  ├─ bench_basic.py
   │     │  │  │  ├─ bench_expand.py
   │     │  │  │  ├─ bench_numbers.py
   │     │  │  │  ├─ bench_sympify.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ bench_arit.cpython-311.pyc
   │     │  │  │     ├─ bench_assumptions.cpython-311.pyc
   │     │  │  │     ├─ bench_basic.cpython-311.pyc
   │     │  │  │     ├─ bench_expand.cpython-311.pyc
   │     │  │  │     ├─ bench_numbers.cpython-311.pyc
   │     │  │  │     ├─ bench_sympify.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ cache.py
   │     │  │  ├─ compatibility.py
   │     │  │  ├─ containers.py
   │     │  │  ├─ core.py
   │     │  │  ├─ coreerrors.py
   │     │  │  ├─ decorators.py
   │     │  │  ├─ evalf.py
   │     │  │  ├─ expr.py
   │     │  │  ├─ exprtools.py
   │     │  │  ├─ facts.py
   │     │  │  ├─ function.py
   │     │  │  ├─ intfunc.py
   │     │  │  ├─ kind.py
   │     │  │  ├─ logic.py
   │     │  │  ├─ mod.py
   │     │  │  ├─ mul.py
   │     │  │  ├─ multidimensional.py
   │     │  │  ├─ numbers.py
   │     │  │  ├─ operations.py
   │     │  │  ├─ parameters.py
   │     │  │  ├─ power.py
   │     │  │  ├─ random.py
   │     │  │  ├─ relational.py
   │     │  │  ├─ rules.py
   │     │  │  ├─ singleton.py
   │     │  │  ├─ sorting.py
   │     │  │  ├─ symbol.py
   │     │  │  ├─ sympify.py
   │     │  │  ├─ tests
   │     │  │  │  ├─ test_args.py
   │     │  │  │  ├─ test_arit.py
   │     │  │  │  ├─ test_assumptions.py
   │     │  │  │  ├─ test_basic.py
   │     │  │  │  ├─ test_cache.py
   │     │  │  │  ├─ test_compatibility.py
   │     │  │  │  ├─ test_complex.py
   │     │  │  │  ├─ test_constructor_postprocessor.py
   │     │  │  │  ├─ test_containers.py
   │     │  │  │  ├─ test_count_ops.py
   │     │  │  │  ├─ test_diff.py
   │     │  │  │  ├─ test_equal.py
   │     │  │  │  ├─ test_eval.py
   │     │  │  │  ├─ test_evalf.py
   │     │  │  │  ├─ test_expand.py
   │     │  │  │  ├─ test_expr.py
   │     │  │  │  ├─ test_exprtools.py
   │     │  │  │  ├─ test_facts.py
   │     │  │  │  ├─ test_function.py
   │     │  │  │  ├─ test_kind.py
   │     │  │  │  ├─ test_logic.py
   │     │  │  │  ├─ test_match.py
   │     │  │  │  ├─ test_multidimensional.py
   │     │  │  │  ├─ test_noncommutative.py
   │     │  │  │  ├─ test_numbers.py
   │     │  │  │  ├─ test_operations.py
   │     │  │  │  ├─ test_parameters.py
   │     │  │  │  ├─ test_power.py
   │     │  │  │  ├─ test_priority.py
   │     │  │  │  ├─ test_random.py
   │     │  │  │  ├─ test_relational.py
   │     │  │  │  ├─ test_rules.py
   │     │  │  │  ├─ test_singleton.py
   │     │  │  │  ├─ test_sorting.py
   │     │  │  │  ├─ test_subs.py
   │     │  │  │  ├─ test_symbol.py
   │     │  │  │  ├─ test_sympify.py
   │     │  │  │  ├─ test_traversal.py
   │     │  │  │  ├─ test_truediv.py
   │     │  │  │  ├─ test_var.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ test_args.cpython-311.pyc
   │     │  │  │     ├─ test_arit.cpython-311.pyc
   │     │  │  │     ├─ test_assumptions.cpython-311.pyc
   │     │  │  │     ├─ test_basic.cpython-311.pyc
   │     │  │  │     ├─ test_cache.cpython-311.pyc
   │     │  │  │     ├─ test_compatibility.cpython-311.pyc
   │     │  │  │     ├─ test_complex.cpython-311.pyc
   │     │  │  │     ├─ test_constructor_postprocessor.cpython-311.pyc
   │     │  │  │     ├─ test_containers.cpython-311.pyc
   │     │  │  │     ├─ test_count_ops.cpython-311.pyc
   │     │  │  │     ├─ test_diff.cpython-311.pyc
   │     │  │  │     ├─ test_equal.cpython-311.pyc
   │     │  │  │     ├─ test_eval.cpython-311.pyc
   │     │  │  │     ├─ test_evalf.cpython-311.pyc
   │     │  │  │     ├─ test_expand.cpython-311.pyc
   │     │  │  │     ├─ test_expr.cpython-311.pyc
   │     │  │  │     ├─ test_exprtools.cpython-311.pyc
   │     │  │  │     ├─ test_facts.cpython-311.pyc
   │     │  │  │     ├─ test_function.cpython-311.pyc
   │     │  │  │     ├─ test_kind.cpython-311.pyc
   │     │  │  │     ├─ test_logic.cpython-311.pyc
   │     │  │  │     ├─ test_match.cpython-311.pyc
   │     │  │  │     ├─ test_multidimensional.cpython-311.pyc
   │     │  │  │     ├─ test_noncommutative.cpython-311.pyc
   │     │  │  │     ├─ test_numbers.cpython-311.pyc
   │     │  │  │     ├─ test_operations.cpython-311.pyc
   │     │  │  │     ├─ test_parameters.cpython-311.pyc
   │     │  │  │     ├─ test_power.cpython-311.pyc
   │     │  │  │     ├─ test_priority.cpython-311.pyc
   │     │  │  │     ├─ test_random.cpython-311.pyc
   │     │  │  │     ├─ test_relational.cpython-311.pyc
   │     │  │  │     ├─ test_rules.cpython-311.pyc
   │     │  │  │     ├─ test_singleton.cpython-311.pyc
   │     │  │  │     ├─ test_sorting.cpython-311.pyc
   │     │  │  │     ├─ test_subs.cpython-311.pyc
   │     │  │  │     ├─ test_symbol.cpython-311.pyc
   │     │  │  │     ├─ test_sympify.cpython-311.pyc
   │     │  │  │     ├─ test_traversal.cpython-311.pyc
   │     │  │  │     ├─ test_truediv.cpython-311.pyc
   │     │  │  │     ├─ test_var.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ trace.py
   │     │  │  ├─ traversal.py
   │     │  │  ├─ _print_helpers.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ add.cpython-311.pyc
   │     │  │     ├─ alphabets.cpython-311.pyc
   │     │  │     ├─ assumptions.cpython-311.pyc
   │     │  │     ├─ assumptions_generated.cpython-311.pyc
   │     │  │     ├─ backend.cpython-311.pyc
   │     │  │     ├─ basic.cpython-311.pyc
   │     │  │     ├─ cache.cpython-311.pyc
   │     │  │     ├─ compatibility.cpython-311.pyc
   │     │  │     ├─ containers.cpython-311.pyc
   │     │  │     ├─ core.cpython-311.pyc
   │     │  │     ├─ coreerrors.cpython-311.pyc
   │     │  │     ├─ decorators.cpython-311.pyc
   │     │  │     ├─ evalf.cpython-311.pyc
   │     │  │     ├─ expr.cpython-311.pyc
   │     │  │     ├─ exprtools.cpython-311.pyc
   │     │  │     ├─ facts.cpython-311.pyc
   │     │  │     ├─ function.cpython-311.pyc
   │     │  │     ├─ intfunc.cpython-311.pyc
   │     │  │     ├─ kind.cpython-311.pyc
   │     │  │     ├─ logic.cpython-311.pyc
   │     │  │     ├─ mod.cpython-311.pyc
   │     │  │     ├─ mul.cpython-311.pyc
   │     │  │     ├─ multidimensional.cpython-311.pyc
   │     │  │     ├─ numbers.cpython-311.pyc
   │     │  │     ├─ operations.cpython-311.pyc
   │     │  │     ├─ parameters.cpython-311.pyc
   │     │  │     ├─ power.cpython-311.pyc
   │     │  │     ├─ random.cpython-311.pyc
   │     │  │     ├─ relational.cpython-311.pyc
   │     │  │     ├─ rules.cpython-311.pyc
   │     │  │     ├─ singleton.cpython-311.pyc
   │     │  │     ├─ sorting.cpython-311.pyc
   │     │  │     ├─ symbol.cpython-311.pyc
   │     │  │     ├─ sympify.cpython-311.pyc
   │     │  │     ├─ trace.cpython-311.pyc
   │     │  │     ├─ traversal.cpython-311.pyc
   │     │  │     ├─ _print_helpers.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ crypto
   │     │  │  ├─ crypto.py
   │     │  │  ├─ tests
   │     │  │  │  ├─ test_crypto.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ test_crypto.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ crypto.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ diffgeom
   │     │  │  ├─ diffgeom.py
   │     │  │  ├─ rn.py
   │     │  │  ├─ tests
   │     │  │  │  ├─ test_class_structure.py
   │     │  │  │  ├─ test_diffgeom.py
   │     │  │  │  ├─ test_function_diffgeom_book.py
   │     │  │  │  ├─ test_hyperbolic_space.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ test_class_structure.cpython-311.pyc
   │     │  │  │     ├─ test_diffgeom.cpython-311.pyc
   │     │  │  │     ├─ test_function_diffgeom_book.cpython-311.pyc
   │     │  │  │     ├─ test_hyperbolic_space.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ diffgeom.cpython-311.pyc
   │     │  │     ├─ rn.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ discrete
   │     │  │  ├─ convolutions.py
   │     │  │  ├─ recurrences.py
   │     │  │  ├─ tests
   │     │  │  │  ├─ test_convolutions.py
   │     │  │  │  ├─ test_recurrences.py
   │     │  │  │  ├─ test_transforms.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ test_convolutions.cpython-311.pyc
   │     │  │  │     ├─ test_recurrences.cpython-311.pyc
   │     │  │  │     ├─ test_transforms.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ transforms.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ convolutions.cpython-311.pyc
   │     │  │     ├─ recurrences.cpython-311.pyc
   │     │  │     ├─ transforms.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ external
   │     │  │  ├─ gmpy.py
   │     │  │  ├─ importtools.py
   │     │  │  ├─ ntheory.py
   │     │  │  ├─ pythonmpq.py
   │     │  │  ├─ tests
   │     │  │  │  ├─ test_autowrap.py
   │     │  │  │  ├─ test_codegen.py
   │     │  │  │  ├─ test_gmpy.py
   │     │  │  │  ├─ test_importtools.py
   │     │  │  │  ├─ test_ntheory.py
   │     │  │  │  ├─ test_numpy.py
   │     │  │  │  ├─ test_pythonmpq.py
   │     │  │  │  ├─ test_scipy.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ test_autowrap.cpython-311.pyc
   │     │  │  │     ├─ test_codegen.cpython-311.pyc
   │     │  │  │     ├─ test_gmpy.cpython-311.pyc
   │     │  │  │     ├─ test_importtools.cpython-311.pyc
   │     │  │  │     ├─ test_ntheory.cpython-311.pyc
   │     │  │  │     ├─ test_numpy.cpython-311.pyc
   │     │  │  │     ├─ test_pythonmpq.cpython-311.pyc
   │     │  │  │     ├─ test_scipy.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ gmpy.cpython-311.pyc
   │     │  │     ├─ importtools.cpython-311.pyc
   │     │  │     ├─ ntheory.cpython-311.pyc
   │     │  │     ├─ pythonmpq.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ functions
   │     │  │  ├─ combinatorial
   │     │  │  │  ├─ factorials.py
   │     │  │  │  ├─ numbers.py
   │     │  │  │  ├─ tests
   │     │  │  │  │  ├─ test_comb_factorials.py
   │     │  │  │  │  ├─ test_comb_numbers.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ test_comb_factorials.cpython-311.pyc
   │     │  │  │  │     ├─ test_comb_numbers.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ factorials.cpython-311.pyc
   │     │  │  │     ├─ numbers.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ elementary
   │     │  │  │  ├─ benchmarks
   │     │  │  │  │  ├─ bench_exp.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ bench_exp.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ complexes.py
   │     │  │  │  ├─ exponential.py
   │     │  │  │  ├─ hyperbolic.py
   │     │  │  │  ├─ integers.py
   │     │  │  │  ├─ miscellaneous.py
   │     │  │  │  ├─ piecewise.py
   │     │  │  │  ├─ tests
   │     │  │  │  │  ├─ test_complexes.py
   │     │  │  │  │  ├─ test_exponential.py
   │     │  │  │  │  ├─ test_hyperbolic.py
   │     │  │  │  │  ├─ test_integers.py
   │     │  │  │  │  ├─ test_interface.py
   │     │  │  │  │  ├─ test_miscellaneous.py
   │     │  │  │  │  ├─ test_piecewise.py
   │     │  │  │  │  ├─ test_trigonometric.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ test_complexes.cpython-311.pyc
   │     │  │  │  │     ├─ test_exponential.cpython-311.pyc
   │     │  │  │  │     ├─ test_hyperbolic.cpython-311.pyc
   │     │  │  │  │     ├─ test_integers.cpython-311.pyc
   │     │  │  │  │     ├─ test_interface.cpython-311.pyc
   │     │  │  │  │     ├─ test_miscellaneous.cpython-311.pyc
   │     │  │  │  │     ├─ test_piecewise.cpython-311.pyc
   │     │  │  │  │     ├─ test_trigonometric.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ trigonometric.py
   │     │  │  │  ├─ _trigonometric_special.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ complexes.cpython-311.pyc
   │     │  │  │     ├─ exponential.cpython-311.pyc
   │     │  │  │     ├─ hyperbolic.cpython-311.pyc
   │     │  │  │     ├─ integers.cpython-311.pyc
   │     │  │  │     ├─ miscellaneous.cpython-311.pyc
   │     │  │  │     ├─ piecewise.cpython-311.pyc
   │     │  │  │     ├─ trigonometric.cpython-311.pyc
   │     │  │  │     ├─ _trigonometric_special.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ special
   │     │  │  │  ├─ benchmarks
   │     │  │  │  │  ├─ bench_special.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ bench_special.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ bessel.py
   │     │  │  │  ├─ beta_functions.py
   │     │  │  │  ├─ bsplines.py
   │     │  │  │  ├─ delta_functions.py
   │     │  │  │  ├─ elliptic_integrals.py
   │     │  │  │  ├─ error_functions.py
   │     │  │  │  ├─ gamma_functions.py
   │     │  │  │  ├─ hyper.py
   │     │  │  │  ├─ mathieu_functions.py
   │     │  │  │  ├─ polynomials.py
   │     │  │  │  ├─ singularity_functions.py
   │     │  │  │  ├─ spherical_harmonics.py
   │     │  │  │  ├─ tensor_functions.py
   │     │  │  │  ├─ tests
   │     │  │  │  │  ├─ test_bessel.py
   │     │  │  │  │  ├─ test_beta_functions.py
   │     │  │  │  │  ├─ test_bsplines.py
   │     │  │  │  │  ├─ test_delta_functions.py
   │     │  │  │  │  ├─ test_elliptic_integrals.py
   │     │  │  │  │  ├─ test_error_functions.py
   │     │  │  │  │  ├─ test_gamma_functions.py
   │     │  │  │  │  ├─ test_hyper.py
   │     │  │  │  │  ├─ test_mathieu.py
   │     │  │  │  │  ├─ test_singularity_functions.py
   │     │  │  │  │  ├─ test_spec_polynomials.py
   │     │  │  │  │  ├─ test_spherical_harmonics.py
   │     │  │  │  │  ├─ test_tensor_functions.py
   │     │  │  │  │  ├─ test_zeta_functions.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ test_bessel.cpython-311.pyc
   │     │  │  │  │     ├─ test_beta_functions.cpython-311.pyc
   │     │  │  │  │     ├─ test_bsplines.cpython-311.pyc
   │     │  │  │  │     ├─ test_delta_functions.cpython-311.pyc
   │     │  │  │  │     ├─ test_elliptic_integrals.cpython-311.pyc
   │     │  │  │  │     ├─ test_error_functions.cpython-311.pyc
   │     │  │  │  │     ├─ test_gamma_functions.cpython-311.pyc
   │     │  │  │  │     ├─ test_hyper.cpython-311.pyc
   │     │  │  │  │     ├─ test_mathieu.cpython-311.pyc
   │     │  │  │  │     ├─ test_singularity_functions.cpython-311.pyc
   │     │  │  │  │     ├─ test_spec_polynomials.cpython-311.pyc
   │     │  │  │  │     ├─ test_spherical_harmonics.cpython-311.pyc
   │     │  │  │  │     ├─ test_tensor_functions.cpython-311.pyc
   │     │  │  │  │     ├─ test_zeta_functions.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ zeta_functions.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ bessel.cpython-311.pyc
   │     │  │  │     ├─ beta_functions.cpython-311.pyc
   │     │  │  │     ├─ bsplines.cpython-311.pyc
   │     │  │  │     ├─ delta_functions.cpython-311.pyc
   │     │  │  │     ├─ elliptic_integrals.cpython-311.pyc
   │     │  │  │     ├─ error_functions.cpython-311.pyc
   │     │  │  │     ├─ gamma_functions.cpython-311.pyc
   │     │  │  │     ├─ hyper.cpython-311.pyc
   │     │  │  │     ├─ mathieu_functions.cpython-311.pyc
   │     │  │  │     ├─ polynomials.cpython-311.pyc
   │     │  │  │     ├─ singularity_functions.cpython-311.pyc
   │     │  │  │     ├─ spherical_harmonics.cpython-311.pyc
   │     │  │  │     ├─ tensor_functions.cpython-311.pyc
   │     │  │  │     ├─ zeta_functions.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ galgebra.py
   │     │  ├─ geometry
   │     │  │  ├─ curve.py
   │     │  │  ├─ ellipse.py
   │     │  │  ├─ entity.py
   │     │  │  ├─ exceptions.py
   │     │  │  ├─ line.py
   │     │  │  ├─ parabola.py
   │     │  │  ├─ plane.py
   │     │  │  ├─ point.py
   │     │  │  ├─ polygon.py
   │     │  │  ├─ tests
   │     │  │  │  ├─ test_curve.py
   │     │  │  │  ├─ test_ellipse.py
   │     │  │  │  ├─ test_entity.py
   │     │  │  │  ├─ test_geometrysets.py
   │     │  │  │  ├─ test_line.py
   │     │  │  │  ├─ test_parabola.py
   │     │  │  │  ├─ test_plane.py
   │     │  │  │  ├─ test_point.py
   │     │  │  │  ├─ test_polygon.py
   │     │  │  │  ├─ test_util.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ test_curve.cpython-311.pyc
   │     │  │  │     ├─ test_ellipse.cpython-311.pyc
   │     │  │  │     ├─ test_entity.cpython-311.pyc
   │     │  │  │     ├─ test_geometrysets.cpython-311.pyc
   │     │  │  │     ├─ test_line.cpython-311.pyc
   │     │  │  │     ├─ test_parabola.cpython-311.pyc
   │     │  │  │     ├─ test_plane.cpython-311.pyc
   │     │  │  │     ├─ test_point.cpython-311.pyc
   │     │  │  │     ├─ test_polygon.cpython-311.pyc
   │     │  │  │     ├─ test_util.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ util.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ curve.cpython-311.pyc
   │     │  │     ├─ ellipse.cpython-311.pyc
   │     │  │     ├─ entity.cpython-311.pyc
   │     │  │     ├─ exceptions.cpython-311.pyc
   │     │  │     ├─ line.cpython-311.pyc
   │     │  │     ├─ parabola.cpython-311.pyc
   │     │  │     ├─ plane.cpython-311.pyc
   │     │  │     ├─ point.cpython-311.pyc
   │     │  │     ├─ polygon.cpython-311.pyc
   │     │  │     ├─ util.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ holonomic
   │     │  │  ├─ holonomic.py
   │     │  │  ├─ holonomicerrors.py
   │     │  │  ├─ numerical.py
   │     │  │  ├─ recurrence.py
   │     │  │  ├─ tests
   │     │  │  │  ├─ test_holonomic.py
   │     │  │  │  ├─ test_recurrence.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ test_holonomic.cpython-311.pyc
   │     │  │  │     ├─ test_recurrence.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ holonomic.cpython-311.pyc
   │     │  │     ├─ holonomicerrors.cpython-311.pyc
   │     │  │     ├─ numerical.cpython-311.pyc
   │     │  │     ├─ recurrence.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ integrals
   │     │  │  ├─ benchmarks
   │     │  │  │  ├─ bench_integrate.py
   │     │  │  │  ├─ bench_trigintegrate.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ bench_integrate.cpython-311.pyc
   │     │  │  │     ├─ bench_trigintegrate.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ deltafunctions.py
   │     │  │  ├─ heurisch.py
   │     │  │  ├─ integrals.py
   │     │  │  ├─ intpoly.py
   │     │  │  ├─ laplace.py
   │     │  │  ├─ manualintegrate.py
   │     │  │  ├─ meijerint.py
   │     │  │  ├─ meijerint_doc.py
   │     │  │  ├─ prde.py
   │     │  │  ├─ quadrature.py
   │     │  │  ├─ rationaltools.py
   │     │  │  ├─ rde.py
   │     │  │  ├─ risch.py
   │     │  │  ├─ singularityfunctions.py
   │     │  │  ├─ tests
   │     │  │  │  ├─ test_deltafunctions.py
   │     │  │  │  ├─ test_failing_integrals.py
   │     │  │  │  ├─ test_heurisch.py
   │     │  │  │  ├─ test_integrals.py
   │     │  │  │  ├─ test_intpoly.py
   │     │  │  │  ├─ test_laplace.py
   │     │  │  │  ├─ test_lineintegrals.py
   │     │  │  │  ├─ test_manual.py
   │     │  │  │  ├─ test_meijerint.py
   │     │  │  │  ├─ test_prde.py
   │     │  │  │  ├─ test_quadrature.py
   │     │  │  │  ├─ test_rationaltools.py
   │     │  │  │  ├─ test_rde.py
   │     │  │  │  ├─ test_risch.py
   │     │  │  │  ├─ test_singularityfunctions.py
   │     │  │  │  ├─ test_transforms.py
   │     │  │  │  ├─ test_trigonometry.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ test_deltafunctions.cpython-311.pyc
   │     │  │  │     ├─ test_failing_integrals.cpython-311.pyc
   │     │  │  │     ├─ test_heurisch.cpython-311.pyc
   │     │  │  │     ├─ test_integrals.cpython-311.pyc
   │     │  │  │     ├─ test_intpoly.cpython-311.pyc
   │     │  │  │     ├─ test_laplace.cpython-311.pyc
   │     │  │  │     ├─ test_lineintegrals.cpython-311.pyc
   │     │  │  │     ├─ test_manual.cpython-311.pyc
   │     │  │  │     ├─ test_meijerint.cpython-311.pyc
   │     │  │  │     ├─ test_prde.cpython-311.pyc
   │     │  │  │     ├─ test_quadrature.cpython-311.pyc
   │     │  │  │     ├─ test_rationaltools.cpython-311.pyc
   │     │  │  │     ├─ test_rde.cpython-311.pyc
   │     │  │  │     ├─ test_risch.cpython-311.pyc
   │     │  │  │     ├─ test_singularityfunctions.cpython-311.pyc
   │     │  │  │     ├─ test_transforms.cpython-311.pyc
   │     │  │  │     ├─ test_trigonometry.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ transforms.py
   │     │  │  ├─ trigonometry.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ deltafunctions.cpython-311.pyc
   │     │  │     ├─ heurisch.cpython-311.pyc
   │     │  │     ├─ integrals.cpython-311.pyc
   │     │  │     ├─ intpoly.cpython-311.pyc
   │     │  │     ├─ laplace.cpython-311.pyc
   │     │  │     ├─ manualintegrate.cpython-311.pyc
   │     │  │     ├─ meijerint.cpython-311.pyc
   │     │  │     ├─ meijerint_doc.cpython-311.pyc
   │     │  │     ├─ prde.cpython-311.pyc
   │     │  │     ├─ quadrature.cpython-311.pyc
   │     │  │     ├─ rationaltools.cpython-311.pyc
   │     │  │     ├─ rde.cpython-311.pyc
   │     │  │     ├─ risch.cpython-311.pyc
   │     │  │     ├─ singularityfunctions.cpython-311.pyc
   │     │  │     ├─ transforms.cpython-311.pyc
   │     │  │     ├─ trigonometry.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ interactive
   │     │  │  ├─ printing.py
   │     │  │  ├─ session.py
   │     │  │  ├─ tests
   │     │  │  │  ├─ test_interactive.py
   │     │  │  │  ├─ test_ipython.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ test_interactive.cpython-311.pyc
   │     │  │  │     ├─ test_ipython.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ traversal.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ printing.cpython-311.pyc
   │     │  │     ├─ session.cpython-311.pyc
   │     │  │     ├─ traversal.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ liealgebras
   │     │  │  ├─ cartan_matrix.py
   │     │  │  ├─ cartan_type.py
   │     │  │  ├─ dynkin_diagram.py
   │     │  │  ├─ root_system.py
   │     │  │  ├─ tests
   │     │  │  │  ├─ test_cartan_matrix.py
   │     │  │  │  ├─ test_cartan_type.py
   │     │  │  │  ├─ test_dynkin_diagram.py
   │     │  │  │  ├─ test_root_system.py
   │     │  │  │  ├─ test_type_A.py
   │     │  │  │  ├─ test_type_B.py
   │     │  │  │  ├─ test_type_C.py
   │     │  │  │  ├─ test_type_D.py
   │     │  │  │  ├─ test_type_E.py
   │     │  │  │  ├─ test_type_F.py
   │     │  │  │  ├─ test_type_G.py
   │     │  │  │  ├─ test_weyl_group.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ test_cartan_matrix.cpython-311.pyc
   │     │  │  │     ├─ test_cartan_type.cpython-311.pyc
   │     │  │  │     ├─ test_dynkin_diagram.cpython-311.pyc
   │     │  │  │     ├─ test_root_system.cpython-311.pyc
   │     │  │  │     ├─ test_type_A.cpython-311.pyc
   │     │  │  │     ├─ test_type_B.cpython-311.pyc
   │     │  │  │     ├─ test_type_C.cpython-311.pyc
   │     │  │  │     ├─ test_type_D.cpython-311.pyc
   │     │  │  │     ├─ test_type_E.cpython-311.pyc
   │     │  │  │     ├─ test_type_F.cpython-311.pyc
   │     │  │  │     ├─ test_type_G.cpython-311.pyc
   │     │  │  │     ├─ test_weyl_group.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ type_a.py
   │     │  │  ├─ type_b.py
   │     │  │  ├─ type_c.py
   │     │  │  ├─ type_d.py
   │     │  │  ├─ type_e.py
   │     │  │  ├─ type_f.py
   │     │  │  ├─ type_g.py
   │     │  │  ├─ weyl_group.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ cartan_matrix.cpython-311.pyc
   │     │  │     ├─ cartan_type.cpython-311.pyc
   │     │  │     ├─ dynkin_diagram.cpython-311.pyc
   │     │  │     ├─ root_system.cpython-311.pyc
   │     │  │     ├─ type_a.cpython-311.pyc
   │     │  │     ├─ type_b.cpython-311.pyc
   │     │  │     ├─ type_c.cpython-311.pyc
   │     │  │     ├─ type_d.cpython-311.pyc
   │     │  │     ├─ type_e.cpython-311.pyc
   │     │  │     ├─ type_f.cpython-311.pyc
   │     │  │     ├─ type_g.cpython-311.pyc
   │     │  │     ├─ weyl_group.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ logic
   │     │  │  ├─ algorithms
   │     │  │  │  ├─ dpll.py
   │     │  │  │  ├─ dpll2.py
   │     │  │  │  ├─ lra_theory.py
   │     │  │  │  ├─ minisat22_wrapper.py
   │     │  │  │  ├─ pycosat_wrapper.py
   │     │  │  │  ├─ z3_wrapper.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ dpll.cpython-311.pyc
   │     │  │  │     ├─ dpll2.cpython-311.pyc
   │     │  │  │     ├─ lra_theory.cpython-311.pyc
   │     │  │  │     ├─ minisat22_wrapper.cpython-311.pyc
   │     │  │  │     ├─ pycosat_wrapper.cpython-311.pyc
   │     │  │  │     ├─ z3_wrapper.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ boolalg.py
   │     │  │  ├─ inference.py
   │     │  │  ├─ tests
   │     │  │  │  ├─ test_boolalg.py
   │     │  │  │  ├─ test_dimacs.py
   │     │  │  │  ├─ test_inference.py
   │     │  │  │  ├─ test_lra_theory.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ test_boolalg.cpython-311.pyc
   │     │  │  │     ├─ test_dimacs.cpython-311.pyc
   │     │  │  │     ├─ test_inference.cpython-311.pyc
   │     │  │  │     ├─ test_lra_theory.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ utilities
   │     │  │  │  ├─ dimacs.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ dimacs.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ boolalg.cpython-311.pyc
   │     │  │     ├─ inference.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ matrices
   │     │  │  ├─ benchmarks
   │     │  │  │  ├─ bench_matrix.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ bench_matrix.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ common.py
   │     │  │  ├─ decompositions.py
   │     │  │  ├─ dense.py
   │     │  │  ├─ determinant.py
   │     │  │  ├─ eigen.py
   │     │  │  ├─ exceptions.py
   │     │  │  ├─ expressions
   │     │  │  │  ├─ adjoint.py
   │     │  │  │  ├─ applyfunc.py
   │     │  │  │  ├─ blockmatrix.py
   │     │  │  │  ├─ companion.py
   │     │  │  │  ├─ determinant.py
   │     │  │  │  ├─ diagonal.py
   │     │  │  │  ├─ dotproduct.py
   │     │  │  │  ├─ factorizations.py
   │     │  │  │  ├─ fourier.py
   │     │  │  │  ├─ funcmatrix.py
   │     │  │  │  ├─ hadamard.py
   │     │  │  │  ├─ inverse.py
   │     │  │  │  ├─ kronecker.py
   │     │  │  │  ├─ matadd.py
   │     │  │  │  ├─ matexpr.py
   │     │  │  │  ├─ matmul.py
   │     │  │  │  ├─ matpow.py
   │     │  │  │  ├─ permutation.py
   │     │  │  │  ├─ sets.py
   │     │  │  │  ├─ slice.py
   │     │  │  │  ├─ special.py
   │     │  │  │  ├─ tests
   │     │  │  │  │  ├─ test_adjoint.py
   │     │  │  │  │  ├─ test_applyfunc.py
   │     │  │  │  │  ├─ test_blockmatrix.py
   │     │  │  │  │  ├─ test_companion.py
   │     │  │  │  │  ├─ test_derivatives.py
   │     │  │  │  │  ├─ test_determinant.py
   │     │  │  │  │  ├─ test_diagonal.py
   │     │  │  │  │  ├─ test_dotproduct.py
   │     │  │  │  │  ├─ test_factorizations.py
   │     │  │  │  │  ├─ test_fourier.py
   │     │  │  │  │  ├─ test_funcmatrix.py
   │     │  │  │  │  ├─ test_hadamard.py
   │     │  │  │  │  ├─ test_indexing.py
   │     │  │  │  │  ├─ test_inverse.py
   │     │  │  │  │  ├─ test_kronecker.py
   │     │  │  │  │  ├─ test_matadd.py
   │     │  │  │  │  ├─ test_matexpr.py
   │     │  │  │  │  ├─ test_matmul.py
   │     │  │  │  │  ├─ test_matpow.py
   │     │  │  │  │  ├─ test_permutation.py
   │     │  │  │  │  ├─ test_sets.py
   │     │  │  │  │  ├─ test_slice.py
   │     │  │  │  │  ├─ test_special.py
   │     │  │  │  │  ├─ test_trace.py
   │     │  │  │  │  ├─ test_transpose.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ test_adjoint.cpython-311.pyc
   │     │  │  │  │     ├─ test_applyfunc.cpython-311.pyc
   │     │  │  │  │     ├─ test_blockmatrix.cpython-311.pyc
   │     │  │  │  │     ├─ test_companion.cpython-311.pyc
   │     │  │  │  │     ├─ test_derivatives.cpython-311.pyc
   │     │  │  │  │     ├─ test_determinant.cpython-311.pyc
   │     │  │  │  │     ├─ test_diagonal.cpython-311.pyc
   │     │  │  │  │     ├─ test_dotproduct.cpython-311.pyc
   │     │  │  │  │     ├─ test_factorizations.cpython-311.pyc
   │     │  │  │  │     ├─ test_fourier.cpython-311.pyc
   │     │  │  │  │     ├─ test_funcmatrix.cpython-311.pyc
   │     │  │  │  │     ├─ test_hadamard.cpython-311.pyc
   │     │  │  │  │     ├─ test_indexing.cpython-311.pyc
   │     │  │  │  │     ├─ test_inverse.cpython-311.pyc
   │     │  │  │  │     ├─ test_kronecker.cpython-311.pyc
   │     │  │  │  │     ├─ test_matadd.cpython-311.pyc
   │     │  │  │  │     ├─ test_matexpr.cpython-311.pyc
   │     │  │  │  │     ├─ test_matmul.cpython-311.pyc
   │     │  │  │  │     ├─ test_matpow.cpython-311.pyc
   │     │  │  │  │     ├─ test_permutation.cpython-311.pyc
   │     │  │  │  │     ├─ test_sets.cpython-311.pyc
   │     │  │  │  │     ├─ test_slice.cpython-311.pyc
   │     │  │  │  │     ├─ test_special.cpython-311.pyc
   │     │  │  │  │     ├─ test_trace.cpython-311.pyc
   │     │  │  │  │     ├─ test_transpose.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ trace.py
   │     │  │  │  ├─ transpose.py
   │     │  │  │  ├─ _shape.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ adjoint.cpython-311.pyc
   │     │  │  │     ├─ applyfunc.cpython-311.pyc
   │     │  │  │     ├─ blockmatrix.cpython-311.pyc
   │     │  │  │     ├─ companion.cpython-311.pyc
   │     │  │  │     ├─ determinant.cpython-311.pyc
   │     │  │  │     ├─ diagonal.cpython-311.pyc
   │     │  │  │     ├─ dotproduct.cpython-311.pyc
   │     │  │  │     ├─ factorizations.cpython-311.pyc
   │     │  │  │     ├─ fourier.cpython-311.pyc
   │     │  │  │     ├─ funcmatrix.cpython-311.pyc
   │     │  │  │     ├─ hadamard.cpython-311.pyc
   │     │  │  │     ├─ inverse.cpython-311.pyc
   │     │  │  │     ├─ kronecker.cpython-311.pyc
   │     │  │  │     ├─ matadd.cpython-311.pyc
   │     │  │  │     ├─ matexpr.cpython-311.pyc
   │     │  │  │     ├─ matmul.cpython-311.pyc
   │     │  │  │     ├─ matpow.cpython-311.pyc
   │     │  │  │     ├─ permutation.cpython-311.pyc
   │     │  │  │     ├─ sets.cpython-311.pyc
   │     │  │  │     ├─ slice.cpython-311.pyc
   │     │  │  │     ├─ special.cpython-311.pyc
   │     │  │  │     ├─ trace.cpython-311.pyc
   │     │  │  │     ├─ transpose.cpython-311.pyc
   │     │  │  │     ├─ _shape.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ graph.py
   │     │  │  ├─ immutable.py
   │     │  │  ├─ inverse.py
   │     │  │  ├─ kind.py
   │     │  │  ├─ matrices.py
   │     │  │  ├─ matrixbase.py
   │     │  │  ├─ normalforms.py
   │     │  │  ├─ reductions.py
   │     │  │  ├─ repmatrix.py
   │     │  │  ├─ solvers.py
   │     │  │  ├─ sparse.py
   │     │  │  ├─ sparsetools.py
   │     │  │  ├─ subspaces.py
   │     │  │  ├─ tests
   │     │  │  │  ├─ test_commonmatrix.py
   │     │  │  │  ├─ test_decompositions.py
   │     │  │  │  ├─ test_determinant.py
   │     │  │  │  ├─ test_domains.py
   │     │  │  │  ├─ test_eigen.py
   │     │  │  │  ├─ test_graph.py
   │     │  │  │  ├─ test_immutable.py
   │     │  │  │  ├─ test_interactions.py
   │     │  │  │  ├─ test_matrices.py
   │     │  │  │  ├─ test_matrixbase.py
   │     │  │  │  ├─ test_normalforms.py
   │     │  │  │  ├─ test_reductions.py
   │     │  │  │  ├─ test_repmatrix.py
   │     │  │  │  ├─ test_solvers.py
   │     │  │  │  ├─ test_sparse.py
   │     │  │  │  ├─ test_sparsetools.py
   │     │  │  │  ├─ test_subspaces.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ test_commonmatrix.cpython-311.pyc
   │     │  │  │     ├─ test_decompositions.cpython-311.pyc
   │     │  │  │     ├─ test_determinant.cpython-311.pyc
   │     │  │  │     ├─ test_domains.cpython-311.pyc
   │     │  │  │     ├─ test_eigen.cpython-311.pyc
   │     │  │  │     ├─ test_graph.cpython-311.pyc
   │     │  │  │     ├─ test_immutable.cpython-311.pyc
   │     │  │  │     ├─ test_interactions.cpython-311.pyc
   │     │  │  │     ├─ test_matrices.cpython-311.pyc
   │     │  │  │     ├─ test_matrixbase.cpython-311.pyc
   │     │  │  │     ├─ test_normalforms.cpython-311.pyc
   │     │  │  │     ├─ test_reductions.cpython-311.pyc
   │     │  │  │     ├─ test_repmatrix.cpython-311.pyc
   │     │  │  │     ├─ test_solvers.cpython-311.pyc
   │     │  │  │     ├─ test_sparse.cpython-311.pyc
   │     │  │  │     ├─ test_sparsetools.cpython-311.pyc
   │     │  │  │     ├─ test_subspaces.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ utilities.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ common.cpython-311.pyc
   │     │  │     ├─ decompositions.cpython-311.pyc
   │     │  │     ├─ dense.cpython-311.pyc
   │     │  │     ├─ determinant.cpython-311.pyc
   │     │  │     ├─ eigen.cpython-311.pyc
   │     │  │     ├─ exceptions.cpython-311.pyc
   │     │  │     ├─ graph.cpython-311.pyc
   │     │  │     ├─ immutable.cpython-311.pyc
   │     │  │     ├─ inverse.cpython-311.pyc
   │     │  │     ├─ kind.cpython-311.pyc
   │     │  │     ├─ matrices.cpython-311.pyc
   │     │  │     ├─ matrixbase.cpython-311.pyc
   │     │  │     ├─ normalforms.cpython-311.pyc
   │     │  │     ├─ reductions.cpython-311.pyc
   │     │  │     ├─ repmatrix.cpython-311.pyc
   │     │  │     ├─ solvers.cpython-311.pyc
   │     │  │     ├─ sparse.cpython-311.pyc
   │     │  │     ├─ sparsetools.cpython-311.pyc
   │     │  │     ├─ subspaces.cpython-311.pyc
   │     │  │     ├─ utilities.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ multipledispatch
   │     │  │  ├─ conflict.py
   │     │  │  ├─ core.py
   │     │  │  ├─ dispatcher.py
   │     │  │  ├─ tests
   │     │  │  │  ├─ test_conflict.py
   │     │  │  │  ├─ test_core.py
   │     │  │  │  ├─ test_dispatcher.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ test_conflict.cpython-311.pyc
   │     │  │  │     ├─ test_core.cpython-311.pyc
   │     │  │  │     ├─ test_dispatcher.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ utils.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ conflict.cpython-311.pyc
   │     │  │     ├─ core.cpython-311.pyc
   │     │  │     ├─ dispatcher.cpython-311.pyc
   │     │  │     ├─ utils.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ ntheory
   │     │  │  ├─ bbp_pi.py
   │     │  │  ├─ continued_fraction.py
   │     │  │  ├─ digits.py
   │     │  │  ├─ ecm.py
   │     │  │  ├─ egyptian_fraction.py
   │     │  │  ├─ elliptic_curve.py
   │     │  │  ├─ factor_.py
   │     │  │  ├─ generate.py
   │     │  │  ├─ modular.py
   │     │  │  ├─ multinomial.py
   │     │  │  ├─ partitions_.py
   │     │  │  ├─ primetest.py
   │     │  │  ├─ qs.py
   │     │  │  ├─ residue_ntheory.py
   │     │  │  ├─ tests
   │     │  │  │  ├─ test_bbp_pi.py
   │     │  │  │  ├─ test_continued_fraction.py
   │     │  │  │  ├─ test_digits.py
   │     │  │  │  ├─ test_ecm.py
   │     │  │  │  ├─ test_egyptian_fraction.py
   │     │  │  │  ├─ test_elliptic_curve.py
   │     │  │  │  ├─ test_factor_.py
   │     │  │  │  ├─ test_generate.py
   │     │  │  │  ├─ test_hypothesis.py
   │     │  │  │  ├─ test_modular.py
   │     │  │  │  ├─ test_multinomial.py
   │     │  │  │  ├─ test_partitions.py
   │     │  │  │  ├─ test_primetest.py
   │     │  │  │  ├─ test_qs.py
   │     │  │  │  ├─ test_residue.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ test_bbp_pi.cpython-311.pyc
   │     │  │  │     ├─ test_continued_fraction.cpython-311.pyc
   │     │  │  │     ├─ test_digits.cpython-311.pyc
   │     │  │  │     ├─ test_ecm.cpython-311.pyc
   │     │  │  │     ├─ test_egyptian_fraction.cpython-311.pyc
   │     │  │  │     ├─ test_elliptic_curve.cpython-311.pyc
   │     │  │  │     ├─ test_factor_.cpython-311.pyc
   │     │  │  │     ├─ test_generate.cpython-311.pyc
   │     │  │  │     ├─ test_hypothesis.cpython-311.pyc
   │     │  │  │     ├─ test_modular.cpython-311.pyc
   │     │  │  │     ├─ test_multinomial.cpython-311.pyc
   │     │  │  │     ├─ test_partitions.cpython-311.pyc
   │     │  │  │     ├─ test_primetest.cpython-311.pyc
   │     │  │  │     ├─ test_qs.cpython-311.pyc
   │     │  │  │     ├─ test_residue.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ bbp_pi.cpython-311.pyc
   │     │  │     ├─ continued_fraction.cpython-311.pyc
   │     │  │     ├─ digits.cpython-311.pyc
   │     │  │     ├─ ecm.cpython-311.pyc
   │     │  │     ├─ egyptian_fraction.cpython-311.pyc
   │     │  │     ├─ elliptic_curve.cpython-311.pyc
   │     │  │     ├─ factor_.cpython-311.pyc
   │     │  │     ├─ generate.cpython-311.pyc
   │     │  │     ├─ modular.cpython-311.pyc
   │     │  │     ├─ multinomial.cpython-311.pyc
   │     │  │     ├─ partitions_.cpython-311.pyc
   │     │  │     ├─ primetest.cpython-311.pyc
   │     │  │     ├─ qs.cpython-311.pyc
   │     │  │     ├─ residue_ntheory.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ parsing
   │     │  │  ├─ ast_parser.py
   │     │  │  ├─ autolev
   │     │  │  │  ├─ Autolev.g4
   │     │  │  │  ├─ test-examples
   │     │  │  │  │  ├─ pydy-example-repo
   │     │  │  │  │  │  ├─ chaos_pendulum.al
   │     │  │  │  │  │  ├─ chaos_pendulum.py
   │     │  │  │  │  │  ├─ double_pendulum.al
   │     │  │  │  │  │  ├─ double_pendulum.py
   │     │  │  │  │  │  ├─ mass_spring_damper.al
   │     │  │  │  │  │  ├─ mass_spring_damper.py
   │     │  │  │  │  │  ├─ non_min_pendulum.al
   │     │  │  │  │  │  ├─ non_min_pendulum.py
   │     │  │  │  │  │  └─ __pycache__
   │     │  │  │  │  │     ├─ chaos_pendulum.cpython-311.pyc
   │     │  │  │  │  │     ├─ double_pendulum.cpython-311.pyc
   │     │  │  │  │  │     ├─ mass_spring_damper.cpython-311.pyc
   │     │  │  │  │  │     └─ non_min_pendulum.cpython-311.pyc
   │     │  │  │  │  ├─ README.txt
   │     │  │  │  │  ├─ ruletest1.al
   │     │  │  │  │  ├─ ruletest1.py
   │     │  │  │  │  ├─ ruletest10.al
   │     │  │  │  │  ├─ ruletest10.py
   │     │  │  │  │  ├─ ruletest11.al
   │     │  │  │  │  ├─ ruletest11.py
   │     │  │  │  │  ├─ ruletest12.al
   │     │  │  │  │  ├─ ruletest12.py
   │     │  │  │  │  ├─ ruletest2.al
   │     │  │  │  │  ├─ ruletest2.py
   │     │  │  │  │  ├─ ruletest3.al
   │     │  │  │  │  ├─ ruletest3.py
   │     │  │  │  │  ├─ ruletest4.al
   │     │  │  │  │  ├─ ruletest4.py
   │     │  │  │  │  ├─ ruletest5.al
   │     │  │  │  │  ├─ ruletest5.py
   │     │  │  │  │  ├─ ruletest6.al
   │     │  │  │  │  ├─ ruletest6.py
   │     │  │  │  │  ├─ ruletest7.al
   │     │  │  │  │  ├─ ruletest7.py
   │     │  │  │  │  ├─ ruletest8.al
   │     │  │  │  │  ├─ ruletest8.py
   │     │  │  │  │  ├─ ruletest9.al
   │     │  │  │  │  ├─ ruletest9.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ ruletest1.cpython-311.pyc
   │     │  │  │  │     ├─ ruletest10.cpython-311.pyc
   │     │  │  │  │     ├─ ruletest11.cpython-311.pyc
   │     │  │  │  │     ├─ ruletest12.cpython-311.pyc
   │     │  │  │  │     ├─ ruletest2.cpython-311.pyc
   │     │  │  │  │     ├─ ruletest3.cpython-311.pyc
   │     │  │  │  │     ├─ ruletest4.cpython-311.pyc
   │     │  │  │  │     ├─ ruletest5.cpython-311.pyc
   │     │  │  │  │     ├─ ruletest6.cpython-311.pyc
   │     │  │  │  │     ├─ ruletest7.cpython-311.pyc
   │     │  │  │  │     ├─ ruletest8.cpython-311.pyc
   │     │  │  │  │     └─ ruletest9.cpython-311.pyc
   │     │  │  │  ├─ _antlr
   │     │  │  │  │  ├─ autolevlexer.py
   │     │  │  │  │  ├─ autolevlistener.py
   │     │  │  │  │  ├─ autolevparser.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ autolevlexer.cpython-311.pyc
   │     │  │  │  │     ├─ autolevlistener.cpython-311.pyc
   │     │  │  │  │     ├─ autolevparser.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ _build_autolev_antlr.py
   │     │  │  │  ├─ _listener_autolev_antlr.py
   │     │  │  │  ├─ _parse_autolev_antlr.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ _build_autolev_antlr.cpython-311.pyc
   │     │  │  │     ├─ _listener_autolev_antlr.cpython-311.pyc
   │     │  │  │     ├─ _parse_autolev_antlr.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ c
   │     │  │  │  ├─ c_parser.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ c_parser.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ fortran
   │     │  │  │  ├─ fortran_parser.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ fortran_parser.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ latex
   │     │  │  │  ├─ errors.py
   │     │  │  │  ├─ lark
   │     │  │  │  │  ├─ grammar
   │     │  │  │  │  │  ├─ greek_symbols.lark
   │     │  │  │  │  │  └─ latex.lark
   │     │  │  │  │  ├─ latex_parser.py
   │     │  │  │  │  ├─ transformer.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ latex_parser.cpython-311.pyc
   │     │  │  │  │     ├─ transformer.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ LaTeX.g4
   │     │  │  │  ├─ LICENSE.txt
   │     │  │  │  ├─ _antlr
   │     │  │  │  │  ├─ latexlexer.py
   │     │  │  │  │  ├─ latexparser.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ latexlexer.cpython-311.pyc
   │     │  │  │  │     ├─ latexparser.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ _build_latex_antlr.py
   │     │  │  │  ├─ _parse_latex_antlr.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ errors.cpython-311.pyc
   │     │  │  │     ├─ _build_latex_antlr.cpython-311.pyc
   │     │  │  │     ├─ _parse_latex_antlr.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ mathematica.py
   │     │  │  ├─ maxima.py
   │     │  │  ├─ sympy_parser.py
   │     │  │  ├─ sym_expr.py
   │     │  │  ├─ tests
   │     │  │  │  ├─ test_ast_parser.py
   │     │  │  │  ├─ test_autolev.py
   │     │  │  │  ├─ test_custom_latex.py
   │     │  │  │  ├─ test_c_parser.py
   │     │  │  │  ├─ test_fortran_parser.py
   │     │  │  │  ├─ test_implicit_multiplication_application.py
   │     │  │  │  ├─ test_latex.py
   │     │  │  │  ├─ test_latex_deps.py
   │     │  │  │  ├─ test_latex_lark.py
   │     │  │  │  ├─ test_mathematica.py
   │     │  │  │  ├─ test_maxima.py
   │     │  │  │  ├─ test_sympy_parser.py
   │     │  │  │  ├─ test_sym_expr.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ test_ast_parser.cpython-311.pyc
   │     │  │  │     ├─ test_autolev.cpython-311.pyc
   │     │  │  │     ├─ test_custom_latex.cpython-311.pyc
   │     │  │  │     ├─ test_c_parser.cpython-311.pyc
   │     │  │  │     ├─ test_fortran_parser.cpython-311.pyc
   │     │  │  │     ├─ test_implicit_multiplication_application.cpython-311.pyc
   │     │  │  │     ├─ test_latex.cpython-311.pyc
   │     │  │  │     ├─ test_latex_deps.cpython-311.pyc
   │     │  │  │     ├─ test_latex_lark.cpython-311.pyc
   │     │  │  │     ├─ test_mathematica.cpython-311.pyc
   │     │  │  │     ├─ test_maxima.cpython-311.pyc
   │     │  │  │     ├─ test_sympy_parser.cpython-311.pyc
   │     │  │  │     ├─ test_sym_expr.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ ast_parser.cpython-311.pyc
   │     │  │     ├─ mathematica.cpython-311.pyc
   │     │  │     ├─ maxima.cpython-311.pyc
   │     │  │     ├─ sympy_parser.cpython-311.pyc
   │     │  │     ├─ sym_expr.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ physics
   │     │  │  ├─ biomechanics
   │     │  │  │  ├─ activation.py
   │     │  │  │  ├─ curve.py
   │     │  │  │  ├─ musculotendon.py
   │     │  │  │  ├─ tests
   │     │  │  │  │  ├─ test_activation.py
   │     │  │  │  │  ├─ test_curve.py
   │     │  │  │  │  ├─ test_mixin.py
   │     │  │  │  │  ├─ test_musculotendon.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ test_activation.cpython-311.pyc
   │     │  │  │  │     ├─ test_curve.cpython-311.pyc
   │     │  │  │  │     ├─ test_mixin.cpython-311.pyc
   │     │  │  │  │     ├─ test_musculotendon.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ _mixin.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ activation.cpython-311.pyc
   │     │  │  │     ├─ curve.cpython-311.pyc
   │     │  │  │     ├─ musculotendon.cpython-311.pyc
   │     │  │  │     ├─ _mixin.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ continuum_mechanics
   │     │  │  │  ├─ arch.py
   │     │  │  │  ├─ beam.py
   │     │  │  │  ├─ cable.py
   │     │  │  │  ├─ tests
   │     │  │  │  │  ├─ test_arch.py
   │     │  │  │  │  ├─ test_beam.py
   │     │  │  │  │  ├─ test_cable.py
   │     │  │  │  │  ├─ test_truss.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ test_arch.cpython-311.pyc
   │     │  │  │  │     ├─ test_beam.cpython-311.pyc
   │     │  │  │  │     ├─ test_cable.cpython-311.pyc
   │     │  │  │  │     ├─ test_truss.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ truss.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ arch.cpython-311.pyc
   │     │  │  │     ├─ beam.cpython-311.pyc
   │     │  │  │     ├─ cable.cpython-311.pyc
   │     │  │  │     ├─ truss.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ control
   │     │  │  │  ├─ control_plots.py
   │     │  │  │  ├─ lti.py
   │     │  │  │  ├─ tests
   │     │  │  │  │  ├─ test_control_plots.py
   │     │  │  │  │  ├─ test_lti.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ test_control_plots.cpython-311.pyc
   │     │  │  │  │     ├─ test_lti.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ control_plots.cpython-311.pyc
   │     │  │  │     ├─ lti.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ hep
   │     │  │  │  ├─ gamma_matrices.py
   │     │  │  │  ├─ tests
   │     │  │  │  │  ├─ test_gamma_matrices.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ test_gamma_matrices.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ gamma_matrices.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ hydrogen.py
   │     │  │  ├─ matrices.py
   │     │  │  ├─ mechanics
   │     │  │  │  ├─ actuator.py
   │     │  │  │  ├─ body.py
   │     │  │  │  ├─ body_base.py
   │     │  │  │  ├─ functions.py
   │     │  │  │  ├─ inertia.py
   │     │  │  │  ├─ joint.py
   │     │  │  │  ├─ jointsmethod.py
   │     │  │  │  ├─ kane.py
   │     │  │  │  ├─ lagrange.py
   │     │  │  │  ├─ linearize.py
   │     │  │  │  ├─ loads.py
   │     │  │  │  ├─ method.py
   │     │  │  │  ├─ models.py
   │     │  │  │  ├─ particle.py
   │     │  │  │  ├─ pathway.py
   │     │  │  │  ├─ rigidbody.py
   │     │  │  │  ├─ system.py
   │     │  │  │  ├─ tests
   │     │  │  │  │  ├─ test_actuator.py
   │     │  │  │  │  ├─ test_body.py
   │     │  │  │  │  ├─ test_functions.py
   │     │  │  │  │  ├─ test_inertia.py
   │     │  │  │  │  ├─ test_joint.py
   │     │  │  │  │  ├─ test_jointsmethod.py
   │     │  │  │  │  ├─ test_kane.py
   │     │  │  │  │  ├─ test_kane2.py
   │     │  │  │  │  ├─ test_kane3.py
   │     │  │  │  │  ├─ test_kane4.py
   │     │  │  │  │  ├─ test_kane5.py
   │     │  │  │  │  ├─ test_lagrange.py
   │     │  │  │  │  ├─ test_lagrange2.py
   │     │  │  │  │  ├─ test_linearity_of_velocity_constraints.py
   │     │  │  │  │  ├─ test_linearize.py
   │     │  │  │  │  ├─ test_loads.py
   │     │  │  │  │  ├─ test_method.py
   │     │  │  │  │  ├─ test_models.py
   │     │  │  │  │  ├─ test_particle.py
   │     │  │  │  │  ├─ test_pathway.py
   │     │  │  │  │  ├─ test_rigidbody.py
   │     │  │  │  │  ├─ test_system.py
   │     │  │  │  │  ├─ test_system_class.py
   │     │  │  │  │  ├─ test_wrapping_geometry.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ test_actuator.cpython-311.pyc
   │     │  │  │  │     ├─ test_body.cpython-311.pyc
   │     │  │  │  │     ├─ test_functions.cpython-311.pyc
   │     │  │  │  │     ├─ test_inertia.cpython-311.pyc
   │     │  │  │  │     ├─ test_joint.cpython-311.pyc
   │     │  │  │  │     ├─ test_jointsmethod.cpython-311.pyc
   │     │  │  │  │     ├─ test_kane.cpython-311.pyc
   │     │  │  │  │     ├─ test_kane2.cpython-311.pyc
   │     │  │  │  │     ├─ test_kane3.cpython-311.pyc
   │     │  │  │  │     ├─ test_kane4.cpython-311.pyc
   │     │  │  │  │     ├─ test_kane5.cpython-311.pyc
   │     │  │  │  │     ├─ test_lagrange.cpython-311.pyc
   │     │  │  │  │     ├─ test_lagrange2.cpython-311.pyc
   │     │  │  │  │     ├─ test_linearity_of_velocity_constraints.cpython-311.pyc
   │     │  │  │  │     ├─ test_linearize.cpython-311.pyc
   │     │  │  │  │     ├─ test_loads.cpython-311.pyc
   │     │  │  │  │     ├─ test_method.cpython-311.pyc
   │     │  │  │  │     ├─ test_models.cpython-311.pyc
   │     │  │  │  │     ├─ test_particle.cpython-311.pyc
   │     │  │  │  │     ├─ test_pathway.cpython-311.pyc
   │     │  │  │  │     ├─ test_rigidbody.cpython-311.pyc
   │     │  │  │  │     ├─ test_system.cpython-311.pyc
   │     │  │  │  │     ├─ test_system_class.cpython-311.pyc
   │     │  │  │  │     ├─ test_wrapping_geometry.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ wrapping_geometry.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ actuator.cpython-311.pyc
   │     │  │  │     ├─ body.cpython-311.pyc
   │     │  │  │     ├─ body_base.cpython-311.pyc
   │     │  │  │     ├─ functions.cpython-311.pyc
   │     │  │  │     ├─ inertia.cpython-311.pyc
   │     │  │  │     ├─ joint.cpython-311.pyc
   │     │  │  │     ├─ jointsmethod.cpython-311.pyc
   │     │  │  │     ├─ kane.cpython-311.pyc
   │     │  │  │     ├─ lagrange.cpython-311.pyc
   │     │  │  │     ├─ linearize.cpython-311.pyc
   │     │  │  │     ├─ loads.cpython-311.pyc
   │     │  │  │     ├─ method.cpython-311.pyc
   │     │  │  │     ├─ models.cpython-311.pyc
   │     │  │  │     ├─ particle.cpython-311.pyc
   │     │  │  │     ├─ pathway.cpython-311.pyc
   │     │  │  │     ├─ rigidbody.cpython-311.pyc
   │     │  │  │     ├─ system.cpython-311.pyc
   │     │  │  │     ├─ wrapping_geometry.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ optics
   │     │  │  │  ├─ gaussopt.py
   │     │  │  │  ├─ medium.py
   │     │  │  │  ├─ polarization.py
   │     │  │  │  ├─ tests
   │     │  │  │  │  ├─ test_gaussopt.py
   │     │  │  │  │  ├─ test_medium.py
   │     │  │  │  │  ├─ test_polarization.py
   │     │  │  │  │  ├─ test_utils.py
   │     │  │  │  │  ├─ test_waves.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ test_gaussopt.cpython-311.pyc
   │     │  │  │  │     ├─ test_medium.cpython-311.pyc
   │     │  │  │  │     ├─ test_polarization.cpython-311.pyc
   │     │  │  │  │     ├─ test_utils.cpython-311.pyc
   │     │  │  │  │     ├─ test_waves.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ utils.py
   │     │  │  │  ├─ waves.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ gaussopt.cpython-311.pyc
   │     │  │  │     ├─ medium.cpython-311.pyc
   │     │  │  │     ├─ polarization.cpython-311.pyc
   │     │  │  │     ├─ utils.cpython-311.pyc
   │     │  │  │     ├─ waves.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ paulialgebra.py
   │     │  │  ├─ pring.py
   │     │  │  ├─ qho_1d.py
   │     │  │  ├─ quantum
   │     │  │  │  ├─ anticommutator.py
   │     │  │  │  ├─ boson.py
   │     │  │  │  ├─ cartesian.py
   │     │  │  │  ├─ cg.py
   │     │  │  │  ├─ circuitplot.py
   │     │  │  │  ├─ circuitutils.py
   │     │  │  │  ├─ commutator.py
   │     │  │  │  ├─ constants.py
   │     │  │  │  ├─ dagger.py
   │     │  │  │  ├─ density.py
   │     │  │  │  ├─ fermion.py
   │     │  │  │  ├─ gate.py
   │     │  │  │  ├─ grover.py
   │     │  │  │  ├─ hilbert.py
   │     │  │  │  ├─ identitysearch.py
   │     │  │  │  ├─ innerproduct.py
   │     │  │  │  ├─ kind.py
   │     │  │  │  ├─ matrixcache.py
   │     │  │  │  ├─ matrixutils.py
   │     │  │  │  ├─ operator.py
   │     │  │  │  ├─ operatorordering.py
   │     │  │  │  ├─ operatorset.py
   │     │  │  │  ├─ pauli.py
   │     │  │  │  ├─ piab.py
   │     │  │  │  ├─ qapply.py
   │     │  │  │  ├─ qasm.py
   │     │  │  │  ├─ qexpr.py
   │     │  │  │  ├─ qft.py
   │     │  │  │  ├─ qubit.py
   │     │  │  │  ├─ represent.py
   │     │  │  │  ├─ sho1d.py
   │     │  │  │  ├─ shor.py
   │     │  │  │  ├─ spin.py
   │     │  │  │  ├─ state.py
   │     │  │  │  ├─ tensorproduct.py
   │     │  │  │  ├─ tests
   │     │  │  │  │  ├─ test_anticommutator.py
   │     │  │  │  │  ├─ test_boson.py
   │     │  │  │  │  ├─ test_cartesian.py
   │     │  │  │  │  ├─ test_cg.py
   │     │  │  │  │  ├─ test_circuitplot.py
   │     │  │  │  │  ├─ test_circuitutils.py
   │     │  │  │  │  ├─ test_commutator.py
   │     │  │  │  │  ├─ test_constants.py
   │     │  │  │  │  ├─ test_dagger.py
   │     │  │  │  │  ├─ test_density.py
   │     │  │  │  │  ├─ test_fermion.py
   │     │  │  │  │  ├─ test_gate.py
   │     │  │  │  │  ├─ test_grover.py
   │     │  │  │  │  ├─ test_hilbert.py
   │     │  │  │  │  ├─ test_identitysearch.py
   │     │  │  │  │  ├─ test_innerproduct.py
   │     │  │  │  │  ├─ test_kind.py
   │     │  │  │  │  ├─ test_matrixutils.py
   │     │  │  │  │  ├─ test_operator.py
   │     │  │  │  │  ├─ test_operatorordering.py
   │     │  │  │  │  ├─ test_operatorset.py
   │     │  │  │  │  ├─ test_pauli.py
   │     │  │  │  │  ├─ test_piab.py
   │     │  │  │  │  ├─ test_printing.py
   │     │  │  │  │  ├─ test_qapply.py
   │     │  │  │  │  ├─ test_qasm.py
   │     │  │  │  │  ├─ test_qexpr.py
   │     │  │  │  │  ├─ test_qft.py
   │     │  │  │  │  ├─ test_qubit.py
   │     │  │  │  │  ├─ test_represent.py
   │     │  │  │  │  ├─ test_sho1d.py
   │     │  │  │  │  ├─ test_shor.py
   │     │  │  │  │  ├─ test_spin.py
   │     │  │  │  │  ├─ test_state.py
   │     │  │  │  │  ├─ test_tensorproduct.py
   │     │  │  │  │  ├─ test_trace.py
   │     │  │  │  │  ├─ test_transforms.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ test_anticommutator.cpython-311.pyc
   │     │  │  │  │     ├─ test_boson.cpython-311.pyc
   │     │  │  │  │     ├─ test_cartesian.cpython-311.pyc
   │     │  │  │  │     ├─ test_cg.cpython-311.pyc
   │     │  │  │  │     ├─ test_circuitplot.cpython-311.pyc
   │     │  │  │  │     ├─ test_circuitutils.cpython-311.pyc
   │     │  │  │  │     ├─ test_commutator.cpython-311.pyc
   │     │  │  │  │     ├─ test_constants.cpython-311.pyc
   │     │  │  │  │     ├─ test_dagger.cpython-311.pyc
   │     │  │  │  │     ├─ test_density.cpython-311.pyc
   │     │  │  │  │     ├─ test_fermion.cpython-311.pyc
   │     │  │  │  │     ├─ test_gate.cpython-311.pyc
   │     │  │  │  │     ├─ test_grover.cpython-311.pyc
   │     │  │  │  │     ├─ test_hilbert.cpython-311.pyc
   │     │  │  │  │     ├─ test_identitysearch.cpython-311.pyc
   │     │  │  │  │     ├─ test_innerproduct.cpython-311.pyc
   │     │  │  │  │     ├─ test_kind.cpython-311.pyc
   │     │  │  │  │     ├─ test_matrixutils.cpython-311.pyc
   │     │  │  │  │     ├─ test_operator.cpython-311.pyc
   │     │  │  │  │     ├─ test_operatorordering.cpython-311.pyc
   │     │  │  │  │     ├─ test_operatorset.cpython-311.pyc
   │     │  │  │  │     ├─ test_pauli.cpython-311.pyc
   │     │  │  │  │     ├─ test_piab.cpython-311.pyc
   │     │  │  │  │     ├─ test_printing.cpython-311.pyc
   │     │  │  │  │     ├─ test_qapply.cpython-311.pyc
   │     │  │  │  │     ├─ test_qasm.cpython-311.pyc
   │     │  │  │  │     ├─ test_qexpr.cpython-311.pyc
   │     │  │  │  │     ├─ test_qft.cpython-311.pyc
   │     │  │  │  │     ├─ test_qubit.cpython-311.pyc
   │     │  │  │  │     ├─ test_represent.cpython-311.pyc
   │     │  │  │  │     ├─ test_sho1d.cpython-311.pyc
   │     │  │  │  │     ├─ test_shor.cpython-311.pyc
   │     │  │  │  │     ├─ test_spin.cpython-311.pyc
   │     │  │  │  │     ├─ test_state.cpython-311.pyc
   │     │  │  │  │     ├─ test_tensorproduct.cpython-311.pyc
   │     │  │  │  │     ├─ test_trace.cpython-311.pyc
   │     │  │  │  │     ├─ test_transforms.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ trace.py
   │     │  │  │  ├─ transforms.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ anticommutator.cpython-311.pyc
   │     │  │  │     ├─ boson.cpython-311.pyc
   │     │  │  │     ├─ cartesian.cpython-311.pyc
   │     │  │  │     ├─ cg.cpython-311.pyc
   │     │  │  │     ├─ circuitplot.cpython-311.pyc
   │     │  │  │     ├─ circuitutils.cpython-311.pyc
   │     │  │  │     ├─ commutator.cpython-311.pyc
   │     │  │  │     ├─ constants.cpython-311.pyc
   │     │  │  │     ├─ dagger.cpython-311.pyc
   │     │  │  │     ├─ density.cpython-311.pyc
   │     │  │  │     ├─ fermion.cpython-311.pyc
   │     │  │  │     ├─ gate.cpython-311.pyc
   │     │  │  │     ├─ grover.cpython-311.pyc
   │     │  │  │     ├─ hilbert.cpython-311.pyc
   │     │  │  │     ├─ identitysearch.cpython-311.pyc
   │     │  │  │     ├─ innerproduct.cpython-311.pyc
   │     │  │  │     ├─ kind.cpython-311.pyc
   │     │  │  │     ├─ matrixcache.cpython-311.pyc
   │     │  │  │     ├─ matrixutils.cpython-311.pyc
   │     │  │  │     ├─ operator.cpython-311.pyc
   │     │  │  │     ├─ operatorordering.cpython-311.pyc
   │     │  │  │     ├─ operatorset.cpython-311.pyc
   │     │  │  │     ├─ pauli.cpython-311.pyc
   │     │  │  │     ├─ piab.cpython-311.pyc
   │     │  │  │     ├─ qapply.cpython-311.pyc
   │     │  │  │     ├─ qasm.cpython-311.pyc
   │     │  │  │     ├─ qexpr.cpython-311.pyc
   │     │  │  │     ├─ qft.cpython-311.pyc
   │     │  │  │     ├─ qubit.cpython-311.pyc
   │     │  │  │     ├─ represent.cpython-311.pyc
   │     │  │  │     ├─ sho1d.cpython-311.pyc
   │     │  │  │     ├─ shor.cpython-311.pyc
   │     │  │  │     ├─ spin.cpython-311.pyc
   │     │  │  │     ├─ state.cpython-311.pyc
   │     │  │  │     ├─ tensorproduct.cpython-311.pyc
   │     │  │  │     ├─ trace.cpython-311.pyc
   │     │  │  │     ├─ transforms.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ secondquant.py
   │     │  │  ├─ sho.py
   │     │  │  ├─ tests
   │     │  │  │  ├─ test_clebsch_gordan.py
   │     │  │  │  ├─ test_hydrogen.py
   │     │  │  │  ├─ test_paulialgebra.py
   │     │  │  │  ├─ test_physics_matrices.py
   │     │  │  │  ├─ test_pring.py
   │     │  │  │  ├─ test_qho_1d.py
   │     │  │  │  ├─ test_secondquant.py
   │     │  │  │  ├─ test_sho.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ test_clebsch_gordan.cpython-311.pyc
   │     │  │  │     ├─ test_hydrogen.cpython-311.pyc
   │     │  │  │     ├─ test_paulialgebra.cpython-311.pyc
   │     │  │  │     ├─ test_physics_matrices.cpython-311.pyc
   │     │  │  │     ├─ test_pring.cpython-311.pyc
   │     │  │  │     ├─ test_qho_1d.cpython-311.pyc
   │     │  │  │     ├─ test_secondquant.cpython-311.pyc
   │     │  │  │     ├─ test_sho.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ units
   │     │  │  │  ├─ definitions
   │     │  │  │  │  ├─ dimension_definitions.py
   │     │  │  │  │  ├─ unit_definitions.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ dimension_definitions.cpython-311.pyc
   │     │  │  │  │     ├─ unit_definitions.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ dimensions.py
   │     │  │  │  ├─ prefixes.py
   │     │  │  │  ├─ quantities.py
   │     │  │  │  ├─ systems
   │     │  │  │  │  ├─ cgs.py
   │     │  │  │  │  ├─ length_weight_time.py
   │     │  │  │  │  ├─ mks.py
   │     │  │  │  │  ├─ mksa.py
   │     │  │  │  │  ├─ natural.py
   │     │  │  │  │  ├─ si.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ cgs.cpython-311.pyc
   │     │  │  │  │     ├─ length_weight_time.cpython-311.pyc
   │     │  │  │  │     ├─ mks.cpython-311.pyc
   │     │  │  │  │     ├─ mksa.cpython-311.pyc
   │     │  │  │  │     ├─ natural.cpython-311.pyc
   │     │  │  │  │     ├─ si.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ tests
   │     │  │  │  │  ├─ test_dimensions.py
   │     │  │  │  │  ├─ test_dimensionsystem.py
   │     │  │  │  │  ├─ test_prefixes.py
   │     │  │  │  │  ├─ test_quantities.py
   │     │  │  │  │  ├─ test_unitsystem.py
   │     │  │  │  │  ├─ test_unit_system_cgs_gauss.py
   │     │  │  │  │  ├─ test_util.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ test_dimensions.cpython-311.pyc
   │     │  │  │  │     ├─ test_dimensionsystem.cpython-311.pyc
   │     │  │  │  │     ├─ test_prefixes.cpython-311.pyc
   │     │  │  │  │     ├─ test_quantities.cpython-311.pyc
   │     │  │  │  │     ├─ test_unitsystem.cpython-311.pyc
   │     │  │  │  │     ├─ test_unit_system_cgs_gauss.cpython-311.pyc
   │     │  │  │  │     ├─ test_util.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ unitsystem.py
   │     │  │  │  ├─ util.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ dimensions.cpython-311.pyc
   │     │  │  │     ├─ prefixes.cpython-311.pyc
   │     │  │  │     ├─ quantities.cpython-311.pyc
   │     │  │  │     ├─ unitsystem.cpython-311.pyc
   │     │  │  │     ├─ util.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ vector
   │     │  │  │  ├─ dyadic.py
   │     │  │  │  ├─ fieldfunctions.py
   │     │  │  │  ├─ frame.py
   │     │  │  │  ├─ functions.py
   │     │  │  │  ├─ point.py
   │     │  │  │  ├─ printing.py
   │     │  │  │  ├─ tests
   │     │  │  │  │  ├─ test_dyadic.py
   │     │  │  │  │  ├─ test_fieldfunctions.py
   │     │  │  │  │  ├─ test_frame.py
   │     │  │  │  │  ├─ test_functions.py
   │     │  │  │  │  ├─ test_output.py
   │     │  │  │  │  ├─ test_point.py
   │     │  │  │  │  ├─ test_printing.py
   │     │  │  │  │  ├─ test_vector.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ test_dyadic.cpython-311.pyc
   │     │  │  │  │     ├─ test_fieldfunctions.cpython-311.pyc
   │     │  │  │  │     ├─ test_frame.cpython-311.pyc
   │     │  │  │  │     ├─ test_functions.cpython-311.pyc
   │     │  │  │  │     ├─ test_output.cpython-311.pyc
   │     │  │  │  │     ├─ test_point.cpython-311.pyc
   │     │  │  │  │     ├─ test_printing.cpython-311.pyc
   │     │  │  │  │     ├─ test_vector.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ vector.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ dyadic.cpython-311.pyc
   │     │  │  │     ├─ fieldfunctions.cpython-311.pyc
   │     │  │  │     ├─ frame.cpython-311.pyc
   │     │  │  │     ├─ functions.cpython-311.pyc
   │     │  │  │     ├─ point.cpython-311.pyc
   │     │  │  │     ├─ printing.cpython-311.pyc
   │     │  │  │     ├─ vector.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ wigner.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ hydrogen.cpython-311.pyc
   │     │  │     ├─ matrices.cpython-311.pyc
   │     │  │     ├─ paulialgebra.cpython-311.pyc
   │     │  │     ├─ pring.cpython-311.pyc
   │     │  │     ├─ qho_1d.cpython-311.pyc
   │     │  │     ├─ secondquant.cpython-311.pyc
   │     │  │     ├─ sho.cpython-311.pyc
   │     │  │     ├─ wigner.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ plotting
   │     │  │  ├─ backends
   │     │  │  │  ├─ base_backend.py
   │     │  │  │  ├─ matplotlibbackend
   │     │  │  │  │  ├─ matplotlib.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ matplotlib.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ textbackend
   │     │  │  │  │  ├─ text.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ text.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ base_backend.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ experimental_lambdify.py
   │     │  │  ├─ intervalmath
   │     │  │  │  ├─ interval_arithmetic.py
   │     │  │  │  ├─ interval_membership.py
   │     │  │  │  ├─ lib_interval.py
   │     │  │  │  ├─ tests
   │     │  │  │  │  ├─ test_intervalmath.py
   │     │  │  │  │  ├─ test_interval_functions.py
   │     │  │  │  │  ├─ test_interval_membership.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ test_intervalmath.cpython-311.pyc
   │     │  │  │  │     ├─ test_interval_functions.cpython-311.pyc
   │     │  │  │  │     ├─ test_interval_membership.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ interval_arithmetic.cpython-311.pyc
   │     │  │  │     ├─ interval_membership.cpython-311.pyc
   │     │  │  │     ├─ lib_interval.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ plot.py
   │     │  │  ├─ plotgrid.py
   │     │  │  ├─ plot_implicit.py
   │     │  │  ├─ pygletplot
   │     │  │  │  ├─ color_scheme.py
   │     │  │  │  ├─ managed_window.py
   │     │  │  │  ├─ plot.py
   │     │  │  │  ├─ plot_axes.py
   │     │  │  │  ├─ plot_camera.py
   │     │  │  │  ├─ plot_controller.py
   │     │  │  │  ├─ plot_curve.py
   │     │  │  │  ├─ plot_interval.py
   │     │  │  │  ├─ plot_mode.py
   │     │  │  │  ├─ plot_modes.py
   │     │  │  │  ├─ plot_mode_base.py
   │     │  │  │  ├─ plot_object.py
   │     │  │  │  ├─ plot_rotation.py
   │     │  │  │  ├─ plot_surface.py
   │     │  │  │  ├─ plot_window.py
   │     │  │  │  ├─ tests
   │     │  │  │  │  ├─ test_plotting.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ test_plotting.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ util.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ color_scheme.cpython-311.pyc
   │     │  │  │     ├─ managed_window.cpython-311.pyc
   │     │  │  │     ├─ plot.cpython-311.pyc
   │     │  │  │     ├─ plot_axes.cpython-311.pyc
   │     │  │  │     ├─ plot_camera.cpython-311.pyc
   │     │  │  │     ├─ plot_controller.cpython-311.pyc
   │     │  │  │     ├─ plot_curve.cpython-311.pyc
   │     │  │  │     ├─ plot_interval.cpython-311.pyc
   │     │  │  │     ├─ plot_mode.cpython-311.pyc
   │     │  │  │     ├─ plot_modes.cpython-311.pyc
   │     │  │  │     ├─ plot_mode_base.cpython-311.pyc
   │     │  │  │     ├─ plot_object.cpython-311.pyc
   │     │  │  │     ├─ plot_rotation.cpython-311.pyc
   │     │  │  │     ├─ plot_surface.cpython-311.pyc
   │     │  │  │     ├─ plot_window.cpython-311.pyc
   │     │  │  │     ├─ util.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ series.py
   │     │  │  ├─ tests
   │     │  │  │  ├─ test_experimental_lambdify.py
   │     │  │  │  ├─ test_plot.py
   │     │  │  │  ├─ test_plot_implicit.py
   │     │  │  │  ├─ test_region_and.png
   │     │  │  │  ├─ test_region_not.png
   │     │  │  │  ├─ test_region_or.png
   │     │  │  │  ├─ test_region_xor.png
   │     │  │  │  ├─ test_series.py
   │     │  │  │  ├─ test_textplot.py
   │     │  │  │  ├─ test_utils.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ test_experimental_lambdify.cpython-311.pyc
   │     │  │  │     ├─ test_plot.cpython-311.pyc
   │     │  │  │     ├─ test_plot_implicit.cpython-311.pyc
   │     │  │  │     ├─ test_series.cpython-311.pyc
   │     │  │  │     ├─ test_textplot.cpython-311.pyc
   │     │  │  │     ├─ test_utils.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ textplot.py
   │     │  │  ├─ utils.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ experimental_lambdify.cpython-311.pyc
   │     │  │     ├─ plot.cpython-311.pyc
   │     │  │     ├─ plotgrid.cpython-311.pyc
   │     │  │     ├─ plot_implicit.cpython-311.pyc
   │     │  │     ├─ series.cpython-311.pyc
   │     │  │     ├─ textplot.cpython-311.pyc
   │     │  │     ├─ utils.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ polys
   │     │  │  ├─ agca
   │     │  │  │  ├─ extensions.py
   │     │  │  │  ├─ homomorphisms.py
   │     │  │  │  ├─ ideals.py
   │     │  │  │  ├─ modules.py
   │     │  │  │  ├─ tests
   │     │  │  │  │  ├─ test_extensions.py
   │     │  │  │  │  ├─ test_homomorphisms.py
   │     │  │  │  │  ├─ test_ideals.py
   │     │  │  │  │  ├─ test_modules.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ test_extensions.cpython-311.pyc
   │     │  │  │  │     ├─ test_homomorphisms.cpython-311.pyc
   │     │  │  │  │     ├─ test_ideals.cpython-311.pyc
   │     │  │  │  │     ├─ test_modules.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ extensions.cpython-311.pyc
   │     │  │  │     ├─ homomorphisms.cpython-311.pyc
   │     │  │  │     ├─ ideals.cpython-311.pyc
   │     │  │  │     ├─ modules.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ appellseqs.py
   │     │  │  ├─ benchmarks
   │     │  │  │  ├─ bench_galoispolys.py
   │     │  │  │  ├─ bench_groebnertools.py
   │     │  │  │  ├─ bench_solvers.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ bench_galoispolys.cpython-311.pyc
   │     │  │  │     ├─ bench_groebnertools.cpython-311.pyc
   │     │  │  │     ├─ bench_solvers.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ compatibility.py
   │     │  │  ├─ constructor.py
   │     │  │  ├─ densearith.py
   │     │  │  ├─ densebasic.py
   │     │  │  ├─ densetools.py
   │     │  │  ├─ dispersion.py
   │     │  │  ├─ distributedmodules.py
   │     │  │  ├─ domainmatrix.py
   │     │  │  ├─ domains
   │     │  │  │  ├─ algebraicfield.py
   │     │  │  │  ├─ characteristiczero.py
   │     │  │  │  ├─ complexfield.py
   │     │  │  │  ├─ compositedomain.py
   │     │  │  │  ├─ domain.py
   │     │  │  │  ├─ domainelement.py
   │     │  │  │  ├─ expressiondomain.py
   │     │  │  │  ├─ expressionrawdomain.py
   │     │  │  │  ├─ field.py
   │     │  │  │  ├─ finitefield.py
   │     │  │  │  ├─ fractionfield.py
   │     │  │  │  ├─ gaussiandomains.py
   │     │  │  │  ├─ gmpyfinitefield.py
   │     │  │  │  ├─ gmpyintegerring.py
   │     │  │  │  ├─ gmpyrationalfield.py
   │     │  │  │  ├─ groundtypes.py
   │     │  │  │  ├─ integerring.py
   │     │  │  │  ├─ modularinteger.py
   │     │  │  │  ├─ mpelements.py
   │     │  │  │  ├─ old_fractionfield.py
   │     │  │  │  ├─ old_polynomialring.py
   │     │  │  │  ├─ polynomialring.py
   │     │  │  │  ├─ pythonfinitefield.py
   │     │  │  │  ├─ pythonintegerring.py
   │     │  │  │  ├─ pythonrational.py
   │     │  │  │  ├─ pythonrationalfield.py
   │     │  │  │  ├─ quotientring.py
   │     │  │  │  ├─ rationalfield.py
   │     │  │  │  ├─ realfield.py
   │     │  │  │  ├─ ring.py
   │     │  │  │  ├─ simpledomain.py
   │     │  │  │  ├─ tests
   │     │  │  │  │  ├─ test_domains.py
   │     │  │  │  │  ├─ test_polynomialring.py
   │     │  │  │  │  ├─ test_quotientring.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ test_domains.cpython-311.pyc
   │     │  │  │  │     ├─ test_polynomialring.cpython-311.pyc
   │     │  │  │  │     ├─ test_quotientring.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ algebraicfield.cpython-311.pyc
   │     │  │  │     ├─ characteristiczero.cpython-311.pyc
   │     │  │  │     ├─ complexfield.cpython-311.pyc
   │     │  │  │     ├─ compositedomain.cpython-311.pyc
   │     │  │  │     ├─ domain.cpython-311.pyc
   │     │  │  │     ├─ domainelement.cpython-311.pyc
   │     │  │  │     ├─ expressiondomain.cpython-311.pyc
   │     │  │  │     ├─ expressionrawdomain.cpython-311.pyc
   │     │  │  │     ├─ field.cpython-311.pyc
   │     │  │  │     ├─ finitefield.cpython-311.pyc
   │     │  │  │     ├─ fractionfield.cpython-311.pyc
   │     │  │  │     ├─ gaussiandomains.cpython-311.pyc
   │     │  │  │     ├─ gmpyfinitefield.cpython-311.pyc
   │     │  │  │     ├─ gmpyintegerring.cpython-311.pyc
   │     │  │  │     ├─ gmpyrationalfield.cpython-311.pyc
   │     │  │  │     ├─ groundtypes.cpython-311.pyc
   │     │  │  │     ├─ integerring.cpython-311.pyc
   │     │  │  │     ├─ modularinteger.cpython-311.pyc
   │     │  │  │     ├─ mpelements.cpython-311.pyc
   │     │  │  │     ├─ old_fractionfield.cpython-311.pyc
   │     │  │  │     ├─ old_polynomialring.cpython-311.pyc
   │     │  │  │     ├─ polynomialring.cpython-311.pyc
   │     │  │  │     ├─ pythonfinitefield.cpython-311.pyc
   │     │  │  │     ├─ pythonintegerring.cpython-311.pyc
   │     │  │  │     ├─ pythonrational.cpython-311.pyc
   │     │  │  │     ├─ pythonrationalfield.cpython-311.pyc
   │     │  │  │     ├─ quotientring.cpython-311.pyc
   │     │  │  │     ├─ rationalfield.cpython-311.pyc
   │     │  │  │     ├─ realfield.cpython-311.pyc
   │     │  │  │     ├─ ring.cpython-311.pyc
   │     │  │  │     ├─ simpledomain.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ euclidtools.py
   │     │  │  ├─ factortools.py
   │     │  │  ├─ fglmtools.py
   │     │  │  ├─ fields.py
   │     │  │  ├─ galoistools.py
   │     │  │  ├─ groebnertools.py
   │     │  │  ├─ heuristicgcd.py
   │     │  │  ├─ matrices
   │     │  │  │  ├─ ddm.py
   │     │  │  │  ├─ dense.py
   │     │  │  │  ├─ dfm.py
   │     │  │  │  ├─ domainmatrix.py
   │     │  │  │  ├─ domainscalar.py
   │     │  │  │  ├─ eigen.py
   │     │  │  │  ├─ exceptions.py
   │     │  │  │  ├─ linsolve.py
   │     │  │  │  ├─ lll.py
   │     │  │  │  ├─ normalforms.py
   │     │  │  │  ├─ rref.py
   │     │  │  │  ├─ sdm.py
   │     │  │  │  ├─ tests
   │     │  │  │  │  ├─ test_ddm.py
   │     │  │  │  │  ├─ test_dense.py
   │     │  │  │  │  ├─ test_domainmatrix.py
   │     │  │  │  │  ├─ test_domainscalar.py
   │     │  │  │  │  ├─ test_eigen.py
   │     │  │  │  │  ├─ test_fflu.py
   │     │  │  │  │  ├─ test_inverse.py
   │     │  │  │  │  ├─ test_linsolve.py
   │     │  │  │  │  ├─ test_lll.py
   │     │  │  │  │  ├─ test_normalforms.py
   │     │  │  │  │  ├─ test_nullspace.py
   │     │  │  │  │  ├─ test_rref.py
   │     │  │  │  │  ├─ test_sdm.py
   │     │  │  │  │  ├─ test_xxm.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ test_ddm.cpython-311.pyc
   │     │  │  │  │     ├─ test_dense.cpython-311.pyc
   │     │  │  │  │     ├─ test_domainmatrix.cpython-311.pyc
   │     │  │  │  │     ├─ test_domainscalar.cpython-311.pyc
   │     │  │  │  │     ├─ test_eigen.cpython-311.pyc
   │     │  │  │  │     ├─ test_fflu.cpython-311.pyc
   │     │  │  │  │     ├─ test_inverse.cpython-311.pyc
   │     │  │  │  │     ├─ test_linsolve.cpython-311.pyc
   │     │  │  │  │     ├─ test_lll.cpython-311.pyc
   │     │  │  │  │     ├─ test_normalforms.cpython-311.pyc
   │     │  │  │  │     ├─ test_nullspace.cpython-311.pyc
   │     │  │  │  │     ├─ test_rref.cpython-311.pyc
   │     │  │  │  │     ├─ test_sdm.cpython-311.pyc
   │     │  │  │  │     ├─ test_xxm.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ _dfm.py
   │     │  │  │  ├─ _typing.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ ddm.cpython-311.pyc
   │     │  │  │     ├─ dense.cpython-311.pyc
   │     │  │  │     ├─ dfm.cpython-311.pyc
   │     │  │  │     ├─ domainmatrix.cpython-311.pyc
   │     │  │  │     ├─ domainscalar.cpython-311.pyc
   │     │  │  │     ├─ eigen.cpython-311.pyc
   │     │  │  │     ├─ exceptions.cpython-311.pyc
   │     │  │  │     ├─ linsolve.cpython-311.pyc
   │     │  │  │     ├─ lll.cpython-311.pyc
   │     │  │  │     ├─ normalforms.cpython-311.pyc
   │     │  │  │     ├─ rref.cpython-311.pyc
   │     │  │  │     ├─ sdm.cpython-311.pyc
   │     │  │  │     ├─ _dfm.cpython-311.pyc
   │     │  │  │     ├─ _typing.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ modulargcd.py
   │     │  │  ├─ monomials.py
   │     │  │  ├─ multivariate_resultants.py
   │     │  │  ├─ numberfields
   │     │  │  │  ├─ basis.py
   │     │  │  │  ├─ exceptions.py
   │     │  │  │  ├─ galoisgroups.py
   │     │  │  │  ├─ galois_resolvents.py
   │     │  │  │  ├─ minpoly.py
   │     │  │  │  ├─ modules.py
   │     │  │  │  ├─ primes.py
   │     │  │  │  ├─ resolvent_lookup.py
   │     │  │  │  ├─ subfield.py
   │     │  │  │  ├─ tests
   │     │  │  │  │  ├─ test_basis.py
   │     │  │  │  │  ├─ test_galoisgroups.py
   │     │  │  │  │  ├─ test_minpoly.py
   │     │  │  │  │  ├─ test_modules.py
   │     │  │  │  │  ├─ test_numbers.py
   │     │  │  │  │  ├─ test_primes.py
   │     │  │  │  │  ├─ test_subfield.py
   │     │  │  │  │  ├─ test_utilities.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ test_basis.cpython-311.pyc
   │     │  │  │  │     ├─ test_galoisgroups.cpython-311.pyc
   │     │  │  │  │     ├─ test_minpoly.cpython-311.pyc
   │     │  │  │  │     ├─ test_modules.cpython-311.pyc
   │     │  │  │  │     ├─ test_numbers.cpython-311.pyc
   │     │  │  │  │     ├─ test_primes.cpython-311.pyc
   │     │  │  │  │     ├─ test_subfield.cpython-311.pyc
   │     │  │  │  │     ├─ test_utilities.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ utilities.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ basis.cpython-311.pyc
   │     │  │  │     ├─ exceptions.cpython-311.pyc
   │     │  │  │     ├─ galoisgroups.cpython-311.pyc
   │     │  │  │     ├─ galois_resolvents.cpython-311.pyc
   │     │  │  │     ├─ minpoly.cpython-311.pyc
   │     │  │  │     ├─ modules.cpython-311.pyc
   │     │  │  │     ├─ primes.cpython-311.pyc
   │     │  │  │     ├─ resolvent_lookup.cpython-311.pyc
   │     │  │  │     ├─ subfield.cpython-311.pyc
   │     │  │  │     ├─ utilities.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ orderings.py
   │     │  │  ├─ orthopolys.py
   │     │  │  ├─ partfrac.py
   │     │  │  ├─ polyclasses.py
   │     │  │  ├─ polyconfig.py
   │     │  │  ├─ polyerrors.py
   │     │  │  ├─ polyfuncs.py
   │     │  │  ├─ polymatrix.py
   │     │  │  ├─ polyoptions.py
   │     │  │  ├─ polyquinticconst.py
   │     │  │  ├─ polyroots.py
   │     │  │  ├─ polytools.py
   │     │  │  ├─ polyutils.py
   │     │  │  ├─ puiseux.py
   │     │  │  ├─ rationaltools.py
   │     │  │  ├─ rings.py
   │     │  │  ├─ ring_series.py
   │     │  │  ├─ rootisolation.py
   │     │  │  ├─ rootoftools.py
   │     │  │  ├─ solvers.py
   │     │  │  ├─ specialpolys.py
   │     │  │  ├─ sqfreetools.py
   │     │  │  ├─ subresultants_qq_zz.py
   │     │  │  ├─ tests
   │     │  │  │  ├─ test_appellseqs.py
   │     │  │  │  ├─ test_constructor.py
   │     │  │  │  ├─ test_densearith.py
   │     │  │  │  ├─ test_densebasic.py
   │     │  │  │  ├─ test_densetools.py
   │     │  │  │  ├─ test_dispersion.py
   │     │  │  │  ├─ test_distributedmodules.py
   │     │  │  │  ├─ test_euclidtools.py
   │     │  │  │  ├─ test_factortools.py
   │     │  │  │  ├─ test_fields.py
   │     │  │  │  ├─ test_galoistools.py
   │     │  │  │  ├─ test_groebnertools.py
   │     │  │  │  ├─ test_heuristicgcd.py
   │     │  │  │  ├─ test_hypothesis.py
   │     │  │  │  ├─ test_injections.py
   │     │  │  │  ├─ test_modulargcd.py
   │     │  │  │  ├─ test_monomials.py
   │     │  │  │  ├─ test_multivariate_resultants.py
   │     │  │  │  ├─ test_orderings.py
   │     │  │  │  ├─ test_orthopolys.py
   │     │  │  │  ├─ test_partfrac.py
   │     │  │  │  ├─ test_polyclasses.py
   │     │  │  │  ├─ test_polyfuncs.py
   │     │  │  │  ├─ test_polymatrix.py
   │     │  │  │  ├─ test_polyoptions.py
   │     │  │  │  ├─ test_polyroots.py
   │     │  │  │  ├─ test_polytools.py
   │     │  │  │  ├─ test_polyutils.py
   │     │  │  │  ├─ test_puiseux.py
   │     │  │  │  ├─ test_pythonrational.py
   │     │  │  │  ├─ test_rationaltools.py
   │     │  │  │  ├─ test_rings.py
   │     │  │  │  ├─ test_ring_series.py
   │     │  │  │  ├─ test_rootisolation.py
   │     │  │  │  ├─ test_rootoftools.py
   │     │  │  │  ├─ test_solvers.py
   │     │  │  │  ├─ test_specialpolys.py
   │     │  │  │  ├─ test_sqfreetools.py
   │     │  │  │  ├─ test_subresultants_qq_zz.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ test_appellseqs.cpython-311.pyc
   │     │  │  │     ├─ test_constructor.cpython-311.pyc
   │     │  │  │     ├─ test_densearith.cpython-311.pyc
   │     │  │  │     ├─ test_densebasic.cpython-311.pyc
   │     │  │  │     ├─ test_densetools.cpython-311.pyc
   │     │  │  │     ├─ test_dispersion.cpython-311.pyc
   │     │  │  │     ├─ test_distributedmodules.cpython-311.pyc
   │     │  │  │     ├─ test_euclidtools.cpython-311.pyc
   │     │  │  │     ├─ test_factortools.cpython-311.pyc
   │     │  │  │     ├─ test_fields.cpython-311.pyc
   │     │  │  │     ├─ test_galoistools.cpython-311.pyc
   │     │  │  │     ├─ test_groebnertools.cpython-311.pyc
   │     │  │  │     ├─ test_heuristicgcd.cpython-311.pyc
   │     │  │  │     ├─ test_hypothesis.cpython-311.pyc
   │     │  │  │     ├─ test_injections.cpython-311.pyc
   │     │  │  │     ├─ test_modulargcd.cpython-311.pyc
   │     │  │  │     ├─ test_monomials.cpython-311.pyc
   │     │  │  │     ├─ test_multivariate_resultants.cpython-311.pyc
   │     │  │  │     ├─ test_orderings.cpython-311.pyc
   │     │  │  │     ├─ test_orthopolys.cpython-311.pyc
   │     │  │  │     ├─ test_partfrac.cpython-311.pyc
   │     │  │  │     ├─ test_polyclasses.cpython-311.pyc
   │     │  │  │     ├─ test_polyfuncs.cpython-311.pyc
   │     │  │  │     ├─ test_polymatrix.cpython-311.pyc
   │     │  │  │     ├─ test_polyoptions.cpython-311.pyc
   │     │  │  │     ├─ test_polyroots.cpython-311.pyc
   │     │  │  │     ├─ test_polytools.cpython-311.pyc
   │     │  │  │     ├─ test_polyutils.cpython-311.pyc
   │     │  │  │     ├─ test_puiseux.cpython-311.pyc
   │     │  │  │     ├─ test_pythonrational.cpython-311.pyc
   │     │  │  │     ├─ test_rationaltools.cpython-311.pyc
   │     │  │  │     ├─ test_rings.cpython-311.pyc
   │     │  │  │     ├─ test_ring_series.cpython-311.pyc
   │     │  │  │     ├─ test_rootisolation.cpython-311.pyc
   │     │  │  │     ├─ test_rootoftools.cpython-311.pyc
   │     │  │  │     ├─ test_solvers.cpython-311.pyc
   │     │  │  │     ├─ test_specialpolys.cpython-311.pyc
   │     │  │  │     ├─ test_sqfreetools.cpython-311.pyc
   │     │  │  │     ├─ test_subresultants_qq_zz.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ appellseqs.cpython-311.pyc
   │     │  │     ├─ compatibility.cpython-311.pyc
   │     │  │     ├─ constructor.cpython-311.pyc
   │     │  │     ├─ densearith.cpython-311.pyc
   │     │  │     ├─ densebasic.cpython-311.pyc
   │     │  │     ├─ densetools.cpython-311.pyc
   │     │  │     ├─ dispersion.cpython-311.pyc
   │     │  │     ├─ distributedmodules.cpython-311.pyc
   │     │  │     ├─ domainmatrix.cpython-311.pyc
   │     │  │     ├─ euclidtools.cpython-311.pyc
   │     │  │     ├─ factortools.cpython-311.pyc
   │     │  │     ├─ fglmtools.cpython-311.pyc
   │     │  │     ├─ fields.cpython-311.pyc
   │     │  │     ├─ galoistools.cpython-311.pyc
   │     │  │     ├─ groebnertools.cpython-311.pyc
   │     │  │     ├─ heuristicgcd.cpython-311.pyc
   │     │  │     ├─ modulargcd.cpython-311.pyc
   │     │  │     ├─ monomials.cpython-311.pyc
   │     │  │     ├─ multivariate_resultants.cpython-311.pyc
   │     │  │     ├─ orderings.cpython-311.pyc
   │     │  │     ├─ orthopolys.cpython-311.pyc
   │     │  │     ├─ partfrac.cpython-311.pyc
   │     │  │     ├─ polyclasses.cpython-311.pyc
   │     │  │     ├─ polyconfig.cpython-311.pyc
   │     │  │     ├─ polyerrors.cpython-311.pyc
   │     │  │     ├─ polyfuncs.cpython-311.pyc
   │     │  │     ├─ polymatrix.cpython-311.pyc
   │     │  │     ├─ polyoptions.cpython-311.pyc
   │     │  │     ├─ polyquinticconst.cpython-311.pyc
   │     │  │     ├─ polyroots.cpython-311.pyc
   │     │  │     ├─ polytools.cpython-311.pyc
   │     │  │     ├─ polyutils.cpython-311.pyc
   │     │  │     ├─ puiseux.cpython-311.pyc
   │     │  │     ├─ rationaltools.cpython-311.pyc
   │     │  │     ├─ rings.cpython-311.pyc
   │     │  │     ├─ ring_series.cpython-311.pyc
   │     │  │     ├─ rootisolation.cpython-311.pyc
   │     │  │     ├─ rootoftools.cpython-311.pyc
   │     │  │     ├─ solvers.cpython-311.pyc
   │     │  │     ├─ specialpolys.cpython-311.pyc
   │     │  │     ├─ sqfreetools.cpython-311.pyc
   │     │  │     ├─ subresultants_qq_zz.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ printing
   │     │  │  ├─ aesaracode.py
   │     │  │  ├─ c.py
   │     │  │  ├─ codeprinter.py
   │     │  │  ├─ conventions.py
   │     │  │  ├─ cxx.py
   │     │  │  ├─ defaults.py
   │     │  │  ├─ dot.py
   │     │  │  ├─ fortran.py
   │     │  │  ├─ glsl.py
   │     │  │  ├─ gtk.py
   │     │  │  ├─ jscode.py
   │     │  │  ├─ julia.py
   │     │  │  ├─ lambdarepr.py
   │     │  │  ├─ latex.py
   │     │  │  ├─ llvmjitcode.py
   │     │  │  ├─ maple.py
   │     │  │  ├─ mathematica.py
   │     │  │  ├─ mathml.py
   │     │  │  ├─ numpy.py
   │     │  │  ├─ octave.py
   │     │  │  ├─ precedence.py
   │     │  │  ├─ pretty
   │     │  │  │  ├─ pretty.py
   │     │  │  │  ├─ pretty_symbology.py
   │     │  │  │  ├─ stringpict.py
   │     │  │  │  ├─ tests
   │     │  │  │  │  ├─ test_pretty.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ test_pretty.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ pretty.cpython-311.pyc
   │     │  │  │     ├─ pretty_symbology.cpython-311.pyc
   │     │  │  │     ├─ stringpict.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ preview.py
   │     │  │  ├─ printer.py
   │     │  │  ├─ pycode.py
   │     │  │  ├─ python.py
   │     │  │  ├─ pytorch.py
   │     │  │  ├─ rcode.py
   │     │  │  ├─ repr.py
   │     │  │  ├─ rust.py
   │     │  │  ├─ smtlib.py
   │     │  │  ├─ str.py
   │     │  │  ├─ tableform.py
   │     │  │  ├─ tensorflow.py
   │     │  │  ├─ tests
   │     │  │  │  ├─ test_aesaracode.py
   │     │  │  │  ├─ test_c.py
   │     │  │  │  ├─ test_codeprinter.py
   │     │  │  │  ├─ test_conventions.py
   │     │  │  │  ├─ test_cupy.py
   │     │  │  │  ├─ test_cxx.py
   │     │  │  │  ├─ test_dot.py
   │     │  │  │  ├─ test_fortran.py
   │     │  │  │  ├─ test_glsl.py
   │     │  │  │  ├─ test_gtk.py
   │     │  │  │  ├─ test_jax.py
   │     │  │  │  ├─ test_jscode.py
   │     │  │  │  ├─ test_julia.py
   │     │  │  │  ├─ test_lambdarepr.py
   │     │  │  │  ├─ test_latex.py
   │     │  │  │  ├─ test_llvmjit.py
   │     │  │  │  ├─ test_maple.py
   │     │  │  │  ├─ test_mathematica.py
   │     │  │  │  ├─ test_mathml.py
   │     │  │  │  ├─ test_numpy.py
   │     │  │  │  ├─ test_octave.py
   │     │  │  │  ├─ test_precedence.py
   │     │  │  │  ├─ test_preview.py
   │     │  │  │  ├─ test_pycode.py
   │     │  │  │  ├─ test_python.py
   │     │  │  │  ├─ test_rcode.py
   │     │  │  │  ├─ test_repr.py
   │     │  │  │  ├─ test_rust.py
   │     │  │  │  ├─ test_smtlib.py
   │     │  │  │  ├─ test_str.py
   │     │  │  │  ├─ test_tableform.py
   │     │  │  │  ├─ test_tensorflow.py
   │     │  │  │  ├─ test_theanocode.py
   │     │  │  │  ├─ test_torch.py
   │     │  │  │  ├─ test_tree.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ test_aesaracode.cpython-311.pyc
   │     │  │  │     ├─ test_c.cpython-311.pyc
   │     │  │  │     ├─ test_codeprinter.cpython-311.pyc
   │     │  │  │     ├─ test_conventions.cpython-311.pyc
   │     │  │  │     ├─ test_cupy.cpython-311.pyc
   │     │  │  │     ├─ test_cxx.cpython-311.pyc
   │     │  │  │     ├─ test_dot.cpython-311.pyc
   │     │  │  │     ├─ test_fortran.cpython-311.pyc
   │     │  │  │     ├─ test_glsl.cpython-311.pyc
   │     │  │  │     ├─ test_gtk.cpython-311.pyc
   │     │  │  │     ├─ test_jax.cpython-311.pyc
   │     │  │  │     ├─ test_jscode.cpython-311.pyc
   │     │  │  │     ├─ test_julia.cpython-311.pyc
   │     │  │  │     ├─ test_lambdarepr.cpython-311.pyc
   │     │  │  │     ├─ test_latex.cpython-311.pyc
   │     │  │  │     ├─ test_llvmjit.cpython-311.pyc
   │     │  │  │     ├─ test_maple.cpython-311.pyc
   │     │  │  │     ├─ test_mathematica.cpython-311.pyc
   │     │  │  │     ├─ test_mathml.cpython-311.pyc
   │     │  │  │     ├─ test_numpy.cpython-311.pyc
   │     │  │  │     ├─ test_octave.cpython-311.pyc
   │     │  │  │     ├─ test_precedence.cpython-311.pyc
   │     │  │  │     ├─ test_preview.cpython-311.pyc
   │     │  │  │     ├─ test_pycode.cpython-311.pyc
   │     │  │  │     ├─ test_python.cpython-311.pyc
   │     │  │  │     ├─ test_rcode.cpython-311.pyc
   │     │  │  │     ├─ test_repr.cpython-311.pyc
   │     │  │  │     ├─ test_rust.cpython-311.pyc
   │     │  │  │     ├─ test_smtlib.cpython-311.pyc
   │     │  │  │     ├─ test_str.cpython-311.pyc
   │     │  │  │     ├─ test_tableform.cpython-311.pyc
   │     │  │  │     ├─ test_tensorflow.cpython-311.pyc
   │     │  │  │     ├─ test_theanocode.cpython-311.pyc
   │     │  │  │     ├─ test_torch.cpython-311.pyc
   │     │  │  │     ├─ test_tree.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ theanocode.py
   │     │  │  ├─ tree.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ aesaracode.cpython-311.pyc
   │     │  │     ├─ c.cpython-311.pyc
   │     │  │     ├─ codeprinter.cpython-311.pyc
   │     │  │     ├─ conventions.cpython-311.pyc
   │     │  │     ├─ cxx.cpython-311.pyc
   │     │  │     ├─ defaults.cpython-311.pyc
   │     │  │     ├─ dot.cpython-311.pyc
   │     │  │     ├─ fortran.cpython-311.pyc
   │     │  │     ├─ glsl.cpython-311.pyc
   │     │  │     ├─ gtk.cpython-311.pyc
   │     │  │     ├─ jscode.cpython-311.pyc
   │     │  │     ├─ julia.cpython-311.pyc
   │     │  │     ├─ lambdarepr.cpython-311.pyc
   │     │  │     ├─ latex.cpython-311.pyc
   │     │  │     ├─ llvmjitcode.cpython-311.pyc
   │     │  │     ├─ maple.cpython-311.pyc
   │     │  │     ├─ mathematica.cpython-311.pyc
   │     │  │     ├─ mathml.cpython-311.pyc
   │     │  │     ├─ numpy.cpython-311.pyc
   │     │  │     ├─ octave.cpython-311.pyc
   │     │  │     ├─ precedence.cpython-311.pyc
   │     │  │     ├─ preview.cpython-311.pyc
   │     │  │     ├─ printer.cpython-311.pyc
   │     │  │     ├─ pycode.cpython-311.pyc
   │     │  │     ├─ python.cpython-311.pyc
   │     │  │     ├─ pytorch.cpython-311.pyc
   │     │  │     ├─ rcode.cpython-311.pyc
   │     │  │     ├─ repr.cpython-311.pyc
   │     │  │     ├─ rust.cpython-311.pyc
   │     │  │     ├─ smtlib.cpython-311.pyc
   │     │  │     ├─ str.cpython-311.pyc
   │     │  │     ├─ tableform.cpython-311.pyc
   │     │  │     ├─ tensorflow.cpython-311.pyc
   │     │  │     ├─ theanocode.cpython-311.pyc
   │     │  │     ├─ tree.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ release.py
   │     │  ├─ sandbox
   │     │  │  ├─ indexed_integrals.py
   │     │  │  ├─ tests
   │     │  │  │  ├─ test_indexed_integrals.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ test_indexed_integrals.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ indexed_integrals.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ series
   │     │  │  ├─ acceleration.py
   │     │  │  ├─ approximants.py
   │     │  │  ├─ aseries.py
   │     │  │  ├─ benchmarks
   │     │  │  │  ├─ bench_limit.py
   │     │  │  │  ├─ bench_order.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ bench_limit.cpython-311.pyc
   │     │  │  │     ├─ bench_order.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ formal.py
   │     │  │  ├─ fourier.py
   │     │  │  ├─ gruntz.py
   │     │  │  ├─ kauers.py
   │     │  │  ├─ limits.py
   │     │  │  ├─ limitseq.py
   │     │  │  ├─ order.py
   │     │  │  ├─ residues.py
   │     │  │  ├─ sequences.py
   │     │  │  ├─ series.py
   │     │  │  ├─ series_class.py
   │     │  │  ├─ tests
   │     │  │  │  ├─ test_approximants.py
   │     │  │  │  ├─ test_aseries.py
   │     │  │  │  ├─ test_demidovich.py
   │     │  │  │  ├─ test_formal.py
   │     │  │  │  ├─ test_fourier.py
   │     │  │  │  ├─ test_gruntz.py
   │     │  │  │  ├─ test_kauers.py
   │     │  │  │  ├─ test_limits.py
   │     │  │  │  ├─ test_limitseq.py
   │     │  │  │  ├─ test_lseries.py
   │     │  │  │  ├─ test_nseries.py
   │     │  │  │  ├─ test_order.py
   │     │  │  │  ├─ test_residues.py
   │     │  │  │  ├─ test_sequences.py
   │     │  │  │  ├─ test_series.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ test_approximants.cpython-311.pyc
   │     │  │  │     ├─ test_aseries.cpython-311.pyc
   │     │  │  │     ├─ test_demidovich.cpython-311.pyc
   │     │  │  │     ├─ test_formal.cpython-311.pyc
   │     │  │  │     ├─ test_fourier.cpython-311.pyc
   │     │  │  │     ├─ test_gruntz.cpython-311.pyc
   │     │  │  │     ├─ test_kauers.cpython-311.pyc
   │     │  │  │     ├─ test_limits.cpython-311.pyc
   │     │  │  │     ├─ test_limitseq.cpython-311.pyc
   │     │  │  │     ├─ test_lseries.cpython-311.pyc
   │     │  │  │     ├─ test_nseries.cpython-311.pyc
   │     │  │  │     ├─ test_order.cpython-311.pyc
   │     │  │  │     ├─ test_residues.cpython-311.pyc
   │     │  │  │     ├─ test_sequences.cpython-311.pyc
   │     │  │  │     ├─ test_series.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ acceleration.cpython-311.pyc
   │     │  │     ├─ approximants.cpython-311.pyc
   │     │  │     ├─ aseries.cpython-311.pyc
   │     │  │     ├─ formal.cpython-311.pyc
   │     │  │     ├─ fourier.cpython-311.pyc
   │     │  │     ├─ gruntz.cpython-311.pyc
   │     │  │     ├─ kauers.cpython-311.pyc
   │     │  │     ├─ limits.cpython-311.pyc
   │     │  │     ├─ limitseq.cpython-311.pyc
   │     │  │     ├─ order.cpython-311.pyc
   │     │  │     ├─ residues.cpython-311.pyc
   │     │  │     ├─ sequences.cpython-311.pyc
   │     │  │     ├─ series.cpython-311.pyc
   │     │  │     ├─ series_class.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ sets
   │     │  │  ├─ conditionset.py
   │     │  │  ├─ contains.py
   │     │  │  ├─ fancysets.py
   │     │  │  ├─ handlers
   │     │  │  │  ├─ add.py
   │     │  │  │  ├─ comparison.py
   │     │  │  │  ├─ functions.py
   │     │  │  │  ├─ intersection.py
   │     │  │  │  ├─ issubset.py
   │     │  │  │  ├─ mul.py
   │     │  │  │  ├─ power.py
   │     │  │  │  ├─ union.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ add.cpython-311.pyc
   │     │  │  │     ├─ comparison.cpython-311.pyc
   │     │  │  │     ├─ functions.cpython-311.pyc
   │     │  │  │     ├─ intersection.cpython-311.pyc
   │     │  │  │     ├─ issubset.cpython-311.pyc
   │     │  │  │     ├─ mul.cpython-311.pyc
   │     │  │  │     ├─ power.cpython-311.pyc
   │     │  │  │     ├─ union.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ ordinals.py
   │     │  │  ├─ powerset.py
   │     │  │  ├─ setexpr.py
   │     │  │  ├─ sets.py
   │     │  │  ├─ tests
   │     │  │  │  ├─ test_conditionset.py
   │     │  │  │  ├─ test_contains.py
   │     │  │  │  ├─ test_fancysets.py
   │     │  │  │  ├─ test_ordinals.py
   │     │  │  │  ├─ test_powerset.py
   │     │  │  │  ├─ test_setexpr.py
   │     │  │  │  ├─ test_sets.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ test_conditionset.cpython-311.pyc
   │     │  │  │     ├─ test_contains.cpython-311.pyc
   │     │  │  │     ├─ test_fancysets.cpython-311.pyc
   │     │  │  │     ├─ test_ordinals.cpython-311.pyc
   │     │  │  │     ├─ test_powerset.cpython-311.pyc
   │     │  │  │     ├─ test_setexpr.cpython-311.pyc
   │     │  │  │     ├─ test_sets.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ conditionset.cpython-311.pyc
   │     │  │     ├─ contains.cpython-311.pyc
   │     │  │     ├─ fancysets.cpython-311.pyc
   │     │  │     ├─ ordinals.cpython-311.pyc
   │     │  │     ├─ powerset.cpython-311.pyc
   │     │  │     ├─ setexpr.cpython-311.pyc
   │     │  │     ├─ sets.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ simplify
   │     │  │  ├─ combsimp.py
   │     │  │  ├─ cse_main.py
   │     │  │  ├─ cse_opts.py
   │     │  │  ├─ epathtools.py
   │     │  │  ├─ fu.py
   │     │  │  ├─ gammasimp.py
   │     │  │  ├─ hyperexpand.py
   │     │  │  ├─ hyperexpand_doc.py
   │     │  │  ├─ powsimp.py
   │     │  │  ├─ radsimp.py
   │     │  │  ├─ ratsimp.py
   │     │  │  ├─ simplify.py
   │     │  │  ├─ sqrtdenest.py
   │     │  │  ├─ tests
   │     │  │  │  ├─ test_combsimp.py
   │     │  │  │  ├─ test_cse.py
   │     │  │  │  ├─ test_cse_diff.py
   │     │  │  │  ├─ test_epathtools.py
   │     │  │  │  ├─ test_fu.py
   │     │  │  │  ├─ test_function.py
   │     │  │  │  ├─ test_gammasimp.py
   │     │  │  │  ├─ test_hyperexpand.py
   │     │  │  │  ├─ test_powsimp.py
   │     │  │  │  ├─ test_radsimp.py
   │     │  │  │  ├─ test_ratsimp.py
   │     │  │  │  ├─ test_rewrite.py
   │     │  │  │  ├─ test_simplify.py
   │     │  │  │  ├─ test_sqrtdenest.py
   │     │  │  │  ├─ test_trigsimp.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ test_combsimp.cpython-311.pyc
   │     │  │  │     ├─ test_cse.cpython-311.pyc
   │     │  │  │     ├─ test_cse_diff.cpython-311.pyc
   │     │  │  │     ├─ test_epathtools.cpython-311.pyc
   │     │  │  │     ├─ test_fu.cpython-311.pyc
   │     │  │  │     ├─ test_function.cpython-311.pyc
   │     │  │  │     ├─ test_gammasimp.cpython-311.pyc
   │     │  │  │     ├─ test_hyperexpand.cpython-311.pyc
   │     │  │  │     ├─ test_powsimp.cpython-311.pyc
   │     │  │  │     ├─ test_radsimp.cpython-311.pyc
   │     │  │  │     ├─ test_ratsimp.cpython-311.pyc
   │     │  │  │     ├─ test_rewrite.cpython-311.pyc
   │     │  │  │     ├─ test_simplify.cpython-311.pyc
   │     │  │  │     ├─ test_sqrtdenest.cpython-311.pyc
   │     │  │  │     ├─ test_trigsimp.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ traversaltools.py
   │     │  │  ├─ trigsimp.py
   │     │  │  ├─ _cse_diff.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ combsimp.cpython-311.pyc
   │     │  │     ├─ cse_main.cpython-311.pyc
   │     │  │     ├─ cse_opts.cpython-311.pyc
   │     │  │     ├─ epathtools.cpython-311.pyc
   │     │  │     ├─ fu.cpython-311.pyc
   │     │  │     ├─ gammasimp.cpython-311.pyc
   │     │  │     ├─ hyperexpand.cpython-311.pyc
   │     │  │     ├─ hyperexpand_doc.cpython-311.pyc
   │     │  │     ├─ powsimp.cpython-311.pyc
   │     │  │     ├─ radsimp.cpython-311.pyc
   │     │  │     ├─ ratsimp.cpython-311.pyc
   │     │  │     ├─ simplify.cpython-311.pyc
   │     │  │     ├─ sqrtdenest.cpython-311.pyc
   │     │  │     ├─ traversaltools.cpython-311.pyc
   │     │  │     ├─ trigsimp.cpython-311.pyc
   │     │  │     ├─ _cse_diff.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ solvers
   │     │  │  ├─ benchmarks
   │     │  │  │  ├─ bench_solvers.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ bench_solvers.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ bivariate.py
   │     │  │  ├─ decompogen.py
   │     │  │  ├─ deutils.py
   │     │  │  ├─ diophantine
   │     │  │  │  ├─ diophantine.py
   │     │  │  │  ├─ tests
   │     │  │  │  │  ├─ test_diophantine.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ test_diophantine.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ diophantine.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ inequalities.py
   │     │  │  ├─ ode
   │     │  │  │  ├─ hypergeometric.py
   │     │  │  │  ├─ lie_group.py
   │     │  │  │  ├─ nonhomogeneous.py
   │     │  │  │  ├─ ode.py
   │     │  │  │  ├─ riccati.py
   │     │  │  │  ├─ single.py
   │     │  │  │  ├─ subscheck.py
   │     │  │  │  ├─ systems.py
   │     │  │  │  ├─ tests
   │     │  │  │  │  ├─ test_lie_group.py
   │     │  │  │  │  ├─ test_ode.py
   │     │  │  │  │  ├─ test_riccati.py
   │     │  │  │  │  ├─ test_single.py
   │     │  │  │  │  ├─ test_subscheck.py
   │     │  │  │  │  ├─ test_systems.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ test_lie_group.cpython-311.pyc
   │     │  │  │  │     ├─ test_ode.cpython-311.pyc
   │     │  │  │  │     ├─ test_riccati.cpython-311.pyc
   │     │  │  │  │     ├─ test_single.cpython-311.pyc
   │     │  │  │  │     ├─ test_subscheck.cpython-311.pyc
   │     │  │  │  │     ├─ test_systems.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ hypergeometric.cpython-311.pyc
   │     │  │  │     ├─ lie_group.cpython-311.pyc
   │     │  │  │     ├─ nonhomogeneous.cpython-311.pyc
   │     │  │  │     ├─ ode.cpython-311.pyc
   │     │  │  │     ├─ riccati.cpython-311.pyc
   │     │  │  │     ├─ single.cpython-311.pyc
   │     │  │  │     ├─ subscheck.cpython-311.pyc
   │     │  │  │     ├─ systems.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ pde.py
   │     │  │  ├─ polysys.py
   │     │  │  ├─ recurr.py
   │     │  │  ├─ simplex.py
   │     │  │  ├─ solvers.py
   │     │  │  ├─ solveset.py
   │     │  │  ├─ tests
   │     │  │  │  ├─ test_constantsimp.py
   │     │  │  │  ├─ test_decompogen.py
   │     │  │  │  ├─ test_inequalities.py
   │     │  │  │  ├─ test_numeric.py
   │     │  │  │  ├─ test_pde.py
   │     │  │  │  ├─ test_polysys.py
   │     │  │  │  ├─ test_recurr.py
   │     │  │  │  ├─ test_simplex.py
   │     │  │  │  ├─ test_solvers.py
   │     │  │  │  ├─ test_solveset.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ test_constantsimp.cpython-311.pyc
   │     │  │  │     ├─ test_decompogen.cpython-311.pyc
   │     │  │  │     ├─ test_inequalities.cpython-311.pyc
   │     │  │  │     ├─ test_numeric.cpython-311.pyc
   │     │  │  │     ├─ test_pde.cpython-311.pyc
   │     │  │  │     ├─ test_polysys.cpython-311.pyc
   │     │  │  │     ├─ test_recurr.cpython-311.pyc
   │     │  │  │     ├─ test_simplex.cpython-311.pyc
   │     │  │  │     ├─ test_solvers.cpython-311.pyc
   │     │  │  │     ├─ test_solveset.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ bivariate.cpython-311.pyc
   │     │  │     ├─ decompogen.cpython-311.pyc
   │     │  │     ├─ deutils.cpython-311.pyc
   │     │  │     ├─ inequalities.cpython-311.pyc
   │     │  │     ├─ pde.cpython-311.pyc
   │     │  │     ├─ polysys.cpython-311.pyc
   │     │  │     ├─ recurr.cpython-311.pyc
   │     │  │     ├─ simplex.cpython-311.pyc
   │     │  │     ├─ solvers.cpython-311.pyc
   │     │  │     ├─ solveset.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ stats
   │     │  │  ├─ compound_rv.py
   │     │  │  ├─ crv.py
   │     │  │  ├─ crv_types.py
   │     │  │  ├─ drv.py
   │     │  │  ├─ drv_types.py
   │     │  │  ├─ error_prop.py
   │     │  │  ├─ frv.py
   │     │  │  ├─ frv_types.py
   │     │  │  ├─ joint_rv.py
   │     │  │  ├─ joint_rv_types.py
   │     │  │  ├─ matrix_distributions.py
   │     │  │  ├─ random_matrix.py
   │     │  │  ├─ random_matrix_models.py
   │     │  │  ├─ rv.py
   │     │  │  ├─ rv_interface.py
   │     │  │  ├─ sampling
   │     │  │  │  ├─ sample_numpy.py
   │     │  │  │  ├─ sample_pymc.py
   │     │  │  │  ├─ sample_scipy.py
   │     │  │  │  ├─ tests
   │     │  │  │  │  ├─ test_sample_continuous_rv.py
   │     │  │  │  │  ├─ test_sample_discrete_rv.py
   │     │  │  │  │  ├─ test_sample_finite_rv.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ test_sample_continuous_rv.cpython-311.pyc
   │     │  │  │  │     ├─ test_sample_discrete_rv.cpython-311.pyc
   │     │  │  │  │     ├─ test_sample_finite_rv.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ sample_numpy.cpython-311.pyc
   │     │  │  │     ├─ sample_pymc.cpython-311.pyc
   │     │  │  │     ├─ sample_scipy.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ stochastic_process.py
   │     │  │  ├─ stochastic_process_types.py
   │     │  │  ├─ symbolic_multivariate_probability.py
   │     │  │  ├─ symbolic_probability.py
   │     │  │  ├─ tests
   │     │  │  │  ├─ test_compound_rv.py
   │     │  │  │  ├─ test_continuous_rv.py
   │     │  │  │  ├─ test_discrete_rv.py
   │     │  │  │  ├─ test_error_prop.py
   │     │  │  │  ├─ test_finite_rv.py
   │     │  │  │  ├─ test_joint_rv.py
   │     │  │  │  ├─ test_matrix_distributions.py
   │     │  │  │  ├─ test_mix.py
   │     │  │  │  ├─ test_random_matrix.py
   │     │  │  │  ├─ test_rv.py
   │     │  │  │  ├─ test_stochastic_process.py
   │     │  │  │  ├─ test_symbolic_multivariate.py
   │     │  │  │  ├─ test_symbolic_probability.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ test_compound_rv.cpython-311.pyc
   │     │  │  │     ├─ test_continuous_rv.cpython-311.pyc
   │     │  │  │     ├─ test_discrete_rv.cpython-311.pyc
   │     │  │  │     ├─ test_error_prop.cpython-311.pyc
   │     │  │  │     ├─ test_finite_rv.cpython-311.pyc
   │     │  │  │     ├─ test_joint_rv.cpython-311.pyc
   │     │  │  │     ├─ test_matrix_distributions.cpython-311.pyc
   │     │  │  │     ├─ test_mix.cpython-311.pyc
   │     │  │  │     ├─ test_random_matrix.cpython-311.pyc
   │     │  │  │     ├─ test_rv.cpython-311.pyc
   │     │  │  │     ├─ test_stochastic_process.cpython-311.pyc
   │     │  │  │     ├─ test_symbolic_multivariate.cpython-311.pyc
   │     │  │  │     ├─ test_symbolic_probability.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ compound_rv.cpython-311.pyc
   │     │  │     ├─ crv.cpython-311.pyc
   │     │  │     ├─ crv_types.cpython-311.pyc
   │     │  │     ├─ drv.cpython-311.pyc
   │     │  │     ├─ drv_types.cpython-311.pyc
   │     │  │     ├─ error_prop.cpython-311.pyc
   │     │  │     ├─ frv.cpython-311.pyc
   │     │  │     ├─ frv_types.cpython-311.pyc
   │     │  │     ├─ joint_rv.cpython-311.pyc
   │     │  │     ├─ joint_rv_types.cpython-311.pyc
   │     │  │     ├─ matrix_distributions.cpython-311.pyc
   │     │  │     ├─ random_matrix.cpython-311.pyc
   │     │  │     ├─ random_matrix_models.cpython-311.pyc
   │     │  │     ├─ rv.cpython-311.pyc
   │     │  │     ├─ rv_interface.cpython-311.pyc
   │     │  │     ├─ stochastic_process.cpython-311.pyc
   │     │  │     ├─ stochastic_process_types.cpython-311.pyc
   │     │  │     ├─ symbolic_multivariate_probability.cpython-311.pyc
   │     │  │     ├─ symbolic_probability.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ strategies
   │     │  │  ├─ branch
   │     │  │  │  ├─ core.py
   │     │  │  │  ├─ tests
   │     │  │  │  │  ├─ test_core.py
   │     │  │  │  │  ├─ test_tools.py
   │     │  │  │  │  ├─ test_traverse.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ test_core.cpython-311.pyc
   │     │  │  │  │     ├─ test_tools.cpython-311.pyc
   │     │  │  │  │     ├─ test_traverse.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ tools.py
   │     │  │  │  ├─ traverse.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ core.cpython-311.pyc
   │     │  │  │     ├─ tools.cpython-311.pyc
   │     │  │  │     ├─ traverse.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ core.py
   │     │  │  ├─ rl.py
   │     │  │  ├─ tests
   │     │  │  │  ├─ test_core.py
   │     │  │  │  ├─ test_rl.py
   │     │  │  │  ├─ test_tools.py
   │     │  │  │  ├─ test_traverse.py
   │     │  │  │  ├─ test_tree.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ test_core.cpython-311.pyc
   │     │  │  │     ├─ test_rl.cpython-311.pyc
   │     │  │  │     ├─ test_tools.cpython-311.pyc
   │     │  │  │     ├─ test_traverse.cpython-311.pyc
   │     │  │  │     ├─ test_tree.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ tools.py
   │     │  │  ├─ traverse.py
   │     │  │  ├─ tree.py
   │     │  │  ├─ util.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ core.cpython-311.pyc
   │     │  │     ├─ rl.cpython-311.pyc
   │     │  │     ├─ tools.cpython-311.pyc
   │     │  │     ├─ traverse.cpython-311.pyc
   │     │  │     ├─ tree.cpython-311.pyc
   │     │  │     ├─ util.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ tensor
   │     │  │  ├─ array
   │     │  │  │  ├─ arrayop.py
   │     │  │  │  ├─ array_comprehension.py
   │     │  │  │  ├─ array_derivatives.py
   │     │  │  │  ├─ dense_ndim_array.py
   │     │  │  │  ├─ expressions
   │     │  │  │  │  ├─ arrayexpr_derivatives.py
   │     │  │  │  │  ├─ array_expressions.py
   │     │  │  │  │  ├─ conv_array_to_indexed.py
   │     │  │  │  │  ├─ conv_array_to_matrix.py
   │     │  │  │  │  ├─ conv_indexed_to_array.py
   │     │  │  │  │  ├─ conv_matrix_to_array.py
   │     │  │  │  │  ├─ from_array_to_indexed.py
   │     │  │  │  │  ├─ from_array_to_matrix.py
   │     │  │  │  │  ├─ from_indexed_to_array.py
   │     │  │  │  │  ├─ from_matrix_to_array.py
   │     │  │  │  │  ├─ tests
   │     │  │  │  │  │  ├─ test_arrayexpr_derivatives.py
   │     │  │  │  │  │  ├─ test_array_expressions.py
   │     │  │  │  │  │  ├─ test_as_explicit.py
   │     │  │  │  │  │  ├─ test_convert_array_to_indexed.py
   │     │  │  │  │  │  ├─ test_convert_array_to_matrix.py
   │     │  │  │  │  │  ├─ test_convert_indexed_to_array.py
   │     │  │  │  │  │  ├─ test_convert_matrix_to_array.py
   │     │  │  │  │  │  ├─ test_deprecated_conv_modules.py
   │     │  │  │  │  │  ├─ __init__.py
   │     │  │  │  │  │  └─ __pycache__
   │     │  │  │  │  │     ├─ test_arrayexpr_derivatives.cpython-311.pyc
   │     │  │  │  │  │     ├─ test_array_expressions.cpython-311.pyc
   │     │  │  │  │  │     ├─ test_as_explicit.cpython-311.pyc
   │     │  │  │  │  │     ├─ test_convert_array_to_indexed.cpython-311.pyc
   │     │  │  │  │  │     ├─ test_convert_array_to_matrix.cpython-311.pyc
   │     │  │  │  │  │     ├─ test_convert_indexed_to_array.cpython-311.pyc
   │     │  │  │  │  │     ├─ test_convert_matrix_to_array.cpython-311.pyc
   │     │  │  │  │  │     ├─ test_deprecated_conv_modules.cpython-311.pyc
   │     │  │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  │  ├─ utils.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ arrayexpr_derivatives.cpython-311.pyc
   │     │  │  │  │     ├─ array_expressions.cpython-311.pyc
   │     │  │  │  │     ├─ conv_array_to_indexed.cpython-311.pyc
   │     │  │  │  │     ├─ conv_array_to_matrix.cpython-311.pyc
   │     │  │  │  │     ├─ conv_indexed_to_array.cpython-311.pyc
   │     │  │  │  │     ├─ conv_matrix_to_array.cpython-311.pyc
   │     │  │  │  │     ├─ from_array_to_indexed.cpython-311.pyc
   │     │  │  │  │     ├─ from_array_to_matrix.cpython-311.pyc
   │     │  │  │  │     ├─ from_indexed_to_array.cpython-311.pyc
   │     │  │  │  │     ├─ from_matrix_to_array.cpython-311.pyc
   │     │  │  │  │     ├─ utils.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ mutable_ndim_array.py
   │     │  │  │  ├─ ndim_array.py
   │     │  │  │  ├─ sparse_ndim_array.py
   │     │  │  │  ├─ tests
   │     │  │  │  │  ├─ test_arrayop.py
   │     │  │  │  │  ├─ test_array_comprehension.py
   │     │  │  │  │  ├─ test_array_derivatives.py
   │     │  │  │  │  ├─ test_immutable_ndim_array.py
   │     │  │  │  │  ├─ test_mutable_ndim_array.py
   │     │  │  │  │  ├─ test_ndim_array.py
   │     │  │  │  │  ├─ test_ndim_array_conversions.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ test_arrayop.cpython-311.pyc
   │     │  │  │  │     ├─ test_array_comprehension.cpython-311.pyc
   │     │  │  │  │     ├─ test_array_derivatives.cpython-311.pyc
   │     │  │  │  │     ├─ test_immutable_ndim_array.cpython-311.pyc
   │     │  │  │  │     ├─ test_mutable_ndim_array.cpython-311.pyc
   │     │  │  │  │     ├─ test_ndim_array.cpython-311.pyc
   │     │  │  │  │     ├─ test_ndim_array_conversions.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ arrayop.cpython-311.pyc
   │     │  │  │     ├─ array_comprehension.cpython-311.pyc
   │     │  │  │     ├─ array_derivatives.cpython-311.pyc
   │     │  │  │     ├─ dense_ndim_array.cpython-311.pyc
   │     │  │  │     ├─ mutable_ndim_array.cpython-311.pyc
   │     │  │  │     ├─ ndim_array.cpython-311.pyc
   │     │  │  │     ├─ sparse_ndim_array.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ functions.py
   │     │  │  ├─ indexed.py
   │     │  │  ├─ index_methods.py
   │     │  │  ├─ tensor.py
   │     │  │  ├─ tests
   │     │  │  │  ├─ test_functions.py
   │     │  │  │  ├─ test_indexed.py
   │     │  │  │  ├─ test_index_methods.py
   │     │  │  │  ├─ test_printing.py
   │     │  │  │  ├─ test_tensor.py
   │     │  │  │  ├─ test_tensor_element.py
   │     │  │  │  ├─ test_tensor_operators.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ test_functions.cpython-311.pyc
   │     │  │  │     ├─ test_indexed.cpython-311.pyc
   │     │  │  │     ├─ test_index_methods.cpython-311.pyc
   │     │  │  │     ├─ test_printing.cpython-311.pyc
   │     │  │  │     ├─ test_tensor.cpython-311.pyc
   │     │  │  │     ├─ test_tensor_element.cpython-311.pyc
   │     │  │  │     ├─ test_tensor_operators.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ toperators.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ functions.cpython-311.pyc
   │     │  │     ├─ indexed.cpython-311.pyc
   │     │  │     ├─ index_methods.cpython-311.pyc
   │     │  │     ├─ tensor.cpython-311.pyc
   │     │  │     ├─ toperators.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ testing
   │     │  │  ├─ matrices.py
   │     │  │  ├─ pytest.py
   │     │  │  ├─ quality_unicode.py
   │     │  │  ├─ randtest.py
   │     │  │  ├─ runtests.py
   │     │  │  ├─ runtests_pytest.py
   │     │  │  ├─ tests
   │     │  │  │  ├─ diagnose_imports.py
   │     │  │  │  ├─ test_code_quality.py
   │     │  │  │  ├─ test_deprecated.py
   │     │  │  │  ├─ test_module_imports.py
   │     │  │  │  ├─ test_pytest.py
   │     │  │  │  ├─ test_runtests_pytest.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ diagnose_imports.cpython-311.pyc
   │     │  │  │     ├─ test_code_quality.cpython-311.pyc
   │     │  │  │     ├─ test_deprecated.cpython-311.pyc
   │     │  │  │     ├─ test_module_imports.cpython-311.pyc
   │     │  │  │     ├─ test_pytest.cpython-311.pyc
   │     │  │  │     ├─ test_runtests_pytest.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ tmpfiles.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ matrices.cpython-311.pyc
   │     │  │     ├─ pytest.cpython-311.pyc
   │     │  │     ├─ quality_unicode.cpython-311.pyc
   │     │  │     ├─ randtest.cpython-311.pyc
   │     │  │     ├─ runtests.cpython-311.pyc
   │     │  │     ├─ runtests_pytest.cpython-311.pyc
   │     │  │     ├─ tmpfiles.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ this.py
   │     │  ├─ unify
   │     │  │  ├─ core.py
   │     │  │  ├─ rewrite.py
   │     │  │  ├─ tests
   │     │  │  │  ├─ test_rewrite.py
   │     │  │  │  ├─ test_sympy.py
   │     │  │  │  ├─ test_unify.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ test_rewrite.cpython-311.pyc
   │     │  │  │     ├─ test_sympy.cpython-311.pyc
   │     │  │  │     ├─ test_unify.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ usympy.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ core.cpython-311.pyc
   │     │  │     ├─ rewrite.cpython-311.pyc
   │     │  │     ├─ usympy.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ utilities
   │     │  │  ├─ autowrap.py
   │     │  │  ├─ codegen.py
   │     │  │  ├─ decorator.py
   │     │  │  ├─ enumerative.py
   │     │  │  ├─ exceptions.py
   │     │  │  ├─ iterables.py
   │     │  │  ├─ lambdify.py
   │     │  │  ├─ magic.py
   │     │  │  ├─ matchpy_connector.py
   │     │  │  ├─ mathml
   │     │  │  │  ├─ data
   │     │  │  │  │  ├─ mmlctop.xsl
   │     │  │  │  │  ├─ mmltex.xsl
   │     │  │  │  │  ├─ simple_mmlctop.xsl
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ memoization.py
   │     │  │  ├─ misc.py
   │     │  │  ├─ pkgdata.py
   │     │  │  ├─ pytest.py
   │     │  │  ├─ randtest.py
   │     │  │  ├─ runtests.py
   │     │  │  ├─ source.py
   │     │  │  ├─ tests
   │     │  │  │  ├─ test_autowrap.py
   │     │  │  │  ├─ test_codegen.py
   │     │  │  │  ├─ test_codegen_julia.py
   │     │  │  │  ├─ test_codegen_octave.py
   │     │  │  │  ├─ test_codegen_rust.py
   │     │  │  │  ├─ test_decorator.py
   │     │  │  │  ├─ test_deprecated.py
   │     │  │  │  ├─ test_enumerative.py
   │     │  │  │  ├─ test_exceptions.py
   │     │  │  │  ├─ test_iterables.py
   │     │  │  │  ├─ test_lambdify.py
   │     │  │  │  ├─ test_matchpy_connector.py
   │     │  │  │  ├─ test_mathml.py
   │     │  │  │  ├─ test_misc.py
   │     │  │  │  ├─ test_pickling.py
   │     │  │  │  ├─ test_source.py
   │     │  │  │  ├─ test_timeutils.py
   │     │  │  │  ├─ test_wester.py
   │     │  │  │  ├─ test_xxe.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ test_autowrap.cpython-311.pyc
   │     │  │  │     ├─ test_codegen.cpython-311.pyc
   │     │  │  │     ├─ test_codegen_julia.cpython-311.pyc
   │     │  │  │     ├─ test_codegen_octave.cpython-311.pyc
   │     │  │  │     ├─ test_codegen_rust.cpython-311.pyc
   │     │  │  │     ├─ test_decorator.cpython-311.pyc
   │     │  │  │     ├─ test_deprecated.cpython-311.pyc
   │     │  │  │     ├─ test_enumerative.cpython-311.pyc
   │     │  │  │     ├─ test_exceptions.cpython-311.pyc
   │     │  │  │     ├─ test_iterables.cpython-311.pyc
   │     │  │  │     ├─ test_lambdify.cpython-311.pyc
   │     │  │  │     ├─ test_matchpy_connector.cpython-311.pyc
   │     │  │  │     ├─ test_mathml.cpython-311.pyc
   │     │  │  │     ├─ test_misc.cpython-311.pyc
   │     │  │  │     ├─ test_pickling.cpython-311.pyc
   │     │  │  │     ├─ test_source.cpython-311.pyc
   │     │  │  │     ├─ test_timeutils.cpython-311.pyc
   │     │  │  │     ├─ test_wester.cpython-311.pyc
   │     │  │  │     ├─ test_xxe.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ timeutils.py
   │     │  │  ├─ tmpfiles.py
   │     │  │  ├─ _compilation
   │     │  │  │  ├─ availability.py
   │     │  │  │  ├─ compilation.py
   │     │  │  │  ├─ runners.py
   │     │  │  │  ├─ tests
   │     │  │  │  │  ├─ test_compilation.py
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     ├─ test_compilation.cpython-311.pyc
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ util.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ availability.cpython-311.pyc
   │     │  │  │     ├─ compilation.cpython-311.pyc
   │     │  │  │     ├─ runners.cpython-311.pyc
   │     │  │  │     ├─ util.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ autowrap.cpython-311.pyc
   │     │  │     ├─ codegen.cpython-311.pyc
   │     │  │     ├─ decorator.cpython-311.pyc
   │     │  │     ├─ enumerative.cpython-311.pyc
   │     │  │     ├─ exceptions.cpython-311.pyc
   │     │  │     ├─ iterables.cpython-311.pyc
   │     │  │     ├─ lambdify.cpython-311.pyc
   │     │  │     ├─ magic.cpython-311.pyc
   │     │  │     ├─ matchpy_connector.cpython-311.pyc
   │     │  │     ├─ memoization.cpython-311.pyc
   │     │  │     ├─ misc.cpython-311.pyc
   │     │  │     ├─ pkgdata.cpython-311.pyc
   │     │  │     ├─ pytest.cpython-311.pyc
   │     │  │     ├─ randtest.cpython-311.pyc
   │     │  │     ├─ runtests.cpython-311.pyc
   │     │  │     ├─ source.cpython-311.pyc
   │     │  │     ├─ timeutils.cpython-311.pyc
   │     │  │     ├─ tmpfiles.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ vector
   │     │  │  ├─ basisdependent.py
   │     │  │  ├─ coordsysrect.py
   │     │  │  ├─ deloperator.py
   │     │  │  ├─ dyadic.py
   │     │  │  ├─ functions.py
   │     │  │  ├─ implicitregion.py
   │     │  │  ├─ integrals.py
   │     │  │  ├─ kind.py
   │     │  │  ├─ operators.py
   │     │  │  ├─ orienters.py
   │     │  │  ├─ parametricregion.py
   │     │  │  ├─ point.py
   │     │  │  ├─ scalar.py
   │     │  │  ├─ tests
   │     │  │  │  ├─ test_coordsysrect.py
   │     │  │  │  ├─ test_dyadic.py
   │     │  │  │  ├─ test_field_functions.py
   │     │  │  │  ├─ test_functions.py
   │     │  │  │  ├─ test_implicitregion.py
   │     │  │  │  ├─ test_integrals.py
   │     │  │  │  ├─ test_operators.py
   │     │  │  │  ├─ test_parametricregion.py
   │     │  │  │  ├─ test_printing.py
   │     │  │  │  ├─ test_vector.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ test_coordsysrect.cpython-311.pyc
   │     │  │  │     ├─ test_dyadic.cpython-311.pyc
   │     │  │  │     ├─ test_field_functions.cpython-311.pyc
   │     │  │  │     ├─ test_functions.cpython-311.pyc
   │     │  │  │     ├─ test_implicitregion.cpython-311.pyc
   │     │  │  │     ├─ test_integrals.cpython-311.pyc
   │     │  │  │     ├─ test_operators.cpython-311.pyc
   │     │  │  │     ├─ test_parametricregion.cpython-311.pyc
   │     │  │  │     ├─ test_printing.cpython-311.pyc
   │     │  │  │     ├─ test_vector.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ vector.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ basisdependent.cpython-311.pyc
   │     │  │     ├─ coordsysrect.cpython-311.pyc
   │     │  │     ├─ deloperator.cpython-311.pyc
   │     │  │     ├─ dyadic.cpython-311.pyc
   │     │  │     ├─ functions.cpython-311.pyc
   │     │  │     ├─ implicitregion.cpython-311.pyc
   │     │  │     ├─ integrals.cpython-311.pyc
   │     │  │     ├─ kind.cpython-311.pyc
   │     │  │     ├─ operators.cpython-311.pyc
   │     │  │     ├─ orienters.cpython-311.pyc
   │     │  │     ├─ parametricregion.cpython-311.pyc
   │     │  │     ├─ point.cpython-311.pyc
   │     │  │     ├─ scalar.cpython-311.pyc
   │     │  │     ├─ vector.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ __init__.py
   │     │  └─ __pycache__
   │     │     ├─ abc.cpython-311.pyc
   │     │     ├─ conftest.cpython-311.pyc
   │     │     ├─ galgebra.cpython-311.pyc
   │     │     ├─ release.cpython-311.pyc
   │     │     ├─ this.cpython-311.pyc
   │     │     └─ __init__.cpython-311.pyc
   │     ├─ sympy-1.14.0.dist-info
   │     │  ├─ entry_points.txt
   │     │  ├─ INSTALLER
   │     │  ├─ licenses
   │     │  │  ├─ AUTHORS
   │     │  │  └─ LICENSE
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  ├─ top_level.txt
   │     │  └─ WHEEL
   │     ├─ tenacity
   │     │  ├─ after.py
   │     │  ├─ asyncio
   │     │  │  ├─ retry.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ retry.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ before.py
   │     │  ├─ before_sleep.py
   │     │  ├─ nap.py
   │     │  ├─ py.typed
   │     │  ├─ retry.py
   │     │  ├─ stop.py
   │     │  ├─ tornadoweb.py
   │     │  ├─ wait.py
   │     │  ├─ _utils.py
   │     │  ├─ __init__.py
   │     │  └─ __pycache__
   │     │     ├─ after.cpython-311.pyc
   │     │     ├─ before.cpython-311.pyc
   │     │     ├─ before_sleep.cpython-311.pyc
   │     │     ├─ nap.cpython-311.pyc
   │     │     ├─ retry.cpython-311.pyc
   │     │     ├─ stop.cpython-311.pyc
   │     │     ├─ tornadoweb.cpython-311.pyc
   │     │     ├─ wait.cpython-311.pyc
   │     │     ├─ _utils.cpython-311.pyc
   │     │     └─ __init__.cpython-311.pyc
   │     ├─ tenacity-9.1.4.dist-info
   │     │  ├─ INSTALLER
   │     │  ├─ licenses
   │     │  │  └─ LICENSE
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  ├─ top_level.txt
   │     │  └─ WHEEL
   │     ├─ tokenizers
   │     │  ├─ decoders
   │     │  │  ├─ __init__.py
   │     │  │  ├─ __init__.pyi
   │     │  │  └─ __pycache__
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ implementations
   │     │  │  ├─ base_tokenizer.py
   │     │  │  ├─ bert_wordpiece.py
   │     │  │  ├─ byte_level_bpe.py
   │     │  │  ├─ char_level_bpe.py
   │     │  │  ├─ sentencepiece_bpe.py
   │     │  │  ├─ sentencepiece_unigram.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ base_tokenizer.cpython-311.pyc
   │     │  │     ├─ bert_wordpiece.cpython-311.pyc
   │     │  │     ├─ byte_level_bpe.cpython-311.pyc
   │     │  │     ├─ char_level_bpe.cpython-311.pyc
   │     │  │     ├─ sentencepiece_bpe.cpython-311.pyc
   │     │  │     ├─ sentencepiece_unigram.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ models
   │     │  │  ├─ __init__.py
   │     │  │  ├─ __init__.pyi
   │     │  │  └─ __pycache__
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ normalizers
   │     │  │  ├─ __init__.py
   │     │  │  ├─ __init__.pyi
   │     │  │  └─ __pycache__
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ pre_tokenizers
   │     │  │  ├─ __init__.py
   │     │  │  ├─ __init__.pyi
   │     │  │  └─ __pycache__
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ processors
   │     │  │  ├─ __init__.py
   │     │  │  ├─ __init__.pyi
   │     │  │  └─ __pycache__
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ tokenizers.pyd
   │     │  ├─ tokenizers.pyi
   │     │  ├─ tools
   │     │  │  ├─ visualizer-styles.css
   │     │  │  ├─ visualizer.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ visualizer.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ trainers
   │     │  │  ├─ __init__.py
   │     │  │  ├─ __init__.pyi
   │     │  │  └─ __pycache__
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ __init__.py
   │     │  ├─ __init__.pyi
   │     │  └─ __pycache__
   │     │     └─ __init__.cpython-311.pyc
   │     ├─ tokenizers-0.22.2.dist-info
   │     │  ├─ INSTALLER
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  └─ WHEEL
   │     ├─ toml
   │     │  ├─ decoder.py
   │     │  ├─ encoder.py
   │     │  ├─ ordered.py
   │     │  ├─ tz.py
   │     │  ├─ __init__.py
   │     │  └─ __pycache__
   │     │     ├─ decoder.cpython-311.pyc
   │     │     ├─ encoder.cpython-311.pyc
   │     │     ├─ ordered.cpython-311.pyc
   │     │     ├─ tz.cpython-311.pyc
   │     │     └─ __init__.cpython-311.pyc
   │     ├─ toml-0.10.2.dist-info
   │     │  ├─ INSTALLER
   │     │  ├─ LICENSE
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  ├─ top_level.txt
   │     │  └─ WHEEL
   │     ├─ tornado
   │     │  ├─ auth.py
   │     │  ├─ autoreload.py
   │     │  ├─ concurrent.py
   │     │  ├─ curl_httpclient.py
   │     │  ├─ escape.py
   │     │  ├─ gen.py
   │     │  ├─ http1connection.py
   │     │  ├─ httpclient.py
   │     │  ├─ httpserver.py
   │     │  ├─ httputil.py
   │     │  ├─ ioloop.py
   │     │  ├─ iostream.py
   │     │  ├─ locale.py
   │     │  ├─ locks.py
   │     │  ├─ log.py
   │     │  ├─ netutil.py
   │     │  ├─ options.py
   │     │  ├─ platform
   │     │  │  ├─ asyncio.py
   │     │  │  ├─ caresresolver.py
   │     │  │  ├─ twisted.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ asyncio.cpython-311.pyc
   │     │  │     ├─ caresresolver.cpython-311.pyc
   │     │  │     ├─ twisted.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ process.py
   │     │  ├─ py.typed
   │     │  ├─ queues.py
   │     │  ├─ routing.py
   │     │  ├─ simple_httpclient.py
   │     │  ├─ speedups.pyd
   │     │  ├─ speedups.pyi
   │     │  ├─ tcpclient.py
   │     │  ├─ tcpserver.py
   │     │  ├─ template.py
   │     │  ├─ test
   │     │  │  ├─ asyncio_test.py
   │     │  │  ├─ auth_test.py
   │     │  │  ├─ autoreload_test.py
   │     │  │  ├─ circlerefs_test.py
   │     │  │  ├─ concurrent_test.py
   │     │  │  ├─ csv_translations
   │     │  │  │  └─ fr_FR.csv
   │     │  │  ├─ curl_httpclient_test.py
   │     │  │  ├─ escape_test.py
   │     │  │  ├─ gen_test.py
   │     │  │  ├─ gettext_translations
   │     │  │  │  └─ fr_FR
   │     │  │  │     └─ LC_MESSAGES
   │     │  │  │        ├─ tornado_test.mo
   │     │  │  │        └─ tornado_test.po
   │     │  │  ├─ http1connection_test.py
   │     │  │  ├─ httpclient_test.py
   │     │  │  ├─ httpserver_test.py
   │     │  │  ├─ httputil_test.py
   │     │  │  ├─ import_test.py
   │     │  │  ├─ ioloop_test.py
   │     │  │  ├─ iostream_test.py
   │     │  │  ├─ locale_test.py
   │     │  │  ├─ locks_test.py
   │     │  │  ├─ log_test.py
   │     │  │  ├─ netutil_test.py
   │     │  │  ├─ options_test.cfg
   │     │  │  ├─ options_test.py
   │     │  │  ├─ options_test_types.cfg
   │     │  │  ├─ options_test_types_str.cfg
   │     │  │  ├─ process_test.py
   │     │  │  ├─ queues_test.py
   │     │  │  ├─ resolve_test_helper.py
   │     │  │  ├─ routing_test.py
   │     │  │  ├─ runtests.py
   │     │  │  ├─ simple_httpclient_test.py
   │     │  │  ├─ static
   │     │  │  │  ├─ dir
   │     │  │  │  │  └─ index.html
   │     │  │  │  ├─ robots.txt
   │     │  │  │  ├─ sample.xml
   │     │  │  │  ├─ sample.xml.bz2
   │     │  │  │  └─ sample.xml.gz
   │     │  │  ├─ static_foo.txt
   │     │  │  ├─ tcpclient_test.py
   │     │  │  ├─ tcpserver_test.py
   │     │  │  ├─ templates
   │     │  │  │  └─ utf8.html
   │     │  │  ├─ template_test.py
   │     │  │  ├─ test.crt
   │     │  │  ├─ test.key
   │     │  │  ├─ testing_test.py
   │     │  │  ├─ twisted_test.py
   │     │  │  ├─ util.py
   │     │  │  ├─ util_test.py
   │     │  │  ├─ websocket_test.py
   │     │  │  ├─ web_test.py
   │     │  │  ├─ wsgi_test.py
   │     │  │  ├─ __init__.py
   │     │  │  ├─ __main__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ asyncio_test.cpython-311.pyc
   │     │  │     ├─ auth_test.cpython-311.pyc
   │     │  │     ├─ autoreload_test.cpython-311.pyc
   │     │  │     ├─ circlerefs_test.cpython-311.pyc
   │     │  │     ├─ concurrent_test.cpython-311.pyc
   │     │  │     ├─ curl_httpclient_test.cpython-311.pyc
   │     │  │     ├─ escape_test.cpython-311.pyc
   │     │  │     ├─ gen_test.cpython-311.pyc
   │     │  │     ├─ http1connection_test.cpython-311.pyc
   │     │  │     ├─ httpclient_test.cpython-311.pyc
   │     │  │     ├─ httpserver_test.cpython-311.pyc
   │     │  │     ├─ httputil_test.cpython-311.pyc
   │     │  │     ├─ import_test.cpython-311.pyc
   │     │  │     ├─ ioloop_test.cpython-311.pyc
   │     │  │     ├─ iostream_test.cpython-311.pyc
   │     │  │     ├─ locale_test.cpython-311.pyc
   │     │  │     ├─ locks_test.cpython-311.pyc
   │     │  │     ├─ log_test.cpython-311.pyc
   │     │  │     ├─ netutil_test.cpython-311.pyc
   │     │  │     ├─ options_test.cpython-311.pyc
   │     │  │     ├─ process_test.cpython-311.pyc
   │     │  │     ├─ queues_test.cpython-311.pyc
   │     │  │     ├─ resolve_test_helper.cpython-311.pyc
   │     │  │     ├─ routing_test.cpython-311.pyc
   │     │  │     ├─ runtests.cpython-311.pyc
   │     │  │     ├─ simple_httpclient_test.cpython-311.pyc
   │     │  │     ├─ tcpclient_test.cpython-311.pyc
   │     │  │     ├─ tcpserver_test.cpython-311.pyc
   │     │  │     ├─ template_test.cpython-311.pyc
   │     │  │     ├─ testing_test.cpython-311.pyc
   │     │  │     ├─ twisted_test.cpython-311.pyc
   │     │  │     ├─ util.cpython-311.pyc
   │     │  │     ├─ util_test.cpython-311.pyc
   │     │  │     ├─ websocket_test.cpython-311.pyc
   │     │  │     ├─ web_test.cpython-311.pyc
   │     │  │     ├─ wsgi_test.cpython-311.pyc
   │     │  │     ├─ __init__.cpython-311.pyc
   │     │  │     └─ __main__.cpython-311.pyc
   │     │  ├─ testing.py
   │     │  ├─ util.py
   │     │  ├─ web.py
   │     │  ├─ websocket.py
   │     │  ├─ wsgi.py
   │     │  ├─ _locale_data.py
   │     │  ├─ __init__.py
   │     │  ├─ __init__.pyi
   │     │  └─ __pycache__
   │     │     ├─ auth.cpython-311.pyc
   │     │     ├─ autoreload.cpython-311.pyc
   │     │     ├─ concurrent.cpython-311.pyc
   │     │     ├─ curl_httpclient.cpython-311.pyc
   │     │     ├─ escape.cpython-311.pyc
   │     │     ├─ gen.cpython-311.pyc
   │     │     ├─ http1connection.cpython-311.pyc
   │     │     ├─ httpclient.cpython-311.pyc
   │     │     ├─ httpserver.cpython-311.pyc
   │     │     ├─ httputil.cpython-311.pyc
   │     │     ├─ ioloop.cpython-311.pyc
   │     │     ├─ iostream.cpython-311.pyc
   │     │     ├─ locale.cpython-311.pyc
   │     │     ├─ locks.cpython-311.pyc
   │     │     ├─ log.cpython-311.pyc
   │     │     ├─ netutil.cpython-311.pyc
   │     │     ├─ options.cpython-311.pyc
   │     │     ├─ process.cpython-311.pyc
   │     │     ├─ queues.cpython-311.pyc
   │     │     ├─ routing.cpython-311.pyc
   │     │     ├─ simple_httpclient.cpython-311.pyc
   │     │     ├─ tcpclient.cpython-311.pyc
   │     │     ├─ tcpserver.cpython-311.pyc
   │     │     ├─ template.cpython-311.pyc
   │     │     ├─ testing.cpython-311.pyc
   │     │     ├─ util.cpython-311.pyc
   │     │     ├─ web.cpython-311.pyc
   │     │     ├─ websocket.cpython-311.pyc
   │     │     ├─ wsgi.cpython-311.pyc
   │     │     ├─ _locale_data.cpython-311.pyc
   │     │     └─ __init__.cpython-311.pyc
   │     ├─ tornado-6.5.5.dist-info
   │     │  ├─ INSTALLER
   │     │  ├─ licenses
   │     │  │  └─ LICENSE
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  ├─ top_level.txt
   │     │  └─ WHEEL
   │     ├─ tqdm
   │     │  ├─ asyncio.py
   │     │  ├─ auto.py
   │     │  ├─ autonotebook.py
   │     │  ├─ cli.py
   │     │  ├─ completion.sh
   │     │  ├─ contrib
   │     │  │  ├─ bells.py
   │     │  │  ├─ concurrent.py
   │     │  │  ├─ discord.py
   │     │  │  ├─ itertools.py
   │     │  │  ├─ logging.py
   │     │  │  ├─ slack.py
   │     │  │  ├─ telegram.py
   │     │  │  ├─ utils_worker.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ bells.cpython-311.pyc
   │     │  │     ├─ concurrent.cpython-311.pyc
   │     │  │     ├─ discord.cpython-311.pyc
   │     │  │     ├─ itertools.cpython-311.pyc
   │     │  │     ├─ logging.cpython-311.pyc
   │     │  │     ├─ slack.cpython-311.pyc
   │     │  │     ├─ telegram.cpython-311.pyc
   │     │  │     ├─ utils_worker.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ dask.py
   │     │  ├─ gui.py
   │     │  ├─ keras.py
   │     │  ├─ notebook.py
   │     │  ├─ rich.py
   │     │  ├─ std.py
   │     │  ├─ tk.py
   │     │  ├─ tqdm.1
   │     │  ├─ utils.py
   │     │  ├─ version.py
   │     │  ├─ _main.py
   │     │  ├─ _monitor.py
   │     │  ├─ _tqdm.py
   │     │  ├─ _tqdm_gui.py
   │     │  ├─ _tqdm_notebook.py
   │     │  ├─ _tqdm_pandas.py
   │     │  ├─ _utils.py
   │     │  ├─ __init__.py
   │     │  ├─ __main__.py
   │     │  └─ __pycache__
   │     │     ├─ asyncio.cpython-311.pyc
   │     │     ├─ auto.cpython-311.pyc
   │     │     ├─ autonotebook.cpython-311.pyc
   │     │     ├─ cli.cpython-311.pyc
   │     │     ├─ dask.cpython-311.pyc
   │     │     ├─ gui.cpython-311.pyc
   │     │     ├─ keras.cpython-311.pyc
   │     │     ├─ notebook.cpython-311.pyc
   │     │     ├─ rich.cpython-311.pyc
   │     │     ├─ std.cpython-311.pyc
   │     │     ├─ tk.cpython-311.pyc
   │     │     ├─ utils.cpython-311.pyc
   │     │     ├─ version.cpython-311.pyc
   │     │     ├─ _main.cpython-311.pyc
   │     │     ├─ _monitor.cpython-311.pyc
   │     │     ├─ _tqdm.cpython-311.pyc
   │     │     ├─ _tqdm_gui.cpython-311.pyc
   │     │     ├─ _tqdm_notebook.cpython-311.pyc
   │     │     ├─ _tqdm_pandas.cpython-311.pyc
   │     │     ├─ _utils.cpython-311.pyc
   │     │     ├─ __init__.cpython-311.pyc
   │     │     └─ __main__.cpython-311.pyc
   │     ├─ tqdm-4.67.3.dist-info
   │     │  ├─ entry_points.txt
   │     │  ├─ INSTALLER
   │     │  ├─ licenses
   │     │  │  └─ LICENCE
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  ├─ top_level.txt
   │     │  └─ WHEEL
   │     ├─ typer
   │     │  ├─ cli.py
   │     │  ├─ colors.py
   │     │  ├─ completion.py
   │     │  ├─ core.py
   │     │  ├─ main.py
   │     │  ├─ models.py
   │     │  ├─ params.py
   │     │  ├─ py.typed
   │     │  ├─ rich_utils.py
   │     │  ├─ testing.py
   │     │  ├─ utils.py
   │     │  ├─ _completion_classes.py
   │     │  ├─ _completion_shared.py
   │     │  ├─ _types.py
   │     │  ├─ _typing.py
   │     │  ├─ __init__.py
   │     │  ├─ __main__.py
   │     │  └─ __pycache__
   │     │     ├─ cli.cpython-311.pyc
   │     │     ├─ colors.cpython-311.pyc
   │     │     ├─ completion.cpython-311.pyc
   │     │     ├─ core.cpython-311.pyc
   │     │     ├─ main.cpython-311.pyc
   │     │     ├─ models.cpython-311.pyc
   │     │     ├─ params.cpython-311.pyc
   │     │     ├─ rich_utils.cpython-311.pyc
   │     │     ├─ testing.cpython-311.pyc
   │     │     ├─ utils.cpython-311.pyc
   │     │     ├─ _completion_classes.cpython-311.pyc
   │     │     ├─ _completion_shared.cpython-311.pyc
   │     │     ├─ _types.cpython-311.pyc
   │     │     ├─ _typing.cpython-311.pyc
   │     │     ├─ __init__.cpython-311.pyc
   │     │     └─ __main__.cpython-311.pyc
   │     ├─ typer-0.24.1.dist-info
   │     │  ├─ entry_points.txt
   │     │  ├─ INSTALLER
   │     │  ├─ licenses
   │     │  │  └─ LICENSE
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  └─ WHEEL
   │     ├─ typing_extensions-4.15.0.dist-info
   │     │  ├─ INSTALLER
   │     │  ├─ licenses
   │     │  │  └─ LICENSE
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  └─ WHEEL
   │     ├─ typing_extensions.py
   │     ├─ typing_inspection
   │     │  ├─ introspection.py
   │     │  ├─ py.typed
   │     │  ├─ typing_objects.py
   │     │  ├─ typing_objects.pyi
   │     │  ├─ __init__.py
   │     │  └─ __pycache__
   │     │     ├─ introspection.cpython-311.pyc
   │     │     ├─ typing_objects.cpython-311.pyc
   │     │     └─ __init__.cpython-311.pyc
   │     ├─ typing_inspection-0.4.2.dist-info
   │     │  ├─ INSTALLER
   │     │  ├─ licenses
   │     │  │  └─ LICENSE
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  └─ WHEEL
   │     ├─ tzdata
   │     │  ├─ zoneinfo
   │     │  │  ├─ Africa
   │     │  │  │  ├─ Abidjan
   │     │  │  │  ├─ Accra
   │     │  │  │  ├─ Addis_Ababa
   │     │  │  │  ├─ Algiers
   │     │  │  │  ├─ Asmara
   │     │  │  │  ├─ Asmera
   │     │  │  │  ├─ Bamako
   │     │  │  │  ├─ Bangui
   │     │  │  │  ├─ Banjul
   │     │  │  │  ├─ Bissau
   │     │  │  │  ├─ Blantyre
   │     │  │  │  ├─ Brazzaville
   │     │  │  │  ├─ Bujumbura
   │     │  │  │  ├─ Cairo
   │     │  │  │  ├─ Casablanca
   │     │  │  │  ├─ Ceuta
   │     │  │  │  ├─ Conakry
   │     │  │  │  ├─ Dakar
   │     │  │  │  ├─ Dar_es_Salaam
   │     │  │  │  ├─ Djibouti
   │     │  │  │  ├─ Douala
   │     │  │  │  ├─ El_Aaiun
   │     │  │  │  ├─ Freetown
   │     │  │  │  ├─ Gaborone
   │     │  │  │  ├─ Harare
   │     │  │  │  ├─ Johannesburg
   │     │  │  │  ├─ Juba
   │     │  │  │  ├─ Kampala
   │     │  │  │  ├─ Khartoum
   │     │  │  │  ├─ Kigali
   │     │  │  │  ├─ Kinshasa
   │     │  │  │  ├─ Lagos
   │     │  │  │  ├─ Libreville
   │     │  │  │  ├─ Lome
   │     │  │  │  ├─ Luanda
   │     │  │  │  ├─ Lubumbashi
   │     │  │  │  ├─ Lusaka
   │     │  │  │  ├─ Malabo
   │     │  │  │  ├─ Maputo
   │     │  │  │  ├─ Maseru
   │     │  │  │  ├─ Mbabane
   │     │  │  │  ├─ Mogadishu
   │     │  │  │  ├─ Monrovia
   │     │  │  │  ├─ Nairobi
   │     │  │  │  ├─ Ndjamena
   │     │  │  │  ├─ Niamey
   │     │  │  │  ├─ Nouakchott
   │     │  │  │  ├─ Ouagadougou
   │     │  │  │  ├─ Porto-Novo
   │     │  │  │  ├─ Sao_Tome
   │     │  │  │  ├─ Timbuktu
   │     │  │  │  ├─ Tripoli
   │     │  │  │  ├─ Tunis
   │     │  │  │  ├─ Windhoek
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ America
   │     │  │  │  ├─ Adak
   │     │  │  │  ├─ Anchorage
   │     │  │  │  ├─ Anguilla
   │     │  │  │  ├─ Antigua
   │     │  │  │  ├─ Araguaina
   │     │  │  │  ├─ Argentina
   │     │  │  │  │  ├─ Buenos_Aires
   │     │  │  │  │  ├─ Catamarca
   │     │  │  │  │  ├─ ComodRivadavia
   │     │  │  │  │  ├─ Cordoba
   │     │  │  │  │  ├─ Jujuy
   │     │  │  │  │  ├─ La_Rioja
   │     │  │  │  │  ├─ Mendoza
   │     │  │  │  │  ├─ Rio_Gallegos
   │     │  │  │  │  ├─ Salta
   │     │  │  │  │  ├─ San_Juan
   │     │  │  │  │  ├─ San_Luis
   │     │  │  │  │  ├─ Tucuman
   │     │  │  │  │  ├─ Ushuaia
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ Aruba
   │     │  │  │  ├─ Asuncion
   │     │  │  │  ├─ Atikokan
   │     │  │  │  ├─ Atka
   │     │  │  │  ├─ Bahia
   │     │  │  │  ├─ Bahia_Banderas
   │     │  │  │  ├─ Barbados
   │     │  │  │  ├─ Belem
   │     │  │  │  ├─ Belize
   │     │  │  │  ├─ Blanc-Sablon
   │     │  │  │  ├─ Boa_Vista
   │     │  │  │  ├─ Bogota
   │     │  │  │  ├─ Boise
   │     │  │  │  ├─ Buenos_Aires
   │     │  │  │  ├─ Cambridge_Bay
   │     │  │  │  ├─ Campo_Grande
   │     │  │  │  ├─ Cancun
   │     │  │  │  ├─ Caracas
   │     │  │  │  ├─ Catamarca
   │     │  │  │  ├─ Cayenne
   │     │  │  │  ├─ Cayman
   │     │  │  │  ├─ Chicago
   │     │  │  │  ├─ Chihuahua
   │     │  │  │  ├─ Ciudad_Juarez
   │     │  │  │  ├─ Coral_Harbour
   │     │  │  │  ├─ Cordoba
   │     │  │  │  ├─ Costa_Rica
   │     │  │  │  ├─ Coyhaique
   │     │  │  │  ├─ Creston
   │     │  │  │  ├─ Cuiaba
   │     │  │  │  ├─ Curacao
   │     │  │  │  ├─ Danmarkshavn
   │     │  │  │  ├─ Dawson
   │     │  │  │  ├─ Dawson_Creek
   │     │  │  │  ├─ Denver
   │     │  │  │  ├─ Detroit
   │     │  │  │  ├─ Dominica
   │     │  │  │  ├─ Edmonton
   │     │  │  │  ├─ Eirunepe
   │     │  │  │  ├─ El_Salvador
   │     │  │  │  ├─ Ensenada
   │     │  │  │  ├─ Fortaleza
   │     │  │  │  ├─ Fort_Nelson
   │     │  │  │  ├─ Fort_Wayne
   │     │  │  │  ├─ Glace_Bay
   │     │  │  │  ├─ Godthab
   │     │  │  │  ├─ Goose_Bay
   │     │  │  │  ├─ Grand_Turk
   │     │  │  │  ├─ Grenada
   │     │  │  │  ├─ Guadeloupe
   │     │  │  │  ├─ Guatemala
   │     │  │  │  ├─ Guayaquil
   │     │  │  │  ├─ Guyana
   │     │  │  │  ├─ Halifax
   │     │  │  │  ├─ Havana
   │     │  │  │  ├─ Hermosillo
   │     │  │  │  ├─ Indiana
   │     │  │  │  │  ├─ Indianapolis
   │     │  │  │  │  ├─ Knox
   │     │  │  │  │  ├─ Marengo
   │     │  │  │  │  ├─ Petersburg
   │     │  │  │  │  ├─ Tell_City
   │     │  │  │  │  ├─ Vevay
   │     │  │  │  │  ├─ Vincennes
   │     │  │  │  │  ├─ Winamac
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ Indianapolis
   │     │  │  │  ├─ Inuvik
   │     │  │  │  ├─ Iqaluit
   │     │  │  │  ├─ Jamaica
   │     │  │  │  ├─ Jujuy
   │     │  │  │  ├─ Juneau
   │     │  │  │  ├─ Kentucky
   │     │  │  │  │  ├─ Louisville
   │     │  │  │  │  ├─ Monticello
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ Knox_IN
   │     │  │  │  ├─ Kralendijk
   │     │  │  │  ├─ La_Paz
   │     │  │  │  ├─ Lima
   │     │  │  │  ├─ Los_Angeles
   │     │  │  │  ├─ Louisville
   │     │  │  │  ├─ Lower_Princes
   │     │  │  │  ├─ Maceio
   │     │  │  │  ├─ Managua
   │     │  │  │  ├─ Manaus
   │     │  │  │  ├─ Marigot
   │     │  │  │  ├─ Martinique
   │     │  │  │  ├─ Matamoros
   │     │  │  │  ├─ Mazatlan
   │     │  │  │  ├─ Mendoza
   │     │  │  │  ├─ Menominee
   │     │  │  │  ├─ Merida
   │     │  │  │  ├─ Metlakatla
   │     │  │  │  ├─ Mexico_City
   │     │  │  │  ├─ Miquelon
   │     │  │  │  ├─ Moncton
   │     │  │  │  ├─ Monterrey
   │     │  │  │  ├─ Montevideo
   │     │  │  │  ├─ Montreal
   │     │  │  │  ├─ Montserrat
   │     │  │  │  ├─ Nassau
   │     │  │  │  ├─ New_York
   │     │  │  │  ├─ Nipigon
   │     │  │  │  ├─ Nome
   │     │  │  │  ├─ Noronha
   │     │  │  │  ├─ North_Dakota
   │     │  │  │  │  ├─ Beulah
   │     │  │  │  │  ├─ Center
   │     │  │  │  │  ├─ New_Salem
   │     │  │  │  │  ├─ __init__.py
   │     │  │  │  │  └─ __pycache__
   │     │  │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  │  ├─ Nuuk
   │     │  │  │  ├─ Ojinaga
   │     │  │  │  ├─ Panama
   │     │  │  │  ├─ Pangnirtung
   │     │  │  │  ├─ Paramaribo
   │     │  │  │  ├─ Phoenix
   │     │  │  │  ├─ Port-au-Prince
   │     │  │  │  ├─ Porto_Acre
   │     │  │  │  ├─ Porto_Velho
   │     │  │  │  ├─ Port_of_Spain
   │     │  │  │  ├─ Puerto_Rico
   │     │  │  │  ├─ Punta_Arenas
   │     │  │  │  ├─ Rainy_River
   │     │  │  │  ├─ Rankin_Inlet
   │     │  │  │  ├─ Recife
   │     │  │  │  ├─ Regina
   │     │  │  │  ├─ Resolute
   │     │  │  │  ├─ Rio_Branco
   │     │  │  │  ├─ Rosario
   │     │  │  │  ├─ Santarem
   │     │  │  │  ├─ Santa_Isabel
   │     │  │  │  ├─ Santiago
   │     │  │  │  ├─ Santo_Domingo
   │     │  │  │  ├─ Sao_Paulo
   │     │  │  │  ├─ Scoresbysund
   │     │  │  │  ├─ Shiprock
   │     │  │  │  ├─ Sitka
   │     │  │  │  ├─ St_Barthelemy
   │     │  │  │  ├─ St_Johns
   │     │  │  │  ├─ St_Kitts
   │     │  │  │  ├─ St_Lucia
   │     │  │  │  ├─ St_Thomas
   │     │  │  │  ├─ St_Vincent
   │     │  │  │  ├─ Swift_Current
   │     │  │  │  ├─ Tegucigalpa
   │     │  │  │  ├─ Thule
   │     │  │  │  ├─ Thunder_Bay
   │     │  │  │  ├─ Tijuana
   │     │  │  │  ├─ Toronto
   │     │  │  │  ├─ Tortola
   │     │  │  │  ├─ Vancouver
   │     │  │  │  ├─ Virgin
   │     │  │  │  ├─ Whitehorse
   │     │  │  │  ├─ Winnipeg
   │     │  │  │  ├─ Yakutat
   │     │  │  │  ├─ Yellowknife
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ Antarctica
   │     │  │  │  ├─ Casey
   │     │  │  │  ├─ Davis
   │     │  │  │  ├─ DumontDUrville
   │     │  │  │  ├─ Macquarie
   │     │  │  │  ├─ Mawson
   │     │  │  │  ├─ McMurdo
   │     │  │  │  ├─ Palmer
   │     │  │  │  ├─ Rothera
   │     │  │  │  ├─ South_Pole
   │     │  │  │  ├─ Syowa
   │     │  │  │  ├─ Troll
   │     │  │  │  ├─ Vostok
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ Arctic
   │     │  │  │  ├─ Longyearbyen
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ Asia
   │     │  │  │  ├─ Aden
   │     │  │  │  ├─ Almaty
   │     │  │  │  ├─ Amman
   │     │  │  │  ├─ Anadyr
   │     │  │  │  ├─ Aqtau
   │     │  │  │  ├─ Aqtobe
   │     │  │  │  ├─ Ashgabat
   │     │  │  │  ├─ Ashkhabad
   │     │  │  │  ├─ Atyrau
   │     │  │  │  ├─ Baghdad
   │     │  │  │  ├─ Bahrain
   │     │  │  │  ├─ Baku
   │     │  │  │  ├─ Bangkok
   │     │  │  │  ├─ Barnaul
   │     │  │  │  ├─ Beirut
   │     │  │  │  ├─ Bishkek
   │     │  │  │  ├─ Brunei
   │     │  │  │  ├─ Calcutta
   │     │  │  │  ├─ Chita
   │     │  │  │  ├─ Choibalsan
   │     │  │  │  ├─ Chongqing
   │     │  │  │  ├─ Chungking
   │     │  │  │  ├─ Colombo
   │     │  │  │  ├─ Dacca
   │     │  │  │  ├─ Damascus
   │     │  │  │  ├─ Dhaka
   │     │  │  │  ├─ Dili
   │     │  │  │  ├─ Dubai
   │     │  │  │  ├─ Dushanbe
   │     │  │  │  ├─ Famagusta
   │     │  │  │  ├─ Gaza
   │     │  │  │  ├─ Harbin
   │     │  │  │  ├─ Hebron
   │     │  │  │  ├─ Hong_Kong
   │     │  │  │  ├─ Hovd
   │     │  │  │  ├─ Ho_Chi_Minh
   │     │  │  │  ├─ Irkutsk
   │     │  │  │  ├─ Istanbul
   │     │  │  │  ├─ Jakarta
   │     │  │  │  ├─ Jayapura
   │     │  │  │  ├─ Jerusalem
   │     │  │  │  ├─ Kabul
   │     │  │  │  ├─ Kamchatka
   │     │  │  │  ├─ Karachi
   │     │  │  │  ├─ Kashgar
   │     │  │  │  ├─ Kathmandu
   │     │  │  │  ├─ Katmandu
   │     │  │  │  ├─ Khandyga
   │     │  │  │  ├─ Kolkata
   │     │  │  │  ├─ Krasnoyarsk
   │     │  │  │  ├─ Kuala_Lumpur
   │     │  │  │  ├─ Kuching
   │     │  │  │  ├─ Kuwait
   │     │  │  │  ├─ Macao
   │     │  │  │  ├─ Macau
   │     │  │  │  ├─ Magadan
   │     │  │  │  ├─ Makassar
   │     │  │  │  ├─ Manila
   │     │  │  │  ├─ Muscat
   │     │  │  │  ├─ Nicosia
   │     │  │  │  ├─ Novokuznetsk
   │     │  │  │  ├─ Novosibirsk
   │     │  │  │  ├─ Omsk
   │     │  │  │  ├─ Oral
   │     │  │  │  ├─ Phnom_Penh
   │     │  │  │  ├─ Pontianak
   │     │  │  │  ├─ Pyongyang
   │     │  │  │  ├─ Qatar
   │     │  │  │  ├─ Qostanay
   │     │  │  │  ├─ Qyzylorda
   │     │  │  │  ├─ Rangoon
   │     │  │  │  ├─ Riyadh
   │     │  │  │  ├─ Saigon
   │     │  │  │  ├─ Sakhalin
   │     │  │  │  ├─ Samarkand
   │     │  │  │  ├─ Seoul
   │     │  │  │  ├─ Shanghai
   │     │  │  │  ├─ Singapore
   │     │  │  │  ├─ Srednekolymsk
   │     │  │  │  ├─ Taipei
   │     │  │  │  ├─ Tashkent
   │     │  │  │  ├─ Tbilisi
   │     │  │  │  ├─ Tehran
   │     │  │  │  ├─ Tel_Aviv
   │     │  │  │  ├─ Thimbu
   │     │  │  │  ├─ Thimphu
   │     │  │  │  ├─ Tokyo
   │     │  │  │  ├─ Tomsk
   │     │  │  │  ├─ Ujung_Pandang
   │     │  │  │  ├─ Ulaanbaatar
   │     │  │  │  ├─ Ulan_Bator
   │     │  │  │  ├─ Urumqi
   │     │  │  │  ├─ Ust-Nera
   │     │  │  │  ├─ Vientiane
   │     │  │  │  ├─ Vladivostok
   │     │  │  │  ├─ Yakutsk
   │     │  │  │  ├─ Yangon
   │     │  │  │  ├─ Yekaterinburg
   │     │  │  │  ├─ Yerevan
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ Atlantic
   │     │  │  │  ├─ Azores
   │     │  │  │  ├─ Bermuda
   │     │  │  │  ├─ Canary
   │     │  │  │  ├─ Cape_Verde
   │     │  │  │  ├─ Faeroe
   │     │  │  │  ├─ Faroe
   │     │  │  │  ├─ Jan_Mayen
   │     │  │  │  ├─ Madeira
   │     │  │  │  ├─ Reykjavik
   │     │  │  │  ├─ South_Georgia
   │     │  │  │  ├─ Stanley
   │     │  │  │  ├─ St_Helena
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ Australia
   │     │  │  │  ├─ ACT
   │     │  │  │  ├─ Adelaide
   │     │  │  │  ├─ Brisbane
   │     │  │  │  ├─ Broken_Hill
   │     │  │  │  ├─ Canberra
   │     │  │  │  ├─ Currie
   │     │  │  │  ├─ Darwin
   │     │  │  │  ├─ Eucla
   │     │  │  │  ├─ Hobart
   │     │  │  │  ├─ LHI
   │     │  │  │  ├─ Lindeman
   │     │  │  │  ├─ Lord_Howe
   │     │  │  │  ├─ Melbourne
   │     │  │  │  ├─ North
   │     │  │  │  ├─ NSW
   │     │  │  │  ├─ Perth
   │     │  │  │  ├─ Queensland
   │     │  │  │  ├─ South
   │     │  │  │  ├─ Sydney
   │     │  │  │  ├─ Tasmania
   │     │  │  │  ├─ Victoria
   │     │  │  │  ├─ West
   │     │  │  │  ├─ Yancowinna
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ Brazil
   │     │  │  │  ├─ Acre
   │     │  │  │  ├─ DeNoronha
   │     │  │  │  ├─ East
   │     │  │  │  ├─ West
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ Canada
   │     │  │  │  ├─ Atlantic
   │     │  │  │  ├─ Central
   │     │  │  │  ├─ Eastern
   │     │  │  │  ├─ Mountain
   │     │  │  │  ├─ Newfoundland
   │     │  │  │  ├─ Pacific
   │     │  │  │  ├─ Saskatchewan
   │     │  │  │  ├─ Yukon
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ CET
   │     │  │  ├─ Chile
   │     │  │  │  ├─ Continental
   │     │  │  │  ├─ EasterIsland
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ CST6CDT
   │     │  │  ├─ Cuba
   │     │  │  ├─ EET
   │     │  │  ├─ Egypt
   │     │  │  ├─ Eire
   │     │  │  ├─ EST
   │     │  │  ├─ EST5EDT
   │     │  │  ├─ Etc
   │     │  │  │  ├─ GMT
   │     │  │  │  ├─ GMT+0
   │     │  │  │  ├─ GMT+1
   │     │  │  │  ├─ GMT+10
   │     │  │  │  ├─ GMT+11
   │     │  │  │  ├─ GMT+12
   │     │  │  │  ├─ GMT+2
   │     │  │  │  ├─ GMT+3
   │     │  │  │  ├─ GMT+4
   │     │  │  │  ├─ GMT+5
   │     │  │  │  ├─ GMT+6
   │     │  │  │  ├─ GMT+7
   │     │  │  │  ├─ GMT+8
   │     │  │  │  ├─ GMT+9
   │     │  │  │  ├─ GMT-0
   │     │  │  │  ├─ GMT-1
   │     │  │  │  ├─ GMT-10
   │     │  │  │  ├─ GMT-11
   │     │  │  │  ├─ GMT-12
   │     │  │  │  ├─ GMT-13
   │     │  │  │  ├─ GMT-14
   │     │  │  │  ├─ GMT-2
   │     │  │  │  ├─ GMT-3
   │     │  │  │  ├─ GMT-4
   │     │  │  │  ├─ GMT-5
   │     │  │  │  ├─ GMT-6
   │     │  │  │  ├─ GMT-7
   │     │  │  │  ├─ GMT-8
   │     │  │  │  ├─ GMT-9
   │     │  │  │  ├─ GMT0
   │     │  │  │  ├─ Greenwich
   │     │  │  │  ├─ UCT
   │     │  │  │  ├─ Universal
   │     │  │  │  ├─ UTC
   │     │  │  │  ├─ Zulu
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ Europe
   │     │  │  │  ├─ Amsterdam
   │     │  │  │  ├─ Andorra
   │     │  │  │  ├─ Astrakhan
   │     │  │  │  ├─ Athens
   │     │  │  │  ├─ Belfast
   │     │  │  │  ├─ Belgrade
   │     │  │  │  ├─ Berlin
   │     │  │  │  ├─ Bratislava
   │     │  │  │  ├─ Brussels
   │     │  │  │  ├─ Bucharest
   │     │  │  │  ├─ Budapest
   │     │  │  │  ├─ Busingen
   │     │  │  │  ├─ Chisinau
   │     │  │  │  ├─ Copenhagen
   │     │  │  │  ├─ Dublin
   │     │  │  │  ├─ Gibraltar
   │     │  │  │  ├─ Guernsey
   │     │  │  │  ├─ Helsinki
   │     │  │  │  ├─ Isle_of_Man
   │     │  │  │  ├─ Istanbul
   │     │  │  │  ├─ Jersey
   │     │  │  │  ├─ Kaliningrad
   │     │  │  │  ├─ Kiev
   │     │  │  │  ├─ Kirov
   │     │  │  │  ├─ Kyiv
   │     │  │  │  ├─ Lisbon
   │     │  │  │  ├─ Ljubljana
   │     │  │  │  ├─ London
   │     │  │  │  ├─ Luxembourg
   │     │  │  │  ├─ Madrid
   │     │  │  │  ├─ Malta
   │     │  │  │  ├─ Mariehamn
   │     │  │  │  ├─ Minsk
   │     │  │  │  ├─ Monaco
   │     │  │  │  ├─ Moscow
   │     │  │  │  ├─ Nicosia
   │     │  │  │  ├─ Oslo
   │     │  │  │  ├─ Paris
   │     │  │  │  ├─ Podgorica
   │     │  │  │  ├─ Prague
   │     │  │  │  ├─ Riga
   │     │  │  │  ├─ Rome
   │     │  │  │  ├─ Samara
   │     │  │  │  ├─ San_Marino
   │     │  │  │  ├─ Sarajevo
   │     │  │  │  ├─ Saratov
   │     │  │  │  ├─ Simferopol
   │     │  │  │  ├─ Skopje
   │     │  │  │  ├─ Sofia
   │     │  │  │  ├─ Stockholm
   │     │  │  │  ├─ Tallinn
   │     │  │  │  ├─ Tirane
   │     │  │  │  ├─ Tiraspol
   │     │  │  │  ├─ Ulyanovsk
   │     │  │  │  ├─ Uzhgorod
   │     │  │  │  ├─ Vaduz
   │     │  │  │  ├─ Vatican
   │     │  │  │  ├─ Vienna
   │     │  │  │  ├─ Vilnius
   │     │  │  │  ├─ Volgograd
   │     │  │  │  ├─ Warsaw
   │     │  │  │  ├─ Zagreb
   │     │  │  │  ├─ Zaporozhye
   │     │  │  │  ├─ Zurich
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ Factory
   │     │  │  ├─ GB
   │     │  │  ├─ GB-Eire
   │     │  │  ├─ GMT
   │     │  │  ├─ GMT+0
   │     │  │  ├─ GMT-0
   │     │  │  ├─ GMT0
   │     │  │  ├─ Greenwich
   │     │  │  ├─ Hongkong
   │     │  │  ├─ HST
   │     │  │  ├─ Iceland
   │     │  │  ├─ Indian
   │     │  │  │  ├─ Antananarivo
   │     │  │  │  ├─ Chagos
   │     │  │  │  ├─ Christmas
   │     │  │  │  ├─ Cocos
   │     │  │  │  ├─ Comoro
   │     │  │  │  ├─ Kerguelen
   │     │  │  │  ├─ Mahe
   │     │  │  │  ├─ Maldives
   │     │  │  │  ├─ Mauritius
   │     │  │  │  ├─ Mayotte
   │     │  │  │  ├─ Reunion
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ Iran
   │     │  │  ├─ iso3166.tab
   │     │  │  ├─ Israel
   │     │  │  ├─ Jamaica
   │     │  │  ├─ Japan
   │     │  │  ├─ Kwajalein
   │     │  │  ├─ leapseconds
   │     │  │  ├─ Libya
   │     │  │  ├─ MET
   │     │  │  ├─ Mexico
   │     │  │  │  ├─ BajaNorte
   │     │  │  │  ├─ BajaSur
   │     │  │  │  ├─ General
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ MST
   │     │  │  ├─ MST7MDT
   │     │  │  ├─ Navajo
   │     │  │  ├─ NZ
   │     │  │  ├─ NZ-CHAT
   │     │  │  ├─ Pacific
   │     │  │  │  ├─ Apia
   │     │  │  │  ├─ Auckland
   │     │  │  │  ├─ Bougainville
   │     │  │  │  ├─ Chatham
   │     │  │  │  ├─ Chuuk
   │     │  │  │  ├─ Easter
   │     │  │  │  ├─ Efate
   │     │  │  │  ├─ Enderbury
   │     │  │  │  ├─ Fakaofo
   │     │  │  │  ├─ Fiji
   │     │  │  │  ├─ Funafuti
   │     │  │  │  ├─ Galapagos
   │     │  │  │  ├─ Gambier
   │     │  │  │  ├─ Guadalcanal
   │     │  │  │  ├─ Guam
   │     │  │  │  ├─ Honolulu
   │     │  │  │  ├─ Johnston
   │     │  │  │  ├─ Kanton
   │     │  │  │  ├─ Kiritimati
   │     │  │  │  ├─ Kosrae
   │     │  │  │  ├─ Kwajalein
   │     │  │  │  ├─ Majuro
   │     │  │  │  ├─ Marquesas
   │     │  │  │  ├─ Midway
   │     │  │  │  ├─ Nauru
   │     │  │  │  ├─ Niue
   │     │  │  │  ├─ Norfolk
   │     │  │  │  ├─ Noumea
   │     │  │  │  ├─ Pago_Pago
   │     │  │  │  ├─ Palau
   │     │  │  │  ├─ Pitcairn
   │     │  │  │  ├─ Pohnpei
   │     │  │  │  ├─ Ponape
   │     │  │  │  ├─ Port_Moresby
   │     │  │  │  ├─ Rarotonga
   │     │  │  │  ├─ Saipan
   │     │  │  │  ├─ Samoa
   │     │  │  │  ├─ Tahiti
   │     │  │  │  ├─ Tarawa
   │     │  │  │  ├─ Tongatapu
   │     │  │  │  ├─ Truk
   │     │  │  │  ├─ Wake
   │     │  │  │  ├─ Wallis
   │     │  │  │  ├─ Yap
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ Poland
   │     │  │  ├─ Portugal
   │     │  │  ├─ PRC
   │     │  │  ├─ PST8PDT
   │     │  │  ├─ ROC
   │     │  │  ├─ ROK
   │     │  │  ├─ Singapore
   │     │  │  ├─ Turkey
   │     │  │  ├─ tzdata.zi
   │     │  │  ├─ UCT
   │     │  │  ├─ Universal
   │     │  │  ├─ US
   │     │  │  │  ├─ Alaska
   │     │  │  │  ├─ Aleutian
   │     │  │  │  ├─ Arizona
   │     │  │  │  ├─ Central
   │     │  │  │  ├─ East-Indiana
   │     │  │  │  ├─ Eastern
   │     │  │  │  ├─ Hawaii
   │     │  │  │  ├─ Indiana-Starke
   │     │  │  │  ├─ Michigan
   │     │  │  │  ├─ Mountain
   │     │  │  │  ├─ Pacific
   │     │  │  │  ├─ Samoa
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ UTC
   │     │  │  ├─ W-SU
   │     │  │  ├─ WET
   │     │  │  ├─ zone.tab
   │     │  │  ├─ zone1970.tab
   │     │  │  ├─ zonenow.tab
   │     │  │  ├─ Zulu
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ zones
   │     │  ├─ __init__.py
   │     │  └─ __pycache__
   │     │     └─ __init__.cpython-311.pyc
   │     ├─ tzdata-2026.1.dist-info
   │     │  ├─ INSTALLER
   │     │  ├─ licenses
   │     │  │  ├─ LICENSE
   │     │  │  └─ licenses
   │     │  │     └─ LICENSE_APACHE
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  ├─ top_level.txt
   │     │  └─ WHEEL
   │     ├─ urllib3
   │     │  ├─ connection.py
   │     │  ├─ connectionpool.py
   │     │  ├─ contrib
   │     │  │  ├─ emscripten
   │     │  │  │  ├─ connection.py
   │     │  │  │  ├─ emscripten_fetch_worker.js
   │     │  │  │  ├─ fetch.py
   │     │  │  │  ├─ request.py
   │     │  │  │  ├─ response.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ connection.cpython-311.pyc
   │     │  │  │     ├─ fetch.cpython-311.pyc
   │     │  │  │     ├─ request.cpython-311.pyc
   │     │  │  │     ├─ response.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ pyopenssl.py
   │     │  │  ├─ socks.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ pyopenssl.cpython-311.pyc
   │     │  │     ├─ socks.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ exceptions.py
   │     │  ├─ fields.py
   │     │  ├─ filepost.py
   │     │  ├─ http2
   │     │  │  ├─ connection.py
   │     │  │  ├─ probe.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ connection.cpython-311.pyc
   │     │  │     ├─ probe.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ poolmanager.py
   │     │  ├─ py.typed
   │     │  ├─ response.py
   │     │  ├─ util
   │     │  │  ├─ connection.py
   │     │  │  ├─ proxy.py
   │     │  │  ├─ request.py
   │     │  │  ├─ response.py
   │     │  │  ├─ retry.py
   │     │  │  ├─ ssltransport.py
   │     │  │  ├─ ssl_.py
   │     │  │  ├─ ssl_match_hostname.py
   │     │  │  ├─ timeout.py
   │     │  │  ├─ url.py
   │     │  │  ├─ util.py
   │     │  │  ├─ wait.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ connection.cpython-311.pyc
   │     │  │     ├─ proxy.cpython-311.pyc
   │     │  │     ├─ request.cpython-311.pyc
   │     │  │     ├─ response.cpython-311.pyc
   │     │  │     ├─ retry.cpython-311.pyc
   │     │  │     ├─ ssltransport.cpython-311.pyc
   │     │  │     ├─ ssl_.cpython-311.pyc
   │     │  │     ├─ ssl_match_hostname.cpython-311.pyc
   │     │  │     ├─ timeout.cpython-311.pyc
   │     │  │     ├─ url.cpython-311.pyc
   │     │  │     ├─ util.cpython-311.pyc
   │     │  │     ├─ wait.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ _base_connection.py
   │     │  ├─ _collections.py
   │     │  ├─ _request_methods.py
   │     │  ├─ _version.py
   │     │  ├─ __init__.py
   │     │  └─ __pycache__
   │     │     ├─ connection.cpython-311.pyc
   │     │     ├─ connectionpool.cpython-311.pyc
   │     │     ├─ exceptions.cpython-311.pyc
   │     │     ├─ fields.cpython-311.pyc
   │     │     ├─ filepost.cpython-311.pyc
   │     │     ├─ poolmanager.cpython-311.pyc
   │     │     ├─ response.cpython-311.pyc
   │     │     ├─ _base_connection.cpython-311.pyc
   │     │     ├─ _collections.cpython-311.pyc
   │     │     ├─ _request_methods.cpython-311.pyc
   │     │     ├─ _version.cpython-311.pyc
   │     │     └─ __init__.cpython-311.pyc
   │     ├─ urllib3-2.6.3.dist-info
   │     │  ├─ INSTALLER
   │     │  ├─ licenses
   │     │  │  └─ LICENSE.txt
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  └─ WHEEL
   │     ├─ uvicorn
   │     │  ├─ config.py
   │     │  ├─ importer.py
   │     │  ├─ lifespan
   │     │  │  ├─ off.py
   │     │  │  ├─ on.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ off.cpython-311.pyc
   │     │  │     ├─ on.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ logging.py
   │     │  ├─ loops
   │     │  │  ├─ asyncio.py
   │     │  │  ├─ auto.py
   │     │  │  ├─ uvloop.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ asyncio.cpython-311.pyc
   │     │  │     ├─ auto.cpython-311.pyc
   │     │  │     ├─ uvloop.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ main.py
   │     │  ├─ middleware
   │     │  │  ├─ asgi2.py
   │     │  │  ├─ message_logger.py
   │     │  │  ├─ proxy_headers.py
   │     │  │  ├─ wsgi.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ asgi2.cpython-311.pyc
   │     │  │     ├─ message_logger.cpython-311.pyc
   │     │  │     ├─ proxy_headers.cpython-311.pyc
   │     │  │     ├─ wsgi.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ protocols
   │     │  │  ├─ http
   │     │  │  │  ├─ auto.py
   │     │  │  │  ├─ flow_control.py
   │     │  │  │  ├─ h11_impl.py
   │     │  │  │  ├─ httptools_impl.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ auto.cpython-311.pyc
   │     │  │  │     ├─ flow_control.cpython-311.pyc
   │     │  │  │     ├─ h11_impl.cpython-311.pyc
   │     │  │  │     ├─ httptools_impl.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ utils.py
   │     │  │  ├─ websockets
   │     │  │  │  ├─ auto.py
   │     │  │  │  ├─ websockets_impl.py
   │     │  │  │  ├─ websockets_sansio_impl.py
   │     │  │  │  ├─ wsproto_impl.py
   │     │  │  │  ├─ __init__.py
   │     │  │  │  └─ __pycache__
   │     │  │  │     ├─ auto.cpython-311.pyc
   │     │  │  │     ├─ websockets_impl.cpython-311.pyc
   │     │  │  │     ├─ websockets_sansio_impl.cpython-311.pyc
   │     │  │  │     ├─ wsproto_impl.cpython-311.pyc
   │     │  │  │     └─ __init__.cpython-311.pyc
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ utils.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ py.typed
   │     │  ├─ server.py
   │     │  ├─ supervisors
   │     │  │  ├─ basereload.py
   │     │  │  ├─ multiprocess.py
   │     │  │  ├─ statreload.py
   │     │  │  ├─ watchfilesreload.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ basereload.cpython-311.pyc
   │     │  │     ├─ multiprocess.cpython-311.pyc
   │     │  │     ├─ statreload.cpython-311.pyc
   │     │  │     ├─ watchfilesreload.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ workers.py
   │     │  ├─ _compat.py
   │     │  ├─ _subprocess.py
   │     │  ├─ _types.py
   │     │  ├─ __init__.py
   │     │  ├─ __main__.py
   │     │  └─ __pycache__
   │     │     ├─ config.cpython-311.pyc
   │     │     ├─ importer.cpython-311.pyc
   │     │     ├─ logging.cpython-311.pyc
   │     │     ├─ main.cpython-311.pyc
   │     │     ├─ server.cpython-311.pyc
   │     │     ├─ workers.cpython-311.pyc
   │     │     ├─ _compat.cpython-311.pyc
   │     │     ├─ _subprocess.cpython-311.pyc
   │     │     ├─ _types.cpython-311.pyc
   │     │     ├─ __init__.cpython-311.pyc
   │     │     └─ __main__.cpython-311.pyc
   │     ├─ uvicorn-0.44.0.dist-info
   │     │  ├─ entry_points.txt
   │     │  ├─ INSTALLER
   │     │  ├─ licenses
   │     │  │  └─ LICENSE.md
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  └─ WHEEL
   │     ├─ watchdog
   │     │  ├─ events.py
   │     │  ├─ observers
   │     │  │  ├─ api.py
   │     │  │  ├─ fsevents.py
   │     │  │  ├─ fsevents2.py
   │     │  │  ├─ inotify.py
   │     │  │  ├─ inotify_buffer.py
   │     │  │  ├─ inotify_c.py
   │     │  │  ├─ kqueue.py
   │     │  │  ├─ polling.py
   │     │  │  ├─ read_directory_changes.py
   │     │  │  ├─ winapi.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ api.cpython-311.pyc
   │     │  │     ├─ fsevents.cpython-311.pyc
   │     │  │     ├─ fsevents2.cpython-311.pyc
   │     │  │     ├─ inotify.cpython-311.pyc
   │     │  │     ├─ inotify_buffer.cpython-311.pyc
   │     │  │     ├─ inotify_c.cpython-311.pyc
   │     │  │     ├─ kqueue.cpython-311.pyc
   │     │  │     ├─ polling.cpython-311.pyc
   │     │  │     ├─ read_directory_changes.cpython-311.pyc
   │     │  │     ├─ winapi.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ py.typed
   │     │  ├─ tricks
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ utils
   │     │  │  ├─ bricks.py
   │     │  │  ├─ delayed_queue.py
   │     │  │  ├─ dirsnapshot.py
   │     │  │  ├─ echo.py
   │     │  │  ├─ event_debouncer.py
   │     │  │  ├─ patterns.py
   │     │  │  ├─ platform.py
   │     │  │  ├─ process_watcher.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ bricks.cpython-311.pyc
   │     │  │     ├─ delayed_queue.cpython-311.pyc
   │     │  │     ├─ dirsnapshot.cpython-311.pyc
   │     │  │     ├─ echo.cpython-311.pyc
   │     │  │     ├─ event_debouncer.cpython-311.pyc
   │     │  │     ├─ patterns.cpython-311.pyc
   │     │  │     ├─ platform.cpython-311.pyc
   │     │  │     ├─ process_watcher.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ version.py
   │     │  ├─ watchmedo.py
   │     │  ├─ __init__.py
   │     │  └─ __pycache__
   │     │     ├─ events.cpython-311.pyc
   │     │     ├─ version.cpython-311.pyc
   │     │     ├─ watchmedo.cpython-311.pyc
   │     │     └─ __init__.cpython-311.pyc
   │     ├─ watchdog-6.0.0.dist-info
   │     │  ├─ AUTHORS
   │     │  ├─ COPYING
   │     │  ├─ entry_points.txt
   │     │  ├─ INSTALLER
   │     │  ├─ LICENSE
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  ├─ top_level.txt
   │     │  └─ WHEEL
   │     ├─ watchfiles
   │     │  ├─ cli.py
   │     │  ├─ filters.py
   │     │  ├─ main.py
   │     │  ├─ py.typed
   │     │  ├─ run.py
   │     │  ├─ version.py
   │     │  ├─ _rust_notify.cp311-win_amd64.pyd
   │     │  ├─ _rust_notify.pyi
   │     │  ├─ __init__.py
   │     │  ├─ __main__.py
   │     │  └─ __pycache__
   │     │     ├─ cli.cpython-311.pyc
   │     │     ├─ filters.cpython-311.pyc
   │     │     ├─ main.cpython-311.pyc
   │     │     ├─ run.cpython-311.pyc
   │     │     ├─ version.cpython-311.pyc
   │     │     ├─ __init__.cpython-311.pyc
   │     │     └─ __main__.cpython-311.pyc
   │     ├─ watchfiles-1.1.1.dist-info
   │     │  ├─ entry_points.txt
   │     │  ├─ INSTALLER
   │     │  ├─ licenses
   │     │  │  └─ LICENSE
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  └─ WHEEL
   │     ├─ websocket
   │     │  ├─ py.typed
   │     │  ├─ tests
   │     │  │  ├─ data
   │     │  │  │  ├─ header01.txt
   │     │  │  │  ├─ header02.txt
   │     │  │  │  └─ header03.txt
   │     │  │  ├─ echo-server.py
   │     │  │  ├─ test_abnf.py
   │     │  │  ├─ test_app.py
   │     │  │  ├─ test_cookiejar.py
   │     │  │  ├─ test_dispatcher.py
   │     │  │  ├─ test_handshake_large_response.py
   │     │  │  ├─ test_http.py
   │     │  │  ├─ test_large_payloads.py
   │     │  │  ├─ test_socket.py
   │     │  │  ├─ test_socket_bugs.py
   │     │  │  ├─ test_ssl_compat.py
   │     │  │  ├─ test_ssl_edge_cases.py
   │     │  │  ├─ test_url.py
   │     │  │  ├─ test_utils.py
   │     │  │  ├─ test_websocket.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ echo-server.cpython-311.pyc
   │     │  │     ├─ test_abnf.cpython-311.pyc
   │     │  │     ├─ test_app.cpython-311.pyc
   │     │  │     ├─ test_cookiejar.cpython-311.pyc
   │     │  │     ├─ test_dispatcher.cpython-311.pyc
   │     │  │     ├─ test_handshake_large_response.cpython-311.pyc
   │     │  │     ├─ test_http.cpython-311.pyc
   │     │  │     ├─ test_large_payloads.cpython-311.pyc
   │     │  │     ├─ test_socket.cpython-311.pyc
   │     │  │     ├─ test_socket_bugs.cpython-311.pyc
   │     │  │     ├─ test_ssl_compat.cpython-311.pyc
   │     │  │     ├─ test_ssl_edge_cases.cpython-311.pyc
   │     │  │     ├─ test_url.cpython-311.pyc
   │     │  │     ├─ test_utils.cpython-311.pyc
   │     │  │     ├─ test_websocket.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ _abnf.py
   │     │  ├─ _app.py
   │     │  ├─ _cookiejar.py
   │     │  ├─ _core.py
   │     │  ├─ _dispatcher.py
   │     │  ├─ _exceptions.py
   │     │  ├─ _handshake.py
   │     │  ├─ _http.py
   │     │  ├─ _logging.py
   │     │  ├─ _socket.py
   │     │  ├─ _ssl_compat.py
   │     │  ├─ _url.py
   │     │  ├─ _utils.py
   │     │  ├─ _wsdump.py
   │     │  ├─ __init__.py
   │     │  └─ __pycache__
   │     │     ├─ _abnf.cpython-311.pyc
   │     │     ├─ _app.cpython-311.pyc
   │     │     ├─ _cookiejar.cpython-311.pyc
   │     │     ├─ _core.cpython-311.pyc
   │     │     ├─ _dispatcher.cpython-311.pyc
   │     │     ├─ _exceptions.cpython-311.pyc
   │     │     ├─ _handshake.cpython-311.pyc
   │     │     ├─ _http.cpython-311.pyc
   │     │     ├─ _logging.cpython-311.pyc
   │     │     ├─ _socket.cpython-311.pyc
   │     │     ├─ _ssl_compat.cpython-311.pyc
   │     │     ├─ _url.cpython-311.pyc
   │     │     ├─ _utils.cpython-311.pyc
   │     │     ├─ _wsdump.cpython-311.pyc
   │     │     └─ __init__.cpython-311.pyc
   │     ├─ websockets
   │     │  ├─ asyncio
   │     │  │  ├─ async_timeout.py
   │     │  │  ├─ client.py
   │     │  │  ├─ compatibility.py
   │     │  │  ├─ connection.py
   │     │  │  ├─ messages.py
   │     │  │  ├─ router.py
   │     │  │  ├─ server.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ async_timeout.cpython-311.pyc
   │     │  │     ├─ client.cpython-311.pyc
   │     │  │     ├─ compatibility.cpython-311.pyc
   │     │  │     ├─ connection.cpython-311.pyc
   │     │  │     ├─ messages.cpython-311.pyc
   │     │  │     ├─ router.cpython-311.pyc
   │     │  │     ├─ server.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ auth.py
   │     │  ├─ cli.py
   │     │  ├─ client.py
   │     │  ├─ connection.py
   │     │  ├─ datastructures.py
   │     │  ├─ exceptions.py
   │     │  ├─ extensions
   │     │  │  ├─ base.py
   │     │  │  ├─ permessage_deflate.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ base.cpython-311.pyc
   │     │  │     ├─ permessage_deflate.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ frames.py
   │     │  ├─ headers.py
   │     │  ├─ http.py
   │     │  ├─ http11.py
   │     │  ├─ imports.py
   │     │  ├─ legacy
   │     │  │  ├─ auth.py
   │     │  │  ├─ client.py
   │     │  │  ├─ exceptions.py
   │     │  │  ├─ framing.py
   │     │  │  ├─ handshake.py
   │     │  │  ├─ http.py
   │     │  │  ├─ protocol.py
   │     │  │  ├─ server.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ auth.cpython-311.pyc
   │     │  │     ├─ client.cpython-311.pyc
   │     │  │     ├─ exceptions.cpython-311.pyc
   │     │  │     ├─ framing.cpython-311.pyc
   │     │  │     ├─ handshake.cpython-311.pyc
   │     │  │     ├─ http.cpython-311.pyc
   │     │  │     ├─ protocol.cpython-311.pyc
   │     │  │     ├─ server.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ protocol.py
   │     │  ├─ proxy.py
   │     │  ├─ py.typed
   │     │  ├─ server.py
   │     │  ├─ speedups.c
   │     │  ├─ speedups.cp311-win_amd64.pyd
   │     │  ├─ speedups.pyi
   │     │  ├─ streams.py
   │     │  ├─ sync
   │     │  │  ├─ client.py
   │     │  │  ├─ connection.py
   │     │  │  ├─ messages.py
   │     │  │  ├─ router.py
   │     │  │  ├─ server.py
   │     │  │  ├─ utils.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ client.cpython-311.pyc
   │     │  │     ├─ connection.cpython-311.pyc
   │     │  │     ├─ messages.cpython-311.pyc
   │     │  │     ├─ router.cpython-311.pyc
   │     │  │     ├─ server.cpython-311.pyc
   │     │  │     ├─ utils.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ typing.py
   │     │  ├─ uri.py
   │     │  ├─ utils.py
   │     │  ├─ version.py
   │     │  ├─ __init__.py
   │     │  ├─ __main__.py
   │     │  └─ __pycache__
   │     │     ├─ auth.cpython-311.pyc
   │     │     ├─ cli.cpython-311.pyc
   │     │     ├─ client.cpython-311.pyc
   │     │     ├─ connection.cpython-311.pyc
   │     │     ├─ datastructures.cpython-311.pyc
   │     │     ├─ exceptions.cpython-311.pyc
   │     │     ├─ frames.cpython-311.pyc
   │     │     ├─ headers.cpython-311.pyc
   │     │     ├─ http.cpython-311.pyc
   │     │     ├─ http11.cpython-311.pyc
   │     │     ├─ imports.cpython-311.pyc
   │     │     ├─ protocol.cpython-311.pyc
   │     │     ├─ proxy.cpython-311.pyc
   │     │     ├─ server.cpython-311.pyc
   │     │     ├─ streams.cpython-311.pyc
   │     │     ├─ typing.cpython-311.pyc
   │     │     ├─ uri.cpython-311.pyc
   │     │     ├─ utils.cpython-311.pyc
   │     │     ├─ version.cpython-311.pyc
   │     │     ├─ __init__.cpython-311.pyc
   │     │     └─ __main__.cpython-311.pyc
   │     ├─ websockets-16.0.dist-info
   │     │  ├─ entry_points.txt
   │     │  ├─ INSTALLER
   │     │  ├─ licenses
   │     │  │  └─ LICENSE
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  ├─ top_level.txt
   │     │  └─ WHEEL
   │     ├─ websocket_client-1.9.0.dist-info
   │     │  ├─ entry_points.txt
   │     │  ├─ INSTALLER
   │     │  ├─ licenses
   │     │  │  └─ LICENSE
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  ├─ top_level.txt
   │     │  └─ WHEEL
   │     ├─ yaml
   │     │  ├─ composer.py
   │     │  ├─ constructor.py
   │     │  ├─ cyaml.py
   │     │  ├─ dumper.py
   │     │  ├─ emitter.py
   │     │  ├─ error.py
   │     │  ├─ events.py
   │     │  ├─ loader.py
   │     │  ├─ nodes.py
   │     │  ├─ parser.py
   │     │  ├─ reader.py
   │     │  ├─ representer.py
   │     │  ├─ resolver.py
   │     │  ├─ scanner.py
   │     │  ├─ serializer.py
   │     │  ├─ tokens.py
   │     │  ├─ _yaml.cp311-win_amd64.pyd
   │     │  ├─ __init__.py
   │     │  └─ __pycache__
   │     │     ├─ composer.cpython-311.pyc
   │     │     ├─ constructor.cpython-311.pyc
   │     │     ├─ cyaml.cpython-311.pyc
   │     │     ├─ dumper.cpython-311.pyc
   │     │     ├─ emitter.cpython-311.pyc
   │     │     ├─ error.cpython-311.pyc
   │     │     ├─ events.cpython-311.pyc
   │     │     ├─ loader.cpython-311.pyc
   │     │     ├─ nodes.cpython-311.pyc
   │     │     ├─ parser.cpython-311.pyc
   │     │     ├─ reader.cpython-311.pyc
   │     │     ├─ representer.cpython-311.pyc
   │     │     ├─ resolver.cpython-311.pyc
   │     │     ├─ scanner.cpython-311.pyc
   │     │     ├─ serializer.cpython-311.pyc
   │     │     ├─ tokens.cpython-311.pyc
   │     │     └─ __init__.cpython-311.pyc
   │     ├─ zipp
   │     │  ├─ compat
   │     │  │  ├─ overlay.py
   │     │  │  ├─ py310.py
   │     │  │  ├─ py313.py
   │     │  │  ├─ __init__.py
   │     │  │  └─ __pycache__
   │     │  │     ├─ overlay.cpython-311.pyc
   │     │  │     ├─ py310.cpython-311.pyc
   │     │  │     ├─ py313.cpython-311.pyc
   │     │  │     └─ __init__.cpython-311.pyc
   │     │  ├─ glob.py
   │     │  ├─ _functools.py
   │     │  ├─ __init__.py
   │     │  └─ __pycache__
   │     │     ├─ glob.cpython-311.pyc
   │     │     ├─ _functools.cpython-311.pyc
   │     │     └─ __init__.cpython-311.pyc
   │     ├─ zipp-3.23.0.dist-info
   │     │  ├─ INSTALLER
   │     │  ├─ licenses
   │     │  │  └─ LICENSE
   │     │  ├─ METADATA
   │     │  ├─ RECORD
   │     │  ├─ top_level.txt
   │     │  └─ WHEEL
   │     ├─ _distutils_hack
   │     │  ├─ override.py
   │     │  ├─ __init__.py
   │     │  └─ __pycache__
   │     │     ├─ override.cpython-311.pyc
   │     │     └─ __init__.cpython-311.pyc
   │     ├─ _yaml
   │     │  ├─ __init__.py
   │     │  └─ __pycache__
   │     │     └─ __init__.cpython-311.pyc
   │     └─ __pycache__
   │        ├─ isympy.cpython-311.pyc
   │        ├─ six.cpython-311.pyc
   │        └─ typing_extensions.cpython-311.pyc
   ├─ pyvenv.cfg
   ├─ Scripts
   │  ├─ activate
   │  ├─ activate.bat
   │  ├─ Activate.ps1
   │  ├─ chroma.exe
   │  ├─ deactivate.bat
   │  ├─ distro.exe
   │  ├─ dotenv.exe
   │  ├─ f2py.exe
   │  ├─ hf.exe
   │  ├─ httpx.exe
   │  ├─ huggingface-cli.exe
   │  ├─ isympy.exe
   │  ├─ jsonschema.exe
   │  ├─ markdown-it.exe
   │  ├─ normalizer.exe
   │  ├─ numpy-config.exe
   │  ├─ onnxruntime_test.exe
   │  ├─ pip.exe
   │  ├─ pip3.11.exe
   │  ├─ pip3.exe
   │  ├─ pybase64.exe
   │  ├─ pygmentize.exe
   │  ├─ pyproject-build.exe
   │  ├─ python.exe
   │  ├─ pythonw.exe
   │  ├─ streamlit.exe
   │  ├─ tiny-agents.exe
   │  ├─ tqdm.exe
   │  ├─ typer.exe
   │  ├─ uvicorn.exe
   │  ├─ watchfiles.exe
   │  ├─ watchmedo.exe
   │  ├─ websockets.exe
   │  └─ wsdump.exe
   └─ share
      ├─ jupyter
      │  └─ nbextensions
      │     └─ pydeck
      │        ├─ extensionRequires.js
      │        ├─ index.js
      │        └─ index.js.map
      └─ man
         └─ man1
            └─ isympy.1

```