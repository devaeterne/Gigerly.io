# api/app/deps.py
"""FastAPI dependencies for authentication, database, etc."""

from typing import Generator, Optional
from fastapi import Depends, HTTPException, status, Request
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
        
        user_id: int = payload.get("sub")
        if user_id is None:
            raise UnauthorizedError("Invalid token")
        
    except JWTError:
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

def require_roles(*allowed_roles: UserRole):
    """Dependency factory to require specific user roles"""
    
    def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in allowed_roles:
            raise ForbiddenError(f"Access denied. Required roles: {', '.join(allowed_roles)}")
        return current_user
    
    return role_checker

# Role-specific dependencies
require_admin = require_roles(UserRole.ADMIN)
require_moderator = require_roles(UserRole.ADMIN, UserRole.MODERATOR)
require_helpdesk = require_roles(UserRole.ADMIN, UserRole.MODERATOR, UserRole.HELPDESK)
require_freelancer = require_roles(UserRole.FREELANCER, UserRole.ADMIN)
require_customer = require_roles(UserRole.CUSTOMER, UserRole.ADMIN)

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
async def rate_limit_check(
    request : Request,
    redis: RedisManager = Depends(get_redis),
    limit: int = 100,
    window: int = 3600
):
    """Rate limiting dependency"""
    
    # Get client IP
    xff = request.headers.get("X-Forwarded-For")
    xri = request.headers.get("X-Real-IP")
    client_ip = request.client.host
    if hasattr(request, 'headers'):
        # Check for forwarded IP
        forwarded_for = request.headers.get('X-Forwarded-For')
        if forwarded_for:
            client_ip = forwarded_for.split(',')[0].strip()
    
    # Check rate limit
    key = f"rate_limit:{client_ip}"
    allowed, remaining = await redis.check_rate_limit(key, limit, window)
    
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
            headers={"Retry-After": str(window)}
        )
    
    return {"remaining": remaining}

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

def get_pagination() -> PaginationParams:
    """Get pagination parameters"""
    return PaginationParams