"""Evaluation domain models for Phase 2 per-skill verdict output."""

from __future__ import annotations

from pydantic import BaseModel, Field


class SkillVerdict(BaseModel):
    """Evaluation result for a single micro-skill against student code.

    The evaluator never returns a full corrected solution.
    fix_hint guides the student toward the fix without giving away the answer.
    """

    skill_id: int = Field(..., description="References MicroSkill.skill_id")
    skill_title: str = Field(..., description="Copied from MicroSkill for display")
    passed: bool = Field(..., description="True if student demonstrated this skill")
    reason: str = Field(
        ...,
        min_length=1,
        description="Why the skill passed or failed",
    )
    student_snippet: str = Field(
        default="",
        description="Relevant lines extracted from student code",
    )
    fix_hint: str = Field(
        default="",
        description="Guiding hint toward the fix — never the full solution",
    )
    affected_lines: list[int] = Field(
        default_factory=list,
        description="Line numbers in student code that triggered this verdict",
    )

    @property
    def is_passing(self) -> bool:
        """Return True if the student passed this skill."""
        return self.passed

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "skill_id": 4,
                    "skill_title": "Use a temporary variable during shift",
                    "passed": False,
                    "reason": "Student overwrites arr[0] before saving its value.",
                    "student_snippet": "arr[4] = arr[0];",
                    "fix_hint": "Think about what happens to arr[0] before the loop finishes. Can you save it somewhere first?",
                    "affected_lines": [18],
                }
            ]
        }
    }


class EvaluationReport(BaseModel):
    """Complete Phase 2 evaluation output for a single student submission.

    Contains one SkillVerdict per approved micro-skill.
    """

    assignment_id: str = Field(..., description="References Assignment.id")
    student_code: str = Field(..., min_length=1, description="Raw student submission")
    verdicts: list[SkillVerdict] = Field(
        default_factory=list,
        description="One verdict per approved micro-skill",
    )

    @property
    def passed_count(self) -> int:
        """Return number of skills the student passed.

        Time complexity: O(n) where n = number of verdicts
        Space complexity: O(1)
        """
        return sum(1 for verdict in self.verdicts if verdict.passed)

    @property
    def failed_count(self) -> int:
        """Return number of skills the student failed.

        Time complexity: O(n) where n = number of verdicts
        Space complexity: O(1)
        """
        return sum(1 for verdict in self.verdicts if not verdict.passed)

    @property
    def total_count(self) -> int:
        """Return total number of evaluated skills."""
        return len(self.verdicts)

    @property
    def pass_rate(self) -> float:
        """Return fraction of skills passed as a value between 0.0 and 1.0.

        Returns:
            float: 0.0 if no verdicts exist.

        Time complexity: O(n)
        Space complexity: O(1)
        """
        if self.total_count == 0:
            return 0.0
        return self.passed_count / self.total_count