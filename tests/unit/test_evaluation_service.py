"""Unit tests for evaluation service (Phase 2)."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from src.app.models.evaluation import EvaluationReport, SkillVerdict
from src.app.models.micro_skill import CheckType, MicroSkill, SkillStatus
from src.app.services.evaluation_service import (
    _parse_verdicts_from_response,
    evaluate_submission,
)

ASSIGNMENT_ID = "array-shift-101"
STUDENT_CODE = """\
#include <stdio.h>
int main() {
    int arr[5];
    int i;
    for(i = 0; i < 5; i++) {
        scanf("%d", &arr[i]);
    }
    arr[4] = arr[0];
    return 0;
}"""


@pytest.fixture
def approved_skills() -> list[MicroSkill]:
    """Reusable list of approved MicroSkills."""
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


@pytest.fixture
def valid_groq_response(approved_skills: list[MicroSkill]) -> str:
    """Valid JSON string mimicking a Groq Phase 2 API response."""
    return json.dumps({
        "verdicts": [
            {
                "skill_id": 1,
                "skill_title": "Access array elements",
                "passed": True,
                "reason": "Student correctly uses arr[i] throughout.",
                "student_snippet": "arr[i] = value;",
                "fix_hint": "",
                "affected_lines": [6, 7],
            },
            {
                "skill_id": 2,
                "skill_title": "Use scanf for input",
                "passed": True,
                "reason": "Student uses scanf to read integers correctly.",
                "student_snippet": 'scanf("%d", &arr[i]);',
                "fix_hint": "",
                "affected_lines": [6],
            },
        ]
    })


def _build_mock_groq_response(content: str) -> MagicMock:
    """Build a mock Groq API response object with the given content string."""
    mock_message = MagicMock()
    mock_message.content = content

    mock_choice = MagicMock()
    mock_choice.message = mock_message

    mock_response = MagicMock()
    mock_response.choices = [mock_choice]

    return mock_response


def test_parse_verdicts_from_response_valid_json(
    valid_groq_response: str,
    approved_skills: list[MicroSkill],
) -> None:
    """_parse_verdicts_from_response returns correct verdicts from valid JSON."""
    verdicts = _parse_verdicts_from_response(valid_groq_response, approved_skills)

    assert len(verdicts) == 2
    assert verdicts[0].skill_id == 1
    assert verdicts[0].passed is True
    assert verdicts[1].skill_id == 2


def test_parse_verdicts_from_response_invalid_json_raises(
    approved_skills: list[MicroSkill],
) -> None:
    """_parse_verdicts_from_response raises ValueError on invalid JSON."""
    with pytest.raises(ValueError, match="not valid JSON"):
        _parse_verdicts_from_response("{ not json }", approved_skills)


def test_parse_verdicts_from_response_missing_verdicts_key_raises(
    approved_skills: list[MicroSkill],
) -> None:
    """_parse_verdicts_from_response raises ValueError when verdicts key absent."""
    with pytest.raises(ValueError, match="missing required 'verdicts' key"):
        _parse_verdicts_from_response(
            json.dumps({"wrong_key": []}),
            approved_skills,
        )


def test_parse_verdicts_from_response_skips_unknown_skill_ids(
    approved_skills: list[MicroSkill],
) -> None:
    """Verdicts referencing unknown skill_ids are silently skipped."""
    raw = json.dumps({
        "verdicts": [
            {
                "skill_id": 999,  # unknown
                "skill_title": "Ghost skill",
                "passed": True,
                "reason": "Unknown skill.",
                "student_snippet": "",
                "fix_hint": "",
                "affected_lines": [],
            },
        ]
    })

    verdicts = _parse_verdicts_from_response(raw, approved_skills)

    assert verdicts == []


def test_parse_verdicts_from_response_skips_malformed_records(
    approved_skills: list[MicroSkill],
) -> None:
    """Malformed verdict records are skipped — valid ones still returned."""
    raw = json.dumps({
        "verdicts": [
            {
                "skill_id": 1,
                "skill_title": "Access array elements",
                "passed": True,
                "reason": "Correct.",
                "student_snippet": "",
                "fix_hint": "",
                "affected_lines": [],
            },
            {
                "skill_id": 2,
                # missing passed field — malformed
                "skill_title": "Use scanf",
                "reason": "Missing passed field.",
            },
        ]
    })

    verdicts = _parse_verdicts_from_response(raw, approved_skills)

    assert len(verdicts) == 1
    assert verdicts[0].skill_id == 1


def test_parse_verdicts_from_response_defaults_optional_fields(
    approved_skills: list[MicroSkill],
) -> None:
    """Optional fields default to empty values when absent from response."""
    raw = json.dumps({
        "verdicts": [
            {
                "skill_id": 1,
                "skill_title": "Access array elements",
                "passed": False,
                "reason": "Missing usage.",
            },
        ]
    })

    verdicts = _parse_verdicts_from_response(raw, approved_skills)

    assert verdicts[0].student_snippet == ""
    assert verdicts[0].fix_hint == ""
    assert verdicts[0].affected_lines == []


@pytest.mark.parametrize("passed,expected_hint", [
    (True, ""),
    (False, "Think about saving arr[0] before shifting."),
])
def test_parse_verdicts_from_response_fix_hint_by_pass_status(
    passed: bool,
    expected_hint: str,
    approved_skills: list[MicroSkill],
) -> None:
    """fix_hint is preserved as returned by model for both pass and fail."""
    raw = json.dumps({
        "verdicts": [
            {
                "skill_id": 1,
                "skill_title": "Access array elements",
                "passed": passed,
                "reason": "Test reason.",
                "fix_hint": expected_hint,
                "affected_lines": [],
            }
        ]
    })

    verdicts = _parse_verdicts_from_response(raw, approved_skills)

    assert verdicts[0].fix_hint == expected_hint


def test_evaluate_submission_raises_when_no_approved_skills() -> None:
    """evaluate_submission raises ValueError when approved_skills is empty."""
    with pytest.raises(ValueError, match="no approved micro-skills"):
        evaluate_submission(
            assignment_id=ASSIGNMENT_ID,
            student_code=STUDENT_CODE,
            approved_skills=[],
            groq_api_key="test-key",
            groq_model="llama-3.3-70b-versatile",
        )


def test_evaluate_submission_returns_evaluation_report(
    approved_skills: list[MicroSkill],
    valid_groq_response: str,
) -> None:
    """evaluate_submission returns a valid EvaluationReport."""
    mock_response = _build_mock_groq_response(valid_groq_response)

    with patch(
        "src.app.services.evaluation_service.Groq"
    ) as mock_groq_class:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_groq_class.return_value = mock_client

        report = evaluate_submission(
            assignment_id=ASSIGNMENT_ID,
            student_code=STUDENT_CODE,
            approved_skills=approved_skills,
            groq_api_key="test-key",
            groq_model="llama-3.3-70b-versatile",
        )

        assert isinstance(report, EvaluationReport)
        assert report.assignment_id == ASSIGNMENT_ID
        assert report.total_count == 2


def test_evaluate_submission_report_contains_student_code(
    approved_skills: list[MicroSkill],
    valid_groq_response: str,
) -> None:
    """EvaluationReport contains the original student code."""
    mock_response = _build_mock_groq_response(valid_groq_response)

    with patch(
        "src.app.services.evaluation_service.Groq"
    ) as mock_groq_class:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_groq_class.return_value = mock_client

        report = evaluate_submission(
            assignment_id=ASSIGNMENT_ID,
            student_code=STUDENT_CODE,
            approved_skills=approved_skills,
            groq_api_key="test-key",
            groq_model="llama-3.3-70b-versatile",
        )

        assert report.student_code == STUDENT_CODE


def test_evaluate_submission_raises_on_api_failure(
    approved_skills: list[MicroSkill],
) -> None:
    """evaluate_submission propagates Groq API exceptions."""
    with patch(
        "src.app.services.evaluation_service.Groq"
    ) as mock_groq_class:
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception(
            "API connection failed"
        )
        mock_groq_class.return_value = mock_client

        with pytest.raises(Exception, match="API connection failed"):
            evaluate_submission(
                assignment_id=ASSIGNMENT_ID,
                student_code=STUDENT_CODE,
                approved_skills=approved_skills,
                groq_api_key="test-key",
                groq_model="llama-3.3-70b-versatile",
            )


def test_evaluate_submission_calls_groq_with_correct_model(
    approved_skills: list[MicroSkill],
    valid_groq_response: str,
) -> None:
    """evaluate_submission passes the correct model to the Groq client."""
    mock_response = _build_mock_groq_response(valid_groq_response)
    expected_model = "llama-3.3-70b-versatile"

    with patch(
        "src.app.services.evaluation_service.Groq"
    ) as mock_groq_class:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_groq_class.return_value = mock_client

        evaluate_submission(
            assignment_id=ASSIGNMENT_ID,
            student_code=STUDENT_CODE,
            approved_skills=approved_skills,
            groq_api_key="test-key",
            groq_model=expected_model,
        )

        call_kwargs = mock_client.chat.completions.create.call_args.kwargs
        assert call_kwargs["model"] == expected_model