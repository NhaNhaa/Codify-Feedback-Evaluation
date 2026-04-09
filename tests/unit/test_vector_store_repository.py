"""Unit tests for vector store repository."""

from __future__ import annotations

import pytest

from src.app.models.micro_skill import CheckType, MicroSkill, SkillStatus
from src.app.repositories.vector_store_repository import (
    delete_assignment_skills,
    retrieve_approved_skills,
    save_approved_skills,
)

ASSIGNMENT_ID = "array-shift-101"


@pytest.fixture
def chroma_path(tmp_path: pytest.TempPathFactory) -> str:
    """Temporary ChromaDB path isolated per test."""
    return str(tmp_path / "chroma")


@pytest.fixture
def mixed_skills() -> list[MicroSkill]:
    """Reusable list of skills with mixed approval statuses."""
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
        MicroSkill(
            skill_id=3,
            title="Pending skill",
            description="Not yet reviewed.",
            check_type=CheckType.SYNTAX,
            status=SkillStatus.PENDING,
        ),
        MicroSkill(
            skill_id=4,
            title="Rejected skill",
            description="Teacher rejected this.",
            check_type=CheckType.LOGIC,
            status=SkillStatus.REJECTED,
        ),
    ]


def test_save_and_retrieve_approved_skills_roundtrip(
    chroma_path: str,
    mixed_skills: list[MicroSkill],
) -> None:
    """Only approved skills are stored and retrieved correctly."""
    save_approved_skills(ASSIGNMENT_ID, mixed_skills, chroma_path)
    retrieved = retrieve_approved_skills(ASSIGNMENT_ID, chroma_path)

    assert len(retrieved) == 2
    retrieved_ids = {skill.skill_id for skill in retrieved}
    assert retrieved_ids == {1, 2}


def test_retrieve_approved_skills_sorted_by_skill_id(
    chroma_path: str,
    mixed_skills: list[MicroSkill],
) -> None:
    """Retrieved skills are sorted by skill_id ascending."""
    save_approved_skills(ASSIGNMENT_ID, mixed_skills, chroma_path)
    retrieved = retrieve_approved_skills(ASSIGNMENT_ID, chroma_path)

    skill_ids = [skill.skill_id for skill in retrieved]
    assert skill_ids == sorted(skill_ids)


def test_retrieve_approved_skills_preserves_fields(
    chroma_path: str,
    mixed_skills: list[MicroSkill],
) -> None:
    """Retrieved skills preserve title, description, and check_type."""
    save_approved_skills(ASSIGNMENT_ID, mixed_skills, chroma_path)
    retrieved = retrieve_approved_skills(ASSIGNMENT_ID, chroma_path)

    skill_1 = next(s for s in retrieved if s.skill_id == 1)
    assert skill_1.title == "Access array elements"
    assert skill_1.check_type == CheckType.LOGIC
    assert skill_1.status == SkillStatus.APPROVED


def test_save_approved_skills_skips_pending_and_rejected(
    chroma_path: str,
    mixed_skills: list[MicroSkill],
) -> None:
    """Pending and rejected skills are never stored in ChromaDB."""
    save_approved_skills(ASSIGNMENT_ID, mixed_skills, chroma_path)
    retrieved = retrieve_approved_skills(ASSIGNMENT_ID, chroma_path)

    statuses = {skill.status for skill in retrieved}
    assert statuses == {SkillStatus.APPROVED}


def test_save_approved_skills_no_approved_skips_upsert(
    chroma_path: str,
) -> None:
    """save_approved_skills with no approved skills stores nothing."""
    pending_only = [
        MicroSkill(
            skill_id=1,
            title="Pending skill",
            description="Not approved.",
            check_type=CheckType.LOGIC,
            status=SkillStatus.PENDING,
        )
    ]
    save_approved_skills(ASSIGNMENT_ID, pending_only, chroma_path)
    retrieved = retrieve_approved_skills(ASSIGNMENT_ID, chroma_path)

    assert retrieved == []


def test_save_approved_skills_is_idempotent(
    chroma_path: str,
    mixed_skills: list[MicroSkill],
) -> None:
    """Calling save twice does not duplicate entries."""
    save_approved_skills(ASSIGNMENT_ID, mixed_skills, chroma_path)
    save_approved_skills(ASSIGNMENT_ID, mixed_skills, chroma_path)

    retrieved = retrieve_approved_skills(ASSIGNMENT_ID, chroma_path)
    assert len(retrieved) == 2


def test_retrieve_approved_skills_empty_when_none_saved(
    chroma_path: str,
) -> None:
    """retrieve_approved_skills returns empty list when nothing was saved."""
    retrieved = retrieve_approved_skills(ASSIGNMENT_ID, chroma_path)

    assert retrieved == []


def test_retrieve_approved_skills_isolated_by_assignment(
    chroma_path: str,
    mixed_skills: list[MicroSkill],
) -> None:
    """Skills from one assignment are not returned for another."""
    save_approved_skills(ASSIGNMENT_ID, mixed_skills, chroma_path)

    retrieved = retrieve_approved_skills("different-assignment-999", chroma_path)

    assert retrieved == []


def test_delete_assignment_skills_removes_all(
    chroma_path: str,
    mixed_skills: list[MicroSkill],
) -> None:
    """delete_assignment_skills removes all stored skills for an assignment."""
    save_approved_skills(ASSIGNMENT_ID, mixed_skills, chroma_path)
    delete_assignment_skills(ASSIGNMENT_ID, chroma_path)

    retrieved = retrieve_approved_skills(ASSIGNMENT_ID, chroma_path)
    assert retrieved == []


def test_delete_assignment_skills_does_not_affect_other_assignments(
    chroma_path: str,
    mixed_skills: list[MicroSkill],
) -> None:
    """Deleting one assignment's skills leaves other assignments intact."""
    other_id = "other-assignment-001"
    other_skills = [
        MicroSkill(
            skill_id=1,
            title="Other skill",
            description="Belongs to other assignment.",
            check_type=CheckType.SYNTAX,
            status=SkillStatus.APPROVED,
        )
    ]

    save_approved_skills(ASSIGNMENT_ID, mixed_skills, chroma_path)
    save_approved_skills(other_id, other_skills, chroma_path)
    delete_assignment_skills(ASSIGNMENT_ID, chroma_path)

    remaining = retrieve_approved_skills(other_id, chroma_path)
    assert len(remaining) == 1
    assert remaining[0].skill_id == 1