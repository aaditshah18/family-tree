from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.models.enums import ChatSessionStatus, MessageRole


class ChatSessionCreate(BaseModel):
    anchor_member_id: UUID
    title: str | None = None


class ChatSessionUpdate(BaseModel):
    title: str | None = None
    status: ChatSessionStatus | None = None


class ChatSessionResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID
    anchor_member_id: UUID
    title: str | None = None
    status: str
    created_at: datetime
    updated_at: datetime


class ChatMessageCreate(BaseModel):
    role: MessageRole
    content: str
    tool_call_data: dict | None = None
    query_type: str | None = None
    falkordb_query: str | None = None
    llm_model: str | None = None
    token_count: int | None = None


class ChatMessageResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID
    session_id: UUID
    role: str
    content: str
    tool_call_data: dict | None = None
    query_type: str | None = None
    falkordb_query: str | None = None
    llm_model: str | None = None
    token_count: int | None = None
    sequence_order: int
    created_at: datetime
