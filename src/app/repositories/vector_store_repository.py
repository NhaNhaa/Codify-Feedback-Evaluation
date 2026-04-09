"""Repository for storing and retrieving approved micro-skills via ChromaDB."""

from __future__ import annotations

import json
import logging

import chromadb

from src.app.models.micro_skill import CheckType, MicroSkill, SkillStatus

logger = logging.getLogger(__name__)

COLLECTION_NAME = "approved_micro_skills"


def _get_collection(
    chroma_path: str,
) -> chromadb.Collection:
    """Initialise a persistent ChromaDB client and return the skills collection.

    Args:
        chroma_path: Path to the ChromaDB embedded storage directory.

    Returns:
        chromadb.Collection: The approved micro-skills collection.

    Time complexity: O(1)
    Space complexity: O(1)
    """
    # Always create a fresh client per call in repository layer.
    # The Streamlit cached client is managed separately in streamlit_app.py
    # for lock-release purposes during wipe operations.
    client = chromadb.PersistentClient(path=chroma_path)
    return client.get_or_create_collection(name=COLLECTION_NAME)


def _build_document_id(assignment_id: str, skill_id: int) -> str:
    """Build a unique ChromaDB document id for a skill.

    Args:
        assignment_id: Unique assignment identifier.
        skill_id: Numeric skill identifier.

    Returns:
        str: Composite document id in the format assignment_id__skill_id.

    Time complexity: O(1)
    Space complexity: O(1)
    """
    return f"{assignment_id}__{skill_id}"


def save_approved_skills(
    assignment_id: str,
    skills: list[MicroSkill],
    chroma_path: str,
) -> None:
    """Upsert approved micro-skills into ChromaDB for the given assignment.

    Only skills with APPROVED status are stored. Previously upserted
    skills for the same assignment_id and skill_id are overwritten.

    Idempotent: safe to call multiple times with the same skills.

    Args:
        assignment_id: Unique assignment identifier.
        skills: Full list of MicroSkills — only APPROVED ones are stored.
        chroma_path: Path to the ChromaDB embedded storage directory.

    Raises:
        RuntimeError: If ChromaDB upsert fails.
    """
    approved_skills = [
        skill for skill in skills
        if skill.status == SkillStatus.APPROVED
    ]

    if not approved_skills:
        logger.warning(
            "No approved skills to save — skipping vector store upsert",
            extra={"assignment_id": assignment_id},
        )
        return

    collection = _get_collection(chroma_path)

    document_ids = [
        _build_document_id(assignment_id, skill.skill_id)
        for skill in approved_skills
    ]
    documents = [
        f"{skill.title}: {skill.description}"
        for skill in approved_skills
    ]
    metadatas = [
        {
            "assignment_id": assignment_id,
            "skill_id": skill.skill_id,
            "title": skill.title,
            "description": skill.description,
            "check_type": skill.check_type.value,
            "status": skill.status.value,
        }
        for skill in approved_skills
    ]

    try:
        collection.upsert(
            ids=document_ids,
            documents=documents,
            metadatas=metadatas,
        )
        logger.info(
            "Approved skills upserted into vector store",
            extra={
                "assignment_id": assignment_id,
                "upserted_count": len(approved_skills),
            },
        )
    except Exception as error:
        logger.error(
            "ChromaDB upsert failed",
            extra={"assignment_id": assignment_id, "error": str(error)},
        )
        raise RuntimeError(
            f"Failed to upsert skills for assignment '{assignment_id}'"
        ) from error


def retrieve_approved_skills(
    assignment_id: str,
    chroma_path: str,
) -> list[MicroSkill]:
    """Retrieve all approved micro-skills for an assignment from ChromaDB.

    Filters by assignment_id metadata field. Returns skills ordered
    by skill_id ascending.

    Args:
        assignment_id: Unique assignment identifier.
        chroma_path: Path to the ChromaDB embedded storage directory.

    Returns:
        list[MicroSkill]: Approved skills sorted by skill_id.
                          Empty list if none exist for the assignment.

    Raises:
        RuntimeError: If ChromaDB query fails.

    Time complexity: O(n log n) where n = number of retrieved skills
    Space complexity: O(n)
    """
    collection = _get_collection(chroma_path)

    try:
        results = collection.get(
            where={"assignment_id": assignment_id},
            include=["metadatas"],
        )
    except Exception as error:
        logger.error(
            "ChromaDB retrieval failed",
            extra={"assignment_id": assignment_id, "error": str(error)},
        )
        raise RuntimeError(
            f"Failed to retrieve skills for assignment '{assignment_id}'"
        ) from error

    if not results["metadatas"]:
        logger.warning(
            "No approved skills found in vector store",
            extra={"assignment_id": assignment_id},
        )
        return []

    skills: list[MicroSkill] = []

    for metadata in results["metadatas"]:
        skill = MicroSkill(
            skill_id=int(metadata["skill_id"]),
            title=str(metadata["title"]),
            description=str(metadata["description"]),
            check_type=CheckType(metadata["check_type"]),
            status=SkillStatus(metadata["status"]),
        )
        skills.append(skill)

    sorted_skills = sorted(skills, key=lambda skill: skill.skill_id)

    logger.info(
        "Approved skills retrieved from vector store",
        extra={
            "assignment_id": assignment_id,
            "retrieved_count": len(sorted_skills),
        },
    )
    return sorted_skills


def delete_assignment_skills(
    assignment_id: str,
    chroma_path: str,
) -> None:
    """Delete all approved skills for an assignment from ChromaDB.

    Used when an assignment is deleted or skills are fully regenerated.

    Args:
        assignment_id: Unique assignment identifier.
        chroma_path: Path to the ChromaDB embedded storage directory.

    Raises:
        RuntimeError: If ChromaDB deletion fails.
    """
    collection = _get_collection(chroma_path)

    try:
        results = collection.get(
            where={"assignment_id": assignment_id},
            include=["metadatas"],
        )

        if not results["ids"]:
            logger.warning(
                "No skills found to delete in vector store",
                extra={"assignment_id": assignment_id},
            )
            return

        collection.delete(ids=results["ids"])

        logger.info(
            "Assignment skills deleted from vector store",
            extra={
                "assignment_id": assignment_id,
                "deleted_count": len(results["ids"]),
            },
        )
    except Exception as error:
        logger.error(
            "ChromaDB deletion failed",
            extra={"assignment_id": assignment_id, "error": str(error)},
        )
        raise RuntimeError(
            f"Failed to delete skills for assignment '{assignment_id}'"
        ) from error