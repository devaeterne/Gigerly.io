# tests/conftest.py
"""Pytest configuration and fixtures (PostgreSQL/async)."""

import os
import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator, Generator
from app.config import settings  

try:
    from httpx import AsyncClient
except ModuleNotFoundError:  # pragma: no cover
    AsyncClient = None

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    AsyncConnection,
    create_async_engine,
    async_sessionmaker,
)

from app.main import app
from app.core.database import get_db
from app.models import User, UserProfile, UserRole, UserStatus

# ZORUNLU: Postgres test DB URL'i (ör: postgresql+asyncpg://user:pass@db:5432/gigerlyio_db_test)
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL") or os.getenv("DATABASE_URL")

if not TEST_DATABASE_URL or not TEST_DATABASE_URL.startswith("postgresql+asyncpg://"):
    raise RuntimeError(
        "TEST_DATABASE_URL must be set to a PostgreSQL DSN, e.g. "
        "postgresql+asyncpg://user:pass@host:5432/dbname"
    )

@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="session")
async def test_db_engine() -> AsyncGenerator[AsyncEngine, None]:
    """Create async engine for tests (PostgreSQL)."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
        future=True,
    )
    try:
        # Not: Şema alembic ile önceden migrate edilmiş olmalı.
        yield engine
    finally:
        await engine.dispose()

@pytest_asyncio.fixture()
async def test_db(test_db_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """
    Per-test session + outer transaction.
    Her test başında BEGIN, sonunda ROLLBACK yaparız; veritabanı temiz kalır.
    """
    async with test_db_engine.connect() as conn:  # type: AsyncConnection
        trans = await conn.begin()
        SessionLocal = async_sessionmaker(bind=conn, expire_on_commit=False, class_=AsyncSession)
        async with SessionLocal() as session:
            try:
                yield session
            finally:
                await session.close()
                # Tüm değişiklikleri geri al
                await trans.rollback()

@pytest.fixture
async def client(test_db) -> AsyncGenerator["AsyncClient", None]:
    """Create test HTTP client with /api/v1 auto-prefix."""

    if AsyncClient is None:  # pragma: no cover
        pytest.skip("httpx not installed")

    async def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db

    prefix = settings.API_V1_STR.rstrip("/")

    async with AsyncClient(app=app, base_url="http://test") as real_client:
        class PrefixedClient:
            def __init__(self, client, prefix):
                self._c = client
                self._p = prefix

            def _fix(self, url: str) -> str:
                # Tam URL ise dokunma
                if url.startswith("http://") or url.startswith("https://"):
                    return url
                # Başa / ekle
                if not url.startswith("/"):
                    url = "/" + url
                # Zaten prefix'li ise bırak, değilse ekle
                if url == self._p or url.startswith(self._p + "/"):
                    return url
                return self._p + url

            async def get(self, url, **kw):     return await self._c.get(self._fix(url), **kw)
            async def post(self, url, **kw):    return await self._c.post(self._fix(url), **kw)
            async def put(self, url, **kw):     return await self._c.put(self._fix(url), **kw)
            async def patch(self, url, **kw):   return await self._c.patch(self._fix(url), **kw)
            async def delete(self, url, **kw):  return await self._c.delete(self._fix(url), **kw)

        yield PrefixedClient(real_client, prefix)

    app.dependency_overrides.clear()


# ---- Test kullanıcıları ----

@pytest_asyncio.fixture()
async def test_user(test_db: AsyncSession) -> User:
    user = User(
        email="test@example.com",
        role=UserRole.freelancer,
        status=UserStatus.active,
        is_active=True,
        is_verified=True,
    )
    test_db.add(user)
    await test_db.flush()

    profile = UserProfile(
        user_id=user.id,
        display_name="Test User",
        currency="USD",
        is_available=True,
        is_profile_public=True,
        total_earnings=0,
        completed_projects=0,
        total_reviews=0,
    )
    test_db.add(profile)
    await test_db.flush()
    await test_db.refresh(user)
    return user

@pytest_asyncio.fixture()
async def test_customer(test_db: AsyncSession) -> User:
    user = User(
        email="customer@example.com",
        role=UserRole.customer,
        status=UserStatus.active,
        is_active=True,
        is_verified=True,
    )
    test_db.add(user)
    await test_db.flush()

    profile = UserProfile(
        user_id=user.id,
        display_name="Test Customer",
        currency="USD",
        is_available=True,
        is_profile_public=True,
        total_earnings=0,
        completed_projects=0,
        total_reviews=0,
    )
    test_db.add(profile)
    await test_db.flush()
    await test_db.refresh(user)
    return user

@pytest_asyncio.fixture()
async def test_admin(test_db: AsyncSession) -> User:
    user = User(
        email="admin@example.com",
        role=UserRole.admin,
        status=UserStatus.active,
        is_active=True,
        is_verified=True,
    )
    test_db.add(user)
    await test_db.flush()

    profile = UserProfile(
        user_id=user.id,
        display_name="Test Admin",
        currency="USD",
        is_available=False,
        is_profile_public=True,
        total_earnings=0,
        completed_projects=0,
        total_reviews=0,
    )
    test_db.add(profile)
    await test_db.flush()
    await test_db.refresh(user)
    return user

# ---- Header yardımcıları ----

@pytest.fixture()
def auth_headers(test_user: User) -> dict:
    from app.routes.auth import create_access_token
    token = create_access_token(data={"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture()
def admin_headers(test_admin: User) -> dict:
    from app.routes.auth import create_access_token
    token = create_access_token(data={"sub": str(test_admin.id)})
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture()
def customer_headers(test_customer: User) -> dict:
    from app.routes.auth import create_access_token
    token = create_access_token(data={"sub": str(test_customer.id)})
    return {"Authorization": f"Bearer {token}"}
