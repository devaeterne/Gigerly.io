# api/app/routes/proposals.py
"""Proposal management routes"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models import Proposal, ProposalStatus, Project, ProjectStatus, User, UserRole, Contract
from app.schemas.proposal import (
    ProposalCreate, ProposalUpdate, ProposalResponse, ProposalListResponse
)
from app.deps import (
    get_current_user, require_freelancer, require_customer,
    get_pagination, PaginationParams
)
from app.core.exceptions import NotFoundError, ForbiddenError, ValidationError
from app.schemas.common import PaginatedResponse, PaginationMeta
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/proposals")

@router.post("", response_model=ProposalResponse)
async def create_proposal(
    proposal_data: ProposalCreate,
    current_user: User = Depends(require_freelancer),
    db: AsyncSession = Depends(get_db)
):
    """Create a new proposal (Freelancer only)"""
    
    # Check if project exists and is open
    result = await db.execute(select(Project).where(Project.id == proposal_data.project_id))
    project = result.scalar_one_or_none()
    
    if not project:
        raise NotFoundError("Project", proposal_data.project_id)
    
    if project.status != ProjectStatus.open:
        raise ValidationError("Project is not accepting proposals")
    
    if not project.allows_proposals:
        raise ValidationError("Project is not accepting proposals")
    
    if project.customer_id == current_user.id:
        raise ValidationError("You cannot submit proposal to your own project")
    
    # Check if freelancer already submitted proposal
    existing_result = await db.execute(
        select(Proposal).where(
            and_(
                Proposal.project_id == proposal_data.project_id,
                Proposal.freelancer_id == current_user.id
            )
        )
    )
    if existing_result.scalar_one_or_none():
        raise ValidationError("You have already submitted a proposal for this project")
    
    # Check proposal limit
    if project.proposal_count >= project.max_proposals:
        raise ValidationError("Project has reached maximum number of proposals")
    
    # Create proposal
    proposal_dict = proposal_data.dict(exclude_unset=True)
    proposal_dict.update({
        "freelancer_id": current_user.id,
        "status": ProposalStatus.pending
    })
    
    proposal = Proposal(**proposal_dict)
    db.add(proposal)
    
    # Update project proposal count
    project.proposal_count += 1
    
    await db.commit()
    await db.refresh(proposal)
    
    logger.info(f"Proposal created: Project {project.id} by {current_user.email} (ID: {proposal.id})")
    
    return proposal

@router.get("", response_model=PaginatedResponse)
async def list_proposals(
    project_id: Optional[int] = Query(None, description="Filter by project"),
    status: Optional[ProposalStatus] = Query(None, description="Filter by status"),
    pagination: PaginationParams = Depends(get_pagination),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List proposals"""
    
    # Build query
    query = select(Proposal).options(
        selectinload(Proposal.project),
        selectinload(Proposal.freelancer).selectinload(User.profile)
    )
    
    # Apply filters based on user role
    filters = []
    
    if current_user.role == UserRole.freelancer:
        # Freelancers see only their own proposals
        filters.append(Proposal.freelancer_id == current_user.id)
    elif current_user.role == UserRole.customer:
        # Customers see proposals for their projects
        query = query.join(Project)
        filters.append(Project.customer_id == current_user.id)
    elif current_user.role not in [UserRole.admin, UserRole.moderator]:
        raise ForbiddenError("Insufficient permissions")
    
    # Apply additional filters
    if project_id:
        filters.append(Proposal.project_id == project_id)
        
        # Additional permission check for specific project
        if current_user.role not in [UserRole.admin, UserRole.moderator]:
            project_result = await db.execute(select(Project).where(Project.id == project_id))
            project = project_result.scalar_one_or_none()
            if not project:
                raise NotFoundError("Project", project_id)
            
            if (current_user.role == UserRole.customer and project.customer_id != current_user.id):
                raise ForbiddenError("You can only view proposals for your own projects")
    
    if status:
        filters.append(Proposal.status == status)
    
    if filters:
        query = query.where(and_(*filters))
    
    # Count total
    count_query = select(Proposal)
    if current_user.role == UserRole.customer and not project_id:
        count_query = count_query.join(Project)
    if filters:
        count_query = count_query.where(and_(*filters))
    
    total_result = await db.execute(count_query)
    total = len(total_result.scalars().all())
    
    # Apply sorting and pagination
    query = query.order_by(desc(Proposal.created_at))
    query = query.offset(pagination.offset).limit(pagination.size)
    result = await db.execute(query)
    proposals = result.scalars().all()
    
    # Convert to list response format
    proposal_list = []
    for proposal in proposals:
        proposal_dict = {
            "id": proposal.id,
            "project_id": proposal.project_id,
            "project_title": proposal.project.title,
            "freelancer_id": proposal.freelancer_id,
            "freelancer_name": proposal.freelancer.profile.display_name if proposal.freelancer.profile else None,
            "cover_letter": proposal.cover_letter[:200] + "..." if len(proposal.cover_letter) > 200 else proposal.cover_letter,
            "bid_amount": proposal.bid_amount,
            "currency": proposal.currency,
            "estimated_delivery_days": proposal.estimated_delivery_days,
            "status": proposal.status,
            "created_at": proposal.created_at
        }
        proposal_list.append(ProposalListResponse(**proposal_dict))
    
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
    
    return PaginatedResponse(data=proposal_list, meta=meta)

@router.get("/{proposal_id}", response_model=ProposalResponse)
async def get_proposal(
    proposal_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get proposal by ID"""
    
    result = await db.execute(
        select(Proposal)
        .options(
            selectinload(Proposal.project),
            selectinload(Proposal.freelancer).selectinload(User.profile)
        )
        .where(Proposal.id == proposal_id)
    )
    proposal = result.scalar_one_or_none()
    
    if not proposal:
        raise NotFoundError("Proposal", proposal_id)
    
    # Check permissions
    if current_user.role not in [UserRole.admin, UserRole.moderator]:
        if (current_user.id != proposal.freelancer_id and 
            current_user.id != proposal.project.customer_id):
            raise ForbiddenError("You can only view your own proposals or proposals for your projects")
    
    return proposal

@router.put("/{proposal_id}", response_model=ProposalResponse)
async def update_proposal(
    proposal_id: int,
    proposal_data: ProposalUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_freelancer)
):
    """Update proposal (Freelancer only)"""
    
    result = await db.execute(
        select(Proposal)
        .options(selectinload(Proposal.project))
        .where(Proposal.id == proposal_id)
    )
    proposal = result.scalar_one_or_none()
    
    if not proposal:
        raise NotFoundError("Proposal", proposal_id)
    
    if current_user.id != proposal.freelancer_id:
        raise ForbiddenError("You can only update your own proposals")
    
    if proposal.status != ProposalStatus.pending:
        raise ValidationError("Only pending proposals can be updated")
    
    # Update proposal fields
    update_data = proposal_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(proposal, field, value)
    
    await db.commit()
    await db.refresh(proposal)
    
    logger.info(f"Proposal updated: {proposal.id} by {current_user.email}")
    
    return proposal

@router.post("/{proposal_id}/accept")
async def accept_proposal(
    proposal_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_customer)
):
    """Accept proposal and create contract (Customer only)"""
    
    result = await db.execute(
        select(Proposal)
        .options(
            selectinload(Proposal.project),
            selectinload(Proposal.freelancer)
        )
        .where(Proposal.id == proposal_id)
    )
    proposal = result.scalar_one_or_none()
    
    if not proposal:
        raise NotFoundError("Proposal", proposal_id)
    
    if current_user.id != proposal.project.customer_id:
        raise ForbiddenError("You can only accept proposals for your own projects")
    
    if proposal.status != ProposalStatus.pending:
        raise ValidationError("Only pending proposals can be accepted")
    
    # Check if project already has accepted proposal
    existing_accepted = await db.execute(
        select(Proposal).where(
            and_(
                Proposal.project_id == proposal.project_id,
                Proposal.status == ProposalStatus.ACCEPTED
            )
        )
    )
    if existing_accepted.scalar_one_or_none():
        raise ValidationError("Project already has an accepted proposal")
    
    # Accept the proposal
    proposal.status = ProposalStatus.ACCEPTED
    
    # Reject all other proposals for this project
    await db.execute(
        Proposal.__table__.update()
        .where(
            and_(
                Proposal.project_id == proposal.project_id,
                Proposal.id != proposal.id,
                Proposal.status == ProposalStatus.pending
            )
        )
        .values(status=ProposalStatus.rejected)
    )
    
    # Update project status
    proposal.project.status = ProjectStatus.in_progress
    proposal.project.allows_proposals = False
    
    await db.commit()
    
    logger.info(f"Proposal accepted: {proposal.id} by {current_user.email}")
    
    return {"message": "Proposal accepted successfully"}

@router.post("/{proposal_id}/reject")
async def reject_proposal(
    proposal_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_customer)
):
    """Reject proposal (Customer only)"""
    
    result = await db.execute(
        select(Proposal)
        .options(selectinload(Proposal.project))
        .where(Proposal.id == proposal_id)
    )
    proposal = result.scalar_one_or_none()
    
    if not proposal:
        raise NotFoundError("Proposal", proposal_id)
    
    if current_user.id != proposal.project.customer_id:
        raise ForbiddenError("You can only reject proposals for your own projects")
    
    if proposal.status != ProposalStatus.pending:
        raise ValidationError("Only pending proposals can be rejected")
    
    proposal.status = ProposalStatus.rejected
    await db.commit()
    
    logger.info(f"Proposal rejected: {proposal.id} by {current_user.email}")
    
    return {"message": "Proposal rejected successfully"}

@router.delete("/{proposal_id}")
async def withdraw_proposal(
    proposal_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_freelancer)
):
    """Withdraw proposal (Freelancer only)"""
    
    result = await db.execute(
        select(Proposal)
        .options(selectinload(Proposal.project))
        .where(Proposal.id == proposal_id)
    )
    proposal = result.scalar_one_or_none()
    
    if not proposal:
        raise NotFoundError("Proposal", proposal_id)
    
    if current_user.id != proposal.freelancer_id:
        raise ForbiddenError("You can only withdraw your own proposals")
    
    if proposal.status == ProposalStatus.ACCEPTED:
        raise ValidationError("Cannot withdraw accepted proposal")
    
    proposal.status = ProposalStatus.WITHDRAWN
    
    # Decrease project proposal count
    proposal.project.proposal_count = max(0, proposal.project.proposal_count - 1)
    
    await db.commit()
    
    logger.info(f"Proposal withdrawn: {proposal.id} by {current_user.email}")
    
    return {"message": "Proposal withdrawn successfully"}