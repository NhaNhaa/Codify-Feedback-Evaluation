"""Micro-skill domain models for Phase 1 skill generation and review."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class CheckType(str, Enum):
    """Categorizes how a micro-skill is evaluated."""

    SYNTAX = "syntax"
    INPUT_OUTPUT = "input_output"
    LOGIC = "logic"


class SkillStatus(str, Enum):
    """Approval state of a micro-skill set by the teacher."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class MicroSkill(BaseModel):
    """A single evaluatable skill candidate generated in Phase 1.

    Each skill targets one specific learning concept and is tied
    to a check type to guide consistent AI evaluation in Phase 2.
    """

    skill_id: int = Field(..., description="Sequential numeric identifier")
    title: str = Field(..., min_length=1, description="Short skill title")
    description: str = Field(
        ...,
        min_length=1,
        description="What the student must demonstrate",
    )
    check_type: CheckType = Field(
        ...,
        description="Evaluation category: syntax, input_output, or logic",
    )
    status: SkillStatus = Field(
        default=SkillStatus.PENDING,
        description="Teacher approval state",
    )
    _original_skill_id: int | None = None  # Internal — for regenerate lookup

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "skill_id": 1,
                    "title": "Access array elements using index",
                    "description": "Student must use arr[i] syntax to read or write array elements.",
                    "check_type": "logic",
                    "status": "pending",
                }
            ]
        }
    }

    def approve(self) -> MicroSkill:
        """Return a new MicroSkill instance with status set to APPROVED.

        Returns:
            MicroSkill: Approved copy of this skill.
        """
        return self.model_copy(update={"status": SkillStatus.APPROVED})

    def reject(self) -> MicroSkill:
        """Return a new MicroSkill instance with status set to REJECTED.

        Returns:
            MicroSkill: Rejected copy of this skill.
        """
        return self.model_copy(update={"status": SkillStatus.REJECTED})

    @property
    def is_approved(self) -> bool:
        """Return True if the teacher has approved this skill."""
        return self.status == SkillStatus.APPROVED

    @property
    def is_pending(self) -> bool:
        """Return True if this skill has not yet been reviewed."""
        return self.status == SkillStatus.PENDING