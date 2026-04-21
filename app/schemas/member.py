from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel

from app.models.enums import Gender


class FamilyMemberBase(BaseModel):
    first_name: str
    last_name: str
    gender: Gender | None = None
    date_of_birth: date | None = None
    date_of_death: date | None = None
    birthplace: str | None = None
    notes: str | None = None


class FamilyMemberCreate(FamilyMemberBase):
    pass


class FamilyMemberUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    gender: Gender | None = None
    date_of_birth: date | None = None
    date_of_death: date | None = None
    birthplace: str | None = None
    notes: str | None = None


class FamilyMemberResponse(FamilyMemberBase):
    model_config = {"from_attributes": True}

    id: UUID
    created_at: datetime
    updated_at: datetime
