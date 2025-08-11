# api/app/deps.py
"""FastAPI dependencies for authentication, database, etc."""

from typing import Generator, Optional, Iterable
from fastapi import Depends, HTTPException, status, Request, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt

from app.core.database import get_db
from app.core.redis import get_redis, RedisManager
from app.config import settings
from app.models import User, UserRole
from app.core.exceptions import UnauthorizedError, ForbiddenError
import logging

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer()

async def get_current_user(
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """Get current authenticated user from JWT token"""
    
    try:
        # Decode JWT token
        payload = jwt.decode(
            credentials.credentials,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
        token_type = payload.get("type")
        if token_type != "access":
            raise UnauthorizedError("Invalid token type")

        user_id_str = payload.get("sub")  # ✅ String olarak al
        if user_id_str is None:
            raise UnauthorizedError("Invalid token")
            
        user_id: int = int(user_id_str)  # ✅ String'i int'e çevir
        
    except (JWTError, ValueError):  # ✅ ValueError'u da yakala
        raise UnauthorizedError("Invalid token")
    
    # Get user from database
    from sqlalchemy import select
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise UnauthorizedError("User not found")
    
    if not user.is_active:
        raise UnauthorizedError("User account is disabled")
    
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise UnauthorizedError("User account is disabled")
    return current_user

async def require_roles(*roles: Iterable[UserRole]):
    async def _inner(user: User = Depends(get_current_user)) -> User:
        # veritabanında rol string ise normalize edelim
        user_role = getattr(user.role, "value", user.role)
        allowed = {getattr(r, "value", r) for r in roles}
        if user_role not in allowed:
            raise ForbiddenError("Insufficient permissions")
        return user
    return _inner

require_customer = awaitable_dependency = require_roles(UserRole.customer)
require_admin    = awaitable_dependency = require_roles(UserRole.admin, UserRole.moderator)

# Role-specific dependencies
require_admin = require_roles(UserRole.admin)
require_moderator = require_roles(UserRole.admin, UserRole.moderator)
require_helpdesk = require_roles(UserRole.admin, UserRole.moderator, UserRole.helpdesk)
require_freelancer = require_roles(UserRole.freelancer, UserRole.admin)
require_customer = require_roles(UserRole.customer, UserRole.admin)

async def get_optional_user(
    db: AsyncSession = Depends(get_db),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[User]:
    """Get current user if authenticated, otherwise None"""
    
    if not credentials:
        return None
    
    try:
        return await get_current_user(db, credentials)
    except (UnauthorizedError, HTTPException):
        return None

# Rate limiting dependency
async def rate_limit_check(request: Request, limit: int = 100, window: int = 60):
    try:
        client_ip = request.headers.get("X-Forwarded-For", request.client.host).split(",")[0].strip()
        key = f"rate_limit:{client_ip}"
        allowed, remaining = await redis.check_rate_limit(key, limit, window)
        if not allowed:
            raise HTTPException(status_code=429, detail="Rate limit exceeded", headers={"Retry-After": str(window)})
        return {"remaining": remaining}
    except Exception:
        # test/dev ortamında sessiz geç
        return {"remaining": limit}

# Pagination dependency
class PaginationParams:
    def __init__(
        self,
        page: int = 1,
        size: int = settings.DEFAULT_PAGE_SIZE,
        max_size: int = settings.MAX_PAGE_SIZE
    ):
        self.page = max(1, page)
        self.size = min(max(1, size), max_size)
        self.offset = (self.page - 1) * self.size


def get_pagination(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size")
) -> PaginationParams:
    """Get pagination parameters"""
    return PaginationParams(page=page, size=size)