from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db import postgres, falkordb
from app.routes import members, relationships, chat


@asynccontextmanager
async def lifespan(app: FastAPI):
    await falkordb.connect()
    yield
    await postgres.engine.dispose()
    await falkordb.disconnect()


app = FastAPI(title="Family Tree API", version="1.0.0", lifespan=lifespan)

app.include_router(members.router, prefix="/api/v1")
app.include_router(relationships.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {"status": "ok", "db": "connected"}
