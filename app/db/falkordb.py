from falkordb import FalkorDB

from app.config import settings

_client: FalkorDB | None = None


def get_client() -> FalkorDB:
    if _client is None:
        raise RuntimeError("FalkorDB client is not connected")
    return _client


async def connect() -> None:
    global _client
    _client = FalkorDB(host=settings.FALKORDB_HOST, port=settings.FALKORDB_PORT)


async def disconnect() -> None:
    global _client
    if _client is not None:
        _client.connection.close()
        _client = None
