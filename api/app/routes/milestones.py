# api/app/routes/milestones.py
"""Milestone management routes"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import User
from app.deps import get_current_user

router = APIRouter(prefix="/milestones")

@router.get("")
async def list_milestones(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List milestones"""
    return {"message": "Milestones endpoint - Coming soon"}

@router.post("/{milestone_id}/fund")
async def fund_milestone(
    milestone_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Fund milestone"""
    return {"message": f"Fund milestone {milestone_id} - Coming soon"}