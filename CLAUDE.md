# Family Tree API — Claude Code Context

## Project Overview
FastAPI backend for a family tree application with dual-write persistence:
- **PostgreSQL** (source of truth) — all structured data
- **FalkorDB** (graph layer) — synced asynchronously for graph traversal queries
- **LangGraph + Gemini** (agent layer, WIP) — natural-language query interface over the graph

## Tech Stack
| Layer | Tech |
|---|---|
| Runtime | Python 3.13.9 |
| API | FastAPI (async/await throughout) |
| ORM | SQLAlchemy 2.0 async + asyncpg |
| Migrations | Alembic |
| Schemas | Pydantic v2 |
| Graph DB | FalkorDB (Redis-compatible, Cypher queries) |
| Agent | LangGraph + langchain-google-genai |
| Config | pydantic-settings + python-dotenv |
| Server | uvicorn |
| Deps | uv (pyproject.toml + uv.lock, all versions pinned `==`) |
| Infra | Docker Compose (postgres:16, falkordb/falkordb:latest) |

## Project Structure
```
app/
├── main.py               # FastAPI app, lifespan (connects Postgres + FalkorDB)
├── config.py             # Settings via pydantic-settings, reads .env
├── models/
│   ├── base.py           # DeclarativeBase only
│   ├── enums.py          # RelationshipType, SyncStatus, MessageRole
│   ├── member.py         # FamilyMember
│   ├── relationship.py   # FamilyRelationship
│   ├── chat.py           # ChatSession, ChatMessage
│   └── operational.py    # SyncLog, LlmAuditLog
├── schemas/              # Pydantic v2 request/response schemas
├── db/
│   ├── postgres.py       # async engine, session factory, get_session dep
│   └── falkordb.py       # FalkorDB client wrapper (connect/disconnect)
├── services/
│   ├── member_service.py      # CRUD against Postgres
│   ├── relationship_service.py
│   ├── sync_service.py        # Dual-write to FalkorDB, retry logic
│   └── chat_service.py        # STUB
├── routes/
│   ├── members.py        # POST/GET /api/v1/members
│   ├── relationships.py  # POST/GET /api/v1/relationships
│   └── chat.py           # STUB
└── agent/                # ALL STUBS — LangGraph agent, not yet implemented
    ├── graph.py
    ├── nodes.py
    ├── tools.py
    ├── queries.py
    └── llm_providers.py
alembic/                  # Migration scripts — do not hand-edit
docker-compose.yml        # postgres + falkordb
pyproject.toml            # uv project file
```

## Environment Setup
```bash
cp .env.example .env       # fill in LLM_API_KEY
uv sync                    # installs from uv.lock
docker compose up -d       # start postgres + falkordb
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

## Environment Variables (.env)

## Key Patterns

### Route → Service → DB
Routes are thin: validate input, call service, fire background task, return response.
Services own all query logic. Never put SQLAlchemy `select()` in a route.

```python
# route
member = await _svc.create_member(db, data)
background_tasks.add_task(sync_service.sync_member_to_knowledge_graph, member.id)
return member

# service
async def create_member(self, db: AsyncSession, data: FamilyMemberCreate) -> FamilyMember:
    member = FamilyMember(**data.model_dump())
    db.add(member)
    await db.commit()
    await db.refresh(member)
    return member
```

### Dual-Write Pattern
Every write to Postgres fires a FastAPI `BackgroundTask` that syncs to FalkorDB.
Sync failure **never** affects the HTTP response. The `sync_log` table records every attempt.

```
POST /members
  └─ INSERT family_members (Postgres, sync)
  └─ BackgroundTask → sync_service.sync_member_to_knowledge_graph()
       └─ MERGE (:Person {id, first_name, last_name}) in FalkorDB
       └─ INSERT sync_log {status: success|failed, attempts: N}
       └─ retry up to 3× with 5-min asyncio.sleep between attempts
```

### FalkorDB Graph Schema
```
(:Person {id: uuid_str, first_name, last_name})
(:Person)-[:PARENT_OF|SPOUSE_OF|SIBLING_OF]->(:Person)
```
Graph name: `"family_tree"`. Always use `MERGE` for nodes to avoid duplicates.
Relationship type is dynamic — interpolated into Cypher string (not a parameter).

### Session Dependency
```python
# Always inject via Depends — never import engine directly in routes/services
db: AsyncSession = Depends(get_session)

# In background tasks (outside request scope), use factory directly:
async with async_session_factory() as db:
    ...
```

### FalkorDB Sync calls are blocking — always wrap with asyncio.to_thread
```python
await asyncio.to_thread(graph.query, cypher, params)
```

## Database Schema (6 tables)
| Table | Purpose |
|---|---|
| `family_members` | Core member data |
| `family_relationships` | Typed edges between members (UniqueConstraint + CheckConstraint) |
| `chat_sessions` | Anchor a chat to a member |
| `chat_messages` | Per-message store w/ JSONB tool_call_data |
| `sync_log` | Audit trail for every Postgres→FalkorDB sync attempt |
| `llm_audit_log` | Token counts, latency, errors per LLM call |

## Implemented vs Stub
| Area | Status |
|---|---|
| Members CRUD | ✅ Done |
| Relationships CRUD | ✅ Done |
| FalkorDB sync w/ retry | ✅ Done |
| sync_log writes | ✅ Done |
| Chat API | 🔲 Stub |
| LangGraph agent | 🔲 Stub |
| LLM audit logging | 🔲 Stub |
| Tests | 🔲 None yet |

## Coding Standards

### Non-negotiable rules
- **Never modify** `app/models/` or `alembic/versions/` — migrations are immutable once generated
- **Always use** `async/await` — no synchronous DB or network calls on the event loop
- **Wrap FalkorDB calls** in `asyncio.to_thread()` — client is sync-only
- **Never catch bare `Exception`** in routes — let FastAPI's exception handlers work; use specific catches
- **Background task failures** must never raise into the response path
- **No print() statements** — use `logging.getLogger(__name__)`

### Adding a new endpoint
1. Add schema to `app/schemas/<domain>.py`
2. Add method to `app/services/<domain>_service.py`
3. Add route to `app/routes/<domain>.py` (thin — no query logic)
4. If it writes, fire a background sync task

### Adding a new migration
```bash
uv run alembic revision --autogenerate -m "describe_change"
# Review the generated file before committing
uv run alembic upgrade head
```
Never hand-edit existing migration files.

### Dependency management (uv)
```bash
uv add package==x.y.z      # add new dep — updates pyproject.toml + uv.lock
uv sync                    # install from lock
uv pip install -r requirements.txt  # also works
```
All versions pinned `==`. No `>=` in pyproject.toml or requirements.txt.

### Error responses
| Code | When |
|---|---|
| 400 | Validation failure (self-relationship, duplicate UniqueConstraint) |
| 404 | Entity not found |
| 500 | Unexpected DB error (let FastAPI default handler return it) |

## Running Checks
```bash
uv run uvicorn app.main:app --reload   # dev server, Swagger at /docs
docker compose ps                      # verify containers healthy
docker exec family_tree_postgres psql -U postgres -d family_tree -c "\dt"
```
