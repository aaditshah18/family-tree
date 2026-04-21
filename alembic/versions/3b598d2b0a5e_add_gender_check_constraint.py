"""add_gender_check_constraint

Revision ID: 3b598d2b0a5e
Revises: 0001
Create Date: 2026-04-21 14:43:00.087930

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "3b598d2b0a5e"
down_revision: Union[str, Sequence[str], None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_check_constraint(
        "ck_member_gender",
        "family_members",
        "gender IN ('Male', 'Female', 'Other')",
    )


def downgrade() -> None:
    op.drop_constraint("ck_member_gender", "family_members", type_="check")
