"""Project tools — AI-callable functions for project management."""
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.tools.registry import register_tool


@register_tool("create_project")
async def create_project(
    db: AsyncSession,
    user_id: int,
    name: str,
    description: Optional[str] = None,
    status: str = "active",
    color: str = "#6366f1",
    deadline: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a new project."""
    from datetime import datetime

    parsed_deadline = None
    if deadline:
        try:
            parsed_deadline = datetime.fromisoformat(deadline.replace("Z", "+00:00"))
        except ValueError:
            parsed_deadline = None

    project = Project(
        name=name,
        description=description,
        status=status,
        color=color,
        deadline=parsed_deadline,
        user_id=user_id,
    )
    db.add(project)
    await db.flush()
    return {
        "id": project.id,
        "name": project.name,
        "status": project.status,
        "color": project.color,
    }


@register_tool("list_projects")
async def list_projects(
    db: AsyncSession,
    user_id: int,
    status: Optional[str] = None,
) -> Dict[str, Any]:
    """List user projects."""
    query = select(Project).where(Project.user_id == user_id)
    if status:
        query = query.where(Project.status == status)
    query = query.order_by(Project.created_at.desc())

    result = await db.execute(query)
    projects = result.scalars().all()

    return {
        "projects": [
            {
                "id": p.id,
                "name": p.name,
                "status": p.status,
                "color": p.color,
                "deadline": p.deadline.isoformat() if p.deadline else None,
            }
            for p in projects
        ],
        "count": len(projects),
    }
