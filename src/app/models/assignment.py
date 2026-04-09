"""Assignment domain model representing a coding exercise."""

from __future__ import annotations

from pydantic import BaseModel, Field


class Assignment(BaseModel):
    """A coding assignment with description, starter code, and test cases.

    This is the core entity that triggers Phase 1 (micro-skill generation).
    """

    id: str = Field(..., description="Unique assignment identifier")
    title: str = Field(..., min_length=1, description="Human-readable title")
    description: str = Field(..., min_length=1, description="Problem statement")
    language: str = Field(
        default="python",
        description="Programming language (python, c, java, etc.)",
    )
    starter_code: str = Field(
        default="",
        description="Boilerplate or starter code provided to students",
    )
    test_cases: list[str] = Field(
        default_factory=list,
        description="Visible test cases or input/output examples",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "array-shift-101",
                    "title": "Array Left Shift",
                    "description": "Shift all elements in an array to the left by one position.",
                    "language": "c",
                    "starter_code": "#include <stdio.h>\n\nint main() {\n    int arr[5];\n    // Your code here\n    return 0;\n}",
                    "test_cases": ["Input: 1 2 3 4 5 -> Output: 2 3 4 5 1"],
                }
            ]
        }
    }