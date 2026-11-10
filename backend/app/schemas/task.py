"""Task Pydantic schemas."""
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str = "medium"   # low|medium|high|critical
    status: str = "todo"       # todo|in_progress|completed|overdue
    due_date: Optional[datetime] = None
    project_id: Optional[int] = None
    tags: List[str] = []
    is_ai_generated: bool = False


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    due_date: Optional[datetime] = None
    project_id: Optional[int] = None
    tags: Optional[List[str]] = None


class TaskResponse(TaskBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TaskBulkUpdate(BaseModel):
    ids: List[int]
    status: Optional[str] = None
    priority: Optional[str] = None
    project_id: Optional[int] = None
