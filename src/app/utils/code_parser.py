"""Pure utility functions for extracting line information from student code."""

from __future__ import annotations

LINE_NOT_FOUND = -1


def extract_affected_lines(
    student_code: str,
    snippet: str,
) -> list[int]:
    """Find all 1-indexed line numbers in student code that contain the snippet.

    Performs a linear scan over each line and checks if the stripped
    snippet appears within the stripped line. Returns an empty list
    if snippet is empty or no match is found.

    Args:
        student_code: The full raw student submission.
        snippet: A short code fragment to search for within the student code.

    Returns:
        list[int]: Sorted list of 1-indexed line numbers containing the snippet.
                   Empty list if snippet is empty or not found.

    Time complexity: O(n * m) where n = lines, m = len(snippet)
    Space complexity: O(k) where k = number of matched lines
    """
    if not snippet.strip():
        return []

    matched_lines: list[int] = []
    stripped_snippet = snippet.strip()

    for line_number, line in enumerate(student_code.splitlines(), start=1):
        if stripped_snippet in line:
            matched_lines.append(line_number)

    return matched_lines


def get_line_content(
    student_code: str,
    line_number: int,
) -> str:
    """Return the content of a specific 1-indexed line from student code.

    Args:
        student_code: The full raw student submission.
        line_number: 1-indexed line number to retrieve.

    Returns:
        str: The line content stripped of leading/trailing whitespace.
             Empty string if line_number is out of range.

    Time complexity: O(n) where n = number of lines
    Space complexity: O(n)
    """
    if line_number < 1:
        return ""

    all_lines = student_code.splitlines()

    if line_number > len(all_lines):
        return ""

    return all_lines[line_number - 1].strip()


def extract_snippet_from_lines(
    student_code: str,
    affected_lines: list[int],
) -> str:
    """Extract and join the content of multiple 1-indexed lines.

    Used to build the student_snippet field in SkillVerdict when
    the AI returns line numbers but not the snippet text itself.

    Args:
        student_code: The full raw student submission.
        affected_lines: Sorted list of 1-indexed line numbers to extract.

    Returns:
        str: Newline-joined content of the requested lines.
             Empty string if affected_lines is empty.

    Time complexity: O(n + k) where n = lines, k = affected lines count
    Space complexity: O(n)
    """
    if not affected_lines:
        return ""

    all_lines = student_code.splitlines()
    total_lines = len(all_lines)

    # Only join valid lines — filter out-of-range line numbers
    valid_lines = [
        all_lines[line_number - 1]
        for line_number in affected_lines
        if 1 <= line_number <= total_lines
    ]

    return "\n".join(valid_lines)


def count_lines(student_code: str) -> int:
    """Return the total number of lines in student code.

    Args:
        student_code: The full raw student submission.

    Returns:
        int: Total line count. Returns 0 for empty input.

    Time complexity: O(n)
    Space complexity: O(1)
    """
    if not student_code.strip():
        return 0

    return len(student_code.splitlines())