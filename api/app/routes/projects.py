# api/app/routes/projects.py
"""Project management routes"""

from typing import Optional, List
import logging
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, and_, or_, desc, asc, cast, String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.exceptions import NotFoundError, ForbiddenError
from app.models import Project, ProjectStatus, User, UserRole
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectListResponse,
)
from app.schemas.common import PaginatedResponse, PaginationMeta
from app.deps import (
    get_optional_user,
    get_current_user,
    require_roles,
    require_customer,   # factory (call it inside Depends)
    get_pagination,
    PaginationParams,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/projects")


def _norm_role(role) -> str:
    return role.value if hasattr(role, "value") else str(role)


def _norm_status(status) -> str:
    return status.value if hasattr(status, "value") else str(status)


@router.post("", response_model=ProjectResponse)
async def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(require_customer()),  # <-- factory ÇAĞRILDI
    db: AsyncSession = Depends(get_db),
):
    """Create a new project (Customer only)."""

    data = project_data.model_dump(exclude_unset=True)
    data.update(
        dict(
            customer_id=current_user.id,
            status=ProjectStatus.draft.value,
            view_count=0,
            proposal_count=0,
            is_featured=False,
            allows_proposals=True,
            max_proposals=50,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
    )

    project = Project(**data)
    db.add(project)
    await db.commit()
    await db.refresh(project)

    # İsteğe bağlı: müşteri profilini eager load edip döndürmek
    res = await db.execute(
        select(Project)
        .options(selectinload(Project.customer).selectinload(User.profile))
        .where(Project.id == project.id)
    )
    project = res.scalar_one()

    return ProjectResponse.model_validate(project, from_attributes=True)


@router.get("", response_model=PaginatedResponse)
async def list_projects(
    status: Optional[ProjectStatus] = Query(None, description="Filter by status"),
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search in title and description"),
    sort_by: str = Query("created_at", pattern="^(created_at|budget_max|deadline|proposal_count)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    pagination: PaginationParams = Depends(get_pagination),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """List projects with filtering and search"""

    query = select(Project).options(
        selectinload(Project.customer).selectinload(User.profile)
    )

    filters = []

    # Rol normalizasyonu
    role = _norm_role(current_user.role) if current_user else None

    # Sadece open projeleri misafire göster
    if not current_user or role not in {"admin", "moderator", "customer"}:
        filters.append(cast(Project.status, String) == ProjectStatus.open.value)
    elif current_user and role == "customer":
        # Müşteri kendi projelerini her statüde görebilir; diğerleri open
        filters.append(
            or_(
                Project.customer_id == current_user.id,
                cast(Project.status, String) == ProjectStatus.open.value,
            )
        )

    if status:
        filters.append(cast(Project.status, String) == _norm_status(status))
    if category:
        filters.append(Project.category == category)
    if search:
        filters.append(
            or_(
                Project.title.ilike(f"%{search}%"),
                Project.description.ilike(f"%{search}%"),
            )
        )

    if filters:
        query = query.where(and_(*filters))

    # total
    total = (await db.execute(query.with_only_columns(Project.id))).unique().rowcount
    # bazı sürümlerde rowcount 0 gelebilir; güvenli sayım:
    if total in (None, 0):
        total = len((await db.execute(query)).scalars().all())

    # sorting
    sort_column = getattr(Project, sort_by)
    query = query.order_by(desc(sort_column) if sort_order == "desc" else asc(sort_column))

    # pagination
    query = query.offset(pagination.offset).limit(pagination.size)
    result = await db.execute(query)
    projects = result.scalars().all()

    items: List[ProjectListResponse] = []
    for p in projects:
        desc_trim = (
            p.description[:200] + "..." if p.description and len(p.description) > 200 else p.description
        )
        items.append(
            ProjectListResponse(
                id=p.id,
                title=p.title,
                description=desc_trim or "",
                customer_id=p.customer_id,
                budget_type=p.budget_type,
                budget_min=p.budget_min,
                budget_max=p.budget_max,
                hourly_rate_min=p.hourly_rate_min,
                hourly_rate_max=p.hourly_rate_max,
                currency=p.currency,
                complexity=p.complexity,
                deadline=p.deadline,
                status=_norm_status(p.status),
                category=p.category,
                required_skills=p.required_skills or [],
                proposal_count=p.proposal_count or 0,
                created_at=p.created_at,
                customer_name=p.customer.profile.display_name if p.customer and p.customer.profile else None,
                budget_display=getattr(p, "budget_display", None),
            )
        )

    pages = (total + pagination.size - 1) // pagination.size
    meta = PaginationMeta(
        page=pagination.page,
        size=pagination.size,
        total=total,
        pages=pages,
        has_next=pagination.page < pages,
        has_prev=pagination.page > 1,
    )
    return PaginatedResponse(data=items, meta=meta)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """Get project by ID (public if status=open)."""

    result = await db.execute(
        select(Project)
        .options(selectinload(Project.customer).selectinload(User.profile))
        .where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise NotFoundError("Project", project_id)

    proj_status = _norm_status(project.status)

    # Kapalı proje => yalnızca sahibi / admin / moderator görür
    if proj_status != ProjectStatus.open.value:
        if not current_user:
            raise ForbiddenError("Project is not publicly available")
        user_role = _norm_role(current_user.role)
        if current_user.id != project.customer_id and user_role not in {"admin", "moderator"}:
            raise ForbiddenError("Project is not publicly available")

    # Sayaç (sahibi değilse)
    if not current_user or current_user.id != project.customer_id:
        project.view_count = (project.view_count or 0) + 1
        await db.commit()

    return ProjectResponse.model_validate(project, from_attributes=True)


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update project"""
    res = await db.execute(select(Project).where(Project.id == project_id))
    project = res.scalar_one_or_none()
    if not project:
        raise NotFoundError("Project", project_id)

    user_role = _norm_role(current_user.role)
    if current_user.id != project.customer_id and user_role not in {"admin", "moderator"}:
        raise ForbiddenError("You can only update your own projects")

    data = project_data.model_dump(exclude_unset=True)
    for k, v in data.items():
        if hasattr(v, "value"):
            v = v.value
        setattr(project, k, v)

    project.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(project)
    return ProjectResponse.model_validate(project, from_attributes=True)


@router.delete("/{project_id}")
async def delete_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete project"""
    res = await db.execute(select(Project).where(Project.id == project_id))
    project = res.scalar_one_or_none()
    if not project:
        raise NotFoundError("Project", project_id)

    user_role = _norm_role(current_user.role)
    if current_user.id != project.customer_id and user_role not in {"admin", "moderator"}:
        raise ForbiddenError("You can only delete your own projects")

    from app.models import Contract, ContractStatus
    contracts_result = await db.execute(
        select(Contract).where(
            and_(
                Contract.project_id == project_id,
                cast(Contract.status, String).in_(
                    [ContractStatus.active.value, ContractStatus.paused.value]
                ),
            )
        )
    )
    if contracts_result.scalars().first():
        raise ForbiddenError("Cannot delete project with active contracts")

    await db.delete(project)
    await db.commit()
    return {"message": "Project deleted successfully"}


@router.post("/{project_id}/publish")
async def publish_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_customer()),  # <-- factory ÇAĞRILDI
):
    """Publish project (make it open for proposals)"""
    res = await db.execute(select(Project).where(Project.id == project_id))
    project = res.scalar_one_or_none()
    if not project:
        raise NotFoundError("Project", project_id)
    if current_user.id != project.customer_id:
        raise ForbiddenError("You can only publish your own projects")

    if _norm_status(project.status) != ProjectStatus.draft.value:
        raise ForbiddenError("Only draft projects can be published")

    project.status = ProjectStatus.open.value
    project.updated_at = datetime.utcnow()
    await db.commit()
    return {"message": "Project published successfully"}


@router.post("/{project_id}/close")
async def close_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_customer()),  # <-- factory ÇAĞRILDI
):
    """Close project (stop accepting proposals)"""
    res = await db.execute(select(Project).where(Project.id == project_id))
    project = res.scalar_one_or_none()
    if not project:
        raise NotFoundError("Project", project_id)
    if current_user.id != project.customer_id:
        raise ForbiddenError("You can only close your own projects")

    if _norm_status(project.status) not in {ProjectStatus.open.value, ProjectStatus.in_progress.value}:
        raise ForbiddenError("Only open or in-progress projects can be closed")

    project.status = ProjectStatus.closed.value
    project.allows_proposals = False
    project.updated_at = datetime.utcnow()
    await db.commit()
    return {"message": "Project closed successfully"}
