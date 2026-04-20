"""uq_member_name_dob

Revision ID: d708315388a2
Revises: 0bbf86d15299
Create Date: 2026-04-20 13:59:50.884456

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "d708315388a2"
down_revision: Union[str, Sequence[str], None] = "0bbf86d15299"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_member_first_last_dob",
        "family_members",
        ["first_name", "last_name", "date_of_birth"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_member_first_last_dob", "family_members", type_="unique")
