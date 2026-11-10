"""Automation tools — AI-callable function to create automations."""
from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.automation import Automation
from app.tools.registry import register_tool


@register_tool("create_automation")
async def create_automation(
    db: AsyncSession,
    user_id: int,
    name: str,
    trigger_type: str,
    trigger_config: Optional[Dict[str, Any]] = None,
    description: Optional[str] = None,
    conditions: Optional[List[Dict[str, Any]]] = None,
    actions: Optional[List[Dict[str, Any]]] = None,
    is_active: bool = True,
) -> Dict[str, Any]:
    """Create a new automation rule."""
    automation = Automation(
        name=name,
        description=description,
        trigger_type=trigger_type,
        trigger_config=trigger_config or {},
        conditions=conditions or [],
        actions=actions or [],
        is_active=is_active,
        user_id=user_id,
    )
    db.add(automation)
    await db.flush()
    return {
        "id": automation.id,
        "name": automation.name,
        "trigger_type": automation.trigger_type,
        "is_active": automation.is_active,
    }
