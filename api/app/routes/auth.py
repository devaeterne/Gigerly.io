# api/app/routes/auth.py
"""Authentication routes"""

from datetime import datetime, timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import JWTError, jwt
from passlib.context import CryptContext
import httpx

from app.core.database import get_db
from app.core.redis import get_redis, RedisManager
from app.config import settings
from app.models import User, UserProfile, UserRole, UserStatus
from app.schemas.user import (
    LoginRequest, LoginResponse, RefreshTokenRequest, GoogleAuthRequest,
    UserResponse, UserCreate, PasswordResetRequest, PasswordResetConfirm,
    ChangePasswordRequest, DeviceTokenCreate, DeviceTokenResponse
)
from app.core.exceptions import UnauthorizedError, ConflictError, NotFoundError, ValidationError
from app.deps import get_current_user, rate_limit_check
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth")

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

async def authenticate_user(db: AsyncSession, email: str, password: str) -> User:
    """Authenticate user with email and password"""
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    
    if not user or not user.password_hash:
        raise UnauthorizedError("Invalid email or password")
    
    if not verify_password(password, user.password_hash):
        raise UnauthorizedError("Invalid email or password")
    
    if not user.is_active:
        raise UnauthorizedError("Account is disabled")
    
    return user

@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(rate_limit_check)
):
    """Register a new user"""
    
    # Check if user already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise ConflictError("Email already registered")
    
    # Validate password if provided
    if not user_data.password and not user_data.google_sub:
        raise ValidationError("Password or Google authentication required")
    
    # Create user
    user_dict = user_data.dict(exclude_unset=True)
    if user_data.password:
        user_dict["password_hash"] = hash_password(user_data.password)
        del user_dict["password"]
    
    # Set default values
    user_dict.update({
        "status": UserStatus.ACTIVE,
        "is_active": True,
        "is_verified": bool(user_data.google_sub),  # Google users are auto-verified
        "email_verified_at": datetime.utcnow() if user_data.google_sub else None
    })
    
    user = User(**user_dict)
    db.add(user)
    await db.flush()
    
    # Create default profile
    profile = UserProfile(
        user_id=user.id,
        currency="USD",
        is_available=True,
        is_profile_public=True,
        total_earnings=0,
        completed_projects=0,
        total_reviews=0
    )
    db.add(profile)
    
    await db.commit()
    await db.refresh(user)
    
    logger.info(f"New user registered: {user.email} (ID: {user.id})")
    
    return user

@router.post("/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db),
    redis: RedisManager = Depends(get_redis),
    _: dict = Depends(rate_limit_check)
):
    """Login with email and password"""
    
    user = await authenticate_user(db, login_data.email, login_data.password)
    
    # Update last login
    user.last_login_at = datetime.utcnow()
    await db.commit()
    
    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    # Store refresh token in Redis
    await redis.set(f"refresh_token:{user.id}", refresh_token, expire=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600)
    
    logger.info(f"User logged in: {user.email} (ID: {user.id})")
    
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=user
    )

@router.post("/refresh", response_model=LoginResponse)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
    redis: RedisManager = Depends(get_redis)
):
    """Refresh access token"""
    
    try:
        payload = jwt.decode(
            refresh_data.refresh_token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        if payload.get("type") != "refresh":
            raise UnauthorizedError("Invalid token type")
        
        user_id = payload.get("sub")
        if not user_id:
            raise UnauthorizedError("Invalid token")
        
    except JWTError:
        raise UnauthorizedError("Invalid refresh token")
    
    # Check if refresh token exists in Redis
    stored_token = await redis.get(f"refresh_token:{user_id}")
    if not stored_token or stored_token != refresh_data.refresh_token:
        raise UnauthorizedError("Invalid refresh token")
    
    # Get user
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()
    
    if not user or not user.is_active:
        raise UnauthorizedError("User not found or disabled")
    
    # Create new tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    new_refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    # Update refresh token in Redis
    await redis.delete(f"refresh_token:{user_id}")
    await redis.set(f"refresh_token:{user_id}", new_refresh_token, expire=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600)
    
    return LoginResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=user
    )

@router.post("/google", response_model=LoginResponse)
async def google_auth(
    google_data: GoogleAuthRequest,
    db: AsyncSession = Depends(get_db),
    redis: RedisManager = Depends(get_redis)
):
    """Authenticate with Google OAuth token"""
    
    # Verify Google token
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"https://www.googleapis.com/oauth2/v1/userinfo?access_token={google_data.google_token}"
            )
            response.raise_for_status()
            google_user = response.json()
            
        except httpx.HTTPError:
            raise UnauthorizedError("Invalid Google token")
    
    if not google_user.get("email"):
        raise UnauthorizedError("Email not provided by Google")
    
    # Check if user exists
    result = await db.execute(
        select(User).where(
            (User.email == google_user["email"]) | 
            (User.google_sub == google_user["id"])
        )
    )
    user = result.scalar_one_or_none()
    
    if user:
        # Update Google info if needed
        if not user.google_sub:
            user.google_sub = google_user["id"]
            user.google_email_verified = google_user.get("verified_email", False)
            user.is_verified = True
            user.email_verified_at = datetime.utcnow()
        
        user.last_login_at = datetime.utcnow()
        await db.commit()
        
    else:
        # Create new user
        user = User(
            email=google_user["email"],
            google_sub=google_user["id"],
            google_email_verified=google_user.get("verified_email", False),
            role=UserRole.FREELANCER,
            status=UserStatus.ACTIVE,
            is_active=True,
            is_verified=True,
            email_verified_at=datetime.utcnow(),
            last_login_at=datetime.utcnow()
        )
        db.add(user)
        await db.flush()
        
        # Create profile with Google info
        profile = UserProfile(
            user_id=user.id,
            display_name=google_user.get("name"),
            first_name=google_user.get("given_name"),
            last_name=google_user.get("family_name"),
            avatar_url=google_user.get("picture"),
            currency="USD",
            is_available=True,
            is_profile_public=True,
            total_earnings=0,
            completed_projects=0,
            total_reviews=0
        )
        db.add(profile)
        await db.commit()
        await db.refresh(user)
        
        logger.info(f"New Google user registered: {user.email} (ID: {user.id})")
    
    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    # Store refresh token
    await redis.set(f"refresh_token:{user.id}", refresh_token, expire=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600)
    
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=user
    )

@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    redis: RedisManager = Depends(get_redis)
):
    """Logout user"""
    
    # Remove refresh token from Redis
    await redis.delete(f"refresh_token:{current_user.id}")
    
    logger.info(f"User logged out: {current_user.email} (ID: {current_user.id})")
    
    return {"message": "Successfully logged out"}

@router.post("/change-password")
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Change user password"""
    
    if not current_user.password_hash:
        raise ValidationError("Account does not have a password set")
    
    if not verify_password(password_data.current_password, current_user.password_hash):
        raise UnauthorizedError("Current password is incorrect")
    
    # Update password
    current_user.password_hash = hash_password(password_data.new_password)
    await db.commit()
    
    logger.info(f"Password changed for user: {current_user.email} (ID: {current_user.id})")
    
    return {"message": "Password updated successfully"}

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@router.post("/device-token", response_model=DeviceTokenResponse)
async def register_device_token(
    token_data: DeviceTokenCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Register FCM device token for push notifications"""
    
    from app.models import DeviceToken
    
    # Check if token already exists
    result = await db.execute(
        select(DeviceToken).where(DeviceToken.fcm_token == token_data.fcm_token)
    )
    existing_token = result.scalar_one_or_none()
    
    if existing_token:
        # Update existing token
        existing_token.user_id = current_user.id
        existing_token.platform = token_data.platform
        existing_token.device_id = token_data.device_id
        existing_token.is_active = True
        existing_token.last_used_at = datetime.utcnow()
        device_token = existing_token
    else:
        # Create new token
        device_token = DeviceToken(
            user_id=current_user.id,
            fcm_token=token_data.fcm_token,
            platform=token_data.platform,
            device_id=token_data.device_id,
            is_active=True,
            last_used_at=datetime.utcnow()
        )
        db.add(device_token)
    
    await db.commit()
    await db.refresh(device_token)
    
    return device_token