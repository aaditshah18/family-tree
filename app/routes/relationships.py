from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres import get_session
from app.schemas.relationship import FamilyRelationshipCreate, FamilyRelationshipResponse
from app.services import sync_service
from app.services.member_service import MemberService
from app.services.relationship_service import RelationshipService

router = APIRouter(prefix="/relationships", tags=["relationships"])
_svc = RelationshipService()
_member_svc = MemberService()


@router.post("", response_model=FamilyRelationshipResponse, status_code=201)
async def create_relationship(
    data: FamilyRelationshipCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_session),
):
    if data.member_id_1 == data.member_id_2:
        raise HTTPException(status_code=400, detail="member_id_1 and member_id_2 must differ")

    if await _member_svc.get_member(db, data.member_id_1) is None:
        raise HTTPException(status_code=404, detail=f"Member {data.member_id_1} not found")
    if await _member_svc.get_member(db, data.member_id_2) is None:
        raise HTTPException(status_code=404, detail=f"Member {data.member_id_2} not found")

    try:
        rel = await _svc.create_relationship(db, data)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Relationship already exists")

    background_tasks.add_task(sync_service.sync_relationship_to_knowledge_graph, rel.id)
    return rel


@router.get("", response_model=list[FamilyRelationshipResponse])
async def list_relationships(db: AsyncSession = Depends(get_session)):
    return await _svc.get_all_relationships(db)


@router.get("/{relationship_id}", response_model=FamilyRelationshipResponse)
async def get_relationship(relationship_id: UUID, db: AsyncSession = Depends(get_session)):
    rel = await _svc.get_relationship(db, relationship_id)
    if rel is None:
        raise HTTPException(status_code=404, detail="Relationship not found")
    return rel
