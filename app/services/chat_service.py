from uuid import UUID
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat import ChatMessage, ChatSession
from app.schemas.chat import ChatMessageCreate, ChatSessionCreate, ChatSessionUpdate


class ChatService:
    async def create_session(self, db: AsyncSession, data: ChatSessionCreate) -> ChatSession:
        session = ChatSession(
            anchor_member_id=data.anchor_member_id,
            title=data.title,
            status="active",
        )
        db.add(session)
        await db.commit()
        await db.refresh(session)
        return session

    async def get_session(self, db: AsyncSession, session_id: UUID) -> ChatSession | None:
        stmt = select(ChatSession).where(ChatSession.id == session_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_sessions(self, db: AsyncSession) -> list[ChatSession]:
        stmt = select(ChatSession).order_by(ChatSession.created_at.desc())
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def update_session(
        self, db: AsyncSession, session_id: UUID, data: ChatSessionUpdate
    ) -> ChatSession | None:
        session = await self.get_session(db, session_id)
        if session is None:
            return None

        update_data = data.model_dump(exclude_unset=True)
        if "title" in update_data:
            session.title = update_data["title"]
        if "status" in update_data:
            session.status = update_data["status"]
        session.updated_at = datetime.now(timezone.utc)

        await db.commit()
        await db.refresh(session)
        return session

    async def add_message(
        self, db: AsyncSession, session_id: UUID, data: ChatMessageCreate
    ) -> ChatMessage:
        stmt = select(func.max(ChatMessage.sequence_order)).where(
            ChatMessage.session_id == session_id
        )
        result = await db.execute(stmt)
        next_sequence_order = (result.scalar() or 0) + 1

        message = ChatMessage(
            session_id=session_id,
            role=data.role,
            content=data.content,
            tool_call_data=data.tool_call_data,
            query_type=data.query_type,
            falkordb_query=data.falkordb_query,
            llm_model=data.llm_model,
            token_count=data.token_count,
            sequence_order=next_sequence_order,
        )
        db.add(message)
        await db.commit()
        await db.refresh(message)
        return message

    async def get_messages(
        self, db: AsyncSession, session_id: UUID
    ) -> list[ChatMessage]:
        stmt = (
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.sequence_order.asc())
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())
