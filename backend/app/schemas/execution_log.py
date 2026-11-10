"""ExecutionLog Pydantic schemas."""
from datetime import datetime
from typing import Optional, Any, Dict

from pydantic import BaseModel


class ExecutionLogBase(BaseModel):
    action_type: str
    status: str = "pending"
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    duration_ms: Optional[int] = None


class ExecutionLogResponse(ExecutionLogBase):
    id: int
    automation_id: Optional[int] = None
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
