# api/app/routes/projects.py
"""Project management routes"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc, asc
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models import Project, ProjectStatus, User, UserRole
from app.schemas.project import (
    ProjectCreate, ProjectUpdate, ProjectResponse, ProjectListResponse, 
    ProjectSearchRequest
)
from app.deps import (
    get_current_user, get_optional_user, require_customer, 
    get_pagination, PaginationParams
)
from app.core.exceptions import NotFoundError, ForbiddenError
from app.schemas.common import PaginatedResponse, PaginationMeta
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/projects")

@router.post("", response_model=ProjectResponse)
async def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(require_customer),
    db: AsyncSession = Depends(get_db)
):
    """Create a new project (Customer only)"""
    
    # Create project
    project_dict = project_data.dict(exclude_unset=True)
    project_dict.update({
        "customer_id": current_user.id,
        "status": ProjectStatus.DRAFT,
        "view_count": 0,
        "proposal_count": 0,
        "is_featured": False,
        "allows_proposals": True
    })
    
    project = Project(**project_dict)
    db.add(project)
    await db.commit()
    await db.refresh(project)
    
    logger.info(f"Project created: {project.title} (ID: {project.id}) by {current_user.email}")
    
    return project

@router.get("", response_model=PaginatedResponse)
async def list_projects(
    status: Optional[ProjectStatus] = Query(None, description="Filter by status"),
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search in title and description"),
    sort_by: str = Query("created_at", pattern="^(created_at|budget_max|deadline|proposal_count)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    pagination: PaginationParams = Depends(get_pagination),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """List projects with filtering and search"""
    
    # Build query
    query = select(Project).options(
        selectinload(Project.customer).selectinload(User.profile)
    )
    
    # Apply filters
    filters = []
    
    # Only show open projects to non-customers, unless it's admin/moderator
    if not current_user or current_user.role not in [UserRole.ADMIN, UserRole.MODERATOR, UserRole.CUSTOMER]:
        filters.append(Project.status == ProjectStatus.OPEN)
    elif current_user and current_user.role == UserRole.CUSTOMER:
        # Customers can see their own projects in any status, others only open
        filters.append(
            or_(
                Project.customer_id == current_user.id,
                Project.status == ProjectStatus.OPEN
            )
        )
    
    # Apply other filters
    if status:
        filters.append(Project.status == status)
    if category:
        filters.append(Project.category == category)
    if search:
        search_filter = or_(
            Project.title.ilike(f"%{search}%"),
            Project.description.ilike(f"%{search}%")
        )
        filters.append(search_filter)
    
    if filters:
        query = query.where(and_(*filters))
    
    # Count total
    count_query = select(Project)
    if filters:
        count_query = count_query.where(and_(*filters))
    
    total_result = await db.execute(count_query)
    total = len(total_result.scalars().all())
    
    # Apply sorting
    sort_column = getattr(Project, sort_by)
    if sort_order == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(asc(sort_column))
    
    # Apply pagination
    query = query.offset(pagination.offset).limit(pagination.size)
    result = await db.execute(query)
    projects = result.scalars().all()
    
    # Convert to list response format
    project_list = []
    for project in projects:
        project_dict = {
            "id": project.id,
            "title": project.title,
            "description": project.description[:200] + "..." if len(project.description) > 200 else project.description,
            "customer_id": project.customer_id,
            "budget_type": project.budget_type,
            "budget_min": project.budget_min,
            "budget_max": project.budget_max,
            "hourly_rate_min": project.hourly_rate_min,
            "hourly_rate_max": project.hourly_rate_max,
            "currency": project.currency,
            "complexity": project.complexity,
            "deadline": project.deadline,
            "status": project.status,
            "category": project.category,
            "required_skills": project.required_skills or [],
            "proposal_count": project.proposal_count,
            "created_at": project.created_at,
            "customer_name": project.customer.profile.display_name if project.customer and project.customer.profile else None,
            "budget_display": project.budget_display
        }
        project_list.append(ProjectListResponse(**project_dict))
    
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
    
    return PaginatedResponse(data=project_list, meta=meta)

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """Get project by ID"""
    
    result = await db.execute(
        select(Project)
        .options(
            selectinload(Project.customer).selectinload(User.profile)
        )
        .where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise NotFoundError("Project", project_id)
    
    # Check permissions
    if project.status != ProjectStatus.OPEN:
        if not current_user:
            raise ForbiddenError("Project is not publicly available")
        if (current_user.id != project.customer_id and 
            current_user.role not in [UserRole.ADMIN, UserRole.MODERATOR]):
            raise ForbiddenError("Project is not publicly available")
    
    # Increment view count (only for non-owners)
    if not current_user or current_user.id != project.customer_id:
        project.view_count += 1
        await db.commit()
    
    return project

@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update project"""
    
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    
    if not project:
        raise NotFoundError("Project", project_id)
    
    # Check permissions
    if (current_user.id != project.customer_id and 
        current_user.role not in [UserRole.ADMIN, UserRole.MODERATOR]):
        raise ForbiddenError("You can only update your own projects")
    
    # Update project fields
    update_data = project_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)
    
    await db.commit()
    await db.refresh(project)
    
    logger.info(f"Project updated: {project.title} (ID: {project.id}) by {current_user.email}")
    
    return project

@router.delete("/{project_id}")
async def delete_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete project"""
    
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    
    if not project:
        raise NotFoundError("Project", project_id)
    
    # Check permissions
    if (current_user.id != project.customer_id and 
        current_user.role not in [UserRole.ADMIN, UserRole.MODERATOR]):
        raise ForbiddenError("You can only delete your own projects")
    
    # Check if project has active contracts
    from app.models import Contract, ContractStatus
    contracts_result = await db.execute(
        select(Contract).where(
            and_(
                Contract.project_id == project_id,
                Contract.status.in_([ContractStatus.ACTIVE, ContractStatus.PAUSED])
            )
        )
    )
    active_contracts = contracts_result.scalars().all()
    
    if active_contracts:
        raise ForbiddenError("Cannot delete project with active contracts")
    
    await db.delete(project)
    await db.commit()
    
    logger.warning(f"Project deleted: {project.title} (ID: {project.id}) by {current_user.email}")
    
    return {"message": "Project deleted successfully"}

@router.post("/{project_id}/publish")
async def publish_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_customer)
):
    """Publish project (make it open for proposals)"""
    
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    
    if not project:
        raise NotFoundError("Project", project_id)
    
    if current_user.id != project.customer_id:
        raise ForbiddenError("You can only publish your own projects")
    
    if project.status != ProjectStatus.DRAFT:
        raise ForbiddenError("Only draft projects can be published")
    
    project.status = ProjectStatus.OPEN
    await db.commit()
    
    logger.info(f"Project published: {project.title} (ID: {project.id}) by {current_user.email}")
    
    return {"message": "Project published successfully"}

@router.post("/{project_id}/close")
async def close_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_customer)
):
    """Close project (stop accepting proposals)"""
    
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    
    if not project:
        raise NotFoundError("Project", project_id)
    
    if current_user.id != project.customer_id:
        raise ForbiddenError("You can only close your own projects")
    
    if project.status not in [ProjectStatus.OPEN, ProjectStatus.IN_PROGRESS]:
        raise ForbiddenError("Only open or in-progress projects can be closed")
    
    project.status = ProjectStatus.CLOSED
    project.allows_proposals = False
    await db.commit()
    
    logger.info(f"Project closed: {project.title} (ID: {project.id}) by {current_user.email}")
    
    return {"message": "Project closed successfully"}