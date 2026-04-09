"""Unit tests for Assignment model."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from src.app.models.assignment import Assignment


def test_assignment_creation_with_required_fields() -> None:
    """Assignment creates successfully with only required fields."""
    assignment = Assignment(
        id="test-001",
        title="Test Assignment",
        description="A simple test problem",
    )

    assert assignment.id == "test-001"
    assert assignment.title == "Test Assignment"
    assert assignment.description == "A simple test problem"
    assert assignment.language == "python"  # default
    assert assignment.starter_code == ""    # default
    assert assignment.test_cases == []      # default_factory


def test_assignment_creation_with_all_fields() -> None:
    """Assignment creates successfully with all fields populated."""
    assignment = Assignment(
        id="array-shift-101",
        title="Array Left Shift",
        description="Shift elements left",
        language="c",
        starter_code="int main() { return 0; }",
        test_cases=["Input: 1 2 3 -> Output: 2 3 1"],
    )

    assert assignment.language == "c"
    assert assignment.starter_code == "int main() { return 0; }"
    assert len(assignment.test_cases) == 1


def test_assignment_missing_id_raises() -> None:
    """ValidationError raised when id is missing."""
    with pytest.raises(ValidationError) as exc_info:
        Assignment(
            title="Test",
            description="Test desc",
        )
    
    assert "id" in str(exc_info.value)


def test_assignment_missing_title_raises() -> None:
    """ValidationError raised when title is missing or empty."""
    with pytest.raises(ValidationError):
        Assignment(
            id="test-001",
            title="",  # empty string fails min_length=1
            description="Test desc",
        )


def test_assignment_missing_description_raises() -> None:
    """ValidationError raised when description is missing."""
    with pytest.raises(ValidationError):
        Assignment(
            id="test-001",
            title="Test",
        )


def test_assignment_test_cases_isolation() -> None:
    """Test cases default_factory ensures separate list instances."""
    a1 = Assignment(id="a1", title="T1", description="D1")
    a2 = Assignment(id="a2", title="T2", description="D2")

    a1.test_cases.append("case1")

    assert a1.test_cases == ["case1"]
    assert a2.test_cases == []  # Should not share reference


def test_assignment_json_roundtrip() -> None:
    """Assignment serializes to and deserializes from JSON correctly."""
    original = Assignment(
        id="roundtrip-001",
        title="Round Trip Test",
        description="Testing serialization",
        language="python",
        starter_code="print('hello')",
        test_cases=["input1", "input2"],
    )

    json_str = original.model_dump_json()
    restored = Assignment.model_validate_json(json_str)

    assert restored.id == original.id
    assert restored.title == original.title
    assert restored.test_cases == original.test_cases