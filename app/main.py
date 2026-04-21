from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.db import postgres, falkordb
from app.routes import members, relationships, chat, ui


@asynccontextmanager
async def lifespan(app: FastAPI):
    await falkordb.connect()
    yield
    await postgres.engine.dispose()
    await falkordb.disconnect()


app = FastAPI(title="Family Tree API", version="1.0.0", lifespan=lifespan)

if Path("static").is_dir():
    app.mount("/static", StaticFiles(directory="static"), name="static")

# UI routes first — no prefix
app.include_router(ui.router)

# API routes
app.include_router(members.router, prefix="/api/v1")
app.include_router(relationships.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {"status": "ok", "db": "connected"}
