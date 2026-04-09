"""Unit tests for skill generation service (Phase 1)."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from src.app.models.assignment import Assignment
from src.app.models.micro_skill import CheckType, MicroSkill, SkillStatus
from src.app.services.skill_generation_service import (
    _parse_skills_from_response,
    generate_candidate_skills,
)

ASSIGNMENT_ID = "array-shift-101"


@pytest.fixture
def sample_assignment() -> Assignment:
    """Reusable Assignment for skill generation tests."""
    return Assignment(
        id=ASSIGNMENT_ID,
        title="Array Left Shift",
        description="Shift all array elements left by one position.",
        language="c",
        starter_code="int main() { return 0; }",
        test_cases=["Input: 1 2 3 -> Output: 2 3 1"],
    )


@pytest.fixture
def valid_groq_response() -> str:
    """Valid JSON string mimicking a Groq API response."""
    return json.dumps({
        "micro_skills": [
            {
                "skill_id": 1,
                "title": "Access array elements",
                "description": "Student uses arr[i] to access elements.",
                "check_type": "logic",
            },
            {
                "skill_id": 2,
                "title": "Use scanf for input",
                "description": "Student reads integers using scanf.",
                "check_type": "input_output",
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


def test_parse_skills_from_response_valid_json(
    valid_groq_response: str,
) -> None:
    """_parse_skills_from_response returns correct skills from valid JSON."""
    skills = _parse_skills_from_response(valid_groq_response)

    assert len(skills) == 2
    assert skills[0].skill_id == 1
    assert skills[0].title == "Access array elements"
    assert skills[0].check_type == CheckType.LOGIC
    assert skills[0].status == SkillStatus.PENDING


def test_parse_skills_from_response_all_pending(
    valid_groq_response: str,
) -> None:
    """All parsed skills default to PENDING status."""
    skills = _parse_skills_from_response(valid_groq_response)

    assert all(skill.status == SkillStatus.PENDING for skill in skills)


def test_parse_skills_from_response_invalid_json_raises() -> None:
    """_parse_skills_from_response raises ValueError on invalid JSON."""
    with pytest.raises(ValueError, match="not valid JSON"):
        _parse_skills_from_response("{ this is not json }")


def test_parse_skills_from_response_missing_key_raises() -> None:
    """_parse_skills_from_response raises ValueError when micro_skills key absent."""
    with pytest.raises(ValueError, match="missing required 'micro_skills' key"):
        _parse_skills_from_response(json.dumps({"wrong_key": []}))


def test_parse_skills_from_response_skips_malformed_records() -> None:
    """Malformed skill records are skipped — valid ones are still returned."""
    raw = json.dumps({
        "micro_skills": [
            {
                "skill_id": 1,
                "title": "Valid skill",
                "description": "Valid description.",
                "check_type": "logic",
            },
            {
                "skill_id": 2,
                # missing title — malformed
                "description": "No title here.",
                "check_type": "syntax",
            },
        ]
    })

    skills = _parse_skills_from_response(raw)

    assert len(skills) == 1
    assert skills[0].skill_id == 1


def test_parse_skills_from_response_invalid_check_type_skipped() -> None:
    """Skills with invalid check_type are skipped gracefully."""
    raw = json.dumps({
        "micro_skills": [
            {
                "skill_id": 1,
                "title": "Valid skill",
                "description": "Valid desc.",
                "check_type": "invalid_type",
            },
        ]
    })

    skills = _parse_skills_from_response(raw)

    assert skills == []


@pytest.mark.parametrize("check_type_str,expected_enum", [
    ("syntax", CheckType.SYNTAX),
    ("input_output", CheckType.INPUT_OUTPUT),
    ("logic", CheckType.LOGIC),
])
def test_parse_skills_from_response_all_check_types(
    check_type_str: str,
    expected_enum: CheckType,
) -> None:
    """_parse_skills_from_response correctly maps all check_type strings."""
    raw = json.dumps({
        "micro_skills": [
            {
                "skill_id": 1,
                "title": "Test skill",
                "description": "Test desc.",
                "check_type": check_type_str,
            }
        ]
    })

    skills = _parse_skills_from_response(raw)

    assert skills[0].check_type == expected_enum


def test_generate_candidate_skills_calls_groq_api(
    sample_assignment: Assignment,
    valid_groq_response: str,
) -> None:
    """generate_candidate_skills calls Groq API with correct model."""
    mock_response = _build_mock_groq_response(valid_groq_response)

    with patch(
        "src.app.services.skill_generation_service.Groq"
    ) as mock_groq_class:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_groq_class.return_value = mock_client

        skills = generate_candidate_skills(
            assignment=sample_assignment,
            groq_api_key="test-key",
            groq_model="llama-3.3-70b-versatile",
        )

        mock_client.chat.completions.create.assert_called_once()
        assert len(skills) == 2


def test_generate_candidate_skills_returns_pending_skills(
    sample_assignment: Assignment,
    valid_groq_response: str,
) -> None:
    """generate_candidate_skills returns skills with PENDING status."""
    mock_response = _build_mock_groq_response(valid_groq_response)

    with patch(
        "src.app.services.skill_generation_service.Groq"
    ) as mock_groq_class:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_groq_class.return_value = mock_client

        skills = generate_candidate_skills(
            assignment=sample_assignment,
            groq_api_key="test-key",
            groq_model="llama-3.3-70b-versatile",
        )

        assert all(skill.status == SkillStatus.PENDING for skill in skills)


def test_generate_candidate_skills_raises_on_api_failure(
    sample_assignment: Assignment,
) -> None:
    """generate_candidate_skills propagates Groq API exceptions."""
    with patch(
        "src.app.services.skill_generation_service.Groq"
    ) as mock_groq_class:
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception(
            "API connection failed"
        )
        mock_groq_class.return_value = mock_client

        with pytest.raises(Exception, match="API connection failed"):
            generate_candidate_skills(
                assignment=sample_assignment,
                groq_api_key="test-key",
                groq_model="llama-3.3-70b-versatile",
            )