from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator
import asyncio

from config.settings import settings


# Create MySQL async engine
DATABASE_URL = f"mysql+asyncmy://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DATABASE}"

engine = create_async_engine(
    DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
    pool_size=5,
    max_overflow=10,
    pool_ping_timeout=300,
    pool_recycle=3600,
)

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create and provide database session"""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Close database connection"""
    await engine.dispose()


class DatabaseService:
    """Service for database operations"""
    
    @staticmethod
    async def save_booking(
        session: AsyncSession,
        name: str,
        email: str,
        date: str,
        time: str,
    ) -> None:
        """Save interview booking to MySQL database"""
        from models.database_models import InterviewBooking
        
        booking = InterviewBooking(
            name=name,
            email=email,
            date=date,
            time=time,
        )
        
        session.add(booking)
        await session.commit()