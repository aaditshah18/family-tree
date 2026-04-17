from sqlalchemy import String, Date, DateTime, ForeignKey, UniqueConstraint, CheckConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
import uuid

from app.models.base import Base


class FamilyRelationship(Base):
    __tablename__ = "family_relationships"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    member_id_1: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("family_members.id"), nullable=False
    )
    member_id_2: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("family_members.id"), nullable=False
    )
    relationship_type: Mapped[str] = mapped_column(String(50), nullable=False)
    start_date: Mapped[Date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[Date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        UniqueConstraint("member_id_1", "member_id_2", "relationship_type", name="uq_relationship"),
        CheckConstraint("member_id_1 != member_id_2", name="ck_no_self_relationship"),
        Index("ix_family_relationships_member_id_1", "member_id_1"),
        Index("ix_family_relationships_member_id_2", "member_id_2"),
    )
