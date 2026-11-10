"""Automation Pydantic schemas."""
from datetime import datetime
from typing import Optional, List, Any, Dict

from pydantic import BaseModel


class AutomationBase(BaseModel):
    name: str
    description: Optional[str] = None
    trigger_type: str = "manual"     # schedule|event|manual|webhook
    trigger: Optional[str] = None     # frontend-friendly alias
    trigger_config: Dict[str, Any] = {}
    conditions: List[Dict[str, Any]] = []
    actions: List[Dict[str, Any]] = []
    is_active: bool = True


class AutomationCreate(AutomationBase):
    pass


class AutomationUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    trigger_type: Optional[str] = None
    trigger_config: Optional[Dict[str, Any]] = None
    conditions: Optional[List[Dict[str, Any]]] = None
    actions: Optional[List[Dict[str, Any]]] = None
    is_active: Optional[bool] = None


class AutomationResponse(AutomationBase):
    id: int
    user_id: int
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    run_count: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
