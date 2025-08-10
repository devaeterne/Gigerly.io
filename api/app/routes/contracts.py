# api/app/routes/contracts.py
"""Contract management routes"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models import Contract, User
from app.deps import get_current_user
from app.core.exceptions import NotFoundError

router = APIRouter(prefix="/contracts")

@router.get("")
async def list_contracts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List user's contracts"""
    return {"message": "Contracts endpoint - Coming soon"}

@router.get("/{contract_id}")
async def get_contract(
    contract_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get contract by ID"""
    return {"message": f"Contract {contract_id} - Coming soon"}