"""Unit tests for prompt builder utility functions."""

from __future__ import annotations

import pytest

from src.app.models.assignment import Assignment
from src.app.models.micro_skill import CheckType, MicroSkill, SkillStatus
from src.app.utils.prompt_builder import (
    build_evaluation_prompt,
    build_skill_generation_prompt,
    _format_test_cases,
    _format_skills_for_evaluation,
)


@pytest.fixture
def sample_assignment() -> Assignment:
    """Reusable Assignment for prompt generation tests."""
    return Assignment(
        id="array-shift-101",
        title="Array Left Shift",
        description="Shift all array elements left by one position.",
        language="c",
        starter_code="int main() { return 0; }",
        test_cases=["Input: 1 2 3 -> Output: 2 3 1"],
    )


@pytest.fixture
def sample_approved_skills() -> list[MicroSkill]:
    """Reusable list of approved MicroSkills for evaluation tests."""
    return [
        MicroSkill(
            skill_id=1,
            title="Access array elements",
            description="Student uses arr[i] to access elements.",
            check_type=CheckType.LOGIC,
            status=SkillStatus.APPROVED,
        ),
        MicroSkill(
            skill_id=2,
            title="Use scanf for input",
            description="Student reads integers using scanf.",
            check_type=CheckType.INPUT_OUTPUT,
            status=SkillStatus.APPROVED,
        ),
    ]


def test_build_skill_generation_prompt_contains_title(
    sample_assignment: Assignment,
) -> None:
    """Phase 1 prompt contains the assignment title."""
    prompt = build_skill_generation_prompt(sample_assignment)

    assert sample_assignment.title in prompt


def test_build_skill_generation_prompt_contains_description(
    sample_assignment: Assignment,
) -> None:
    """Phase 1 prompt contains the assignment description."""
    prompt = build_skill_generation_prompt(sample_assignment)

    assert sample_assignment.description in prompt


def test_build_skill_generation_prompt_contains_language(
    sample_assignment: Assignment,
) -> None:
    """Phase 1 prompt contains the programming language."""
    prompt = build_skill_generation_prompt(sample_assignment)

    assert sample_assignment.language in prompt


def test_build_skill_generation_prompt_contains_starter_code(
    sample_assignment: Assignment,
) -> None:
    """Phase 1 prompt contains starter code when provided."""
    prompt = build_skill_generation_prompt(sample_assignment)

    assert sample_assignment.starter_code in prompt


def test_build_skill_generation_prompt_contains_test_cases(
    sample_assignment: Assignment,
) -> None:
    """Phase 1 prompt contains the test case content."""
    prompt = build_skill_generation_prompt(sample_assignment)

    assert sample_assignment.test_cases[0] in prompt


def test_build_skill_generation_prompt_contains_json_structure(
    sample_assignment: Assignment,
) -> None:
    """Phase 1 prompt instructs model to return micro_skills JSON key."""
    prompt = build_skill_generation_prompt(sample_assignment)

    assert "micro_skills" in prompt


def test_build_skill_generation_prompt_no_starter_code() -> None:
    """Phase 1 prompt handles missing starter code gracefully."""
    assignment = Assignment(
        id="no-starter-001",
        title="No Starter",
        description="Write from scratch.",
    )
    prompt = build_skill_generation_prompt(assignment)

    assert "No starter code provided." in prompt


def test_build_evaluation_prompt_contains_student_code(
    sample_approved_skills: list[MicroSkill],
) -> None:
    """Phase 2 prompt contains the student code."""
    student_code = "for(i=0; i<5; i++) arr[i] = i;"
    prompt = build_evaluation_prompt(student_code, sample_approved_skills)

    assert student_code in prompt


def test_build_evaluation_prompt_contains_all_skill_titles(
    sample_approved_skills: list[MicroSkill],
) -> None:
    """Phase 2 prompt contains all approved skill titles."""
    prompt = build_evaluation_prompt("some code", sample_approved_skills)

    for skill in sample_approved_skills:
        assert skill.title in prompt


def test_build_evaluation_prompt_contains_verdicts_key(
    sample_approved_skills: list[MicroSkill],
) -> None:
    """Phase 2 prompt instructs model to return verdicts JSON key."""
    prompt = build_evaluation_prompt("some code", sample_approved_skills)

    assert "verdicts" in prompt


def test_build_evaluation_prompt_no_full_solution_instruction(
    sample_approved_skills: list[MicroSkill],
) -> None:
    """Phase 2 prompt explicitly forbids returning full corrected code."""
    prompt = build_evaluation_prompt("some code", sample_approved_skills)

    assert "NEVER give the full corrected code" in prompt


@pytest.mark.parametrize("test_cases,expected_substring", [
    ([], "No test cases provided."),
    (["Input: 1 -> Output: 2"], "1. Input: 1 -> Output: 2"),
    (["case one", "case two"], "1. case one"),
])
def test_format_test_cases_various_inputs(
    test_cases: list[str],
    expected_substring: str,
) -> None:
    """_format_test_cases handles empty, single, and multiple cases."""
    result = _format_test_cases(test_cases)

    assert expected_substring in result


def test_format_skills_for_evaluation_empty() -> None:
    """_format_skills_for_evaluation returns placeholder for empty list."""
    result = _format_skills_for_evaluation([])

    assert result == "No approved skills available."


def test_format_skills_for_evaluation_contains_check_type(
    sample_approved_skills: list[MicroSkill],
) -> None:
    """_format_skills_for_evaluation includes check_type for each skill."""
    result = _format_skills_for_evaluation(sample_approved_skills)

    assert "logic" in result
    assert "input_output" in result