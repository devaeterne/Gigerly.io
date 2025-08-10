import pytest
from jose import jwt
from fastapi.security import HTTPAuthorizationCredentials

from app.routes.auth import create_access_token, create_refresh_token
from app.deps import get_current_user
from app.config import settings
from app.core.exceptions import UnauthorizedError


@pytest.mark.asyncio
async def test_token_type_claims():
    access = create_access_token({"sub": "1"})
    refresh = create_refresh_token({"sub": "1"})

    payload_access = jwt.decode(access, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    payload_refresh = jwt.decode(refresh, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])

    assert payload_access.get("type") == "access"
    assert payload_refresh.get("type") == "refresh"


@pytest.mark.asyncio
async def test_get_current_user_rejects_refresh_token(test_db, test_user):
    token = create_refresh_token({"sub": str(test_user.id)})
    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

    with pytest.raises(UnauthorizedError):
        await get_current_user(test_db, creds)


@pytest.mark.asyncio
async def test_get_current_user_accepts_access_token(test_db, test_user):
    token = create_access_token({"sub": str(test_user.id)})
    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

    user = await get_current_user(test_db, creds)
    assert user.id == test_user.id
