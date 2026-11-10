"""User model."""
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    theme_preference: Mapped[str] = mapped_column(String(50), default="system")
    timezone: Mapped[str] = mapped_column(String(100), default="UTC")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    tasks: Mapped[list["Task"]] = relationship("Task", back_populates="user", cascade="all, delete-orphan")  # noqa: F821
    projects: Mapped[list["Project"]] = relationship("Project", back_populates="user", cascade="all, delete-orphan")  # noqa: F821
    calendar_events: Mapped[list["CalendarEvent"]] = relationship("CalendarEvent", back_populates="user", cascade="all, delete-orphan")  # noqa: F821
    file_documents: Mapped[list["FileDocument"]] = relationship("FileDocument", back_populates="user", cascade="all, delete-orphan")  # noqa: F821
    automations: Mapped[list["Automation"]] = relationship("Automation", back_populates="user", cascade="all, delete-orphan")  # noqa: F821
    execution_logs: Mapped[list["ExecutionLog"]] = relationship("ExecutionLog", back_populates="user", cascade="all, delete-orphan")  # noqa: F821
    ai_sessions: Mapped[list["AISession"]] = relationship("AISession", back_populates="user", cascade="all, delete-orphan")  # noqa: F821
