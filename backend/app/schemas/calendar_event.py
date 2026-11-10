"""CalendarEvent Pydantic schemas."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, model_validator


class CalendarEventBase(BaseModel):
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    all_day: bool = False
    event_type: str = "personal"   # personal|work|meeting|reminder
    task_id: Optional[int] = None

    @model_validator(mode="after")
    def end_after_start(self) -> "CalendarEventBase":
        if not self.all_day and self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time")
        return self


class CalendarEventCreate(CalendarEventBase):
    pass


class CalendarEventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    all_day: Optional[bool] = None
    event_type: Optional[str] = None
    task_id: Optional[int] = None


class CalendarEventResponse(CalendarEventBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
