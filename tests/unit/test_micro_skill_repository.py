"""Unit tests for micro-skill repository."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.app.models.micro_skill import CheckType, MicroSkill, SkillStatus
from src.app.repositories.micro_skill_repository import (
    load_approved_skills,
    load_skill_review_state,
    save_skill_review_state,
    update_single_skill_status,
)

ASSIGNMENT_ID = "array-shift-101"


@pytest.fixture
def data_dir(tmp_path: pytest.TempPathFactory) -> str:
    """Temporary data directory isolated per test."""
    return str(tmp_path)


@pytest.fixture
def sample_skills() -> list[MicroSkill]:
    """Reusable list of MicroSkills with mixed statuses."""
    return [
        MicroSkill(
            skill_id=1,
            title="Access array elements",
            description="Student uses arr[i].",
            check_type=CheckType.LOGIC,
            status=SkillStatus.APPROVED,
        ),
        MicroSkill(
            skill_id=2,
            title="Use scanf for input",
            description="Student reads integers using scanf.",
            check_type=CheckType.INPUT_OUTPUT,
            status=SkillStatus.PENDING,
        ),
        MicroSkill(
            skill_id=3,
            title="Use temporary variable",
            description="Student uses a temp variable during shift.",
            check_type=CheckType.LOGIC,
            status=SkillStatus.REJECTED,
        ),
    ]


def test_save_and_load_skill_review_state_roundtrip(
    data_dir: str,
    sample_skills: list[MicroSkill],
) -> None:
    """Skills saved and reloaded match original instances exactly."""
    save_skill_review_state(ASSIGNMENT_ID, sample_skills, data_dir)
    loaded = load_skill_review_state(ASSIGNMENT_ID, data_dir)

    assert len(loaded) == len(sample_skills)
    assert loaded[0].skill_id == sample_skills[0].skill_id
    assert loaded[0].status == SkillStatus.APPROVED


def test_save_skill_review_state_creates_file(
    data_dir: str,
    sample_skills: list[MicroSkill],
) -> None:
    """save_skill_review_state writes a JSON file to the skills directory."""
    save_skill_review_state(ASSIGNMENT_ID, sample_skills, data_dir)

    file_path = Path(data_dir) / "skills" / f"{ASSIGNMENT_ID}_skills.json"
    assert file_path.exists()


def test_save_skill_review_state_is_idempotent(
    data_dir: str,
    sample_skills: list[MicroSkill],
) -> None:
    """Calling save twice overwrites cleanly without error."""
    save_skill_review_state(ASSIGNMENT_ID, sample_skills, data_dir)
    save_skill_review_state(ASSIGNMENT_ID, sample_skills, data_dir)

    loaded = load_skill_review_state(ASSIGNMENT_ID, data_dir)
    assert len(loaded) == len(sample_skills)


def test_load_skill_review_state_returns_empty_when_not_found(
    data_dir: str,
) -> None:
    """load_skill_review_state returns empty list when no file exists."""
    result = load_skill_review_state("nonexistent-assignment", data_dir)

    assert result == []


def test_load_skill_review_state_raises_on_invalid_json(
    data_dir: str,
) -> None:
    """load_skill_review_state raises ValueError on corrupt file."""
    skills_dir = Path(data_dir) / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    bad_file = skills_dir / f"{ASSIGNMENT_ID}_skills.json"
    bad_file.write_text("{ not valid json }", encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid skill review state JSON"):
        load_skill_review_state(ASSIGNMENT_ID, data_dir)


def test_load_approved_skills_returns_only_approved(
    data_dir: str,
    sample_skills: list[MicroSkill],
) -> None:
    """load_approved_skills filters to only APPROVED status skills."""
    save_skill_review_state(ASSIGNMENT_ID, sample_skills, data_dir)

    approved = load_approved_skills(ASSIGNMENT_ID, data_dir)

    assert len(approved) == 1
    assert approved[0].skill_id == 1
    assert approved[0].status == SkillStatus.APPROVED


def test_load_approved_skills_returns_empty_when_none_approved(
    data_dir: str,
) -> None:
    """load_approved_skills returns empty list when no approved skills exist."""
    pending_skills = [
        MicroSkill(
            skill_id=1,
            title="Pending skill",
            description="Not approved yet.",
            check_type=CheckType.LOGIC,
            status=SkillStatus.PENDING,
        )
    ]
    save_skill_review_state(ASSIGNMENT_ID, pending_skills, data_dir)

    approved = load_approved_skills(ASSIGNMENT_ID, data_dir)

    assert approved == []


def test_update_single_skill_status_approves_correctly(
    data_dir: str,
    sample_skills: list[MicroSkill],
) -> None:
    """update_single_skill_status sets skill_id=2 from PENDING to APPROVED."""
    save_skill_review_state(ASSIGNMENT_ID, sample_skills, data_dir)

    updated = update_single_skill_status(
        assignment_id=ASSIGNMENT_ID,
        skill_id=2,
        new_status=SkillStatus.APPROVED,
        data_dir=data_dir,
    )

    skill_2 = next(s for s in updated if s.skill_id == 2)
    assert skill_2.status == SkillStatus.APPROVED


def test_update_single_skill_status_does_not_mutate_others(
    data_dir: str,
    sample_skills: list[MicroSkill],
) -> None:
    """update_single_skill_status leaves all other skills unchanged."""
    save_skill_review_state(ASSIGNMENT_ID, sample_skills, data_dir)

    updated = update_single_skill_status(
        assignment_id=ASSIGNMENT_ID,
        skill_id=2,
        new_status=SkillStatus.APPROVED,
        data_dir=data_dir,
    )

    skill_1 = next(s for s in updated if s.skill_id == 1)
    skill_3 = next(s for s in updated if s.skill_id == 3)
    assert skill_1.status == SkillStatus.APPROVED
    assert skill_3.status == SkillStatus.REJECTED


def test_update_single_skill_status_persists_to_disk(
    data_dir: str,
    sample_skills: list[MicroSkill],
) -> None:
    """Updated status is persisted and reloaded correctly from disk."""
    save_skill_review_state(ASSIGNMENT_ID, sample_skills, data_dir)

    update_single_skill_status(
        assignment_id=ASSIGNMENT_ID,
        skill_id=2,
        new_status=SkillStatus.APPROVED,
        data_dir=data_dir,
    )

    reloaded = load_skill_review_state(ASSIGNMENT_ID, data_dir)
    skill_2 = next(s for s in reloaded if s.skill_id == 2)
    assert skill_2.status == SkillStatus.APPROVED