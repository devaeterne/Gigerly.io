# api/app/core/database.py
from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import logging

from app.config import settings

logger = logging.getLogger(__name__)

# --- Async engine (app runtime) ---
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_size=20,
    max_overflow=0,
)

# Async session factory
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# --- Sync engine (alembic/migration/admin işleri için) ---
sync_engine = create_engine(
    settings.DATABASE_URL.replace("+asyncpg", "+psycopg2"),
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_recycle=3600,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine,
)

# Metadata (gerekirse)
metadata = MetaData()


async def get_db() -> AsyncSession:
    """FastAPI dependency: async DB session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """
    Uygulama başlangıcında DB init.
    Alembic kullanıyoruz; tabloları burada yaratmıyoruz.
    İstersen ayar üzerinden koşullu yaratma bırakıyoruz.
    """
    from app.models import Base  # mapper'ların yüklenmesi için import şart

    if getattr(settings, "DB_AUTO_CREATE", False):
        # SADECE geliştirici ortamında kullan (boş DB'yi hızlı ayağa kaldırmak için)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database created via metadata.create_all (DB_AUTO_CREATE=True)")
    else:
        logger.info("Database init: skipping create_all (using Alembic migrations)")


async def close_db() -> None:
    """Engine'i kapat"""
    await engine.dispose()
    logger.info("Database connections closed")


async def check_db_health() -> bool:
    """Basit sağlık testi"""
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False
get_session = get_db