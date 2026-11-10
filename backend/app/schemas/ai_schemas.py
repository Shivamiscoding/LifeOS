"""AI-related Pydantic schemas."""
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class ToolCall(BaseModel):
    tool_name: str
    arguments: Dict[str, Any] = {}
    result: Optional[Any] = None
    status: str = "pending"   # pending|success|failed
    error: Optional[str] = None


class ActionPlan(BaseModel):
    intent: str
    description: str
    tool_calls: List[ToolCall]
    estimated_duration_ms: int = 0


class AIResponse(BaseModel):
    content: str
    plan: Optional[ActionPlan] = None
    raw_response: Optional[Dict[str, Any]] = None


class AICommandRequest(BaseModel):
    command: str
    context_override: Optional[Dict[str, Any]] = None


class AISessionResponse(BaseModel):
    id: int
    user_id: int
    command: str
    plan: Optional[Dict[str, Any]] = None
    status: str
    result_summary: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    created_at: datetime

    model_config = {"from_attributes": True}
