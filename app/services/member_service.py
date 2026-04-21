from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select, or_, func
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

    async def get_all_members(
        self, db: AsyncSession, search: str | None = None
    ) -> list[FamilyMember]:
        query = select(FamilyMember)
        if search:
            term = f"%{search}%"
            full_name = func.concat(FamilyMember.first_name, " ", FamilyMember.last_name)
            query = query.where(
                or_(
                    FamilyMember.first_name.ilike(term),
                    FamilyMember.last_name.ilike(term),
                    full_name.ilike(term),
                )
            )
        result = await db.execute(query)
        return list(result.scalars().all())
