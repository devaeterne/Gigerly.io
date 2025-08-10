# app/routes/projects.py
"""Project management routes"""

from typing import List, Optional
import logging

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, and_, or_, desc, asc, cast, String, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.redis import redis_manager
from app.models import Project, ProjectStatus, User, UserRole
from app.schemas.project import (
    ProjectCreate, ProjectUpdate, ProjectResponse, ProjectListResponse
)
from app.deps import (
    get_current_user, get_optional_user, require_customer,
    get_pagination, PaginationParams
)
from app.core.exceptions import NotFoundError, ForbiddenError
from app.schemas.common import PaginatedResponse, PaginationMeta

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/projects")


@router.post("", response_model=ProjectResponse)
async def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(require_customer),
    session: AsyncSession = Depends(get_db),
):
    """Create a new project (Customer only)"""

    # Project dict + güvenli varsayılanlar
    project_dict = project_data.model_dump(exclude_unset=True)
    project_dict.update(
        {
            "customer_id": current_user.id,
            "status": ProjectStatus.draft.value,
            "view_count": 0,
            "proposal_count": 0,
            "is_featured": False,
            "allows_proposals": True,
            # JSON alanları None gelirse response validation patlamasın
            "required_skills": project_dict.get("required_skills") or [],
            "attachments": project_dict.get("attachments") or [],
            "tags": project_dict.get("tags") or [],
        }
    )

    project = Project(**project_dict)
    session.add(project)
    await session.commit()

    # İlişkileri yüklü bir şekilde tekrar çek (DetachedInstanceError önler)
    res = await session.execute(
        select(Project)
        .options(
            selectinload(Project.customer).selectinload(User.profile)
        )
        .where(Project.id == project.id)
    )
    project = res.scalar_one()

    # Yine de None kalmışsa temizle
    if project.required_skills is None:
        project.required_skills = []

    logger.info(
        "Project created: %s (ID: %s) by %s",
        project.title, project.id, current_user.email
    )

    return ProjectResponse.model_validate(project, from_attributes=True)


@router.get("", response_model=PaginatedResponse)
async def list_projects(
    status: Optional[ProjectStatus] = Query(None, description="Filter by status"),
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search in title and description"),
    sort_by: str = Query("created_at", pattern="^(created_at|budget_max|deadline|proposal_count)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    pagination: PaginationParams = Depends(get_pagination),
    session: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """List projects with filtering and search"""

    base_query = select(Project).options(
        selectinload(Project.customer).selectinload(User.profile)
    )

    filters = []

    # Rol bazlı görünürlük
    if not current_user or current_user.role not in [
        UserRole.admin.value,
        UserRole.moderator.value,
        UserRole.customer.value,
    ]:
        # Misafirler sadece open görsün
        filters.append(cast(Project.status, String) == ProjectStatus.open.value)
    elif current_user and current_user.role == UserRole.customer.value:
        # Müşteri kendi projelerini (her statü) + açık projeleri görsün
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
        filters.append(
            or_(
                Project.title.ilike(f"%{search}%"),
                Project.description.ilike(f"%{search}%"),
            )
        )

    if filters:
        base_query = base_query.where(and_(*filters))

    # Total count
    count_q = select(func.count(Project.id))
    if filters:
        count_q = count_q.where(and_(*filters))
    total = (await session.execute(count_q)).scalar_one()

    # Sıralama
    sort_column = getattr(Project, sort_by)
    order_expr = desc(sort_column) if sort_order == "desc" else asc(sort_column)

    # Sayfalama + çekim
    query = base_query.order_by(order_expr).offset(pagination.offset).limit(pagination.size)
    projects = (await session.execute(query)).scalars().all()

    # Liste response elemanları
    items: List[ProjectListResponse] = []
    for p in projects:
        # required_skills None ise [] yap
        req_skills = p.required_skills or []
        # kısa açıklama
        short_desc = p.description[:200] + "..." if p.description and len(p.description) > 200 else p.description

        item = ProjectListResponse(
            id=p.id,
            title=p.title,
            description=short_desc,
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
            required_skills=req_skills,
            proposal_count=p.proposal_count,
            created_at=p.created_at,
            customer_name=p.customer.profile.display_name if p.customer and p.customer.profile else None,
            budget_display=getattr(p, "budget_display", None),
        )
        items.append(item)

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
    session: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """Get project by ID"""

    res = await session.execute(
        select(Project)
        .options(
            selectinload(Project.customer).selectinload(User.profile)
        )
        .where(Project.id == project_id)
    )
    project = res.scalar_one_or_none()
    if not project:
        raise NotFoundError("Project", project_id)

    # Erişim kontrolü
    if project.status != ProjectStatus.open.value:
        if not current_user:
            raise ForbiddenError("Project is not publicly available")
        if (current_user.id != project.customer_id and
                current_user.role not in [UserRole.admin.value, UserRole.moderator.value]):
            raise ForbiddenError("Project is not publicly available")

    # Sahibi değilse view counter'ı Redis'te artır
    if not current_user or current_user.id != project.customer_id:
        await redis_manager.incr(f"project:{project_id}:views")

    if project.required_skills is None:
        project.required_skills = []

    return ProjectResponse.model_validate(project, from_attributes=True)


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update project"""

    res = await session.execute(select(Project).where(Project.id == project_id))
    project = res.scalar_one_or_none()
    if not project:
        raise NotFoundError("Project", project_id)

    # Yetki kontrolü
    if (current_user.id != project.customer_id and
            current_user.role not in [UserRole.admin.value, UserRole.moderator.value]):
        raise ForbiddenError("You can only update your own projects")

    # Güncelle
    update_data = project_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(value, "value"):  # Enum ise
            value = value.value
        setattr(project, field, value)

    await session.commit()

    # İlişkili müşteriyle geri çek
    res = await session.execute(
        select(Project)
        .options(selectinload(Project.customer).selectinload(User.profile))
        .where(Project.id == project.id)
    )
    project = res.scalar_one()
    if project.required_skills is None:
        project.required_skills = []

    logger.info(
        "Project updated: %s (ID: %s) by %s",
        project.title, project.id, current_user.email
    )

    return ProjectResponse.model_validate(project, from_attributes=True)


@router.delete("/{project_id}")
async def delete_project(
    project_id: int,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete project"""

    res = await session.execute(select(Project).where(Project.id == project_id))
    project = res.scalar_one_or_none()
    if not project:
        raise NotFoundError("Project", project_id)

    if (current_user.id != project.customer_id and
            current_user.role not in [UserRole.admin.value, UserRole.moderator.value]):
        raise ForbiddenError("You can only delete your own projects")

    # Aktif kontrat var mı?
    from app.models import Contract, ContractStatus
    contracts_res = await session.execute(
        select(Contract).where(
            and_(
                Contract.project_id == project_id,
                cast(Contract.status, String).in_(
                    [ContractStatus.active.value, ContractStatus.paused.value]
                ),
            )
        )
    )
    if contracts_res.scalars().first():
        raise ForbiddenError("Cannot delete project with active contracts")

    await session.delete(project)
    await session.commit()

    logger.warning(
        "Project deleted: %s (ID: %s) by %s",
        project.title, project.id, current_user.email
    )

    return {"message": "Project deleted successfully"}


@router.post("/{project_id}/publish")
async def publish_project(
    project_id: int,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_customer),
):
    """Publish project (make it open for proposals)"""

    res = await session.execute(select(Project).where(Project.id == project_id))
    project = res.scalar_one_or_none()
    if not project:
        raise NotFoundError("Project", project_id)

    if current_user.id != project.customer_id:
        raise ForbiddenError("You can only publish your own projects")

    if project.status != ProjectStatus.draft.value:
        raise ForbiddenError("Only draft projects can be published")

    project.status = ProjectStatus.open.value
    await session.commit()

    logger.info(
        "Project published: %s (ID: %s) by %s",
        project.title, project.id, current_user.email
    )

    return {"message": "Project published successfully"}


@router.post("/{project_id}/close")
async def close_project(
    project_id: int,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_customer),
):
    """Close project (stop accepting proposals)"""

    res = await session.execute(select(Project).where(Project.id == project_id))
    project = res.scalar_one_or_none()
    if not project:
        raise NotFoundError("Project", project_id)

    if current_user.id != project.customer_id:
        raise ForbiddenError("You can only close your own projects")

    if project.status not in [ProjectStatus.open.value, ProjectStatus.in_progress.value]:
        raise ForbiddenError("Only open or in-progress projects can be closed")

    project.status = ProjectStatus.closed.value
    project.allows_proposals = False
    await session.commit()

    logger.info(
        "Project closed: %s (ID: %s) by %s",
        project.title, project.id, current_user.email
    )

    return {"message": "Project closed successfully"}
