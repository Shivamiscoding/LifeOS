"""Pagination helper."""
from typing import TypeVar, Generic, List, Optional
from pydantic import BaseModel

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool


def paginate(items: List[T], total: int, page: int, page_size: int) -> PaginatedResponse[T]:
    """Build a paginated response."""
    total_pages = max(1, (total + page_size - 1) // page_size)
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    )


def get_offset(page: int, page_size: int) -> int:
    return (page - 1) * page_size
