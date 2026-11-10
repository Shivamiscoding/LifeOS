"""Calendar tools — AI-callable functions for calendar management."""
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.calendar_event import CalendarEvent
from app.tools.registry import register_tool


@register_tool("create_calendar_event")
async def create_calendar_event(
    db: AsyncSession,
    user_id: int,
    title: str,
    start_time: str,
    end_time: str,
    description: Optional[str] = None,
    all_day: bool = False,
    event_type: str = "personal",
    task_id: Optional[int] = None,
) -> Dict[str, Any]:
    """Create a new calendar event."""
    try:
        start = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
        end = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
    except ValueError as exc:
        return {"error": f"Invalid datetime format: {exc}"}

    event = CalendarEvent(
        title=title,
        description=description,
        start_time=start,
        end_time=end,
        all_day=all_day,
        event_type=event_type,
        task_id=task_id,
        user_id=user_id,
    )
    db.add(event)
    await db.flush()
    return {
        "id": event.id,
        "title": event.title,
        "start_time": event.start_time.isoformat(),
        "end_time": event.end_time.isoformat(),
        "event_type": event.event_type,
    }


@register_tool("list_calendar_events")
async def list_calendar_events(
    db: AsyncSession,
    user_id: int,
    start: Optional[str] = None,
    end: Optional[str] = None,
    limit: int = 20,
) -> Dict[str, Any]:
    """List calendar events for the user, optionally within a date range."""
    query = select(CalendarEvent).where(CalendarEvent.user_id == user_id)

    if start:
        try:
            start_dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
            query = query.where(CalendarEvent.start_time >= start_dt)
        except ValueError:
            pass
    if end:
        try:
            end_dt = datetime.fromisoformat(end.replace("Z", "+00:00"))
            query = query.where(CalendarEvent.end_time <= end_dt)
        except ValueError:
            pass

    query = query.order_by(CalendarEvent.start_time.asc()).limit(limit)
    result = await db.execute(query)
    events = result.scalars().all()

    return {
        "events": [
            {
                "id": e.id,
                "title": e.title,
                "start_time": e.start_time.isoformat(),
                "end_time": e.end_time.isoformat(),
                "event_type": e.event_type,
                "all_day": e.all_day,
            }
            for e in events
        ],
        "count": len(events),
    }
