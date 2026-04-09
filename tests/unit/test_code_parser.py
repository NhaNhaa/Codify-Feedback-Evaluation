"""Unit tests for code parser utility functions."""

from __future__ import annotations

import pytest

from src.app.utils.code_parser import (
    count_lines,
    extract_affected_lines,
    extract_snippet_from_lines,
    get_line_content,
)

SAMPLE_C_CODE = """\
#include <stdio.h>

int main() {
    int arr[5];
    int i;
    for(i = 0; i < 5; i++) {
        scanf("%d", &arr[i]);
    }
    arr[4] = arr[0];
    return 0;
}"""


def test_extract_affected_lines_single_match() -> None:
    """Returns correct 1-indexed line for a single matching snippet."""
    result = extract_affected_lines(SAMPLE_C_CODE, "arr[4] = arr[0]")

    assert result == [9]


def test_extract_affected_lines_multiple_matches() -> None:
    """Returns all line numbers when snippet appears on multiple lines."""
    code = "x = 1\nx = 2\ny = 3\nx = 4"
    result = extract_affected_lines(code, "x =")

    assert result == [1, 2, 4]


def test_extract_affected_lines_no_match() -> None:
    """Returns empty list when snippet is not found in student code."""
    result = extract_affected_lines(SAMPLE_C_CODE, "while(true)")

    assert result == []


def test_extract_affected_lines_empty_snippet() -> None:
    """Returns empty list when snippet is an empty string."""
    result = extract_affected_lines(SAMPLE_C_CODE, "")

    assert result == []


def test_extract_affected_lines_whitespace_only_snippet() -> None:
    """Returns empty list when snippet contains only whitespace."""
    result = extract_affected_lines(SAMPLE_C_CODE, "   ")

    assert result == []


def test_extract_affected_lines_first_line() -> None:
    """Correctly identifies a match on line 1."""
    result = extract_affected_lines(SAMPLE_C_CODE, "#include")

    assert result == [1]


@pytest.mark.parametrize("snippet,expected_lines", [
    ("int arr[5]", [4]),
    ("int i", [5]),
    ("return 0", [10]),
])
def test_extract_affected_lines_parametrized(
    snippet: str,
    expected_lines: list[int],
) -> None:
    """extract_affected_lines returns correct lines for various snippets."""
    result = extract_affected_lines(SAMPLE_C_CODE, snippet)

    assert result == expected_lines


def test_get_line_content_valid_line() -> None:
    """Returns correct stripped content for a valid 1-indexed line."""
    result = get_line_content(SAMPLE_C_CODE, 4)

    assert result == "int arr[5];"


def test_get_line_content_first_line() -> None:
    """Returns correct content for line 1."""
    result = get_line_content(SAMPLE_C_CODE, 1)

    assert result == "#include <stdio.h>"


def test_get_line_content_out_of_range() -> None:
    """Returns empty string when line number exceeds total lines."""
    result = get_line_content(SAMPLE_C_CODE, 999)

    assert result == ""


def test_get_line_content_zero_line_number() -> None:
    """Returns empty string for line number zero."""
    result = get_line_content(SAMPLE_C_CODE, 0)

    assert result == ""


def test_get_line_content_negative_line_number() -> None:
    """Returns empty string for negative line numbers."""
    result = get_line_content(SAMPLE_C_CODE, -1)

    assert result == ""


def test_extract_snippet_from_lines_valid() -> None:
    """Returns joined content of valid affected lines."""
    result = extract_snippet_from_lines(SAMPLE_C_CODE, [4, 5])

    assert "int arr[5];" in result
    assert "int i;" in result


def test_extract_snippet_from_lines_empty_list() -> None:
    """Returns empty string when affected_lines is empty."""
    result = extract_snippet_from_lines(SAMPLE_C_CODE, [])

    assert result == ""


def test_extract_snippet_from_lines_out_of_range_filtered() -> None:
    """Silently filters out-of-range line numbers."""
    result = extract_snippet_from_lines(SAMPLE_C_CODE, [1, 999])

    assert "#include <stdio.h>" in result
    assert result.count("\n") == 0  # only one valid line returned


def test_count_lines_normal_code() -> None:
    """Returns correct total line count for multi-line code."""
    result = count_lines(SAMPLE_C_CODE)

    assert result == 11


def test_count_lines_empty_string() -> None:
    """Returns 0 for empty input."""
    result = count_lines("")

    assert result == 0


def test_count_lines_whitespace_only() -> None:
    """Returns 0 for whitespace-only input."""
    result = count_lines("   \n   ")

    assert result == 0


def test_count_lines_single_line() -> None:
    """Returns 1 for single-line code."""
    result = count_lines("int x = 5;")

    assert result == 1