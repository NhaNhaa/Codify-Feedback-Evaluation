"""Pure functions for building Phase 1 and Phase 2 prompts."""

from __future__ import annotations

from src.app.models.assignment import Assignment
from src.app.models.micro_skill import MicroSkill

# Instruct the model to return strict JSON — no markdown fences
_JSON_REMINDER = "Return only valid JSON. No markdown. No explanation outside the JSON."


def build_skill_generation_prompt(assignment: Assignment) -> str:
    """Build the Phase 1 prompt for generating candidate micro-skills.

    The prompt instructs the model to analyze the assignment and return
    a list of micro-skills in strict JSON format. Each description must
    be one actionable sentence telling the student exactly what to do
    and how — including the specific syntax, function, or technique expected.
    The teacher will then approve or reject each skill before they can
    be used in evaluation.

    Args:
        assignment: The assignment to generate micro-skills for.

    Returns:
        str: A fully formatted prompt string ready for the Groq API.

    Time complexity: O(n) where n = number of test cases
    Space complexity: O(n)
    """
    test_cases_block = _format_test_cases(assignment.test_cases)

    return f"""You are an expert computer science educator analyzing a coding assignment.

Your task is to identify the key micro-skills a student must demonstrate to solve this assignment correctly.

ASSIGNMENT DETAILS
------------------
Title: {assignment.title}
Language: {assignment.language}
Description:
{assignment.description}

Starter Code:
{assignment.starter_code or "No starter code provided."}

Test Cases:
{test_cases_block}

INSTRUCTIONS
------------
Generate a list of micro-skills. Each micro-skill must:
- Target exactly one learning concept
- Be written as one actionable sentence telling the student exactly what
  to do and how — including the specific syntax, function, or technique expected
- Follow this description style exactly:

    GOOD: "Be able to access array elements using index notation arr[i] inside a for loop"
    GOOD: "Use scanf to read 5 integers into an array using a for loop"
    GOOD: "Be able to shift elements left using arr[i-1] = arr[i] and handle the first cell separately"
    GOOD: "Avoid losing data during shifting by saving arr[0] into a temporary variable before the loop starts"

    BAD: "Understand array shifting" — too vague, no how
    BAD: "Use a loop" — too vague, no what or why
    BAD: "Handle edge cases" — not actionable, no specific technique

- Be assigned one check_type: "syntax", "input_output", or "logic"

check_type guide:
- syntax      : correct language syntax or structure (e.g. proper loop, variable declaration)
- input_output : reading input or producing correct output format (e.g. scanf, printf, print)
- logic       : algorithmic correctness or data manipulation (e.g. correct indexing, temp variable)

Return a JSON object with this exact structure:
{{
  "micro_skills": [
    {{
      "skill_id": 1,
      "title": "short skill title",
      "description": "one actionable sentence — what to do and exactly how",
      "check_type": "syntax" | "input_output" | "logic"
    }}
  ]
}}

{_JSON_REMINDER}"""


def _format_code_with_line_numbers(code: str) -> str:
    """Format code with 1-indexed line numbers for AI evaluation.

    Args:
        code: Raw student code (already stripped).

    Returns:
        str: Code with line numbers prepended (e.g., "   1: int main() {").

    Time complexity: O(n) where n = number of lines
    Space complexity: O(n)
    """
    lines = code.splitlines()
    return "\n".join(f"{i+1:4d}: {line}" for i, line in enumerate(lines))


def build_evaluation_prompt(
    student_code: str,
    approved_skills: list[MicroSkill],
) -> str:
    """Build the Phase 2 prompt for evaluating a student submission.

    The prompt instructs the model to assess the student code against
    each approved micro-skill and return a per-skill verdict. The model
    must never return a full corrected solution — only guiding hints.

    Args:
        student_code: The raw code submitted by the student.
        approved_skills: Approved micro-skills retrieved from the vector store.

    Returns:
        str: A fully formatted prompt string ready for the Groq API.

    Time complexity: O(n) where n = number of approved skills
    Space complexity: O(n)
    """
    numbered_code = _format_code_with_line_numbers(student_code)
    skills_block = _format_skills_for_evaluation(approved_skills)

    return f"""You are an expert computer science educator evaluating a student's code submission.

Assess the student code against each micro-skill below.
For each skill, determine if the student demonstrated it correctly.

STUDENT CODE (with line numbers)
--------------------------------
{numbered_code}

MICRO-SKILLS TO EVALUATE
-------------------------
{skills_block}

INSTRUCTIONS
------------
For each micro-skill return a verdict. Rules:
- passed    : true if the student clearly demonstrated the skill, false otherwise
- reason    : one or two sentences explaining the verdict
- student_snippet: the exact lines from the student code that triggered the verdict (empty string if none)
- fix_hint  : if failed, a guiding hint toward the fix — NEVER give the full corrected code
- affected_lines: list of line numbers (1-indexed) from the code above relevant to this verdict. Use the exact line numbers as shown.

Return a JSON object with this exact structure:
{{
  "verdicts": [
    {{
      "skill_id": 1,
      "skill_title": "skill title here",
      "passed": true,
      "reason": "explanation here",
      "student_snippet": "relevant code lines here",
      "fix_hint": "hint here or empty string if passed",
      "affected_lines": [1, 2]
    }}
  ]
}}

{_JSON_REMINDER}"""


def _format_test_cases(test_cases: list[str]) -> str:
    """Format test cases into a numbered list string.

    Args:
        test_cases: List of test case strings.

    Returns:
        str: Numbered list or a placeholder if empty.

    Time complexity: O(n)
    Space complexity: O(n)
    """
    if not test_cases:
        return "No test cases provided."

    parts = [f"{i + 1}. {case}" for i, case in enumerate(test_cases)]
    return "\n".join(parts)


def _format_skills_for_evaluation(skills: list[MicroSkill]) -> str:
    """Format approved micro-skills into a numbered block for the prompt.

    Args:
        skills: Approved micro-skills to include in the evaluation prompt.

    Returns:
        str: Formatted skill block or placeholder if empty.

    Time complexity: O(n)
    Space complexity: O(n)
    """
    if not skills:
        return "No approved skills available."

    parts = [
        f"Skill {skill.skill_id} [{skill.check_type.value}]\n"
        f"Title: {skill.title}\n"
        f"Description: {skill.description}"
        for skill in skills
    ]
    return "\n\n".join(parts)