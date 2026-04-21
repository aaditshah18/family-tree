from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.operational import SyncLog


class SyncLogService:
    async def get_sync_logs(
        self,
        db: AsyncSession,
        status: str | None = None,
        limit: int = 50,
    ) -> list[SyncLog]:
        query = select(SyncLog).order_by(desc(SyncLog.created_at)).limit(limit)
        if status:
            query = query.where(SyncLog.status == status)
        result = await db.execute(query)
        return list(result.scalars().all())
