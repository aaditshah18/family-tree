from types import SimpleNamespace
from uuid import uuid4
from unittest.mock import AsyncMock, Mock

import pytest

from app.models.chat import ChatSession
from app.schemas.chat import ChatMessageCreate, ChatSessionUpdate
from app.services.chat_service import ChatService


@pytest.mark.asyncio
async def test_update_session_uses_enum_value_for_status() -> None:
    service = ChatService()
    session = ChatSession(anchor_member_id=uuid4(), title="Initial", status="active")
    db = AsyncMock()

    service.get_session = AsyncMock(return_value=session)
    payload = ChatSessionUpdate(status="archived")

    updated = await service.update_session(db, uuid4(), payload)

    assert updated is session
    assert session.status == "archived"
    db.commit.assert_awaited_once()
    db.refresh.assert_awaited_once_with(session)


@pytest.mark.asyncio
async def test_add_message_assigns_next_sequence_and_role_value() -> None:
    service = ChatService()
    db = AsyncMock()

    lock_result = Mock()
    max_result = Mock()
    max_result.scalar.return_value = 2
    db.execute = AsyncMock(side_effect=[lock_result, max_result])

    captured = []

    def _capture_add(message) -> None:
        captured.append(message)

    db.add = _capture_add
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    payload = ChatMessageCreate(role="user", content="hello")
    created = await service.add_message(db, uuid4(), payload)

    assert created is captured[0]
    assert created.role == "user"
    assert created.sequence_order == 3
    assert db.execute.await_count == 2
    db.commit.assert_awaited_once()
    db.refresh.assert_awaited_once_with(created)


@pytest.mark.asyncio
async def test_update_session_allows_explicit_title_clear() -> None:
    service = ChatService()
    session = ChatSession(anchor_member_id=uuid4(), title="To be cleared", status="active")
    db = AsyncMock()

    service.get_session = AsyncMock(return_value=session)
    payload = ChatSessionUpdate(title=None)

    updated = await service.update_session(db, uuid4(), payload)

    assert updated is session
    assert session.title is None
    db.commit.assert_awaited_once()
