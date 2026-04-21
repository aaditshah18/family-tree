from fastapi import APIRouter

from app.routes import members, relationships, chat, sync_log

API_PREFIX = "/api/v1"

api_router = APIRouter(prefix=API_PREFIX)
api_router.include_router(members.router)
api_router.include_router(relationships.router)
api_router.include_router(chat.router)
api_router.include_router(sync_log.router)
