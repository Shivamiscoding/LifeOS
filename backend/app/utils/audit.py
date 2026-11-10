"""Audit logging helper."""
import logging
from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.execution_log import ExecutionLog

logger = logging.getLogger(__name__)


async def log_action(
    db: AsyncSession,
    user_id: int,
    action_type: str,
    status: str = "success",
    input_data: Optional[dict] = None,
    output_data: Optional[dict] = None,
    error_message: Optional[str] = None,
    automation_id: Optional[int] = None,
    duration_ms: Optional[int] = None,
) -> ExecutionLog:
    """Create an audit log entry in the database."""
    log_entry = ExecutionLog(
        user_id=user_id,
        action_type=action_type,
        status=status,
        input_data=input_data,
        output_data=output_data,
        error_message=error_message,
        automation_id=automation_id,
        duration_ms=duration_ms,
    )
    db.add(log_entry)
    await db.flush()
    logger.info(
        "Audit log: user=%s action=%s status=%s",
        user_id,
        action_type,
        status,
    )
    return log_entry
