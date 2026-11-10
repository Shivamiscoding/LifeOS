"""LifeOS API entrypoint.

The project started with the domain models and tool layer in place.  This module
keeps the HTTP surface deliberately small and composable while exposing every
capability used by the web client.
"""
from __future__ import annotations

import mimetypes
import os
import re
import secrets
import time
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional
from uuid import uuid4

from fastapi import Depends, FastAPI, File, HTTPException, Query, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import and_, delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.bharatcode_provider import BharatCodeProvider
from app.ai.context import get_user_context
from app.ai.mock_provider import MockAIProvider
from app.ai.planner import create_plan
from app.config import get_settings
from app.database import AsyncSessionLocal, create_all_tables, get_db
from app.models.ai_session import AISession
from app.models.automation import Automation
from app.models.calendar_event import CalendarEvent
from app.models.execution_log import ExecutionLog
from app.models.file_document import FileDocument
from app.models.project import Project
from app.models.task import Task
from app.models.user import User
from app.schemas.ai_schemas import AICommandRequest, ActionPlan
from app.schemas.automation import AutomationCreate, AutomationUpdate
from app.schemas.calendar_event import CalendarEventCreate, CalendarEventUpdate
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.schemas.task import TaskBulkUpdate, TaskCreate, TaskUpdate
from app.schemas.user import LoginRequest, UserCreate, UserUpdate
from app.security.auth import create_access_token, get_current_user
from app.security.password import hash_password, verify_password
from app.tools.executor import execute_plan
from app.utils.audit import log_action
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

settings = get_settings()
scheduler = AsyncIOScheduler(timezone="UTC")


def _user(user: User) -> dict[str, Any]:
    return {
        "id": str(user.id), "email": user.email, "name": user.full_name or user.username,
        "username": user.username, "timezone": user.timezone, "themePreference": user.theme_preference,
        "createdAt": user.created_at.isoformat() if user.created_at else None,
        "updatedAt": user.updated_at.isoformat() if user.updated_at else None,
    }


def _task(task: Task) -> dict[str, Any]:
    return {
        "id": str(task.id), "title": task.title, "description": task.description,
        "priority": task.priority, "status": task.status, "dueDate": task.due_date.isoformat() if task.due_date else None,
        "projectId": str(task.project_id) if task.project_id else None, "tags": task.tags or [],
        "isAiGenerated": task.is_ai_generated,
        "createdAt": task.created_at.isoformat() if task.created_at else None,
        "updatedAt": task.updated_at.isoformat() if task.updated_at else None,
    }


def _project(project: Project, task_count: int = 0, completed: int = 0) -> dict[str, Any]:
    return {
        "id": str(project.id), "name": project.name, "description": project.description,
        "deadline": project.deadline.isoformat() if project.deadline else None, "status": project.status,
        "color": project.color, "taskCount": task_count, "completedTaskCount": completed,
        "createdAt": project.created_at.isoformat() if project.created_at else None,
        "updatedAt": project.updated_at.isoformat() if project.updated_at else None,
    }


def _event(event: CalendarEvent) -> dict[str, Any]:
    return {
        "id": str(event.id), "title": event.title, "description": event.description,
        "startTime": event.start_time.isoformat(), "endTime": event.end_time.isoformat(),
        "allDay": event.all_day, "eventType": event.event_type, "taskId": str(event.task_id) if event.task_id else None,
        "createdAt": event.created_at.isoformat() if event.created_at else None,
        "updatedAt": event.updated_at.isoformat() if event.updated_at else None,
    }


def _automation(item: Automation) -> dict[str, Any]:
    return {
        "id": str(item.id), "name": item.name, "description": item.description,
        "trigger": item.trigger_type, "triggerType": item.trigger_type, "triggerConfig": item.trigger_config or {},
        "conditions": item.conditions or [], "actions": item.actions or [], "isActive": item.is_active,
        "lastRunAt": item.last_run.isoformat() if item.last_run else None,
        "nextRun": item.next_run.isoformat() if item.next_run else None, "runCount": item.run_count,
        "createdAt": item.created_at.isoformat() if item.created_at else None,
        "updatedAt": item.updated_at.isoformat() if item.updated_at else None,
    }


def _session(session: AISession) -> dict[str, Any]:
    plan = session.plan or {}
    return {
        "id": str(session.id), "command": session.command, "status": session.status,
        "plan": plan.get("tool_calls", []) if isinstance(plan, dict) else plan,
        "planDetails": plan, "result": session.result_summary, "resultSummary": session.result_summary,
        "toolCalls": session.tool_calls or [], "createdAt": session.created_at.isoformat() if session.created_at else None,
        "updatedAt": session.created_at.isoformat() if session.created_at else None,
    }


@asynccontextmanager
async def lifespan(_: FastAPI):
    await create_all_tables()
    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    async with AsyncSessionLocal() as session:
        automations = (await session.execute(select(Automation).where(Automation.is_active.is_(True), Automation.trigger_type == "schedule"))).scalars().all()
        for automation in automations:
            cron = (automation.trigger_config or {}).get("cron")
            if cron:
                try:
                    scheduler.add_job(_scheduled_automation, CronTrigger.from_crontab(cron, timezone="UTC"), args=[automation.id], id=f"automation-{automation.id}", replace_existing=True)
                except (ValueError, KeyError):
                    continue
    scheduler.start()
    yield
    scheduler.shutdown(wait=False)


app = FastAPI(title="LifeOS API", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "lifeos-api"}


@app.get("/api/v1/health")
async def api_health() -> dict[str, str]:
    return await health()


@app.post("/api/v1/auth/register/")
async def register(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(User).where(or_(User.email == payload.email, User.username == payload.username)))
    if existing.scalar_one_or_none():
        raise HTTPException(409, "Email or username is already registered")
    user = User(email=payload.email, username=payload.username, full_name=payload.full_name,
                hashed_password=hash_password(payload.password), timezone=payload.timezone,
                theme_preference=payload.theme_preference)
    db.add(user); await db.flush(); await db.refresh(user)
    token = create_access_token({"sub": str(user.id)})
    return {"access": token, "token_type": "bearer", "user": _user(user)}


@app.post("/api/v1/auth/login/")
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid email or password")
    return {"access": create_access_token({"sub": str(user.id)}), "token_type": "bearer", "user": _user(user)}


@app.get("/api/v1/auth/me/")
async def me(user: User = Depends(get_current_user)):
    return _user(user)


@app.patch("/api/v1/auth/me/")
async def update_me(payload: UserUpdate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    data = payload.model_dump(exclude_unset=True)
    if "password" in data:
        data["hashed_password"] = hash_password(data.pop("password"))
    if "name" in data and data["name"] is not None:
        user.full_name = data.pop("name")
    if "full_name" in data and data["full_name"] is not None:
        user.full_name = data.pop("full_name")
    for key, value in data.items():
        if hasattr(user, key): setattr(user, key, value)
    await db.flush(); await db.refresh(user)
    return _user(user)


@app.post("/api/v1/auth/change-password/")
async def change_password(payload: dict[str, str], user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if not verify_password(payload.get("oldPassword", ""), user.hashed_password):
        raise HTTPException(400, "Current password is incorrect")
    if len(payload.get("newPassword", "")) < 8: raise HTTPException(422, "New password must be at least 8 characters")
    user.hashed_password = hash_password(payload["newPassword"]); await db.flush()
    return {"message": "Password updated"}


@app.post("/api/v1/auth/logout/")
async def logout():
    return {"message": "Signed out"}


@app.get("/api/v1/tasks/")
async def list_tasks(status_filter: Optional[str] = Query(None, alias="status"), priority: Optional[str] = None,
                     project_id: Optional[int] = None, search: Optional[str] = None,
                     page: int = 1, page_size: int = 100, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    query = select(Task).where(Task.user_id == user.id)
    count = select(func.count()).select_from(Task).where(Task.user_id == user.id)
    if status_filter: query = query.where(Task.status == status_filter); count = count.where(Task.status == status_filter)
    if priority: query = query.where(Task.priority == priority); count = count.where(Task.priority == priority)
    if project_id is not None: query = query.where(Task.project_id == project_id); count = count.where(Task.project_id == project_id)
    if search: query = query.where(Task.title.ilike(f"%{search}%")); count = count.where(Task.title.ilike(f"%{search}%"))
    total = (await db.execute(count)).scalar() or 0
    rows = (await db.execute(query.order_by(Task.due_date.asc().nullslast(), Task.created_at.desc()).offset((page-1)*page_size).limit(page_size))).scalars().all()
    return {"results": [_task(t) for t in rows], "items": [_task(t) for t in rows], "count": total, "total": total}


@app.post("/api/v1/tasks/")
async def create_task(payload: TaskCreate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    task = Task(**payload.model_dump(), user_id=user.id); db.add(task); await db.flush(); await db.refresh(task)
    return _task(task)


@app.get("/api/v1/tasks/{task_id}/")
async def get_task(task_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    task = (await db.execute(select(Task).where(Task.id == task_id, Task.user_id == user.id))).scalar_one_or_none()
    if not task: raise HTTPException(404, "Task not found")
    return _task(task)


@app.patch("/api/v1/tasks/{task_id}/")
async def update_task(task_id: int, payload: TaskUpdate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    task = (await db.execute(select(Task).where(Task.id == task_id, Task.user_id == user.id))).scalar_one_or_none()
    if not task: raise HTTPException(404, "Task not found")
    for key, value in payload.model_dump(exclude_unset=True).items(): setattr(task, key, value)
    await db.flush(); await db.refresh(task); return _task(task)


@app.delete("/api/v1/tasks/{task_id}/")
async def delete_task(task_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    task = (await db.execute(select(Task).where(Task.id == task_id, Task.user_id == user.id))).scalar_one_or_none()
    if not task: raise HTTPException(404, "Task not found")
    await db.delete(task); return {"deleted": True, "id": str(task_id)}


@app.post("/api/v1/tasks/bulk-status/")
async def bulk_status(payload: TaskBulkUpdate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    rows = (await db.execute(select(Task).where(Task.id.in_(payload.ids), Task.user_id == user.id))).scalars().all()
    for task in rows:
        if payload.status is not None: task.status = payload.status
        if payload.priority is not None: task.priority = payload.priority
        if payload.project_id is not None: task.project_id = payload.project_id
    await db.flush(); return {"updated": len(rows)}


@app.get("/api/v1/projects/")
async def list_projects(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    projects = (await db.execute(select(Project).where(Project.user_id == user.id).order_by(Project.created_at.desc()))).scalars().all()
    results = []
    for project in projects:
        total = (await db.execute(select(func.count()).select_from(Task).where(Task.project_id == project.id))).scalar() or 0
        done = (await db.execute(select(func.count()).select_from(Task).where(Task.project_id == project.id, Task.status == "completed"))).scalar() or 0
        results.append(_project(project, total, done))
    return {"results": results, "items": results, "count": len(results), "total": len(results)}


@app.post("/api/v1/projects/")
async def create_project(payload: ProjectCreate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    project = Project(**payload.model_dump(), user_id=user.id); db.add(project); await db.flush(); await db.refresh(project); return _project(project)


@app.get("/api/v1/projects/{project_id}/")
async def get_project(project_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    project = (await db.execute(select(Project).where(Project.id == project_id, Project.user_id == user.id))).scalar_one_or_none()
    if not project: raise HTTPException(404, "Project not found")
    total = (await db.execute(select(func.count()).select_from(Task).where(Task.project_id == project.id))).scalar() or 0
    done = (await db.execute(select(func.count()).select_from(Task).where(Task.project_id == project.id, Task.status == "completed"))).scalar() or 0
    return _project(project, total, done)


@app.patch("/api/v1/projects/{project_id}/")
async def update_project(project_id: int, payload: ProjectUpdate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    project = (await db.execute(select(Project).where(Project.id == project_id, Project.user_id == user.id))).scalar_one_or_none()
    if not project: raise HTTPException(404, "Project not found")
    for key, value in payload.model_dump(exclude_unset=True).items(): setattr(project, key, value)
    await db.flush(); return _project(project)


@app.delete("/api/v1/projects/{project_id}/")
async def delete_project(project_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    project = (await db.execute(select(Project).where(Project.id == project_id, Project.user_id == user.id))).scalar_one_or_none()
    if not project: raise HTTPException(404, "Project not found")
    await db.delete(project); return {"deleted": True}


@app.get("/api/v1/calendar/")
async def list_calendar(start: Optional[datetime] = None, end: Optional[datetime] = None, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    query = select(CalendarEvent).where(CalendarEvent.user_id == user.id)
    if start: query = query.where(CalendarEvent.start_time >= start)
    if end: query = query.where(CalendarEvent.end_time <= end)
    events = (await db.execute(query.order_by(CalendarEvent.start_time.asc()))).scalars().all()
    return [_event(e) for e in events]


@app.post("/api/v1/calendar/")
async def create_calendar(payload: CalendarEventCreate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    conflict = (await db.execute(select(CalendarEvent).where(CalendarEvent.user_id == user.id,
        CalendarEvent.start_time < payload.end_time, CalendarEvent.end_time > payload.start_time))).scalar_one_or_none()
    event = CalendarEvent(**payload.model_dump(), user_id=user.id); db.add(event); await db.flush(); await db.refresh(event)
    data = _event(event); data["conflict"] = bool(conflict); return data


@app.get("/api/v1/calendar/{event_id}/")
async def get_calendar(event_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    event = (await db.execute(select(CalendarEvent).where(CalendarEvent.id == event_id, CalendarEvent.user_id == user.id))).scalar_one_or_none()
    if not event: raise HTTPException(404, "Event not found")
    return _event(event)


@app.patch("/api/v1/calendar/{event_id}/")
async def update_calendar(event_id: int, payload: CalendarEventUpdate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    event = (await db.execute(select(CalendarEvent).where(CalendarEvent.id == event_id, CalendarEvent.user_id == user.id))).scalar_one_or_none()
    if not event: raise HTTPException(404, "Event not found")
    for key, value in payload.model_dump(exclude_unset=True).items(): setattr(event, key, value)
    if event.end_time <= event.start_time and not event.all_day: raise HTTPException(422, "End time must be after start time")
    await db.flush(); return _event(event)


@app.delete("/api/v1/calendar/{event_id}/")
async def delete_calendar(event_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    event = (await db.execute(select(CalendarEvent).where(CalendarEvent.id == event_id, CalendarEvent.user_id == user.id))).scalar_one_or_none()
    if not event: raise HTTPException(404, "Event not found")
    await db.delete(event); return {"deleted": True}


def _extract_text(path: Path, mime: str) -> str:
    try:
        if mime == "text/plain" or path.suffix.lower() in {".txt", ".csv"}: return path.read_text(errors="ignore")[:200_000]
        if path.suffix.lower() == ".pdf":
            from PyPDF2 import PdfReader
            return "\n".join((page.extract_text() or "") for page in PdfReader(str(path)).pages)[:200_000]
        if path.suffix.lower() == ".docx":
            from docx import Document
            return "\n".join(p.text for p in Document(str(path)).paragraphs)[:200_000]
    except Exception:
        return ""
    return ""


@app.get("/api/v1/files/")
async def list_files(mime_type: Optional[str] = None, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    query = select(FileDocument).where(FileDocument.user_id == user.id)
    if mime_type: query = query.where(FileDocument.file_type == mime_type)
    files = (await db.execute(query.order_by(FileDocument.created_at.desc()))).scalars().all()
    result = [{"id": str(f.id), "name": f.original_name, "originalName": f.original_name, "mimeType": f.file_type,
               "size": f.file_size, "summary": f.summary, "uploadedAt": f.created_at.isoformat() if f.created_at else None,
               "category": f.category, "tags": f.tags or []} for f in files]
    return {"results": result, "items": result, "count": len(result), "total": len(result)}


@app.post("/api/v1/files/")
async def upload_file(file: UploadFile = File(...), db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    allowed = {".pdf", ".docx", ".txt", ".csv"}; suffix = Path(file.filename or "").suffix.lower()
    if suffix not in allowed: raise HTTPException(415, "Only PDF, DOCX, TXT, and CSV files are supported")
    data = await file.read()
    if len(data) > settings.max_upload_size_bytes: raise HTTPException(413, "File exceeds upload size limit")
    stored = f"{uuid4().hex}{suffix}"; path = Path(settings.upload_dir) / stored; path.write_bytes(data)
    mime = file.content_type or mimetypes.guess_type(file.filename or "")[0] or "application/octet-stream"
    document = FileDocument(filename=stored, original_name=file.filename or stored, file_path=str(path), file_type=mime,
                            file_size=len(data), extracted_text=_extract_text(path, mime), user_id=user.id)
    db.add(document); await db.flush(); await db.refresh(document)
    return {"id": str(document.id), "name": document.original_name, "mimeType": document.file_type,
            "size": document.file_size, "summary": document.summary, "uploadedAt": document.created_at.isoformat() if document.created_at else None}


@app.post("/api/v1/files/{file_id}/summarize/")
async def summarize_file(file_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    document = (await db.execute(select(FileDocument).where(FileDocument.id == file_id, FileDocument.user_id == user.id))).scalar_one_or_none()
    if not document: raise HTTPException(404, "File not found")
    text = (document.extracted_text or "").strip()
    document.summary = (text[:800] + ("…" if len(text) > 800 else "")) if text else "No extractable text was found in this document."
    await db.flush(); return {"summary": document.summary}


@app.delete("/api/v1/files/{file_id}/")
async def delete_file(file_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    document = (await db.execute(select(FileDocument).where(FileDocument.id == file_id, FileDocument.user_id == user.id))).scalar_one_or_none()
    if not document: raise HTTPException(404, "File not found")
    try: Path(document.file_path).unlink(missing_ok=True)
    except OSError: pass
    await db.delete(document); return {"deleted": True}


@app.get("/api/v1/automations/")
async def list_automations(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    rows = (await db.execute(select(Automation).where(Automation.user_id == user.id).order_by(Automation.created_at.desc()))).scalars().all()
    result = [_automation(a) for a in rows]; return {"results": result, "items": result, "count": len(result), "total": len(result)}


@app.post("/api/v1/automations/")
async def create_automation(payload: AutomationCreate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    data = payload.model_dump(); data["trigger_type"] = data.get("trigger") or data.get("trigger_type") or "manual"; data.pop("trigger", None)
    item = Automation(**data, user_id=user.id); db.add(item); await db.flush(); await db.refresh(item); return _automation(item)


@app.get("/api/v1/automations/{automation_id}/")
async def get_automation(automation_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    item = (await db.execute(select(Automation).where(Automation.id == automation_id, Automation.user_id == user.id))).scalar_one_or_none()
    if not item: raise HTTPException(404, "Automation not found")
    return _automation(item)


@app.patch("/api/v1/automations/{automation_id}/")
async def update_automation(automation_id: int, payload: AutomationUpdate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    item = (await db.execute(select(Automation).where(Automation.id == automation_id, Automation.user_id == user.id))).scalar_one_or_none()
    if not item: raise HTTPException(404, "Automation not found")
    data = payload.model_dump(exclude_unset=True)
    if "trigger_type" in data: item.trigger_type = data.pop("trigger_type")
    for key, value in data.items(): setattr(item, key, value)
    await db.flush(); return _automation(item)


@app.delete("/api/v1/automations/{automation_id}/")
async def delete_automation(automation_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    item = (await db.execute(select(Automation).where(Automation.id == automation_id, Automation.user_id == user.id))).scalar_one_or_none()
    if not item: raise HTTPException(404, "Automation not found")
    await db.delete(item); return {"deleted": True}


async def _scheduled_automation(automation_id: int) -> None:
    """Run a scheduled automation in its own short-lived database session."""
    async with AsyncSessionLocal() as db:
        item = (await db.execute(select(Automation).where(Automation.id == automation_id, Automation.is_active.is_(True)))).scalar_one_or_none()
        if not item:
            return
        user = (await db.execute(select(User).where(User.id == item.user_id))).scalar_one_or_none()
        if user:
            await _run_automation(item, db, user)
        await db.commit()


async def _run_automation(item: Automation, db: AsyncSession, user: User) -> ExecutionLog:
    started = time.monotonic(); outputs = []; failed = None
    try:
        for action in item.actions or []:
            name = action.get("type") or action.get("tool_name")
            if not name: continue
            from app.tools.registry import registry
            tool = registry.get(name)
            if not tool: raise ValueError(f"Unknown automation action: {name}")
            outputs.append(await tool(db=db, user_id=user.id, **(action.get("config") or action.get("arguments") or {})))
        status_value = "success"
    except Exception as exc:
        status_value = "failed"; failed = str(exc)
    log = await log_action(db, user.id, "automation", status_value, {"automation_id": item.id}, {"outputs": outputs}, failed, item.id, int((time.monotonic()-started)*1000))
    item.last_run = datetime.now(timezone.utc); item.run_count += 1; await db.flush(); return log


@app.post("/api/v1/automations/{automation_id}/execute/")
async def execute_automation(automation_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    item = (await db.execute(select(Automation).where(Automation.id == automation_id, Automation.user_id == user.id))).scalar_one_or_none()
    if not item: raise HTTPException(404, "Automation not found")
    log = await _run_automation(item, db, user)
    return {"id": str(log.id), "automationId": str(item.id), "status": log.status, "startedAt": log.created_at.isoformat() if log.created_at else None, "error": log.error_message, "logs": log.output_data}


@app.get("/api/v1/automations/{automation_id}/history/")
async def automation_history(automation_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    logs = (await db.execute(select(ExecutionLog).where(ExecutionLog.automation_id == automation_id, ExecutionLog.user_id == user.id).order_by(ExecutionLog.created_at.desc()))).scalars().all()
    result = [{"id": str(l.id), "automationId": str(automation_id), "status": l.status, "startedAt": l.created_at.isoformat() if l.created_at else None, "finishedAt": l.updated_at.isoformat() if l.updated_at else None, "error": l.error_message, "logs": l.output_data} for l in logs]
    return {"results": result, "items": result, "count": len(result), "total": len(result)}


def _provider():
    return BharatCodeProvider() if settings.ai_provider.lower() == "bharatcode" and settings.bharatcode_api_key not in {"", "mock-key"} else MockAIProvider()


@app.post("/api/v1/ai/command/")
async def ai_command(payload: AICommandRequest, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    if not payload.command.strip(): raise HTTPException(422, "Command cannot be empty")
    context = await get_user_context(user.id, db); context.update(payload.context_override or {})
    session = AISession(user_id=user.id, command=payload.command, status="running"); db.add(session); await db.flush()
    try:
        plan, message = await create_plan(payload.command, context, _provider())
        executed = await execute_plan(plan, user.id, db)
        session.plan = plan.model_dump(); session.tool_calls = [call.model_dump() for call in executed]
        session.status = "completed" if all(c.status == "success" for c in executed) else "failed"
        session.result_summary = message
        await log_action(db, user.id, "ai_command", session.status, {"command": payload.command}, {"tools": len(executed)})
    except Exception as exc:
        session.status = "failed"; session.result_summary = str(exc); await db.flush()
    await db.refresh(session); return _session(session)


@app.get("/api/v1/ai/sessions/")
async def ai_sessions(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    rows = (await db.execute(select(AISession).where(AISession.user_id == user.id).order_by(AISession.created_at.desc()).limit(50))).scalars().all()
    result = [_session(s) for s in rows]; return {"results": result, "items": result, "count": len(result), "total": len(result)}


@app.get("/api/v1/ai/sessions/{session_id}/")
@app.get("/api/v1/ai/sessions/{session_id}/status/")
async def ai_session(session_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    session = (await db.execute(select(AISession).where(AISession.id == session_id, AISession.user_id == user.id))).scalar_one_or_none()
    if not session: raise HTTPException(404, "AI session not found")
    return _session(session)


@app.get("/api/v1/insights/stats/")
async def insight_stats(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    now = datetime.now(timezone.utc); start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    total = (await db.execute(select(func.count()).select_from(Task).where(Task.user_id == user.id))).scalar() or 0
    completed_today = (await db.execute(select(func.count()).select_from(Task).where(Task.user_id == user.id, Task.status == "completed", Task.updated_at >= start))).scalar() or 0
    active_projects = (await db.execute(select(func.count()).select_from(Project).where(Project.user_id == user.id, Project.status == "active"))).scalar() or 0
    pending_events = (await db.execute(select(func.count()).select_from(CalendarEvent).where(CalendarEvent.user_id == user.id, CalendarEvent.start_time >= now))).scalar() or 0
    completed = (await db.execute(select(func.count()).select_from(Task).where(Task.user_id == user.id, Task.status == "completed"))).scalar() or 0
    return {"totalTasks": total, "completedToday": completed_today, "activeProjects": active_projects, "pendingEvents": pending_events, "streak": 0, "avgCompletionRate": round(completed / total * 100, 1) if total else 0}


@app.get("/api/v1/insights/")
async def insights(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    today = datetime.now(timezone.utc).date(); productivity = []
    for offset in range(13, -1, -1):
        day = today - timedelta(days=offset); start = datetime.combine(day, datetime.min.time(), tzinfo=timezone.utc); end = start + timedelta(days=1)
        created = (await db.execute(select(func.count()).select_from(Task).where(Task.user_id == user.id, Task.created_at >= start, Task.created_at < end))).scalar() or 0
        done = (await db.execute(select(func.count()).select_from(Task).where(Task.user_id == user.id, Task.status == "completed", Task.updated_at >= start, Task.updated_at < end))).scalar() or 0
        productivity.append({"date": day.isoformat(), "created": created, "completed": done})
    tasks = (await db.execute(select(Task).where(Task.user_id == user.id))).scalars().all()
    priority = [{"priority": p, "count": sum(1 for t in tasks if t.priority == p)} for p in ["low", "medium", "high", "critical"]]
    projects = (await db.execute(select(Project).where(Project.user_id == user.id))).scalars().all(); rates = []
    for p in projects:
        p_tasks = [t for t in tasks if t.project_id == p.id]; done = sum(1 for t in p_tasks if t.status == "completed")
        rates.append({"projectName": p.name, "rate": round(done / len(p_tasks) * 100) if p_tasks else 0, "total": len(p_tasks), "completed": done})
    return {"productivity": productivity, "priorityDistribution": priority, "dayOfWeekData": [], "projectCompletionRates": rates}


@app.exception_handler(Exception)
async def unhandled(_: Any, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
