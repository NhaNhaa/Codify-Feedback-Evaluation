"""Repository for persisting and retrieving micro-skill review states as JSON."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from src.app.models.micro_skill import MicroSkill, SkillStatus

logger = logging.getLogger(__name__)

SKILLS_SUBDIR = "skills"


def _resolve_skills_dir(data_dir: str) -> Path:
    """Resolve and create the skills storage directory if absent.

    Args:
        data_dir: Root data directory from settings.

    Returns:
        Path: Resolved path to the skills subdirectory.

    Time complexity: O(1)
    Space complexity: O(1)
    """
    skills_dir = Path(data_dir) / SKILLS_SUBDIR
    skills_dir.mkdir(parents=True, exist_ok=True)
    return skills_dir


def _build_skills_path(data_dir: str, assignment_id: str) -> Path:
    """Build the full file path for a given assignment's skill review state.

    Args:
        data_dir: Root data directory from settings.
        assignment_id: Unique assignment identifier.

    Returns:
        Path: Full path to the skills JSON file.

    Time complexity: O(1)
    Space complexity: O(1)
    """
    skills_dir = _resolve_skills_dir(data_dir)
    return skills_dir / f"{assignment_id}_skills.json"


def save_skill_review_state(
    assignment_id: str,
    skills: list[MicroSkill],
    data_dir: str,
) -> None:
    """Persist the full list of micro-skills with their review states to disk.

    Idempotent: overwrites the existing file for the assignment on each call.
    Stores all skills regardless of status — approved, rejected, and pending.

    Args:
        assignment_id: Unique assignment identifier.
        skills: Full list of MicroSkill instances with current status.
        data_dir: Root data directory from settings.

    Raises:
        OSError: If the file cannot be written.
    """
    file_path = _build_skills_path(data_dir, assignment_id)

    skill_records = [skill.model_dump() for skill in skills]
    payload = json.dumps(skill_records, indent=2)

    try:
        file_path.write_text(payload, encoding="utf-8")
        logger.info(
            "Skill review state saved",
            extra={
                "assignment_id": assignment_id,
                "skill_count": len(skills),
            },
        )
    except OSError as error:
        logger.error(
            "Failed to save skill review state",
            extra={"assignment_id": assignment_id, "error": str(error)},
        )
        raise


def load_skill_review_state(
    assignment_id: str,
    data_dir: str,
) -> list[MicroSkill]:
    """Load all micro-skills and their review states for an assignment.

    Args:
        assignment_id: Unique assignment identifier.
        data_dir: Root data directory from settings.

    Returns:
        list[MicroSkill]: All skills with their current review status.
                          Empty list if no file exists for the assignment.

    Raises:
        ValueError: If the file content cannot be parsed as valid skill JSON.
    """
    file_path = _build_skills_path(data_dir, assignment_id)

    if not file_path.exists():
        logger.debug(
            "Skill review state file not found (expected after reset)",
            extra={"assignment_id": assignment_id},
        )
        return []

    try:
        raw_content = file_path.read_text(encoding="utf-8")
        skill_records = json.loads(raw_content)
        skills = [MicroSkill.model_validate(record) for record in skill_records]
        logger.info(
            "Skill review state loaded",
            extra={
                "assignment_id": assignment_id,
                "skill_count": len(skills),
            },
        )
        return skills
    except (ValueError, KeyError) as error:
        logger.error(
            "Failed to parse skill review state",
            extra={"assignment_id": assignment_id, "error": str(error)},
        )
        raise ValueError(
            f"Invalid skill review state JSON for assignment '{assignment_id}'"
        ) from error


def load_approved_skills(
    assignment_id: str,
    data_dir: str,
) -> list[MicroSkill]:
    """Load only teacher-approved micro-skills for an assignment.

    Filters the full skill review state to return only skills with
    APPROVED status. This enforces the hard rule that AI-generated
    micro-skills must be approved before use in student evaluation.

    Args:
        assignment_id: Unique assignment identifier.
        data_dir: Root data directory from settings.

    Returns:
        list[MicroSkill]: Only approved skills. Empty list if none exist.

    Time complexity: O(n) where n = total number of skills
    Space complexity: O(k) where k = number of approved skills
    """
    all_skills = load_skill_review_state(assignment_id, data_dir)

    approved_skills = [
        skill for skill in all_skills
        if skill.status == SkillStatus.APPROVED
    ]

    logger.info(
        "Approved skills loaded",
        extra={
            "assignment_id": assignment_id,
            "approved_count": len(approved_skills),
            "total_count": len(all_skills),
        },
    )
    return approved_skills


def update_single_skill_status(
    assignment_id: str,
    skill_id: int,
    new_status: SkillStatus,
    data_dir: str,
) -> list[MicroSkill]:
    """Update the review status of one skill and persist the full state.

    Loads the current state, updates the matching skill, then saves.
    If no skill matches skill_id the state is saved unchanged.

    Args:
        assignment_id: Unique assignment identifier.
        skill_id: The skill_id of the MicroSkill to update.
        new_status: The new SkillStatus to apply.
        data_dir: Root data directory from settings.

    Returns:
        list[MicroSkill]: Updated full list of skills after the change.

    Raises:
        ValueError: If the skill review state file is corrupt.
    """
    all_skills = load_skill_review_state(assignment_id, data_dir)

    updated_skills = [
        skill.model_copy(update={"status": new_status})
        if skill.skill_id == skill_id
        else skill
        for skill in all_skills
    ]

    save_skill_review_state(assignment_id, updated_skills, data_dir)

    logger.info(
        "Single skill status updated",
        extra={
            "assignment_id": assignment_id,
            "skill_id": skill_id,
            "new_status": new_status.value,
        },
    )
    return updated_skills