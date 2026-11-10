"""Task tools — AI-callable functions for task management."""
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task
from app.tools.registry import register_tool


@register_tool("create_task")
async def create_task(
    db: AsyncSession,
    user_id: int,
    title: str,
    description: Optional[str] = None,
    priority: str = "medium",
    status: str = "todo",
    due_date: Optional[str] = None,
    tags: Optional[List[str]] = None,
    project_id: Optional[int] = None,
    is_ai_generated: bool = False,
) -> Dict[str, Any]:
    """Create a new task for the user."""
    parsed_due = None
    if due_date:
        try:
            parsed_due = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
        except ValueError:
            parsed_due = None

    task = Task(
        title=title,
        description=description,
        priority=priority,
        status=status,
        due_date=parsed_due,
        tags=tags or [],
        project_id=project_id,
        is_ai_generated=is_ai_generated,
        user_id=user_id,
    )
    db.add(task)
    await db.flush()
    return {
        "id": task.id,
        "title": task.title,
        "priority": task.priority,
        "status": task.status,
        "due_date": task.due_date.isoformat() if task.due_date else None,
    }


@register_tool("update_task")
async def update_task(
    db: AsyncSession,
    user_id: int,
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    priority: Optional[str] = None,
    status: Optional[str] = None,
    due_date: Optional[str] = None,
) -> Dict[str, Any]:
    """Update an existing task."""
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.user_id == user_id)
    )
    task = result.scalar_one_or_none()
    if not task:
        return {"error": f"Task {task_id} not found"}

    if title is not None:
        task.title = title
    if description is not None:
        task.description = description
    if priority is not None:
        task.priority = priority
    if status is not None:
        task.status = status
    if due_date is not None:
        try:
            task.due_date = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
        except ValueError:
            pass

    await db.flush()
    return {"id": task.id, "title": task.title, "status": task.status, "updated": True}


@register_tool("delete_task")
async def delete_task(
    db: AsyncSession,
    user_id: int,
    task_id: int,
    confirmed: bool = False,
) -> Dict[str, Any]:
    """Delete a task. Requires confirmed=True as a safety check."""
    if not confirmed:
        return {
            "requires_confirmation": True,
            "message": f"Are you sure you want to delete task {task_id}? Pass confirmed=True to proceed.",
        }

    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.user_id == user_id)
    )
    task = result.scalar_one_or_none()
    if not task:
        return {"error": f"Task {task_id} not found"}

    await db.delete(task)
    await db.flush()
    return {"deleted": True, "task_id": task_id}


@register_tool("list_tasks")
async def list_tasks(
    db: AsyncSession,
    user_id: int,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    project_id: Optional[int] = None,
    limit: int = 20,
    sort_by: str = "created_at",
) -> Dict[str, Any]:
    """List tasks for the user with optional filters."""
    query = select(Task).where(Task.user_id == user_id)

    if status:
        query = query.where(Task.status == status)
    if priority:
        query = query.where(Task.priority == priority)
    if project_id:
        query = query.where(Task.project_id == project_id)

    sort_col = getattr(Task, sort_by, Task.created_at)
    query = query.order_by(sort_col.desc()).limit(limit)

    result = await db.execute(query)
    tasks = result.scalars().all()

    return {
        "tasks": [
            {
                "id": t.id,
                "title": t.title,
                "priority": t.priority,
                "status": t.status,
                "due_date": t.due_date.isoformat() if t.due_date else None,
            }
            for t in tasks
        ],
        "count": len(tasks),
    }


@register_tool("mark_overdue_tasks")
async def mark_overdue_tasks(
    db: AsyncSession,
    user_id: int,
) -> Dict[str, Any]:
    """Mark all past-due incomplete tasks as overdue."""
    now = datetime.now(timezone.utc)

    result = await db.execute(
        select(Task).where(
            Task.user_id == user_id,
            Task.status.in_(["todo", "in_progress"]),
            Task.due_date < now,
            Task.due_date.isnot(None),
        )
    )
    tasks = result.scalars().all()

    count = 0
    for task in tasks:
        task.status = "overdue"
        count += 1

    await db.flush()
    return {"marked_overdue": count}
