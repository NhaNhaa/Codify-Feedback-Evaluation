"""Phase 1 service — generates candidate micro-skills via Groq API."""

from __future__ import annotations

import json
import logging

from groq import Groq

from src.app.models.assignment import Assignment
from src.app.models.micro_skill import CheckType, MicroSkill, SkillStatus
from src.app.utils.prompt_builder import build_skill_generation_prompt

logger = logging.getLogger(__name__)

MAX_TOKENS = 1024
TEMPERATURE = 0.3


def _parse_skills_from_response(raw_content: str) -> list[MicroSkill]:
    """Parse the Groq API response into a list of MicroSkill instances.

    Expects a JSON object with a top-level "micro_skills" array.
    Each element must contain skill_id, title, description, check_type.

    Args:
        raw_content: Raw string response from the Groq API.

    Returns:
        list[MicroSkill]: Parsed candidate skills with PENDING status.

    Raises:
        ValueError: If JSON is malformed or required fields are missing.

    Time complexity: O(n) where n = number of skills in response
    Space complexity: O(n)
    """
    try:
        parsed = json.loads(raw_content)
    except json.JSONDecodeError as error:
        logger.error(
            "Failed to parse Groq response as JSON",
            extra={"error": str(error), "raw_content": raw_content[:200]},
        )
        raise ValueError("Groq response is not valid JSON") from error

    if "micro_skills" not in parsed:
        raise ValueError(
            "Groq response missing required 'micro_skills' key"
        )

    candidate_skills: list[MicroSkill] = []

    for record in parsed["micro_skills"]:
        try:
            skill = MicroSkill(
                skill_id=record["skill_id"],
                title=record["title"],
                description=record["description"],
                check_type=CheckType(record["check_type"]),
                status=SkillStatus.PENDING,
            )
            candidate_skills.append(skill)
        except (KeyError, ValueError) as error:
            logger.warning(
                "Skipping malformed skill record",
                extra={"record": record, "error": str(error)},
            )

    return candidate_skills


def generate_candidate_skills(
    assignment: Assignment,
    groq_api_key: str,
    groq_model: str,
) -> list[MicroSkill]:
    """Call Groq API (Phase 1) to generate candidate micro-skills.

    Sends the assignment details to the model and parses the structured
    JSON response into MicroSkill instances. All returned skills have
    PENDING status — the teacher must approve each one before they
    can be used in student evaluation.

    Args:
        assignment: The assignment to generate micro-skills for.
        groq_api_key: Groq API authentication key.
        groq_model: Groq model identifier string.

    Returns:
        list[MicroSkill]: Candidate skills with PENDING status.
                          Empty list if the model returns no valid skills.

    Raises:
        ValueError: If the API response cannot be parsed into valid skills.
        groq.APIError: If the Groq API call fails.
    """
    prompt = build_skill_generation_prompt(assignment)

    client = Groq(api_key=groq_api_key)

    logger.info(
        "Calling Groq API for Phase 1 skill generation",
        extra={
            "assignment_id": assignment.id,
            "model": groq_model,
        },
    )

    try:
        response = client.chat.completions.create(
            model=groq_model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert computer science educator. "
                        "Always respond with valid JSON only. "
                        "No markdown. No explanation outside the JSON."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE,
        )
    except Exception as error:
        logger.error(
            "Groq API call failed during Phase 1",
            extra={"assignment_id": assignment.id, "error": str(error)},
        )
        raise

    raw_content = response.choices[0].message.content or ""

    logger.info(
        "Groq API Phase 1 response received",
        extra={
            "assignment_id": assignment.id,
            "response_length": len(raw_content),
        },
    )

    candidate_skills = _parse_skills_from_response(raw_content)

    logger.info(
        "Candidate skills generated",
        extra={
            "assignment_id": assignment.id,
            "skill_count": len(candidate_skills),
        },
    )

    return candidate_skills