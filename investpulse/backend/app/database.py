from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=False)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_session():
    async with async_session_maker() as session:
        yield session


async def init_db():
    # Import models so they register with Base.metadata
    import app.models.alert  # noqa: F401
    import app.models.alert_history  # noqa: F401
    import app.models.market  # noqa: F401
    import app.models.portfolio  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
