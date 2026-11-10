"""Automation model."""
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Automation(Base):
    __tablename__ = "automations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(2000), nullable=True)
    trigger_type: Mapped[str] = mapped_column(String(50), nullable=False)  # schedule|event
    trigger_config: Mapped[dict] = mapped_column(JSON, default=dict)       # e.g. {"cron": "0 9 * * 1"}
    conditions: Mapped[list] = mapped_column(JSON, default=list)           # list of condition dicts
    actions: Mapped[list] = mapped_column(JSON, default=list)              # list of action dicts
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    last_run: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    next_run: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    run_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="automations")  # noqa: F821
    execution_logs: Mapped[list["ExecutionLog"]] = relationship("ExecutionLog", back_populates="automation", cascade="all, delete-orphan")  # noqa: F821
