"""User-related schemas (Pydantic v2 compatible)"""

from typing import List, Optional
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field
from pydantic.types import condecimal

from app.models import UserRole, UserStatus
from .common import SkillSchema, MoneyAmount
from .notification import (
    DeviceTokenCreate,
    DeviceTokenUpdate,
    DeviceTokenResponse,
    RegisterDeviceTokenRequest,
    UpdateDeviceTokenRequest,
)

# Ratings like 4.75 -> DECIMAL(3,2)
AverageRating = condecimal(max_digits=3, decimal_places=2, ge=0, le=5)


# -------- Core user schemas --------
class UserBase(BaseModel):
    email: EmailStr
    role: UserRole = UserRole.customer  # Bu "customer" döndürür - Migration'la uyumlu
    status: UserStatus = UserStatus.active  # Bu "active" döndürür - Migration'la uyumlu  
    is_active: bool = True
    is_verified: bool = False

class UserCreate(BaseModel):
    email: EmailStr
    password: Optional[str] = Field(None, min_length=8)
    google_sub: Optional[str] = None  # Google OAuth id
    role: UserRole = UserRole.customer  # Bu "customer" döndürür


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None


class UserResponse(UserBase):
    id: int
    google_sub: Optional[str] = None
    google_email_verified: Optional[bool] = None
    last_login_at: Optional[datetime] = None
    email_verified_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    id: int
    email: str
    role: UserRole
    status: UserStatus
    is_active: bool
    display_name: Optional[str] = None
    title: Optional[str] = None
    country: Optional[str] = None
    average_rating: Optional[AverageRating] = None
    completed_projects: int = 0
    created_at: datetime

    class Config:
        from_attributes = True

# -------- Authentication schemas --------

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int  # seconds (e.g. 3600)


# Canonical refresh names
class RefreshRequest(BaseModel):
    refresh_token: str


class RefreshResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

# Backward-compat import aliases used by auth.py (if any)
class RefreshTokenRequest(RefreshRequest):
    pass

class RefreshTokenResponse(RefreshResponse):
    pass

# -------- Google OAuth / One-tap --------

class GoogleAuthRequest(BaseModel):
    # Google Sign-In / One Tap: client'tan gelen ID token
    id_token: str

class GoogleAuthCodeRequest(BaseModel):
    # Authorization code flow
    code: str
    redirect_uri: Optional[str] = None

class GoogleLinkRequest(BaseModel):
    id_token: str

class GoogleUnlinkRequest(BaseModel):
    pass

class GoogleAuthResponse(LoginResponse):
    pass

# -------- Registration / Email verify --------

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    role: UserRole = UserRole.customer

class RegisterResponse(BaseModel):
    user: UserResponse
    verification_required: bool = True

class EmailVerifyRequest(BaseModel):
    token: str

class ResendVerificationRequest(BaseModel):
    email: EmailStr

# -------- Password reset / change --------

class PasswordResetRequest(BaseModel):
    """Start reset (forgot password)"""
    email: EmailStr

class PasswordResetConfirmRequest(BaseModel):
    """Complete reset with token"""
    token: str
    new_password: str = Field(..., min_length=8)

class ResetPasswordRequest(PasswordResetRequest):
    pass

class ResetPasswordConfirmRequest(PasswordResetConfirmRequest):
    pass

class PasswordChangeRequest(BaseModel):
    """Authenticated password change"""
    current_password: str
    new_password: str = Field(..., min_length=8)

# 🔧 Geriye dönük isimler (auth.py importları için)
class PasswordReset(PasswordResetRequest):
    pass

class PasswordResetConfirm(PasswordResetConfirmRequest):
    pass

class ChangePasswordRequest(PasswordChangeRequest):
    pass

# (muhtemelen gerekmeyecek ama varsa)
class ChangePasswordResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None

# -------- Profile schemas --------

class UserProfileBase(BaseModel):
    display_name: Optional[str] = Field(None, max_length=100)
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    title: Optional[str] = Field(None, max_length=200)
    bio: Optional[str] = Field(None, max_length=2000)
    skills: Optional[List[SkillSchema]] = None
    hourly_rate: Optional[MoneyAmount] = None
    currency: str = Field("USD", pattern=r"^[A-Z]{3}$")
    country: Optional[str] = Field(None, max_length=100)
    city: Optional[str] = Field(None, max_length=100)
    timezone: Optional[str] = Field(None, max_length=50)
    website: Optional[str] = Field(None, max_length=500)
    linkedin_url: Optional[str] = Field(None, max_length=500)
    github_url: Optional[str] = Field(None, max_length=500)
    avatar_url: Optional[str] = Field(None, max_length=500)
    cover_image_url: Optional[str] = Field(None, max_length=500)
    total_earnings: MoneyAmount = 0
    completed_projects: int = 0
    average_rating: Optional[AverageRating] = None
    total_reviews: int = 0
    is_available: bool = False
    is_profile_public: bool = True


class UserProfileCreate(UserProfileBase):
    user_id: int


class UserProfileUpdate(BaseModel):
    display_name: Optional[str] = Field(None, max_length=100)
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    title: Optional[str] = Field(None, max_length=200)
    bio: Optional[str] = None
    skills: Optional[List[SkillSchema]] = None
    hourly_rate: Optional[MoneyAmount] = None
    currency: Optional[str] = Field(None, pattern=r"^[A-Z]{3}$")
    country: Optional[str] = Field(None, max_length=100)
    city: Optional[str] = Field(None, max_length=100)
    timezone: Optional[str] = Field(None, max_length=50)
    website: Optional[str] = Field(None, max_length=500)
    linkedin_url: Optional[str] = Field(None, max_length=500)
    github_url: Optional[str] = Field(None, max_length=500)
    avatar_url: Optional[str] = Field(None, max_length=500)
    cover_image_url: Optional[str] = Field(None, max_length=500)
    is_available: Optional[bool] = None
    is_profile_public: Optional[bool] = None


class UserProfileResponse(UserProfileBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
