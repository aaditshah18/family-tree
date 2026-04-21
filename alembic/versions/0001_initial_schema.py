"""initial_schema

Revision ID: 0001
Revises:
Create Date: 2026-04-21

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- family_members ---
    op.create_table(
        "family_members",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column("gender", sa.String(20), nullable=True),
        sa.Column("date_of_birth", sa.Date(), nullable=True),
        sa.Column("date_of_death", sa.Date(), nullable=True),
        sa.Column("birthplace", sa.String(255), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("first_name", "last_name", "date_of_birth", name="uq_member_first_last_dob"),
    )
    op.create_index("ix_family_members_last_first", "family_members", ["last_name", "first_name"])

    # --- family_relationships ---
    op.create_table(
        "family_relationships",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("member_id_1", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("member_id_2", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("relationship_type", sa.String(50), nullable=False),
        sa.Column("bidirectional", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["member_id_1"], ["family_members.id"]),
        sa.ForeignKeyConstraint(["member_id_2"], ["family_members.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("member_id_1", "member_id_2", "relationship_type", name="uq_relationship"),
        sa.CheckConstraint("member_id_1 != member_id_2", name="ck_no_self_relationship"),
    )
    op.create_index("ix_family_relationships_member_id_1", "family_relationships", ["member_id_1"])
    op.create_index("ix_family_relationships_member_id_2", "family_relationships", ["member_id_2"])

    # --- chat_sessions ---
    op.create_table(
        "chat_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("anchor_member_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(255), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["anchor_member_id"], ["family_members.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_chat_sessions_anchor_member_id", "chat_sessions", ["anchor_member_id"])
    op.create_index("ix_chat_sessions_created_at_desc", "chat_sessions", ["created_at"])

    # --- chat_messages ---
    op.create_table(
        "chat_messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("tool_call_data", postgresql.JSONB(), nullable=True),
        sa.Column("query_type", sa.String(50), nullable=True),
        sa.Column("falkordb_query", sa.Text(), nullable=True),
        sa.Column("llm_model", sa.String(100), nullable=True),
        sa.Column("token_count", sa.Integer(), nullable=True),
        sa.Column("sequence_order", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["chat_sessions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_chat_messages_session_sequence", "chat_messages", ["session_id", "sequence_order"])

    # --- sync_log ---
    op.create_table(
        "sync_log",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("entity_type", sa.String(50), nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("operation", sa.String(20), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_sync_log_status_attempts", "sync_log", ["status", "attempts"])

    # --- llm_audit_log ---
    op.create_table(
        "llm_audit_log",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("message_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("agent_node", sa.String(100), nullable=False),
        sa.Column("llm_provider", sa.String(50), nullable=False),
        sa.Column("llm_model", sa.String(100), nullable=False),
        sa.Column("prompt_tokens", sa.Integer(), nullable=True),
        sa.Column("completion_tokens", sa.Integer(), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["chat_sessions.id"]),
        sa.ForeignKeyConstraint(["message_id"], ["chat_messages.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_llm_audit_log_session_id", "llm_audit_log", ["session_id"])
    op.create_index("ix_llm_audit_log_created_at_desc", "llm_audit_log", ["created_at"])


def downgrade() -> None:
    op.drop_table("llm_audit_log")
    op.drop_table("sync_log")
    op.drop_table("chat_messages")
    op.drop_table("chat_sessions")
    op.drop_table("family_relationships")
    op.drop_table("family_members")
