# api/app/deps.py
"""FastAPI dependencies for authentication, authorization, DB and helpers."""

from __future__ import annotations

from typing import Optional, Union
import logging

from fastapi import Depends, HTTPException, Request, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.database import get_db
from app.core.redis import get_redis, RedisManager
from app.core.exceptions import UnauthorizedError, ForbiddenError
from app.models import User, UserRole

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------------
# Security
# ------------------------------------------------------------------------------

# auto_error=False => Authorization header yoksa 403 yerine biz 401 fırlatıyoruz.
security = HTTPBearer(auto_error=False)

# ------------------------------------------------------------------------------
# Auth helpers
# ------------------------------------------------------------------------------

async def get_current_user(
    db: AsyncSession = Depends(get_db),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    request: Request,
) -> User:
    """Extract and validate current user from a Bearer access token.

    - Token yok => 401
    - Token decode edilemedi / type != 'access' => 401
    - Kullanıcı bulunamadı / pasif => 401
    """
    token = None
    if credentials:
        token = credentials.credentials
    else:
        token = request.cookies.get("access_token") if request else None

    if not token:
        raise UnauthorizedError("Authorization header missing")

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
        if payload.get("type") != "access":
            raise UnauthorizedError("Invalid token type")

        sub = payload.get("sub")
        if sub is None:
            raise UnauthorizedError("Invalid token: missing subject")

        user_id = int(sub)  # sub string ise normalize et
    except (JWTError, ValueError):
        raise UnauthorizedError("Invalid token")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise UnauthorizedError("User not found")
    if not getattr(user, "is_active", False):
        raise UnauthorizedError("User account is disabled")

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Ensure user is active (redundant guard)."""
    if not current_user.is_active:
        raise UnauthorizedError("User account is disabled")
    return current_user


def _norm_role(role: Union[str, UserRole]) -> str:
    """Normalize role to string value."""
    return role.value if hasattr(role, "value") else str(role)


def require_roles(*roles: Union[str, UserRole]):
    """Dependency factory to enforce role-based access.

    Usage:
        Depends(require_roles(UserRole.admin))
        Depends(require_roles("admin", "moderator"))
    """
    allowed = {_norm_role(r) for r in roles}

    async def checker(current_user: User = Depends(get_current_user)) -> User:
        user_role = _norm_role(current_user.role)
        if user_role not in allowed:
            raise ForbiddenError("Insufficient permissions")
        return current_user

    return checker


# Convenience factories
def require_customer():
    return require_roles(UserRole.customer)


def require_freelancer():
    return require_roles(UserRole.freelancer)


def require_admin():
    return require_roles(UserRole.admin)


def require_moderator():
    return require_roles(UserRole.admin, UserRole.moderator)


def require_helpdesk():
    return require_roles(UserRole.admin, UserRole.moderator, UserRole.helpdesk)


async def get_optional_user(
    db: AsyncSession = Depends(get_db),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    ),
) -> Optional[User]:
    """Return current user if token is present & valid; otherwise None."""
    if not credentials:
        return None
    try:
        return await get_current_user(db=db, credentials=credentials)
    except (UnauthorizedError, HTTPException):
        return None


# ------------------------------------------------------------------------------
# Rate limiting
# ------------------------------------------------------------------------------

async def rate_limit_check(
    request: Request,
    redis: RedisManager = Depends(get_redis),
    limit: int = 100,
    window: int = 60,
):
    """Simple IP-based rate limit guard.

    Redis yoksa / hata olursa sessiz geçer (dev/test kolaylığı).
    """
    try:
        client_ip = (
            request.headers.get("X-Forwarded-For", request.client.host)
            .split(",")[0]
            .strip()
        )
        key = f"rate_limit:{client_ip}"
        allowed, remaining = await redis.check_rate_limit(key, limit, window)
        if not allowed:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded",
                headers={"Retry-After": str(window)},
            )
        return {"remaining": remaining}
    except Exception:  # pragma: no cover (test/dev)
        return {"remaining": limit}


# ------------------------------------------------------------------------------
# Pagination
# ------------------------------------------------------------------------------

class PaginationParams:
    def __init__(
        self,
        page: int = 1,
        size: int = settings.DEFAULT_PAGE_SIZE,
        max_size: int = settings.MAX_PAGE_SIZE,
    ):
        self.page = max(1, page)
        self.size = min(max(1, size), max_size)
        self.offset = (self.page - 1) * self.size


def get_pagination(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
) -> PaginationParams:
    """Return normalized pagination parameters."""
    return PaginationParams(page=page, size=size)
