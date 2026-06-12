from collections.abc import AsyncIterator

from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.db.base import Base


SQLITE_FALLBACK_URL = "sqlite+aiosqlite:///./leadhunter.db"


def _create_session_factory(database_url: str):
    engine = create_async_engine(database_url, pool_pre_ping=True)
    return engine, async_sessionmaker(engine, expire_on_commit=False)


engine, AsyncSessionLocal = _create_session_factory(str(settings.database_url))


async def init_db() -> None:
    global engine, AsyncSessionLocal

    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except (OperationalError, OSError) as exc:
        if str(engine.url) == SQLITE_FALLBACK_URL:
            raise
        engine, AsyncSessionLocal = _create_session_factory(SQLITE_FALLBACK_URL)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        yield session
