import pytest
from pydantic import ValidationError

from app.schemas.chat import ChatMessageCreate, ChatSessionUpdate


def test_chat_message_create_rejects_invalid_role() -> None:
    with pytest.raises(ValidationError):
        ChatMessageCreate(role="invalid", content="hello")


def test_chat_session_update_rejects_invalid_status() -> None:
    with pytest.raises(ValidationError):
        ChatSessionUpdate(status="closed")


def test_chat_session_update_accepts_valid_status() -> None:
    update = ChatSessionUpdate(status="archived")
    assert update.status is not None
    assert update.status.value == "archived"
