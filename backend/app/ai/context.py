"""User context builder for AI prompts."""
from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task
from app.models.project import Project
from app.models.calendar_event import CalendarEvent
from app.models.execution_log import ExecutionLog


async def get_user_context(user_id: int, db: AsyncSession) -> Dict[str, Any]:
    """
    Fetch relevant user data to inject as context into AI prompts.
    Returns a dict with pending tasks, upcoming events, active projects,
    and recent activity.
    """
    now = datetime.now(timezone.utc)
    week_ahead = now + timedelta(days=7)

    # Pending / in-progress tasks
    tasks_result = await db.execute(
        select(Task)
        .where(Task.user_id == user_id, Task.status.in_(["todo", "in_progress"]))
        .order_by(Task.due_date.asc().nullslast(), Task.priority.desc())
        .limit(20)
    )
    pending_tasks = tasks_result.scalars().all()

    # Upcoming calendar events (next 7 days)
    events_result = await db.execute(
        select(CalendarEvent)
        .where(
            CalendarEvent.user_id == user_id,
            CalendarEvent.start_time >= now,
            CalendarEvent.start_time <= week_ahead,
        )
        .order_by(CalendarEvent.start_time.asc())
        .limit(10)
    )
    upcoming_events = events_result.scalars().all()

    # Active projects
    projects_result = await db.execute(
        select(Project)
        .where(Project.user_id == user_id, Project.status == "active")
        .limit(10)
    )
    active_projects = projects_result.scalars().all()

    # Task counts
    total_result = await db.execute(
        select(func.count()).select_from(Task).where(Task.user_id == user_id)
    )
    total_tasks = total_result.scalar() or 0

    completed_result = await db.execute(
        select(func.count()).select_from(Task).where(
            Task.user_id == user_id, Task.status == "completed"
        )
    )
    completed_tasks = completed_result.scalar() or 0

    # Recent activity
    recent_logs_result = await db.execute(
        select(ExecutionLog)
        .where(ExecutionLog.user_id == user_id)
        .order_by(ExecutionLog.created_at.desc())
        .limit(5)
    )
    recent_logs = recent_logs_result.scalars().all()

    return {
        "current_time": now.isoformat(),
        "pending_tasks": [
            {
                "id": t.id,
                "title": t.title,
                "priority": t.priority,
                "status": t.status,
                "due_date": t.due_date.isoformat() if t.due_date else None,
                "project_id": t.project_id,
            }
            for t in pending_tasks
        ],
        "upcoming_events": [
            {
                "id": e.id,
                "title": e.title,
                "start_time": e.start_time.isoformat(),
                "end_time": e.end_time.isoformat(),
                "event_type": e.event_type,
            }
            for e in upcoming_events
        ],
        "active_projects": [
            {"id": p.id, "name": p.name, "status": p.status}
            for p in active_projects
        ],
        "stats": {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "completion_rate": round(completed_tasks / total_tasks * 100, 1) if total_tasks else 0,
        },
        "recent_activity": [
            {
                "action_type": log.action_type,
                "status": log.status,
                "created_at": log.created_at.isoformat(),
            }
            for log in recent_logs
        ],
    }
