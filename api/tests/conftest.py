# api/tests/conftest.py
"""Pytest configuration and fixtures"""

import pytest
import asyncio
from typing import AsyncGenerator, Generator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import get_db
from app.models import Base, User, UserProfile, UserRole, UserStatus
from app.config import settings

# Test database URL (in-memory SQLite for speed)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def test_db_engine():
    """Create test database engine"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=StaticPool,
        connect_args={
            "check_same_thread": False,
        },
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    await engine.dispose()

@pytest.fixture
async def test_db(test_db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session"""
    TestSessionLocal = async_sessionmaker(
        test_db_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with TestSessionLocal() as session:
        yield session

@pytest.fixture
async def client(test_db) -> AsyncGenerator[AsyncClient, None]:
    """Create test HTTP client"""
    
    async def override_get_db():
        yield test_db
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()

@pytest.fixture
async def test_user(test_db: AsyncSession) -> User:
    """Create a test user"""
    user = User(
        email="test@example.com",
        role=UserRole.FREELANCER,
        status=UserStatus.ACTIVE,
        is_active=True,
        is_verified=True
    )
    test_db.add(user)
    await test_db.flush()
    
    # Create profile
    profile = UserProfile(
        user_id=user.id,
        display_name="Test User",
        currency="USD",
        is_available=True,
        is_profile_public=True,
        total_earnings=0,
        completed_projects=0,
        total_reviews=0
    )
    test_db.add(profile)
    await test_db.commit()
    await test_db.refresh(user)
    
    return user

@pytest.fixture
async def test_customer(test_db: AsyncSession) -> User:
    """Create a test customer"""
    user = User(
        email="customer@example.com",
        role=UserRole.CUSTOMER,
        status=UserStatus.ACTIVE,
        is_active=True,
        is_verified=True
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
        total_reviews=0
    )
    test_db.add(profile)
    await test_db.commit()
    await test_db.refresh(user)
    
    return user

@pytest.fixture
async def test_admin(test_db: AsyncSession) -> User:
    """Create a test admin"""
    user = User(
        email="admin@example.com",
        role=UserRole.ADMIN,
        status=UserStatus.ACTIVE,
        is_active=True,
        is_verified=True
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
        total_reviews=0
    )
    test_db.add(profile)
    await test_db.commit()
    await test_db.refresh(user)
    
    return user

@pytest.fixture
def auth_headers(test_user: User) -> dict:
    """Create authorization headers for test user"""
    from app.routes.auth import create_access_token
    
    token = create_access_token(data={"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def admin_headers(test_admin: User) -> dict:
    """Create authorization headers for admin user"""
    from app.routes.auth import create_access_token
    
    token = create_access_token(data={"sub": str(test_admin.id)})
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def customer_headers(test_customer: User) -> dict:
    """Create authorization headers for customer user"""
    from app.routes.auth import create_access_token
    
    token = create_access_token(data={"sub": str(test_customer.id)})
    return {"Authorization": f"Bearer {token}"}