"""Phase 2 service — evaluates student code against approved micro-skills."""

from __future__ import annotations

import json
import logging
import re

from groq import Groq

from src.app.models.evaluation import EvaluationReport, SkillVerdict
from src.app.models.micro_skill import MicroSkill
from src.app.utils.prompt_builder import build_evaluation_prompt

logger = logging.getLogger(__name__)

MAX_TOKENS = 2048
TEMPERATURE = 0.2


def _strip_line_numbers_from_snippet(snippet: str) -> str:
    """Remove line number prefixes (e.g., '   7: ') from each line of the snippet.

    Args:
        snippet: The raw snippet string possibly containing line numbers.

    Returns:
        str: Clean code without the leading numbers.
    """
    if not snippet:
        return ""
    lines = snippet.splitlines()
    cleaned_lines = []
    for line in lines:
        # Matches optional spaces, digits, colon, optional space
        cleaned = re.sub(r"^\s*\d+:\s?", "", line)
        cleaned_lines.append(cleaned)
    return "\n".join(cleaned_lines)


def _parse_verdicts_from_response(
    raw_content: str,
    approved_skills: list[MicroSkill],
) -> list[SkillVerdict]:
    """Parse Groq API response into a list of SkillVerdict instances.

    Expects a JSON object with a top-level "verdicts" array.
    Malformed individual verdict records are skipped with a warning.
    Missing fix_hint is replaced with an empty string for passing skills.

    Args:
        raw_content: Raw string response from the Groq API.
        approved_skills: Used to validate that returned skill_ids are known.

    Returns:
        list[SkillVerdict]: Parsed verdicts for each evaluated skill.

    Raises:
        ValueError: If JSON is malformed or "verdicts" key is missing.

    Time complexity: O(n) where n = number of verdicts in response
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

    if "verdicts" not in parsed:
        raise ValueError("Groq response missing required 'verdicts' key")

    known_skill_ids: set[int] = {skill.skill_id for skill in approved_skills}
    verdicts: list[SkillVerdict] = []

    for record in parsed["verdicts"]:
        try:
            skill_id = int(record["skill_id"])

            if skill_id not in known_skill_ids:
                logger.warning(
                    "Skipping verdict with unknown skill_id",
                    extra={"skill_id": skill_id},
                )
                continue

            raw_snippet = str(record.get("student_snippet", ""))
            cleaned_snippet = _strip_line_numbers_from_snippet(raw_snippet)

            verdict = SkillVerdict(
                skill_id=skill_id,
                skill_title=str(record.get("skill_title", "")),
                passed=bool(record["passed"]),
                reason=str(record["reason"]),
                student_snippet=cleaned_snippet,
                fix_hint=str(record.get("fix_hint", "")),
                affected_lines=[
                    int(line) for line in record.get("affected_lines", [])
                ],
            )
            verdicts.append(verdict)
        except (KeyError, ValueError, TypeError) as error:
            logger.warning(
                "Skipping malformed verdict record",
                extra={"record": record, "error": str(error)},
            )

    return verdicts


def evaluate_submission(
    assignment_id: str,
    student_code: str,
    approved_skills: list[MicroSkill],
    groq_api_key: str,
    groq_model: str,
) -> EvaluationReport:
    """Call Groq API (Phase 2) to evaluate student code against approved skills.

    This is the hard enforcement point — evaluation only proceeds when
    approved_skills is non-empty. The model is instructed to return
    per-skill verdicts with hints only. Full corrected solutions are
    explicitly forbidden in the prompt.

    Args:
        assignment_id: Unique assignment identifier for the report.
        student_code: The raw code submitted by the student.
        approved_skills: Teacher-approved micro-skills to evaluate against.
        groq_api_key: Groq API authentication key.
        groq_model: Groq model identifier string.

    Returns:
        EvaluationReport: Full report with one SkillVerdict per approved skill.

    Raises:
        ValueError: If approved_skills is empty — evaluation cannot proceed.
        ValueError: If the API response cannot be parsed into valid verdicts.
        groq.APIError: If the Groq API call fails.
    """
    if not approved_skills:
        raise ValueError(
            "Evaluation cannot proceed — no approved micro-skills found. "
            "The teacher must approve at least one skill before evaluation."
        )

    prompt = build_evaluation_prompt(student_code, approved_skills)
    client = Groq(api_key=groq_api_key)

    logger.info(
        "Calling Groq API for Phase 2 evaluation",
        extra={
            "assignment_id": assignment_id,
            "model": groq_model,
            "approved_skill_count": len(approved_skills),
        },
    )

    try:
        response = client.chat.completions.create(
            model=groq_model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert computer science educator evaluating "
                        "student code. Always respond with valid JSON only. "
                        "Never include the full corrected solution in your response. "
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
            "Groq API call failed during Phase 2",
            extra={"assignment_id": assignment_id, "error": str(error)},
        )
        raise

    raw_content = response.choices[0].message.content or ""

    logger.info(
        "Groq API Phase 2 response received",
        extra={
            "assignment_id": assignment_id,
            "response_length": len(raw_content),
        },
    )

    verdicts = _parse_verdicts_from_response(raw_content, approved_skills)

    report = EvaluationReport(
        assignment_id=assignment_id,
        student_code=student_code,
        verdicts=verdicts,
    )

    logger.info(
        "Evaluation report generated",
        extra={
            "assignment_id": assignment_id,
            "passed_count": report.passed_count,
            "failed_count": report.failed_count,
            "total_count": report.total_count,
        },
    )

    return report