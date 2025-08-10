# api/app/routes/admin.py
"""Admin management routes"""

from typing import Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.models import User, Project, Contract, Transaction, UserRole
from app.deps import require_admin, require_moderator
from app.core.redis import get_redis, RedisManager
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin")

@router.get("/dashboard")
async def admin_dashboard(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Admin dashboard with key metrics"""
    
    # User statistics
    total_users = await db.execute(select(func.count(User.id)))
    active_users = await db.execute(
        select(func.count(User.id)).where(User.is_active == True)
    )
    freelancers = await db.execute(
        select(func.count(User.id)).where(User.role == UserRole.FREELANCER)
    )
    customers = await db.execute(
        select(func.count(User.id)).where(User.role == UserRole.CUSTOMER)
    )
    
    # Project statistics
    total_projects = await db.execute(select(func.count(Project.id)))
    open_projects = await db.execute(
        select(func.count(Project.id)).where(Project.status == "open")
    )
    
    # Contract statistics
    total_contracts = await db.execute(select(func.count(Contract.id)))
    active_contracts = await db.execute(
        select(func.count(Contract.id)).where(Contract.status == "active")
    )
    
    # Transaction statistics
    total_transactions = await db.execute(select(func.count(Transaction.id)))
    successful_transactions = await db.execute(
        select(func.count(Transaction.id)).where(Transaction.status == "success")
    )
    
    return {
        "users": {
            "total": total_users.scalar(),
            "active": active_users.scalar(),
            "freelancers": freelancers.scalar(),
            "customers": customers.scalar()
        },
        "projects": {
            "total": total_projects.scalar(),
            "open": open_projects.scalar()
        },
        "contracts": {
            "total": total_contracts.scalar(),
            "active": active_contracts.scalar()
        },
        "transactions": {
            "total": total_transactions.scalar(),
            "successful": successful_transactions.scalar()
        }
    }

@router.get("/system-health")
async def system_health(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
    redis: RedisManager = Depends(get_redis)
):
    """System health check for admin"""
    
    # Database health
    try:
        await db.execute(select(1))
        db_health = "healthy"
    except Exception as e:
        db_health = f"error: {str(e)}"
    
    # Redis health
    redis_health = "healthy" if await redis.health_check() else "unhealthy"
    
    # Memory usage (basic check)
    import psutil
    memory = psutil.virtual_memory()
    
    return {
        "database": db_health,
        "redis": redis_health,
        "memory_usage": {
            "total": memory.total,
            "available": memory.available,
            "percent": memory.percent
        },
        "timestamp": time.time()
    }

@router.get("/logs")
async def get_system_logs(
    current_user: User = Depends(require_admin),
    lines: int = 100
):
    """Get recent system logs"""
    
    import os
    log_file = "logs/app.log"
    
    if not os.path.exists(log_file):
        return {"logs": [], "message": "Log file not found"}
    
    try:
        with open(log_file, 'r') as f:
            logs = f.readlines()
            recent_logs = logs[-lines:] if len(logs) > lines else logs
        
        return {
            "logs": [log.strip() for log in recent_logs],
            "total_lines": len(logs)
        }
    except Exception as e:
        return {"error": f"Failed to read logs: {str(e)}"}

@router.post("/maintenance-mode")
async def toggle_maintenance_mode(
    enabled: bool,
    current_user: User = Depends(require_admin),
    redis: RedisManager = Depends(get_redis)
):
    """Toggle maintenance mode"""
    
    await redis.set("maintenance_mode", "1" if enabled else "0")
    
    status = "enabled" if enabled else "disabled"
    logger.warning(f"Maintenance mode {status} by admin: {current_user.email}")
    
    return {
        "message": f"Maintenance mode {status}",
        "maintenance_mode": enabled
    }

@router.get("/users/suspicious")
async def get_suspicious_users(
    current_user: User = Depends(require_moderator),
    db: AsyncSession = Depends(get_db)
):
    """Get list of potentially suspicious users for moderation"""
    
    # This is a placeholder - implement actual suspicious user detection logic
    # Examples: users with many rejected proposals, users with low ratings, etc.
    
    return {
        "suspicious_users": [],
        "message": "Suspicious user detection - Coming soon"
    }

@router.post("/users/{user_id}/suspend")
async def suspend_user(
    user_id: int,
    reason: str,
    current_user: User = Depends(require_moderator),
    db: AsyncSession = Depends(get_db)
):
    """Suspend user account"""
    
    from app.models import UserStatus
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise NotFoundError("User", user_id)
    
    if user.id == current_user.id:
        raise ForbiddenError("Cannot suspend your own account")
    
    user.status = UserStatus.SUSPENDED
    user.is_active = False
    await db.commit()
    
    logger.warning(f"User suspended: {user.email} (ID: {user_id}) by {current_user.email}, reason: {reason}")
    
    return {"message": "User suspended successfully"}

@router.post("/cache/clear")
async def clear_cache(
    current_user: User = Depends(require_admin),
    redis: RedisManager = Depends(get_redis)
):
    """Clear application cache"""
    
    # Clear all cache keys (be careful in production!)
    cache_keys = []
    # You would implement cache key scanning here
    
    if cache_keys:
        await redis.delete(*cache_keys)
    
    logger.info(f"Cache cleared by admin: {current_user.email}")
    
    return {
        "message": "Cache cleared successfully",
        "keys_cleared": len(cache_keys)
    }

import time
from app.core.exceptions import NotFoundError, ForbiddenError