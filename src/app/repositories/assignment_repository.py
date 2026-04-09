"""Repository for persisting and retrieving Assignment entities as JSON files."""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path

from src.app.models.assignment import Assignment

logger = logging.getLogger(__name__)

ASSIGNMENTS_SUBDIR = "assignments"


def _resolve_assignments_dir(data_dir: str) -> Path:
    """Resolve and create the assignments storage directory if absent.

    Args:
        data_dir: Root data directory from settings.

    Returns:
        Path: Resolved path to the assignments subdirectory.

    Time complexity: O(1)
    Space complexity: O(1)
    """
    assignments_dir = Path(data_dir) / ASSIGNMENTS_SUBDIR
    assignments_dir.mkdir(parents=True, exist_ok=True)
    return assignments_dir


def _build_assignment_path(data_dir: str, assignment_id: str) -> Path:
    """Build the full file path for a given assignment id.

    Args:
        data_dir: Root data directory from settings.
        assignment_id: Unique assignment identifier.

    Returns:
        Path: Full path to the assignment JSON file.

    Time complexity: O(1)
    Space complexity: O(1)
    """
    assignments_dir = _resolve_assignments_dir(data_dir)
    return assignments_dir / f"{assignment_id}.json"


def save_assignment(
    assignment: Assignment,
    data_dir: str,
) -> None:
    """Persist an Assignment to disk as a JSON file.

    Idempotent: calling with the same assignment overwrites the existing file.

    Args:
        assignment: The Assignment instance to persist.
        data_dir: Root data directory from settings.

    Raises:
        OSError: If the file cannot be written due to permissions or disk issues.
    """
    file_path = _build_assignment_path(data_dir, assignment.id)

    try:
        file_path.write_text(
            assignment.model_dump_json(indent=2),
            encoding="utf-8",
        )
        logger.info(
            "Assignment saved",
            extra={"assignment_id": assignment.id, "path": str(file_path)},
        )
    except OSError as error:
        logger.error(
            "Failed to save assignment",
            extra={"assignment_id": assignment.id, "error": str(error)},
        )
        raise


def load_assignment(
    assignment_id: str,
    data_dir: str,
) -> Assignment | None:
    """Load an Assignment from disk by its id.

    Args:
        assignment_id: Unique assignment identifier.
        data_dir: Root data directory from settings.

    Returns:
        Assignment: The loaded Assignment instance.
        None: If no file exists for the given id.

    Raises:
        ValueError: If the file content is not valid Assignment JSON.
    """
    file_path = _build_assignment_path(data_dir, assignment_id)

    if not file_path.exists():
        logger.warning(
            "Assignment file not found",
            extra={"assignment_id": assignment_id, "path": str(file_path)},
        )
        return None

    try:
        raw_content = file_path.read_text(encoding="utf-8")
        assignment = Assignment.model_validate_json(raw_content)
        logger.info(
            "Assignment loaded",
            extra={"assignment_id": assignment_id},
        )
        return assignment
    except (ValueError, KeyError) as error:
        logger.error(
            "Failed to parse assignment file",
            extra={"assignment_id": assignment_id, "error": str(error)},
        )
        raise ValueError(
            f"Invalid assignment JSON for id '{assignment_id}'"
        ) from error


def list_assignments(data_dir: str) -> list[Assignment]:
    """Load all assignments from the assignments directory.

    Skips files that fail validation with a warning log — does not raise.

    Args:
        data_dir: Root data directory from settings.

    Returns:
        list[Assignment]: All successfully loaded assignments, sorted by id.

    Time complexity: O(n log n) where n = number of assignment files
    Space complexity: O(n)
    """
    assignments_dir = _resolve_assignments_dir(data_dir)
    loaded_assignments: list[Assignment] = []

    for file_path in sorted(assignments_dir.glob("*.json")):
        try:
            raw_content = file_path.read_text(encoding="utf-8")
            assignment = Assignment.model_validate_json(raw_content)
            loaded_assignments.append(assignment)
        except (ValueError, KeyError) as error:
            logger.warning(
                "Skipping invalid assignment file",
                extra={"path": str(file_path), "error": str(error)},
            )

    logger.info(
        "Assignments listed",
        extra={"count": len(loaded_assignments)},
    )
    return loaded_assignments


def delete_assignment(
    assignment_id: str,
    data_dir: str,
) -> bool:
    """Delete an assignment JSON file from disk.

    Args:
        assignment_id: Unique assignment identifier.
        data_dir: Root data directory from settings.

    Returns:
        bool: True if the file was deleted, False if it did not exist.

    Raises:
        OSError: If the file exists but cannot be deleted.
    """
    file_path = _build_assignment_path(data_dir, assignment_id)

    if not file_path.exists():
        logger.warning(
            "Assignment not found for deletion",
            extra={"assignment_id": assignment_id},
        )
        return False

    try:
        os.remove(file_path)
        logger.info(
            "Assignment deleted",
            extra={"assignment_id": assignment_id},
        )
        return True
    except OSError as error:
        logger.error(
            "Failed to delete assignment",
            extra={"assignment_id": assignment_id, "error": str(error)},
        )
        raise