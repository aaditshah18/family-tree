from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.member import FamilyMember
from app.schemas.member import FamilyMemberCreate


class MemberService:
    async def create_member(self, db: AsyncSession, data: FamilyMemberCreate) -> FamilyMember:
        duplicate = await db.execute(
            select(FamilyMember).where(
                FamilyMember.first_name == data.first_name,
                FamilyMember.last_name == data.last_name,
                FamilyMember.date_of_birth == data.date_of_birth,
            )
        )
        if duplicate.scalar_one_or_none() is not None:
            raise HTTPException(
                status_code=409,
                detail=f"Member '{data.first_name} {data.last_name}' with date of birth '{data.date_of_birth}' already exists",
            )

        member = FamilyMember(**data.model_dump())
        db.add(member)
        await db.commit()
        await db.refresh(member)
        return member

    async def get_member(self, db: AsyncSession, member_id: UUID) -> FamilyMember | None:
        result = await db.execute(select(FamilyMember).where(FamilyMember.id == member_id))
        return result.scalar_one_or_none()

    async def get_all_members(self, db: AsyncSession) -> list[FamilyMember]:
        result = await db.execute(select(FamilyMember))
        return list(result.scalars().all())
