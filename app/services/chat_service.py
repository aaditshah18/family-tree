from uuid import UUID


class ChatService:
    async def get_session(self, session_id: UUID):
        pass

    async def list_sessions(self):
        pass

    async def create_session(self, data):
        pass

    async def get_messages(self, session_id: UUID):
        pass

    async def add_message(self, session_id: UUID, data):
        pass
