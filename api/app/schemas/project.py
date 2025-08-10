# app/schemas/project.py
from __future__ import annotations

from datetime import date, datetime
from typing import Any, List, Optional

from pydantic import BaseModel, Field, ConfigDict, model_validator, field_validator

from app.models import ProjectStatus, ProjectBudgetType, ProjectComplexity
from .user import UserLite


# ---------- Base ----------
class ProjectBase(BaseModel):
    title: str = Field(..., min_length=10, max_length=200)
    description: str = Field(..., min_length=50, max_length=5000)
    budget_type: ProjectBudgetType = ProjectBudgetType.fixed
    currency: str = Field("USD", pattern=r"^[A-Z]{3}$")

    model_config = ConfigDict(from_attributes=True)


# ---------- Create / Update ----------
class ProjectCreate(BaseModel):
    title: str = Field(..., max_length=200)
    description: str
    budget_type: ProjectBudgetType = ProjectBudgetType.fixed
    currency: str = Field(default="USD", min_length=3, max_length=3)
    category: Optional[str] = None
    subcategory: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ProjectUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=10, max_length=200)
    description: Optional[str] = Field(None, min_length=50, max_length=5000)

    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    hourly_rate_min: Optional[float] = None
    hourly_rate_max: Optional[float] = None

    complexity: Optional[ProjectComplexity] = None
    estimated_duration: Optional[int] = Field(None, ge=1, le=365)
    deadline: Optional[date] = None

    category: Optional[str] = Field(None, max_length=100)
    subcategory: Optional[str] = Field(None, max_length=100)
    required_skills: Optional[List[str]] = None

    status: Optional[ProjectStatus] = None
    allows_proposals: Optional[bool] = None
    max_proposals: Optional[int] = Field(None, ge=1, le=200)

    tags: Optional[List[str]] = None
    attachments: Optional[List[Any]] = None

    @model_validator(mode="after")
    def _validate_ranges_and_deadline(self):
        if self.budget_min is not None and self.budget_max is not None:
            if self.budget_max < self.budget_min:
                raise ValueError("budget_max must be >= budget_min")
        if self.hourly_rate_min is not None and self.hourly_rate_max is not None:
            if self.hourly_rate_max < self.hourly_rate_min:
                raise ValueError("hourly_rate_max must be >= hourly_rate_min")
        if self.deadline is not None and self.deadline <= date.today():
            raise ValueError("deadline must be in the future")
        return self

    model_config = ConfigDict(from_attributes=True)


# ---------- Responses ----------
class ProjectResponse(BaseModel):
    # ORM objelerinden alan okumayı aç
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str

    customer_id: int
    budget_type: ProjectBudgetType
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    hourly_rate_min: Optional[float] = None
    hourly_rate_max: Optional[float] = None
    currency: str

    complexity: Optional[ProjectComplexity] = None
    estimated_duration: Optional[int] = None
    deadline: Optional[date] = None

    status: ProjectStatus
    category: Optional[str] = None
    subcategory: Optional[str] = None

    # None gelirse boş listeye çevir
    required_skills: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    attachments: List[Any] = Field(default_factory=list)

    is_featured: bool
    allows_proposals: bool
    max_proposals: int
    slug: Optional[str] = None
    view_count: int
    proposal_count: int
    created_at: datetime
    updated_at: datetime

    # İlişki
    customer: Optional[UserLite] = None

    # UI yardımcı alanı (opsiyonel)
    budget_display: Optional[str] = None

    @field_validator("required_skills", mode="before")
    @classmethod
    def none_or_json_to_list(cls, v):
        if v is None:
            return []
        if isinstance(v, str):
            import json
            try:
                return json.loads(v)
            except Exception:
                return []
        return v


class ProjectListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    customer_id: int

    budget_type: ProjectBudgetType
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    hourly_rate_min: Optional[float] = None
    hourly_rate_max: Optional[float] = None
    currency: str

    complexity: Optional[ProjectComplexity] = None
    deadline: Optional[date] = None
    status: ProjectStatus
    category: Optional[str] = None

    required_skills: List[str] = Field(default_factory=list)
    proposal_count: int
    created_at: datetime

    # liste görünümü için yardımcı alanlar
    customer_name: Optional[str] = None
    budget_display: Optional[str] = None


class ProjectSearchRequest(BaseModel):
    q: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    budget_type: Optional[ProjectBudgetType] = None
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    complexity: Optional[ProjectComplexity] = None
    skills: Optional[List[str]] = None
    sort_by: str = Field("created_at", pattern=r"^(created_at|budget_max|deadline|proposal_count)$")
    sort_order: str = Field("desc", pattern=r"^(asc|desc)$")
