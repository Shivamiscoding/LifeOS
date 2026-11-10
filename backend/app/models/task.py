"""Task model."""
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(5000), nullable=True)
    priority: Mapped[str] = mapped_column(String(20), default="medium")   # low|medium|high|critical
    status: Mapped[str] = mapped_column(String(30), default="todo")        # todo|in_progress|completed|overdue
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    tags: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    is_ai_generated: Mapped[bool] = mapped_column(Boolean, default=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    project_id: Mapped[Optional[int]] = mapped_column(ForeignKey("projects.id"), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="tasks")  # noqa: F821
    project: Mapped[Optional["Project"]] = relationship("Project", back_populates="tasks")  # noqa: F821
    calendar_events: Mapped[list["CalendarEvent"]] = relationship("CalendarEvent", back_populates="task")  # noqa: F821
