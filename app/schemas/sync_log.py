from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class SyncLogResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID
    entity_type: str
    entity_id: UUID
    operation: str
    status: str
    attempts: int
    last_error: str | None
    synced_at: datetime | None
    created_at: datetime
