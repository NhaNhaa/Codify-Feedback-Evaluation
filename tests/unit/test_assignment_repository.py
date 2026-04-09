"""Unit tests for assignment repository."""

from __future__ import annotations

import pytest

from src.app.models.assignment import Assignment
from src.app.repositories.assignment_repository import (
    delete_assignment,
    list_assignments,
    load_assignment,
    save_assignment,
)


@pytest.fixture
def data_dir(tmp_path: pytest.TempPathFactory) -> str:
    """Temporary data directory isolated per test."""
    return str(tmp_path)


@pytest.fixture
def sample_assignment() -> Assignment:
    """Reusable Assignment instance."""
    return Assignment(
        id="test-repo-001",
        title="Repo Test Assignment",
        description="Testing repository persistence.",
        language="python",
        starter_code="print('hello')",
        test_cases=["Input: none -> Output: hello"],
    )


def test_save_assignment_creates_file(
    data_dir: str,
    sample_assignment: Assignment,
) -> None:
    """save_assignment writes a JSON file to the assignments directory."""
    from pathlib import Path

    save_assignment(sample_assignment, data_dir)

    file_path = Path(data_dir) / "assignments" / f"{sample_assignment.id}.json"
    assert file_path.exists()


def test_save_assignment_is_idempotent(
    data_dir: str,
    sample_assignment: Assignment,
) -> None:
    """Calling save_assignment twice does not raise and overwrites cleanly."""
    save_assignment(sample_assignment, data_dir)
    save_assignment(sample_assignment, data_dir)

    loaded = load_assignment(sample_assignment.id, data_dir)
    assert loaded is not None
    assert loaded.id == sample_assignment.id


def test_load_assignment_returns_correct_instance(
    data_dir: str,
    sample_assignment: Assignment,
) -> None:
    """load_assignment returns the same Assignment that was saved."""
    save_assignment(sample_assignment, data_dir)

    loaded = load_assignment(sample_assignment.id, data_dir)

    assert loaded is not None
    assert loaded.id == sample_assignment.id
    assert loaded.title == sample_assignment.title
    assert loaded.test_cases == sample_assignment.test_cases


def test_load_assignment_returns_none_when_not_found(
    data_dir: str,
) -> None:
    """load_assignment returns None when no file exists for the given id."""
    result = load_assignment("nonexistent-id", data_dir)

    assert result is None


def test_load_assignment_raises_on_invalid_json(
    data_dir: str,
) -> None:
    """load_assignment raises ValueError when file contains invalid JSON."""
    from pathlib import Path

    assignments_dir = Path(data_dir) / "assignments"
    assignments_dir.mkdir(parents=True, exist_ok=True)
    bad_file = assignments_dir / "bad-assignment.json"
    bad_file.write_text("{ not valid json }", encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid assignment JSON"):
        load_assignment("bad-assignment", data_dir)


def test_list_assignments_empty_dir(data_dir: str) -> None:
    """list_assignments returns empty list when no files exist."""
    result = list_assignments(data_dir)

    assert result == []


def test_list_assignments_returns_all_saved(
    data_dir: str,
    sample_assignment: Assignment,
) -> None:
    """list_assignments returns all saved assignments."""
    second_assignment = Assignment(
        id="test-repo-002",
        title="Second Assignment",
        description="Another test.",
    )

    save_assignment(sample_assignment, data_dir)
    save_assignment(second_assignment, data_dir)

    result = list_assignments(data_dir)

    assert len(result) == 2


def test_list_assignments_skips_invalid_files(
    data_dir: str,
    sample_assignment: Assignment,
) -> None:
    """list_assignments skips corrupted files and returns valid ones."""
    from pathlib import Path

    save_assignment(sample_assignment, data_dir)

    bad_file = Path(data_dir) / "assignments" / "corrupt.json"
    bad_file.write_text("{ bad json }", encoding="utf-8")

    result = list_assignments(data_dir)

    assert len(result) == 1
    assert result[0].id == sample_assignment.id


def test_delete_assignment_removes_file(
    data_dir: str,
    sample_assignment: Assignment,
) -> None:
    """delete_assignment removes the file and returns True."""
    save_assignment(sample_assignment, data_dir)

    result = delete_assignment(sample_assignment.id, data_dir)

    assert result is True
    assert load_assignment(sample_assignment.id, data_dir) is None


def test_delete_assignment_returns_false_when_not_found(
    data_dir: str,
) -> None:
    """delete_assignment returns False when the file does not exist."""
    result = delete_assignment("nonexistent-id", data_dir)

    assert result is False