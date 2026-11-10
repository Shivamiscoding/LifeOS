"""Task business logic service."""
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate


async def create_task(db: AsyncSession, user_id: int, data: TaskCreate) -> Task:
    task = Task(**data.model_dump(), user_id=user_id)
    db.add(task)
    await db.flush()
    await db.refresh(task)
    return task


async def get_task(db: AsyncSession, task_id: int, user_id: int) -> Optional[Task]:
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def list_tasks(
    db: AsyncSession,
    user_id: int,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    project_id: Optional[int] = None,
    search: Optional[str] = None,
    sort_by: str = "created_at",
    sort_desc: bool = True,
    offset: int = 0,
    limit: int = 20,
) -> tuple[List[Task], int]:
    query = select(Task).where(Task.user_id == user_id)
    count_query = select(func.count()).select_from(Task).where(Task.user_id == user_id)

    if status:
        query = query.where(Task.status == status)
        count_query = count_query.where(Task.status == status)
    if priority:
        query = query.where(Task.priority == priority)
        count_query = count_query.where(Task.priority == priority)
    if project_id is not None:
        query = query.where(Task.project_id == project_id)
        count_query = count_query.where(Task.project_id == project_id)
    if search:
        like = f"%{search}%"
        query = query.where(Task.title.ilike(like))
        count_query = count_query.where(Task.title.ilike(like))

    sort_col = getattr(Task, sort_by, Task.created_at)
    query = query.order_by(sort_col.desc() if sort_desc else sort_col.asc())
    query = query.offset(offset).limit(limit)

    result = await db.execute(query)
    count_result = await db.execute(count_query)
    return result.scalars().all(), count_result.scalar() or 0


async def update_task(db: AsyncSession, task: Task, data: TaskUpdate) -> Task:
    update_data = data.model_dump(exclude_unset=True)
    for key, val in update_data.items():
        setattr(task, key, val)
    await db.flush()
    await db.refresh(task)
    return task


async def delete_task(db: AsyncSession, task: Task) -> None:
    await db.delete(task)
    await db.flush()


async def bulk_update_tasks(
    db: AsyncSession,
    user_id: int,
    ids: List[int],
    status: Optional[str] = None,
    priority: Optional[str] = None,
    project_id: Optional[int] = None,
) -> int:
    result = await db.execute(
        select(Task).where(Task.id.in_(ids), Task.user_id == user_id)
    )
    tasks = result.scalars().all()
    for task in tasks:
        if status is not None:
            task.status = status
        if priority is not None:
            task.priority = priority
        if project_id is not None:
            task.project_id = project_id
    await db.flush()
    return len(tasks)
