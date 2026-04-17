from uuid import UUID


class MemberService:
    async def get_member(self, member_id: UUID):
        pass

    async def list_members(self):
        pass

    async def create_member(self, data):
        pass

    async def update_member(self, member_id: UUID, data):
        pass

    async def delete_member(self, member_id: UUID):
        pass
