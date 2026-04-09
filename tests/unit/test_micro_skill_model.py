"""Unit tests for MicroSkill, CheckType, and SkillStatus models."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from src.app.models.micro_skill import CheckType, MicroSkill, SkillStatus


@pytest.fixture
def sample_skill() -> MicroSkill:
    """Reusable valid MicroSkill instance."""
    return MicroSkill(
        skill_id=1,
        title="Access array elements",
        description="Student uses arr[i] to access elements.",
        check_type=CheckType.LOGIC,
    )


def test_micro_skill_creation_defaults(sample_skill: MicroSkill) -> None:
    """MicroSkill defaults to PENDING status on creation."""
    assert sample_skill.status == SkillStatus.PENDING
    assert sample_skill.is_pending is True
    assert sample_skill.is_approved is False


def test_micro_skill_approve_returns_new_instance(sample_skill: MicroSkill) -> None:
    """approve() returns a new instance and does not mutate the original."""
    approved = sample_skill.approve()

    assert approved.status == SkillStatus.APPROVED
    assert approved.is_approved is True
    assert sample_skill.status == SkillStatus.PENDING  # original unchanged


def test_micro_skill_reject_returns_new_instance(sample_skill: MicroSkill) -> None:
    """reject() returns a new instance and does not mutate the original."""
    rejected = sample_skill.reject()

    assert rejected.status == SkillStatus.REJECTED
    assert sample_skill.status == SkillStatus.PENDING  # original unchanged


def test_micro_skill_preserves_fields_after_approve(sample_skill: MicroSkill) -> None:
    """approve() preserves all fields except status."""
    approved = sample_skill.approve()

    assert approved.skill_id == sample_skill.skill_id
    assert approved.title == sample_skill.title
    assert approved.description == sample_skill.description
    assert approved.check_type == sample_skill.check_type


@pytest.mark.parametrize("check_type", [
    CheckType.SYNTAX,
    CheckType.INPUT_OUTPUT,
    CheckType.LOGIC,
])
def test_micro_skill_all_check_types_accepted(check_type: CheckType) -> None:
    """MicroSkill accepts all valid CheckType values."""
    skill = MicroSkill(
        skill_id=1,
        title="Test skill",
        description="Test description",
        check_type=check_type,
    )

    assert skill.check_type == check_type


def test_micro_skill_missing_title_raises() -> None:
    """ValidationError raised when title is empty."""
    with pytest.raises(ValidationError):
        MicroSkill(
            skill_id=1,
            title="",
            description="Valid description",
            check_type=CheckType.LOGIC,
        )


def test_micro_skill_invalid_check_type_raises() -> None:
    """ValidationError raised when check_type is not a valid enum value."""
    with pytest.raises(ValidationError):
        MicroSkill(
            skill_id=1,
            title="Test",
            description="Test desc",
            check_type="invalid_type",  # type: ignore[arg-type]
        )


def test_micro_skill_json_roundtrip(sample_skill: MicroSkill) -> None:
    """MicroSkill serializes and deserializes from JSON correctly."""
    json_str = sample_skill.model_dump_json()
    restored = MicroSkill.model_validate_json(json_str)

    assert restored.skill_id == sample_skill.skill_id
    assert restored.check_type == sample_skill.check_type
    assert restored.status == sample_skill.status