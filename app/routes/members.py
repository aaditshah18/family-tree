from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres import get_session
from app.schemas.member import FamilyMemberCreate, FamilyMemberResponse
from app.services import sync_service
from app.services.member_service import MemberService

router = APIRouter(prefix="/members", tags=["members"])
_svc = MemberService()


@router.post("", response_model=FamilyMemberResponse, status_code=201)
async def create_member(
    data: FamilyMemberCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_session),
):
    member = await _svc.create_member(db, data)
    background_tasks.add_task(sync_service.sync_member_to_knowledge_graph, member.id)
    return member


@router.get("", response_model=list[FamilyMemberResponse])
async def list_members(db: AsyncSession = Depends(get_session)):
    return await _svc.get_all_members(db)


@router.get("/{member_id}", response_model=FamilyMemberResponse)
async def get_member(member_id: UUID, db: AsyncSession = Depends(get_session)):
    member = await _svc.get_member(db, member_id)
    if member is None:
        raise HTTPException(status_code=404, detail="Member not found")
    return member
