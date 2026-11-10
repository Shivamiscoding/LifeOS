"""FileDocument Pydantic schemas."""
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


class FileDocumentBase(BaseModel):
    original_name: str
    file_type: str
    file_size: int
    category: str = "general"
    tags: List[str] = []


class FileDocumentResponse(FileDocumentBase):
    id: int
    filename: str
    file_path: str
    extracted_text: Optional[str] = None
    summary: Optional[str] = None
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class FileDocumentUpdate(BaseModel):
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    summary: Optional[str] = None
