from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(tags=["ui"])
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"title": "Family Tree — Add Data"},
    )


@router.get("/sync-log", response_class=HTMLResponse)
async def sync_log(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="sync_log.html",
        context={"title": "Sync Log"},
    )
