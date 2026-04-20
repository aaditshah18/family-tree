from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.relationship import FamilyRelationship
from app.schemas.relationship import FamilyRelationshipCreate


class RelationshipService:
    async def create_relationship(self, db: AsyncSession, data: FamilyRelationshipCreate) -> FamilyRelationship:
        rel = FamilyRelationship(**data.model_dump())
        db.add(rel)
        await db.commit()
        await db.refresh(rel)
        return rel

    async def get_relationship(self, db: AsyncSession, rel_id: UUID) -> FamilyRelationship | None:
        result = await db.execute(select(FamilyRelationship).where(FamilyRelationship.id == rel_id))
        return result.scalar_one_or_none()

    async def get_all_relationships(self, db: AsyncSession) -> list[FamilyRelationship]:
        result = await db.execute(select(FamilyRelationship))
        return list(result.scalars().all())
