from uuid import UUID


class RelationshipService:
    async def get_relationship(self, relationship_id: UUID):
        pass

    async def list_relationships(self, member_id: UUID | None = None):
        pass

    async def create_relationship(self, data):
        pass

    async def update_relationship(self, relationship_id: UUID, data):
        pass

    async def delete_relationship(self, relationship_id: UUID):
        pass
