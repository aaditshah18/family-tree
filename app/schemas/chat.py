from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.models.enums import MessageRole


class ChatSessionBase(BaseModel):
    anchor_member_id: UUID
    title: str | None = None


class ChatSessionCreate(ChatSessionBase):
    pass


class ChatSessionResponse(ChatSessionBase):
    model_config = {"from_attributes": True}

    id: UUID
    status: str
    created_at: datetime
    updated_at: datetime


class ChatMessageBase(BaseModel):
    session_id: UUID
    role: MessageRole
    content: str
    tool_call_data: dict | None = None
    query_type: str | None = None
    falkordb_query: str | None = None
    llm_model: str | None = None
    token_count: int | None = None
    sequence_order: int


class ChatMessageCreate(ChatMessageBase):
    pass


class ChatMessageResponse(ChatMessageBase):
    model_config = {"from_attributes": True}

    id: UUID
    created_at: datetime
