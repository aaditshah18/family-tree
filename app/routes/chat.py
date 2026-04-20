from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres import get_session
from app.models.member import FamilyMember
from app.schemas.chat import (
    ChatMessageCreate,
    ChatMessageResponse,
    ChatSessionCreate,
    ChatSessionResponse,
    ChatSessionUpdate,
)
from app.services.chat_service import ChatService

router = APIRouter(prefix="/chat/sessions", tags=["chat"])
chat_service = ChatService()


@router.post("", response_model=ChatSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_chat_session(
    payload: ChatSessionCreate,
    db: AsyncSession = Depends(get_session),
) -> ChatSessionResponse:
    member_result = await db.execute(
        select(FamilyMember.id).where(FamilyMember.id == payload.anchor_member_id)
    )
    if member_result.scalar_one_or_none() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Anchor member not found",
        )

    session = await chat_service.create_session(db, payload)
    return ChatSessionResponse.model_validate(session)


@router.get("", response_model=list[ChatSessionResponse])
async def list_chat_sessions(
    db: AsyncSession = Depends(get_session),
) -> list[ChatSessionResponse]:
    sessions = await chat_service.get_all_sessions(db)
    return [ChatSessionResponse.model_validate(session) for session in sessions]


@router.get("/{id}", response_model=ChatSessionResponse)
async def get_chat_session(
    id: UUID, db: AsyncSession = Depends(get_session)
) -> ChatSessionResponse:
    session = await chat_service.get_session(db, id)
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Chat session not found"
        )
    return ChatSessionResponse.model_validate(session)


@router.patch("/{id}", response_model=ChatSessionResponse)
async def update_chat_session(
    id: UUID,
    payload: ChatSessionUpdate,
    db: AsyncSession = Depends(get_session),
) -> ChatSessionResponse:
    session = await chat_service.update_session(db, id, payload)
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Chat session not found"
        )
    return ChatSessionResponse.model_validate(session)


@router.post(
    "/{id}/messages",
    response_model=ChatMessageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_chat_message(
    id: UUID,
    payload: ChatMessageCreate,
    db: AsyncSession = Depends(get_session),
) -> ChatMessageResponse:
    session = await chat_service.get_session(db, id)
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Chat session not found"
        )

    message = await chat_service.add_message(db, id, payload)
    return ChatMessageResponse.model_validate(message)


@router.get("/{id}/messages", response_model=list[ChatMessageResponse])
async def list_chat_messages(
    id: UUID,
    db: AsyncSession = Depends(get_session),
) -> list[ChatMessageResponse]:
    session = await chat_service.get_session(db, id)
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Chat session not found"
        )

    messages = await chat_service.get_messages(db, id)
    return [ChatMessageResponse.model_validate(message) for message in messages]
