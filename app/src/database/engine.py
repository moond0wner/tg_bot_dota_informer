"""Engine database"""
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession

from ..utils.config import settings
from ..database.models import Base

engine = create_async_engine(url=f"mysql+aiomysql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}/{settings.DB_NAME}", echo=True)

async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def start_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

