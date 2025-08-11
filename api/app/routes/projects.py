# app/routes/projects.py
"""Project management routes"""

from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import (
    select, and_, or_, desc, asc, cast, String, func
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models import Project, ProjectStatus, User, UserRole
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectListResponse,
)
from app.deps import (
    get_current_user,
    get_optional_user,
    require_customer,           # müşteriye kısıtlı uçlar için
    get_pagination,
    PaginationParams,
)
from app.core.exceptions import NotFoundError, ForbiddenError
from app.schemas.common import PaginatedResponse, PaginationMeta

import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/projects")


def _role_value(role) -> str:
    """User.role hem Enum hem str olabilir; güvenli normalize."""
    return getattr(role, "value", role)


@router.post("", response_model=ProjectResponse)
async def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(require_customer),
    db: AsyncSession = Depends(get_db),
):
    """Create a new project (customer only)."""

    data = project_data.model_dump(exclude_unset=True)
    data.update(
        {
            "customer_id": current_user.id,
            "status": ProjectStatus.draft.value,  # DB string saklıyor varsayımı
            "view_count": 0,
            "proposal_count": 0,
            "is_featured": False,
            "allows_proposals": True,
        }
    )

    project = Project(**data)
    db.add(project)
    await db.commit()
    # ilişki alanlarını (customer) doldurmak için refresh
    await db.refresh(project)

    logger.info(
        "Project created: %s (ID: %s) by %s",
        project.title,
        project.id,
        current_user.email,
    )

    return project  # response_model with from_attributes=True => otomatik serialize


@router.get("", response_model=PaginatedResponse)
async def list_projects(
    status: Optional[ProjectStatus] = Query(None, description="Filter by status"),
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search in title and description"),
    sort_by: str = Query(
        "created_at", pattern="^(created_at|budget_max|deadline|proposal_count)$"
    ),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    pagination: PaginationParams = Depends(get_pagination),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """List projects with filtering, search, sorting, pagination."""

    query = (
        select(Project)
        .options(selectinload(Project.customer).selectinload(User.profile))
    )

    filters = []

    # Görünürlük: misafir/freelancer sadece 'open' görsün.
    if not current_user or _role_value(current_user.role) not in {
        UserRole.admin.value,
        UserRole.moderator.value,
        UserRole.customer.value,
    }:
        filters.append(cast(Project.status, String) == ProjectStatus.open.value)
    elif current_user and _role_value(current_user.role) == UserRole.customer.value:
        # Customer kendi tüm projelerini + open projeleri görür
        filters.append(
            or_(
                Project.customer_id == current_user.id,
                cast(Project.status, String) == ProjectStatus.open.value,
            )
        )

    # Diğer filtreler
    if status:
        filters.append(cast(Project.status, String) == status.value)
    if category:
        filters.append(Project.category == category)
    if search:
        like = f"%{search}%"
        filters.append(or_(Project.title.ilike(like), Project.description.ilike(like)))

    if filters:
        query = query.where(and_(*filters))

    # Toplam (COUNT) — tüm satırları çekmek yerine performanslı sayım
    count_q = select(func.count()).select_from(Project)
    if filters:
        count_q = count_q.where(and_(*filters))
    total = (await db.execute(count_q)).scalar_one()

    # Sıralama
    sort_column = getattr(Project, sort_by)
    query = query.order_by(desc(sort_column) if sort_order == "desc" else asc(sort_column))

    # Sayfalama
    query = query.offset(pagination.offset).limit(pagination.size)

    result = await db.execute(query)
    projects = result.scalars().all()

    # Liste response item'ları
    items: List[ProjectListResponse] = []
    for p in projects:
        desc_preview = (
            (p.description[:200] + "...") if p.description and len(p.description) > 200 else p.description
        )
        items.append(
            ProjectListResponse(
                id=p.id,
                title=p.title,
                description=desc_preview or "",
                customer_id=p.customer_id,
                budget_type=p.budget_type,
                budget_min=p.budget_min,
                budget_max=p.budget_max,
                hourly_rate_min=p.hourly_rate_min,
                hourly_rate_max=p.hourly_rate_max,
                currency=p.currency,
                complexity=p.complexity,
                deadline=p.deadline,
                status=p.status,
                category=p.category,
                required_skills=p.required_skills or [],
                proposal_count=p.proposal_count or 0,
                created_at=p.created_at,
                customer_name=p.customer.profile.display_name
                if p.customer and p.customer.profile
                else None,
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
    """Get project by ID (görünürlük kontrolü ile)."""

    result = await db.execute(
        select(Project)
        .options(selectinload(Project.customer).selectinload(User.profile))
        .where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise NotFoundError("Project", project_id)

    # Görünürlük: 'open' değilse; sahibi veya admin/mod değilse yasak
    if project.status != ProjectStatus.open.value:
        if not current_user:
            raise ForbiddenError("Project is not publicly available")
        if (
            current_user.id != project.customer_id
            and _role_value(current_user.role)
            not in {UserRole.admin.value, UserRole.moderator.value}
        ):
            raise ForbiddenError("Project is not publicly available")

    # Sahibi olmayan görüntülemelerde view_count artır
    if not current_user or current_user.id != project.customer_id:
        project.view_count = (project.view_count or 0) + 1
        await db.commit()

    return project


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update project (owner or admin/mod)."""

    proj_res = await db.execute(select(Project).where(Project.id == project_id))
    project = proj_res.scalar_one_or_none()
    if not project:
        raise NotFoundError("Project", project_id)

    # Yetki
    if current_user.id != project.customer_id and _role_value(current_user.role) not in {
        UserRole.admin.value,
        UserRole.moderator.value,
    }:
        raise ForbiddenError("You can only update your own projects")

    # Alanları uygula
    update_data = project_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        # Enum -> str
        if hasattr(value, "value"):
            value = value.value
        # required_skills None ise boş listeye çekmek isteyebilirsiniz; burada geleni yazarız
        setattr(project, field, value)

    await db.commit()
    await db.refresh(project)

    logger.info(
        "Project updated: %s (ID: %s) by %s",
        project.title,
        project.id,
        current_user.email,
    )

    return project


@router.delete("/{project_id}")
async def delete_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete project (owner or admin/mod; aktif contract yoksa)."""

    proj_res = await db.execute(select(Project).where(Project.id == project_id))
    project = proj_res.scalar_one_or_none()
    if not project:
        raise NotFoundError("Project", project_id)

    if current_user.id != project.customer_id and _role_value(current_user.role) not in {
        UserRole.admin.value,
        UserRole.moderator.value,
    }:
        raise ForbiddenError("You can only delete your own projects")

    # Aktif contract kontrolü
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

    logger.warning(
        "Project deleted: %s (ID: %s) by %s",
        project.title,
        project.id,
        current_user.email,
    )

    return {"message": "Project deleted successfully"}


@router.post("/{project_id}/publish")
async def publish_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_customer),
):
    """Publish project (draft -> open)."""

    res = await db.execute(select(Project).where(Project.id == project_id))
    project = res.scalar_one_or_none()
    if not project:
        raise NotFoundError("Project", project_id)

    if current_user.id != project.customer_id:
        raise ForbiddenError("You can only publish your own projects")

    if project.status != ProjectStatus.draft.value:
        raise ForbiddenError("Only draft projects can be published")

    project.status = ProjectStatus.open.value
    await db.commit()

    logger.info(
        "Project published: %s (ID: %s) by %s",
        project.title,
        project.id,
        current_user.email,
    )

    return {"message": "Project published successfully"}


@router.post("/{project_id}/close")
async def close_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_customer),
):
    """Close project (open/in_progress -> closed)."""

    res = await db.execute(select(Project).where(Project.id == project_id))
    project = res.scalar_one_or_none()
    if not project:
        raise NotFoundError("Project", project_id)

    if current_user.id != project.customer_id:
        raise ForbiddenError("You can only close your own projects")

    if project.status not in {ProjectStatus.open.value, ProjectStatus.in_progress.value}:
        raise ForbiddenError("Only open or in-progress projects can be closed")

    project.status = ProjectStatus.closed.value
    project.allows_proposals = False
    await db.commit()

    logger.info(
        "Project closed: %s (ID: %s) by %s",
        project.title,
        project.id,
        current_user.email,
    )

    return {"message": "Project closed successfully"}
