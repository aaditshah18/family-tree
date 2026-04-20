"""chat_message_sequence_uniqueness

Revision ID: 7c8a9f3f4d12
Revises: 0bbf86d15299
Create Date: 2026-04-20 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7c8a9f3f4d12"
down_revision: Union[str, Sequence[str], None] = "0bbf86d15299"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "uq_chat_messages_session_sequence",
        "chat_messages",
        ["session_id", "sequence_order"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("uq_chat_messages_session_sequence", table_name="chat_messages")
