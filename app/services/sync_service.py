import asyncio
import logging
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select

from app.db import falkordb as falkordb_db
from app.db.postgres import async_session_factory
from app.models.member import FamilyMember
from app.models.operational import SyncLog
from app.models.relationship import FamilyRelationship

logger = logging.getLogger(__name__)

_MAX_ATTEMPTS = 3
_RETRY_DELAY = 300  # 5 minutes


async def _write_sync_log(
    entity_type: str,
    entity_id: UUID,
    operation: str,
    status: str,
    attempts: int,
    last_error: str | None = None,
) -> None:
    async with async_session_factory() as db:
        log = SyncLog(
            entity_type=entity_type,
            entity_id=entity_id,
            operation=operation,
            status=status,
            attempts=attempts,
            last_error=last_error,
            synced_at=datetime.now(timezone.utc) if status == "success" else None,
        )
        db.add(log)
        await db.commit()


async def sync_member_to_knowledge_graph(member_id: UUID) -> None:
    for attempt in range(1, _MAX_ATTEMPTS + 1):
        try:
            async with async_session_factory() as db:
                result = await db.execute(select(FamilyMember).where(FamilyMember.id == member_id))
                member = result.scalar_one_or_none()
                if member is None:
                    raise ValueError(f"Member {member_id} not found in Postgres")

            graph = falkordb_db.get_client().select_graph("family_tree")
            await asyncio.to_thread(
                graph.query,
                (
                    "MERGE (p:Person {id: $id}) "
                    "SET p.first_name = $first_name, "
                    "    p.last_name = $last_name, "
                    "    p.gender = $gender, "
                    "    p.date_of_birth = $date_of_birth, "
                    "    p.date_of_death = $date_of_death, "
                    "    p.birthplace = $birthplace, "
                    "    p.notes = $notes"
                ),
                {
                    "id": str(member.id),
                    "first_name": member.first_name,
                    "last_name": member.last_name,
                    "gender": member.gender,
                    "date_of_birth": str(member.date_of_birth) if member.date_of_birth else None,
                    "date_of_death": str(member.date_of_death) if member.date_of_death else None,
                    "birthplace": member.birthplace if member.birthplace else None,
                    "notes": member.notes if member.notes else None,
                },
            )

            await _write_sync_log("member", member_id, "CREATE", "success", attempt)
            return

        except Exception as e:
            logger.warning("sync_member attempt %d/%d for %s failed: %s", attempt, _MAX_ATTEMPTS, member_id, e)
            await _write_sync_log("member", member_id, "CREATE", "failed", attempt, str(e))
            if attempt < _MAX_ATTEMPTS:
                await asyncio.sleep(_RETRY_DELAY)


async def sync_relationship_to_knowledge_graph(relationship_id: UUID) -> None:
    for attempt in range(1, _MAX_ATTEMPTS + 1):
        try:
            async with async_session_factory() as db:
                result = await db.execute(
                    select(FamilyRelationship).where(FamilyRelationship.id == relationship_id)
                )
                rel = result.scalar_one_or_none()
                if rel is None:
                    raise ValueError(f"Relationship {relationship_id} not found in Postgres")

            graph = falkordb_db.get_client().select_graph("family_tree")
            cypher = (
                f"MATCH (a:Person {{id: $id1}}), (b:Person {{id: $id2}}) "
                f"CREATE (a)-[:{rel.relationship_type}]->(b)"
            )
            await asyncio.to_thread(
                graph.query,
                cypher,
                {"id1": str(rel.member_id_1), "id2": str(rel.member_id_2)},
            )

            await _write_sync_log("relationship", relationship_id, "CREATE", "success", attempt)
            return

        except Exception as e:
            logger.warning(
                "sync_relationship attempt %d/%d for %s failed: %s",
                attempt, _MAX_ATTEMPTS, relationship_id, e,
            )
            await _write_sync_log("relationship", relationship_id, "CREATE", "failed", attempt, str(e))
            if attempt < _MAX_ATTEMPTS:
                await asyncio.sleep(_RETRY_DELAY)
