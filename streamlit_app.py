"""Codify — single top-to-bottom flow Streamlit application."""

from __future__ import annotations

import logging

import streamlit as st

from src.app.config import get_settings
from src.app.models.assignment import Assignment
from src.app.models.evaluation import EvaluationReport, SkillVerdict
from src.app.models.micro_skill import CheckType, MicroSkill, SkillStatus
from src.app.repositories.assignment_repository import (
    list_assignments,
    save_assignment,
)
from src.app.repositories.micro_skill_repository import (
    load_approved_skills,
    load_skill_review_state,
    save_skill_review_state,
    update_single_skill_status,
)
from src.app.repositories.vector_store_repository import (
    retrieve_approved_skills,
    save_approved_skills,
    COLLECTION_NAME,
)
from src.app.services.evaluation_service import evaluate_submission
from src.app.services.skill_generation_service import generate_candidate_skills

logger = logging.getLogger(__name__)

PAGE_TITLE = "Codify — Feedback Evaluation Platform"
PAGE_ICON = "🎓"
SUPPORTED_LANGUAGES = ["python", "c", "java", "javascript", "cpp"]
MIN_CODE_LENGTH = 10
MIN_APPROVED_SKILLS = 1

CHECK_TYPE_ORDER: dict[str, int] = {
    CheckType.SYNTAX.value: 0,
    CheckType.INPUT_OUTPUT.value: 1,
    CheckType.LOGIC.value: 2,
}

# ── example presets ───────────────────────────────────────────────────────────

EXAMPLE_ASSIGNMENTS: dict[str, dict] = {
    "🇨 Array Left Shift (C)": {
        "id": "array-left-shift-c",
        "title": "Array Left Shift",
        "language": "c",
        "description": (
            "Write a C program that reads 5 integers into an array, "
            "shifts all elements one position to the left, "
            "and places the first element at the end. "
            "Print the resulting array enclosed in curly braces.\n\n"
            "Example:\n"
            "Input : 1 2 3 4 5\n"
            "Output: {2, 3, 4, 5, 1}"
        ),
        "starter_code": (
            "#include <stdio.h>\n\n"
            "int main() {\n\n"
            "    int arr[5];\n\n"
            "    // 1. Input array\n\n"
            "    // 2. Shift elements to the left\n\n"
            "    // 3. Output result\n\n"
            "    return 0;\n"
            "}"
        ),
        "test_cases": (
            "Input: 1 2 3 4 5 -> Output: {2, 3, 4, 5, 1}\n"
            "Input: 5 4 3 2 1 -> Output: {4, 3, 2, 1, 5}"
        ),
    },
    "🐍 FizzBuzz (Python)": {
        "id": "fizzbuzz-python",
        "title": "FizzBuzz",
        "language": "python",
        "description": (
            "Write a Python program that prints numbers from 1 to 20.\n"
            "For multiples of 3 print 'Fizz'.\n"
            "For multiples of 5 print 'Buzz'.\n"
            "For multiples of both 3 and 5 print 'FizzBuzz'.\n\n"
            "Example output:\n"
            "1\n2\nFizz\n4\nBuzz\nFizz\n7\n8\nFizz\nBuzz\n..."
        ),
        "starter_code": (
            "# FizzBuzz\n\n"
            "for i in range(1, 21):\n"
            "    # Your logic here\n"
            "    pass"
        ),
        "test_cases": (
            "i=3 -> Fizz\n"
            "i=5 -> Buzz\n"
            "i=15 -> FizzBuzz\n"
            "i=1 -> 1"
        ),
    },
}

EXAMPLE_STUDENT_CODES: dict[str, str] = {
    "🇨 Array Left Shift — Wrong": (
        "#include <stdio.h>\n\n"
        "int main() {\n"
        "    int arr[5];\n"
        "    int i;\n\n"
        "    printf(\"Enter 5 numbers:\\n\");\n"
        "    for(i = 0; i < 5; i++) {\n"
        "        scanf(\"%d\", &arr[i]);\n"
        "    }\n\n"
        "    for(i = 1; i < 5; i++) {\n"
        "        arr[i - 1] = arr[i];\n"
        "    }\n"
        "    arr[4] = arr[0];\n\n"
        "    printf(\"{\");\n"
        "    for(i = 0; i < 5; i++) {\n"
        "        printf(\"%d\", arr[i]);\n"
        "        if(i < 4) printf(\", \");\n"
        "    }\n"
        "    printf(\"}\");\n\n"
        "    return 0;\n"
        "}"
    ),
    "🐍 FizzBuzz — Wrong": (
        "# FizzBuzz — missing combined case\n\n"
        "for i in range(1, 21):\n"
        "    if i % 3 == 0:\n"
        "        print('Fizz')\n"
        "    elif i % 5 == 0:\n"
        "        print('Buzz')\n"
        "    else:\n"
        "        print(i)\n"
    ),
}


@st.cache_resource
def _get_cached_chroma_client(chroma_path: str) -> "chromadb.PersistentClient":
    """Return a cached ChromaDB client shared across all Streamlit reruns.

    Caching ensures only one SQLite connection exists at a time,
    which allows us to call .reset() on the exact instance holding
    the file lock before deletion — fixing WinError 32 on Windows.

    Args:
        chroma_path: Path to ChromaDB embedded storage directory.

    Returns:
        chromadb.PersistentClient: Shared persistent client instance.
    """
    import chromadb
    return chromadb.PersistentClient(path=chroma_path)

# ── line-numbered code renderer ───────────────────────────────────────────────

def _render_line_numbered_code(
    code: str,
    language: str = "c",
    start_line: int = 1,
) -> None:
    """Render code with VSCode-style line numbers starting at `start_line`.

    Args:
        code: The code string to render.
        language: Programming language label shown in the header bar.
        start_line: The line number for the first line of the snippet.

    Time complexity: O(n) where n = number of lines
    Space complexity: O(n)
    """
    import html as html_module

    lines = code.split("\n")  # Preserve trailing empty lines if any

    gutter_rows = "".join(
        f'<div class="line-number">{start_line + i}</div>'
        for i in range(len(lines))
    )
    code_rows = "".join(
        f'<div class="code-line">{html_module.escape(line) if line else "&nbsp;"}</div>'
        for line in lines
    )

    html_block = f"""
    <div class="code-wrapper">
        <div class="code-header">
            <span class="lang-label">{language}</span>
        </div>
        <div class="code-body">
            <div class="gutter">{gutter_rows}</div>
            <div class="code-content">{code_rows}</div>
        </div>
    </div>
    <style>
        .code-wrapper {{
            border-radius: 8px;
            overflow: hidden;
            border: 1px solid #30363d;
            font-family: 'SF Mono', 'Monaco', 'Inconsolata', 'Fira Code', 'Courier New', monospace;
            font-size: 13px;
            margin-bottom: 12px;
            background-color: #0d1117;
        }}
        .code-header {{
            background-color: #161b22;
            padding: 6px 12px;
            border-bottom: 1px solid #30363d;
        }}
        .lang-label {{
            color: #8b949e;
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .code-body {{
            display: flex;
            line-height: 20px;
        }}
        .gutter {{
            background-color: #0d1117;
            padding: 8px 0;
            min-width: 48px;
            text-align: right;
            border-right: 1px solid #30363d;
            user-select: none;
        }}
        .line-number {{
            color: #484f58;
            padding: 0 12px 0 8px;
            line-height: 20px;
            font-size: 13px;
        }}
        .code-content {{
            padding: 8px 16px;
            flex: 1;
            overflow-x: auto;
            white-space: pre;
        }}
        .code-line {{
            color: #e6edf3;
            line-height: 20px;
            white-space: pre;
            font-size: 13px;
        }}
    </style>
    """
    st.html(html_block)


# ── section divider helper ────────────────────────────────────────────────────


def _spacer(size: int = 1) -> None:
    """Render vertical whitespace.

    Args:
        size: Number of blank lines to insert.
    """
    st.markdown("<br>" * size, unsafe_allow_html=True)


# ── landing header ────────────────────────────────────────────────────────────


def _render_landing_header() -> None:
    """Render the centered hero header."""
    st.markdown(
        """
        <div style="text-align: center; padding: 3rem 0 2rem 0;">
            <h1 style="font-size: 3.2rem; font-weight: 800; margin-bottom: 0.6rem;">
                🎓 Codify.works
            </h1>
            <p style="font-size: 1.15rem; color: #8b949e; margin-bottom: 0.8rem;">
                AI-powered coding assignment feedback
            </p>
            <p style="font-size: 0.95rem; color: #6e7681;
                      max-width: 620px; margin: 0 auto; line-height: 1.7;">
                Inspired by HackerRank and CodeGrade —
                Codify evaluates student code against specific micro-skills
                and gives targeted hints without ever revealing the full answer.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()


# ── step 1 — assignment form ──────────────────────────────────────────────────


def _render_step_1_assignment_form(settings) -> None:
    """Render assignment creation form with example presets.

    Args:
        settings: Application settings loaded from environment.
    """
    _spacer(1)

    st.markdown(
        """
        <div style="padding: 0.5rem 0 0.2rem 0;">
            <h2 style="margin-bottom: 0.2rem;">📝 Step 1 — Create an Assignment</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("📖 How to fill this in — click to read", expanded=False):
        _spacer(1)
        st.markdown(
            """
- Fill in every field below to describe the assignment
- Or click one of the **Quick Fill** buttons to auto-load a ready-made example
- Once filled, click **Save Assignment** at the bottom
- You can create multiple assignments — they all appear in the dropdown in Step 2
            """
        )
        _spacer(1)

    _spacer(1)

    st.markdown("**⚡ Quick Fill — load a ready-made example:**")
    _spacer(1)

    example_cols = st.columns(len(EXAMPLE_ASSIGNMENTS))
    for col, (label, preset) in zip(example_cols, EXAMPLE_ASSIGNMENTS.items()):
        with col:
            if st.button(label, use_container_width=True, key=f"preset_{label}"):
                st.session_state["prefill"] = preset

    _spacer(2)

    prefill = st.session_state.get("prefill", {})

    with st.form("assignment_form", clear_on_submit=False):
        _spacer(1)

        col_left, col_right = st.columns(2)

        with col_left:
            assignment_id = st.text_input(
                "Assignment ID",
                value=prefill.get("id", ""),
                placeholder="e.g. array-left-shift-c  (no spaces — use hyphens)",
                help="Unique identifier for this assignment. Used internally.",
            )
            _spacer(1)

            title = st.text_input(
                "Assignment Title",
                value=prefill.get("title", ""),
                placeholder="e.g. Array Left Shift",
            )
            _spacer(1)

            language = st.selectbox(
                "Programming Language",
                options=SUPPORTED_LANGUAGES,
                index=(
                    SUPPORTED_LANGUAGES.index(prefill["language"])
                    if prefill.get("language") in SUPPORTED_LANGUAGES
                    else 0
                ),
            )

        with col_right:
            test_cases_raw = st.text_area(
                "Test Cases  (one per line)",
                value=prefill.get("test_cases", ""),
                placeholder=(
                    "Input: 1 2 3 4 5 -> Output: {2, 3, 4, 5, 1}\n"
                    "Input: 5 4 3 2 1 -> Output: {4, 3, 2, 1, 5}"
                ),
                height=178,
                help="Write one test case per line so students know what to expect.",
            )

        _spacer(1)

        description = st.text_area(
            "Problem Description",
            value=prefill.get("description", ""),
            placeholder=(
                "Describe clearly what the student must do.\n"
                "Include the expected input format and output format.\n\n"
                "Example:\n"
                "Write a C program that reads 5 integers into an array,\n"
                "shifts all elements one position to the left,\n"
                "and places the first element at the end."
            ),
            height=180,
        )

        _spacer(1)

        starter_code = st.text_area(
            "Starter Code  (optional — boilerplate for students)",
            value=prefill.get("starter_code", ""),
            placeholder=(
                "#include <stdio.h>\n\n"
                "int main() {\n\n"
                "    // Your code here\n\n"
                "    return 0;\n"
                "}"
            ),
            height=180,
        )

        _spacer(1)

        submitted = st.form_submit_button(
            "💾 Save Assignment",
            type="primary",
            use_container_width=True,
        )

    if not submitted:
        return

    if not assignment_id.strip() or not title.strip() or not description.strip():
        st.error("❌ Assignment ID, Title, and Description are all required.")
        return

    if " " in assignment_id.strip():
        st.error(
            "❌ Assignment ID must not contain spaces. "
            "Use hyphens instead — e.g. array-left-shift-c"
        )
        return

    test_cases = [
        line.strip()
        for line in test_cases_raw.splitlines()
        if line.strip()
    ]

    assignment = Assignment(
        id=assignment_id.strip(),
        title=title.strip(),
        description=description.strip(),
        language=language,
        starter_code=starter_code.strip(),
        test_cases=test_cases,
    )

    try:
        save_assignment(assignment, settings.data_dir)
        st.success(
            f"✅ Assignment **{assignment.title}** saved! "
            "Scroll down to Step 2 to generate micro-skills."
        )
        st.session_state.pop("prefill", None)
        logger.info("Assignment saved", extra={"assignment_id": assignment.id})
    except OSError as error:
        st.error(f"❌ Failed to save assignment: {error}")


# ── step 2 — skill generation ─────────────────────────────────────────────────

def _render_step_2_skill_generation(settings) -> None:
    """Render Phase 1 skill generation section.

    Args:
        settings: Application settings loaded from environment.
    """
    _spacer(2)
    st.divider()
    _spacer(1)

    st.markdown(
        """
        <div style="padding: 0.5rem 0 0.2rem 0;">
            <h2 style="margin-bottom: 0.2rem;">🤖 Step 2 — Generate Micro-Skills</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("📖 What happens here — click to read", expanded=False):
        _spacer(1)
        st.markdown(
            """
- Select the assignment you created in Step 1
- Click **Generate Micro-Skills** — the AI analyzes your assignment
- The AI will produce a list of skills the student must demonstrate
- Each skill has a **check type**: 🔤 Syntax, 📥 Input/Output, or 🧠 Logic
- This takes a few seconds — please wait for the results to appear
            """
        )
        _spacer(1)

    _spacer(1)

    assignments = list_assignments(settings.data_dir)

    if not assignments:
        st.info(
            "💡 No assignments found yet. "
            "Complete Step 1 above to create your first assignment."
        )
        return

    assignment_options = {a.title: a for a in assignments}

    _spacer(1)

    selected_title = st.selectbox(
        "Select the assignment to generate skills for",
        options=list(assignment_options.keys()),
        key="teacher_assignment_select",
    )
    selected_assignment = assignment_options[selected_title]

    _spacer(1)

    if st.button(
        "✨ Generate Micro-Skills",
        type="primary",
        use_container_width=True,
        key="generate_skills_btn",
    ):
        with st.spinner(
            "🤖 AI is analyzing the assignment and generating micro-skills... "
            "This usually takes 5–10 seconds."
        ):
            try:
                candidate_skills = generate_candidate_skills(
                    assignment=selected_assignment,
                    groq_api_key=settings.groq_api_key,
                    groq_model=settings.groq_model,
                )

                # Renumber skill_id sequentially starting from 1
                # regardless of what the model returned
                renumbered_skills = [
                    skill.model_copy(update={"skill_id": index + 1})
                    for index, skill in enumerate(candidate_skills)
                ]

                save_skill_review_state(
                    assignment_id=selected_assignment.id,
                    skills=renumbered_skills,
                    data_dir=settings.data_dir,
                )
                st.success(
                    f"✅ {len(renumbered_skills)} micro-skills generated. "
                    "Scroll down to Step 3 to review them."
                )
                logger.info(
                    "Candidate skills generated and renumbered",
                    extra={
                        "assignment_id": selected_assignment.id,
                        "count": len(renumbered_skills),
                    },
                )
            except ValueError as error:
                st.error(f"❌ Failed to parse skill response: {error}")
            except Exception as error:
                st.error(f"❌ Groq API error: {error}")

    _render_step_3_skill_review(
        selected_assignment=selected_assignment,
        settings=settings,
    )


# ── step 3 — skill review ─────────────────────────────────────────────────────

def _render_step_3_skill_review(
    selected_assignment: Assignment,
    settings,
) -> None:
    """Render the approve/reject skill review panel.

    Enforces a minimum of MIN_APPROVED_SKILLS before the student
    section unlocks. If all skills are rejected, the teacher is prompted
    to regenerate individual rejected skills without losing approved ones.

    Skills are sorted by check_type (syntax → input_output → logic)
    and then renumbered sequentially so display order matches skill_id.

    Args:
        selected_assignment: The currently selected assignment.
        settings: Application settings loaded from environment.
    """
    all_skills = load_skill_review_state(
        selected_assignment.id,
        settings.data_dir,
    )

    if not all_skills:
        return

    _spacer(2)
    st.divider()
    _spacer(1)

    st.markdown(
        """
        <div style="padding: 0.5rem 0 0.2rem 0;">
            <h2 style="margin-bottom: 0.2rem;">📋 Step 3 — Review Micro-Skills</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("📖 How to review skills — click to read", expanded=False):
        _spacer(1)
        st.markdown(
            f"""
- Read each micro-skill card carefully
- Click ✅ **Approve** if the skill correctly describes something the student must do
- Click ❌ **Reject** if the skill is wrong, irrelevant, or too vague
- You need **at least {MIN_APPROVED_SKILLS} approved skill** to unlock student evaluation
- If you reject a skill and want a better one, click 🔄 **Regenerate This Skill**
- Regenerating only replaces that one skill — all your approved skills are kept safe
- Skills are ordered: 🔤 Syntax →  Input/Output →  Logic
            """
        )
        _spacer(1)

    _spacer(1)

    approved_count = sum(
        1 for skill in all_skills if skill.status == SkillStatus.APPROVED
    )
    pending_count = sum(
        1 for skill in all_skills if skill.status == SkillStatus.PENDING
    )
    rejected_count = sum(
        1 for skill in all_skills if skill.status == SkillStatus.REJECTED
    )

    col_approved, col_pending, col_rejected, col_minimum = st.columns(4)
    col_approved.metric("✅ Approved", approved_count)
    col_pending.metric("⏳ Pending", pending_count)
    col_rejected.metric("❌ Rejected", rejected_count)
    col_minimum.metric("🔒 Minimum Required", MIN_APPROVED_SKILLS)

    _spacer(1)

    # Gate check — warn if below minimum
    if approved_count < MIN_APPROVED_SKILLS:
        if rejected_count == len(all_skills):
            st.error(
                f"❌ You have rejected all {rejected_count} skills. "
                f"You need at least {MIN_APPROVED_SKILLS} approved skill to proceed.\n\n"
                "Use the **🔄 Regenerate This Skill** button on any rejected skill below "
                "to get a replacement — your other approved skills will not be affected."
            )
        else:
            st.warning(
                f"⏳ You need at least **{MIN_APPROVED_SKILLS} approved skill** "
                "before students can be evaluated. "
                f"Currently approved: **{approved_count}**."
            )
    elif pending_count == 0:
        st.success(
            f"🎉 All skills reviewed — {approved_count} approved. "
            "Scroll down to the Student Submission section."
        )
    else:
        st.info(
            f"⏳ {pending_count} skill(s) still waiting for your review below."
        )

    _spacer(1)

    # Sort: syntax → input_output → logic
    sorted_skills = sorted(
        all_skills,
        key=lambda skill: CHECK_TYPE_ORDER.get(skill.check_type.value, 99),
    )

    # Renumber skill_id sequentially after sorting so display order matches ID
    # We store the original skill_id in a temporary field for regenerate lookup
    renumbered_skills = []
    for new_index, skill in enumerate(sorted_skills, start=1):
        renumbered_skill = skill.model_copy(
            update={
                "skill_id": new_index,
                "_original_skill_id": skill.skill_id,  # keep original for regen
            }
        )
        renumbered_skills.append(renumbered_skill)

    check_type_labels = {
        CheckType.SYNTAX.value: "🔤 Syntax",
        CheckType.INPUT_OUTPUT.value: "📥 Input / Output",
        CheckType.LOGIC.value: "🧠 Logic",
    }

    current_group: str | None = None

    for skill in renumbered_skills:
        group_label = check_type_labels.get(
            skill.check_type.value, skill.check_type.value
        )

        if skill.check_type.value != current_group:
            _spacer(1)
            st.markdown(f"#### {group_label}")
            current_group = skill.check_type.value

        status_icon = {
            SkillStatus.PENDING: "⏳",
            SkillStatus.APPROVED: "✅",
            SkillStatus.REJECTED: "❌",
        }[skill.status]

        # Use the original skill ID for all update operations
        original_id = getattr(skill, "_original_skill_id", None) or skill.skill_id

        with st.container(border=True):
            _spacer(1)

            col_info, col_approve, col_reject = st.columns([7, 1, 1])

            with col_info:
                st.markdown(
                    f"{status_icon} **Skill {skill.skill_id} — {skill.title}**"
                )
                _spacer(1)
                st.markdown(f"_{skill.description}_")

            with col_approve:
                if st.button(
                    "✅",
                    key=f"approve_{selected_assignment.id}_{skill.skill_id}",
                    disabled=skill.status == SkillStatus.APPROVED,
                    use_container_width=True,
                    help="Approve this skill",
                ):
                    updated_skills = update_single_skill_status(
                        assignment_id=selected_assignment.id,
                        skill_id=original_id,
                        new_status=SkillStatus.APPROVED,
                        data_dir=settings.data_dir,
                    )
                    _sync_approved_to_vector_store(
                        assignment_id=selected_assignment.id,
                        skills=updated_skills,
                        chroma_path=settings.chroma_path,
                    )
                    st.rerun()

            with col_reject:
                if st.button(
                    "❌",
                    key=f"reject_{selected_assignment.id}_{skill.skill_id}",
                    disabled=skill.status == SkillStatus.REJECTED,
                    use_container_width=True,
                    help="Reject this skill",
                ):
                    update_single_skill_status(
                        assignment_id=selected_assignment.id,
                        skill_id=original_id,
                        new_status=SkillStatus.REJECTED,
                        data_dir=settings.data_dir,
                    )
                    st.rerun()

            # Regenerate button — only visible on rejected skills
            if skill.status == SkillStatus.REJECTED:
                _spacer(1)
                if st.button(
                    "🔄 Regenerate This Skill",
                    key=f"regen_{selected_assignment.id}_{skill.skill_id}",
                    use_container_width=True,
                    help=(
                        "Ask the AI to generate a replacement for this skill only. "
                        "All other approved skills are kept."
                    ),
                ):
                    _regenerate_single_skill(
                        assignment=selected_assignment,
                        original_skill_id=original_id,
                        displayed_skill_id=skill.skill_id,
                        settings=settings,
                    )

            _spacer(1)


def _regenerate_single_skill(
    assignment: Assignment,
    original_skill_id: int,
    displayed_skill_id: int,
    settings,
) -> None:
    """Regenerate one rejected skill without affecting approved skills.

    Args:
        assignment: The assignment to regenerate a skill for.
        original_skill_id: The stored skill_id of the rejected skill to replace.
        displayed_skill_id: The renumbered ID shown to the teacher.
        settings: Application settings loaded from environment.
    """
    with st.spinner(
        f"🔄 Regenerating Skill {displayed_skill_id} — keeping all approved skills..."
    ):
        try:
            new_candidates = generate_candidate_skills(
                assignment=assignment,
                groq_api_key=settings.groq_api_key,
                groq_model=settings.groq_model,
            )

            if not new_candidates:
                st.error("❌ AI returned no skills. Please try again.")
                return

            all_skills = load_skill_review_state(
                assignment.id,
                settings.data_dir,
            )

            # Find the index of the skill to replace (using original skill_id)
            target_index = next(
                (i for i, skill in enumerate(all_skills) if skill.skill_id == original_skill_id),
                None,
            )

            if target_index is None:
                st.error(f"❌ Skill {displayed_skill_id} not found. Please refresh.")
                return

            # Choose a replacement: prefer same position index if available,
            # otherwise fall back to the first new candidate.
            replacement_index = min(target_index, len(new_candidates) - 1)
            replacement_candidate = new_candidates[replacement_index]

            replacement = replacement_candidate.model_copy(
                update={"skill_id": original_skill_id, "status": SkillStatus.PENDING}
            )

            updated_skills = all_skills.copy()
            updated_skills[target_index] = replacement

            save_skill_review_state(
                assignment_id=assignment.id,
                skills=updated_skills,
                data_dir=settings.data_dir,
            )

            st.success(
                f"✅ Skill {displayed_skill_id} has been replaced with a new candidate. "
                "Review it above."
            )
            logger.info(
                "Single skill regenerated",
                extra={
                    "assignment_id": assignment.id,
                    "original_skill_id": original_skill_id,
                    "displayed_skill_id": displayed_skill_id,
                },
            )
            st.rerun()

        except ValueError as error:
            st.error(f"❌ Failed to parse replacement skill: {error}")
        except Exception as error:
            st.error(f"❌ Groq API error: {error}")


def _sync_approved_to_vector_store(
    assignment_id: str,
    skills: list[MicroSkill],
    chroma_path: str,
) -> None:
    """Sync approved skills to ChromaDB after every approve action.

    Args:
        assignment_id: Unique assignment identifier.
        skills: Full updated skill list after status change.
        chroma_path: ChromaDB embedded storage path.
    """
    try:
        save_approved_skills(
            assignment_id=assignment_id,
            skills=skills,
            chroma_path=chroma_path,
        )
        logger.info(
            "Vector store synced after approval",
            extra={"assignment_id": assignment_id},
        )
    except RuntimeError as error:
        st.warning(f"⚠️ Vector store sync failed: {error}")


# ── step 4 — student submission ───────────────────────────────────────────────


def _render_step_4_student_submission(settings) -> None:
    """Render the student code submission and evaluation section.

    Only renders if at least one assignment has approved skills.

    Args:
        settings: Application settings loaded from environment.
    """
    _spacer(2)
    st.divider()
    _spacer(1)

    st.markdown(
        """
        <div style="padding: 0.5rem 0 0.2rem 0;">
            <h2 style="margin-bottom: 0.2rem;">💻 Step 4 — Student Code Submission</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("📖 How to submit your code — click to read", expanded=False):
        _spacer(1)
        st.markdown(
            """
- Select your assignment from the dropdown
- Paste or type your full code in the editor below
- Or click one of the **Quick Load** buttons to use a sample submission
- The editor shows line numbers — the AI feedback references these exact line numbers
- Click **Submit for Evaluation** when ready
- Read your per-skill feedback — failed skills include a 💡 hint to guide you
- The AI will **never** show you the full corrected solution — only guiding hints
            """
        )
        _spacer(1)

    _spacer(1)

    assignments = list_assignments(settings.data_dir)

    if not assignments:
        st.info(
            "💡 No assignments available yet. "
            "Complete Steps 1–3 above first."
        )
        return

    # Only show assignments that have at least MIN_APPROVED_SKILLS
    eligible_assignments = [
        assignment for assignment in assignments
        if len(load_approved_skills(assignment.id, settings.data_dir))
        >= MIN_APPROVED_SKILLS
    ]

    if not eligible_assignments:
        st.warning(
            f"⚠️ No assignments are ready for student evaluation yet.\n\n"
            f"The teacher must approve at least **{MIN_APPROVED_SKILLS} micro-skill** "
            "per assignment in Step 3 above before students can submit."
        )
        return

    assignment_options = {a.title: a for a in eligible_assignments}

    selected_title = st.selectbox(
        "📚 Select Your Assignment",
        options=list(assignment_options.keys()),
        key="student_assignment_select",
    )
    selected_assignment = assignment_options[selected_title]

    _spacer(1)

    _render_skills_preview(
        assignment_id=selected_assignment.id,
        data_dir=settings.data_dir,
    )

    _spacer(1)

    approved_skills = retrieve_approved_skills(
        assignment_id=selected_assignment.id,
        chroma_path=settings.chroma_path,
    )

    _render_code_editor_and_submit(
        selected_assignment=selected_assignment,
        approved_skills=approved_skills,
        settings=settings,
    )


def _render_skills_preview(assignment_id: str, data_dir: str) -> None:
    """Render a collapsed preview of approved skills for the student.

    Args:
        assignment_id: Unique assignment identifier.
        data_dir: Root data directory from settings.
    """
    approved_skills = load_approved_skills(assignment_id, data_dir)

    if not approved_skills:
        return

    sorted_skills = sorted(
        approved_skills,
        key=lambda skill: CHECK_TYPE_ORDER.get(skill.check_type.value, 99),
    )

    with st.expander(
        f"📋 You will be evaluated on {len(approved_skills)} micro-skill(s) "
        "— click to preview",
        expanded=False,
    ):
        _spacer(1)

        check_type_labels = {
            CheckType.SYNTAX.value: "🔤 Syntax",
            CheckType.INPUT_OUTPUT.value: "📥 Input / Output",
            CheckType.LOGIC.value: "🧠 Logic",
        }
        current_group: str | None = None

        for skill in sorted_skills:
            group_label = check_type_labels.get(
                skill.check_type.value, skill.check_type.value
            )
            if skill.check_type.value != current_group:
                st.markdown(f"**{group_label}**")
                current_group = skill.check_type.value

            st.markdown(f"&nbsp;&nbsp;• {skill.description}")

        _spacer(1)


def _render_code_editor_and_submit(
    selected_assignment: Assignment,
    approved_skills: list[MicroSkill],
    settings,
) -> None:
    """Render code editor with example buttons and evaluation trigger."""
    _spacer(1)
    st.subheader("📤 Student Code Submission")

    st.markdown("**⚡ Quick Load — use a sample submission:**")
    _spacer(1)

    example_cols = st.columns(len(EXAMPLE_STUDENT_CODES))
    for col, (label, code) in zip(
        example_cols, EXAMPLE_STUDENT_CODES.items()
    ):
        with col:
            if st.button(
                label,
                key=f"code_example_{label}",
                use_container_width=True,
            ):
                # Write stripped version into session state
                st.session_state["student_code_input"] = code.strip()

    _spacer(1)

    # Initialize key if not yet set
    if "student_code_input" not in st.session_state:
        st.session_state["student_code_input"] = ""

    student_code = st.text_area(
        "Paste or type your full code here",
        height=380,
        placeholder=(
            "Paste your complete solution here.\n\n"
            "The line numbers shown in your feedback\n"
            "match the lines in this editor."
        ),
        help=(
            "Write your full solution. "
            "The AI will reference exact line numbers in its feedback."
        ),
        key="student_code_input",
    )

    # Trim leading/trailing whitespace to align line numbers
    student_code = student_code.strip() if student_code else ""

    _spacer(1)

    if student_code and len(student_code) >= MIN_CODE_LENGTH:
        st.markdown("**👁️ Code Preview with Line Numbers:**")
        _spacer(1)
        _render_line_numbered_code(
            student_code,
            language=selected_assignment.language,
        )
        _spacer(1)

    submitted = st.button(
        "🚀 Submit for Evaluation",
        type="primary",
        use_container_width=True,
        key="submit_evaluation_btn",
    )

    if not submitted:
        return

    if not student_code or len(student_code) < MIN_CODE_LENGTH:
        st.error(
            "❌ Your code is too short. "
            f"Please paste your full solution "
            f"(minimum {MIN_CODE_LENGTH} characters)."
        )
        return

    _spacer(1)

    with st.spinner(
        "🤖 AI is evaluating your code against each micro-skill... "
        "This takes a few seconds."
    ):
        try:
            report = evaluate_submission(
                assignment_id=selected_assignment.id,
                student_code=student_code,  # already stripped
                approved_skills=approved_skills,
                groq_api_key=settings.groq_api_key,
                groq_model=settings.groq_model,
            )
            logger.info(
                "Evaluation completed",
                extra={
                    "assignment_id": selected_assignment.id,
                    "passed": report.passed_count,
                    "total": report.total_count,
                },
            )
            _render_evaluation_report(report, selected_assignment.language)

        except ValueError as error:
            st.error(f"❌ Evaluation error: {error}")
        except Exception as error:
            st.error(f"❌ Groq API error: {error}")


# ── evaluation report ─────────────────────────────────────────────────────────


def _render_evaluation_report(
    report: EvaluationReport,
    language: str,
) -> None:
    """Render the full evaluation report.

    Args:
        report: The EvaluationReport returned by the evaluation service.
        language: Programming language for code block display.
    """
    _spacer(1)
    st.divider()
    _spacer(1)
    st.subheader("📊 Your Evaluation Report")
    _spacer(1)

    _render_summary_metrics(report)

    _spacer(1)
    st.divider()
    _spacer(1)

    _render_verdict_cards(report, language)


def _render_summary_metrics(report: EvaluationReport) -> None:
    """Render the top-level pass/fail summary metrics.

    Args:
        report: The EvaluationReport to summarise.
    """
    col_passed, col_failed, col_total, col_rate = st.columns(4)
    col_passed.metric("✅ Skills Passed", report.passed_count)
    col_failed.metric("❌ Skills Failed", report.failed_count)
    col_total.metric("📋 Total Skills", report.total_count)
    col_rate.metric("🎯 Pass Rate", f"{report.pass_rate * 100:.0f}%")

    _spacer(1)

    if report.pass_rate == 1.0:
        st.success("🎉 Perfect score! You demonstrated every required skill.")
    elif report.pass_rate >= 0.5:
        st.warning(
            f"📈 Good progress — {report.failed_count} skill(s) still need work. "
            "Read the hints below."
        )
    else:
        st.error(
            "📚 Keep going — read each hint below carefully and try again. "
            "Focus on one failed skill at a time."
        )


def _render_verdict_cards(
    report: EvaluationReport,
    language: str,
) -> None:
    """Render individual verdict cards ordered syntax → input_output → logic.

    Args:
        report: The EvaluationReport containing all verdicts.
        language: Programming language for snippet display.
    """
    for verdict in report.verdicts:
        _render_single_verdict_card(verdict, language)
        _spacer(1)


def _render_single_verdict_card(
    verdict: SkillVerdict,
    language: str,
) -> None:
    """Render one verdict card for a single micro-skill result.

    Args:
        verdict: The SkillVerdict to render.
        language: Programming language for code snippet display.
    """
    icon = "✅" if verdict.passed else "❌"

    with st.container(border=True):
        _spacer(1)

        st.markdown(
            f"{icon} **Skill {verdict.skill_id} — {verdict.skill_title}**"
        )
        _spacer(1)

        st.markdown(f"**What the AI found:** {verdict.reason}")

        if verdict.student_snippet:
            _spacer(1)
            st.markdown("**Relevant code in your submission:**")

            # Determine starting line number for the snippet.
            start_line = (
                verdict.affected_lines[0] if verdict.affected_lines else 1
            )

            _render_line_numbered_code(
                verdict.student_snippet,
                language,
                start_line=start_line,
            )

        if not verdict.passed and verdict.fix_hint:
            _spacer(1)
            st.info(f"💡 **Hint to fix this:** {verdict.fix_hint}")

        if verdict.passed:
            _spacer(1)
            st.success("Well done — this skill is demonstrated correctly.")

        _spacer(1)


# ── reset section ─────────────────────────────────────────────────────────────


def _render_reset_database_section(settings) -> None:
    """Render the danger-zone reset panel at the bottom of the page.

    Args:
        settings: Application settings loaded from environment.
    """
    _spacer(3)
    st.divider()

    with st.expander("⚠️ Danger Zone — Reset All Data", expanded=False):
        _spacer(1)

        st.error(
            "**This will permanently delete everything:**\n\n"
            "- All saved assignments\n"
            "- All micro-skill review states\n"
            "- All approved skills in the vector database\n\n"
            "Use this before a fresh demo to clear old test data."
        )

        _spacer(1)

        confirm_input = st.text_input(
            "Type RESET to confirm",
            placeholder="RESET",
            key="reset_confirm_input",
        )

        _spacer(1)

        if st.button(
            "🗑️ Delete All Data",
            type="primary",
            use_container_width=True,
            key="reset_all_btn",
        ):
            if confirm_input.strip() != "RESET":
                st.warning("⚠️ You must type RESET exactly to confirm.")
                return

            _wipe_all_data(settings)

        _spacer(1)


def _wipe_all_data(settings) -> None:
    """Delete all assignments, skill states, and ChromaDB collection data.

    This function avoids file‑lock issues on Windows by using ChromaDB's
    API to delete the collection instead of removing the directory.
    Assignments and skills JSON files are deleted normally.

    Args:
        settings: Application settings loaded from environment.
    """
    import shutil
    from pathlib import Path

    errors: list[str] = []

    # 1. Delete ChromaDB collection via the client API
    try:
        cached_client = _get_cached_chroma_client(settings.chroma_path)
        try:
            cached_client.delete_collection(COLLECTION_NAME)
            logger.info("ChromaDB collection '%s' deleted", COLLECTION_NAME)
        except Exception:
            # Collection may not exist — that's fine
            logger.info("ChromaDB collection '%s' not found; nothing to delete", COLLECTION_NAME)
    except Exception as error:
        logger.warning("ChromaDB cleanup failed: %s", str(error))

    # 2. Clear Streamlit's cache to force a fresh client on next use
    st.cache_resource.clear()
    _get_cached_chroma_client.clear()

    # 3. Wipe assignments directory
    assignments_dir = Path(settings.data_dir) / "assignments"
    if assignments_dir.exists():
        try:
            shutil.rmtree(assignments_dir)
            assignments_dir.mkdir(parents=True, exist_ok=True)
            logger.info("Assignments directory wiped")
        except OSError as error:
            errors.append(f"Assignments: {error}")

    # 4. Wipe skills directory
    skills_dir = Path(settings.data_dir) / "skills"
    if skills_dir.exists():
        try:
            shutil.rmtree(skills_dir)
            skills_dir.mkdir(parents=True, exist_ok=True)
            logger.info("Skills directory wiped")
        except OSError as error:
            errors.append(f"Skills: {error}")

    if errors:
        st.error("❌ Some deletions failed:\n" + "\n".join(errors))
        return

    st.success("✅ All data wiped. The app is ready for a fresh start.")
    st.session_state.clear()
    logger.info("Full database reset completed")
    st.rerun()


# ── entry point ───────────────────────────────────────────────────────────────


def main() -> None:
    """Render the full Codify single-page top-to-bottom application."""
    st.set_page_config(
        page_title=PAGE_TITLE,
        page_icon=PAGE_ICON,
        layout="wide",
    )

    settings = get_settings()

    _render_landing_header()

    _, center, _ = st.columns([1, 6, 1])

    with center:
        _render_step_1_assignment_form(settings)
        _render_step_2_skill_generation(settings)
        _render_step_4_student_submission(settings)
        _render_reset_database_section(settings)

    logger.info("Codify app rendered")


main()