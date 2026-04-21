from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres import get_session
from app.schemas.sync_log import SyncLogResponse
from app.services.sync_log_service import SyncLogService

router = APIRouter(prefix="/sync-log", tags=["sync-log"])
_svc = SyncLogService()


@router.get("", response_model=list[SyncLogResponse])
async def list_sync_logs(
    status: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=500),
    db: AsyncSession = Depends(get_session),
):
    return await _svc.get_sync_logs(db, status=status, limit=limit)
