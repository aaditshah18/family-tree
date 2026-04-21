from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.models.enums import RelationshipType


class FamilyRelationshipBase(BaseModel):
    member_id_1: UUID
    member_id_2: UUID
    relationship_type: RelationshipType
    bidirectional: bool = False


class FamilyRelationshipCreate(FamilyRelationshipBase):
    pass


class FamilyRelationshipUpdate(BaseModel):
    relationship_type: RelationshipType | None = None
    bidirectional: bool | None = None


class FamilyRelationshipResponse(FamilyRelationshipBase):
    model_config = {"from_attributes": True}

    id: UUID
    created_at: datetime
