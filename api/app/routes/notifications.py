# api/app/routes/notifications.py
"""Notification management routes"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models import Notification, NotificationType, User
from app.deps import get_current_user, get_pagination, PaginationParams
from app.schemas.common import PaginatedResponse, PaginationMeta
from app.core.exceptions import NotFoundError
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/notifications")

@router.get("", response_model=PaginatedResponse)
async def list_notifications(
    unread_only: bool = Query(False, description="Show only unread notifications"),
    type_filter: Optional[NotificationType] = Query(None, description="Filter by notification type"),
    pagination: PaginationParams = Depends(get_pagination),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List user's notifications"""
    
    # Build query
    query = select(Notification).where(Notification.user_id == current_user.id)
    
    # Apply filters
    if unread_only:
        query = query.where(Notification.is_read == False)
    
    if type_filter:
        query = query.where(Notification.type == type_filter)
    
    # Count total
    total_result = await db.execute(query)
    total = len(total_result.scalars().all())
    
    # Apply sorting and pagination
    query = query.order_by(desc(Notification.created_at))
    query = query.offset(pagination.offset).limit(pagination.size)
    result = await db.execute(query)
    notifications = result.scalars().all()
    
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
    
    return PaginatedResponse(data=notifications, meta=meta)

@router.post("/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark notification as read"""
    
    result = await db.execute(
        select(Notification).where(
            and_(
                Notification.id == notification_id,
                Notification.user_id == current_user.id
            )
        )
    )
    notification = result.scalar_one_or_none()
    
    if not notification:
        raise NotFoundError("Notification", notification_id)
    
    notification.mark_as_read()
    await db.commit()
    
    return {"message": "Notification marked as read"}

@router.post("/read-all")
async def mark_all_notifications_read(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark all notifications as read"""
    
    await db.execute(
        Notification.__table__.update()
        .where(
            and_(
                Notification.user_id == current_user.id,
                Notification.is_read == False
            )
        )
        .values(is_read=True)
    )
    await db.commit()
    
    return {"message": "All notifications marked as read"}

@router.get("/unread-count")
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get count of unread notifications"""
    
    result = await db.execute(
        select(Notification).where(
            and_(
                Notification.user_id == current_user.id,
                Notification.is_read == False
            )
        )
    )
    unread_notifications = result.scalars().all()
    
    return {"unread_count": len(unread_notifications)}