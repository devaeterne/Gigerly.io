# api/app/routes/users.py
"""User management routes"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models import User, UserProfile, UserRole
from app.schemas.user import (
    UserResponse, UserListResponse, UserProfileUpdate, UserProfileResponse,
    UserUpdate
)
from app.deps import get_current_user, require_admin, require_moderator, get_pagination, PaginationParams
from app.core.exceptions import NotFoundError, ForbiddenError
from app.schemas.common import PaginatedResponse, PaginationMeta
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users")

@router.get("/me", response_model=UserResponse)
async def get_my_profile(current_user: User = Depends(get_current_user)):
    """Get current user's profile"""
    return current_user

@router.put("/me/profile", response_model=UserProfileResponse)
async def update_my_profile(
    profile_data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update current user's profile"""
    
    if not current_user.profile:
        raise NotFoundError("Profile not found")
    
    # Update profile fields
    update_data = profile_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_user.profile, field, value)
    
    await db.commit()
    await db.refresh(current_user.profile)
    
    logger.info(f"Profile updated for user: {current_user.email} (ID: {current_user.id})")
    
    return current_user.profile

@router.get("", response_model=PaginatedResponse)
async def list_users(
    role: Optional[UserRole] = Query(None, description="Filter by user role"),
    search: Optional[str] = Query(None, description="Search by name or email"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    pagination: PaginationParams = Depends(get_pagination),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_moderator)
):
    """List users (Admin/Moderator only)"""
    
    # Build query
    query = select(User).options(selectinload(User.profile))
    
    # Apply filters
    filters = []
    if role:
        filters.append(User.role == role)
    if is_active is not None:
        filters.append(User.is_active == is_active)
    if search:
        search_filter = or_(
            User.email.ilike(f"%{search}%"),
            UserProfile.display_name.ilike(f"%{search}%"),
            UserProfile.first_name.ilike(f"%{search}%"),
            UserProfile.last_name.ilike(f"%{search}%")
        )
        query = query.join(UserProfile, isouter=True)
        filters.append(search_filter)
    
    if filters:
        query = query.where(and_(*filters))
    
    # Count total
    count_query = select(User)
    if filters:
        if search:
            count_query = count_query.join(UserProfile, isouter=True)
        count_query = count_query.where(and_(*filters))
    
    total_result = await db.execute(count_query)
    total = len(total_result.scalars().all())
    
    # Apply pagination
    query = query.offset(pagination.offset).limit(pagination.size)
    result = await db.execute(query)
    users = result.scalars().all()
    
    # Convert to list response format
    user_list = []
    for user in users:
        user_dict = {
            "id": user.id,
            "email": user.email,
            "role": user.role,
            "status": user.status,
            "is_active": user.is_active,
            "created_at": user.created_at,
            "display_name": user.profile.display_name if user.profile else None,
            "title": user.profile.title if user.profile else None,
            "country": user.profile.country if user.profile else None,
            "average_rating": user.profile.average_rating if user.profile else None,
            "completed_projects": user.profile.completed_projects if user.profile else 0,
        }
        user_list.append(UserListResponse(**user_dict))
    
    # Pagination metadata
    pages = (total + pagination.size - 1) // pagination.size
    meta = PaginationMeta(
        page=pagination.page,
        size=pagination.size,
        total=total,
        pages=pages,
        has_next=pagination.page < pages,
        has_prev=pagination.page > 1
    )
    
    return PaginatedResponse(data=user_list, meta=meta)

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user by ID"""
    
    result = await db.execute(
        select(User)
        .options(selectinload(User.profile))
        .where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise NotFoundError("User", user_id)
    
    # Check permissions
    if current_user.role not in ["admin", "moderator"]:
        # Only show public profiles to other users
        if not user.profile or not user.profile.is_profile_public:
            raise ForbiddenError("Profile is private")
    
    return user

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Update user (Admin only)"""
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise NotFoundError("User", user_id)
    
    # Update user fields
    update_data = user_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    await db.commit()
    await db.refresh(user)
    
    logger.info(f"User updated by admin: {user.email} (ID: {user.id}) by {current_user.email}")
    
    return user

@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Delete user (Admin only)"""
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise NotFoundError("User", user_id)
    
    if user.id == current_user.id:
        raise ForbiddenError("Cannot delete your own account")
    
    await db.delete(user)
    await db.commit()
    
    logger.warning(f"User deleted by admin: {user.email} (ID: {user.id}) by {current_user.email}")
    
    return {"message": "User deleted successfully"}
