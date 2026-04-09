"""Unit tests for SkillVerdict and EvaluationReport models."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from src.app.models.evaluation import EvaluationReport, SkillVerdict


@pytest.fixture
def passing_verdict() -> SkillVerdict:
    """Reusable passing SkillVerdict."""
    return SkillVerdict(
        skill_id=1,
        skill_title="Access array elements",
        passed=True,
        reason="Student correctly uses arr[i] throughout.",
        student_snippet="arr[i] = value;",
        affected_lines=[5, 6],
    )


@pytest.fixture
def failing_verdict() -> SkillVerdict:
    """Reusable failing SkillVerdict."""
    return SkillVerdict(
        skill_id=2,
        skill_title="Use temporary variable",
        passed=False,
        reason="No temporary variable found before overwriting arr[0].",
        fix_hint="Save arr[0] before the loop starts.",
        affected_lines=[18],
    )


@pytest.fixture
def sample_report(
    passing_verdict: SkillVerdict,
    failing_verdict: SkillVerdict,
) -> EvaluationReport:
    """Reusable EvaluationReport with one pass and one fail."""
    return EvaluationReport(
        assignment_id="array-shift-101",
        student_code="int main() { return 0; }",
        verdicts=[passing_verdict, failing_verdict],
    )


def test_skill_verdict_is_passing_true(passing_verdict: SkillVerdict) -> None:
    """is_passing returns True for a passed verdict."""
    assert passing_verdict.is_passing is True


def test_skill_verdict_is_passing_false(failing_verdict: SkillVerdict) -> None:
    """is_passing returns False for a failed verdict."""
    assert failing_verdict.is_passing is False


def test_skill_verdict_defaults() -> None:
    """SkillVerdict defaults student_snippet, fix_hint, and affected_lines."""
    verdict = SkillVerdict(
        skill_id=1,
        skill_title="Test skill",
        passed=True,
        reason="All good.",
    )

    assert verdict.student_snippet == ""
    assert verdict.fix_hint == ""
    assert verdict.affected_lines == []


def test_skill_verdict_missing_reason_raises() -> None:
    """ValidationError raised when reason is missing."""
    with pytest.raises(ValidationError):
        SkillVerdict(
            skill_id=1,
            skill_title="Test",
            passed=True,
        )


def test_evaluation_report_passed_count(sample_report: EvaluationReport) -> None:
    """passed_count returns correct number of passing verdicts."""
    assert sample_report.passed_count == 1


def test_evaluation_report_failed_count(sample_report: EvaluationReport) -> None:
    """failed_count returns correct number of failing verdicts."""
    assert sample_report.failed_count == 1


def test_evaluation_report_total_count(sample_report: EvaluationReport) -> None:
    """total_count returns total number of verdicts."""
    assert sample_report.total_count == 2


@pytest.mark.parametrize("passed_count,total,expected_rate", [
    (2, 2, 1.0),
    (1, 2, 0.5),
    (0, 2, 0.0),
])
def test_evaluation_report_pass_rate(
    passed_count: int,
    total: int,
    expected_rate: float,
) -> None:
    """pass_rate returns correct fraction for various pass/fail combinations."""
    verdicts = [
        SkillVerdict(
            skill_id=i,
            skill_title=f"Skill {i}",
            passed=(i < passed_count),
            reason="test",
        )
        for i in range(total)
    ]
    report = EvaluationReport(
        assignment_id="test-001",
        student_code="some code",
        verdicts=verdicts,
    )

    assert report.pass_rate == expected_rate


def test_evaluation_report_pass_rate_empty_verdicts() -> None:
    """pass_rate returns 0.0 when no verdicts exist."""
    report = EvaluationReport(
        assignment_id="test-001",
        student_code="some code",
    )

    assert report.pass_rate == 0.0


def test_evaluation_report_json_roundtrip(
    sample_report: EvaluationReport,
) -> None:
    """EvaluationReport serializes and deserializes from JSON correctly."""
    json_str = sample_report.model_dump_json()
    restored = EvaluationReport.model_validate_json(json_str)

    assert restored.assignment_id == sample_report.assignment_id
    assert restored.total_count == sample_report.total_count
    assert restored.verdicts[0].skill_id == sample_report.verdicts[0].skill_id