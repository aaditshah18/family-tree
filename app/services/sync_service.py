from uuid import UUID


class SyncService:
    async def sync_member(self, member_id: UUID):
        pass

    async def sync_relationship(self, relationship_id: UUID):
        pass

    async def retry_failed(self):
        pass
