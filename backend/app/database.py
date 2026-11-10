"""Async SQLAlchemy database setup."""
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings

settings = get_settings()

# Create engine — supports both SQLite (aiosqlite) and PostgreSQL (asyncpg)
connect_args = {}
if "sqlite" in settings.database_url:
    connect_args = {"check_same_thread": False}

engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    connect_args=connect_args,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that provides a database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def create_all_tables() -> None:
    """Create all database tables on startup."""
    # Import all models so they register with Base.metadata
    import app.models.user  # noqa: F401
    import app.models.project  # noqa: F401
    import app.models.task  # noqa: F401
    import app.models.calendar_event  # noqa: F401
    import app.models.file_document  # noqa: F401
    import app.models.automation  # noqa: F401
    import app.models.execution_log  # noqa: F401
    import app.models.ai_session  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
