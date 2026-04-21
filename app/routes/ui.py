from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres import get_session
from app.services.member_service import MemberService
from app.services.sync_log_service import SyncLogService

templates = Jinja2Templates(directory="templates")
router = APIRouter(tags=["ui"])
_sync_log_svc = SyncLogService()
_member_svc = MemberService()


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@router.get("/sync-log", response_class=HTMLResponse)
async def sync_log_page(request: Request):
    return templates.TemplateResponse(request=request, name="sync_log.html")


@router.get("/sync-log/table", response_class=HTMLResponse)
async def sync_log_table(
    request: Request,
    status: str | None = Query(default=None),
    db: AsyncSession = Depends(get_session),
):
    rows = await _sync_log_svc.get_sync_logs(db, status=status or None, limit=50)
    return templates.TemplateResponse(
        request=request,
        name="partials/sync_log_table.html",
        context={"rows": rows},
    )


@router.get("/members/search", response_class=HTMLResponse)
async def member_search(
    request: Request,
    q: str = Query(default=""),
    slot: str = Query(default="member_id_1"),
    db: AsyncSession = Depends(get_session),
):
    members = await _member_svc.get_all_members(db, search=q if q else None)
    return templates.TemplateResponse(
        request=request,
        name="partials/member_search_results.html",
        context={"members": members, "query": q, "slot": slot},
    )
