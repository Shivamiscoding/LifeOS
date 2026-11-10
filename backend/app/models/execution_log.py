"""ExecutionLog model."""
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ExecutionLog(Base):
    __tablename__ = "execution_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    automation_id: Mapped[Optional[int]] = mapped_column(ForeignKey("automations.id"), nullable=True, index=True)
    action_type: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g. "create_task", "send_report"
    status: Mapped[str] = mapped_column(String(30), default="pending")     # pending|running|success|failed
    input_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    output_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    duration_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="execution_logs")  # noqa: F821
    automation: Mapped[Optional["Automation"]] = relationship("Automation", back_populates="execution_logs")  # noqa: F821
