from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel


class FamilyMemberBase(BaseModel):
    first_name: str
    last_name: str
    gender: str | None = None
    date_of_birth: date | None = None
    date_of_death: date | None = None
    birthplace: str | None = None
    notes: str | None = None


class FamilyMemberCreate(FamilyMemberBase):
    pass


class FamilyMemberUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    gender: str | None = None
    date_of_birth: date | None = None
    date_of_death: date | None = None
    birthplace: str | None = None
    notes: str | None = None


class FamilyMemberResponse(FamilyMemberBase):
    model_config = {"from_attributes": True}

    id: UUID
    created_at: datetime
    updated_at: datetime
