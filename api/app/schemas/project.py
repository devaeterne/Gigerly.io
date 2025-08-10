"""Project-related schemas"""

from typing import List, Optional
from datetime import datetime, date

from pydantic import BaseModel, Field, model_validator

from app.models import ProjectStatus, ProjectBudgetType, ProjectComplexity
from .common import MoneyAmount, SkillSchema, AttachmentSchema

class ProjectBase(BaseModel):
    title: str = Field(..., min_length=10, max_length=200)
    description: str = Field(..., min_length=50, max_length=5000)
    budget_type: ProjectBudgetType = ProjectBudgetType.fixed
    currency: str = Field("USD", pattern=r"^[A-Z]{3}$")

class ProjectCreate(ProjectBase):
    # Budget fields
    budget_min: Optional[MoneyAmount] = None
    budget_max: Optional[MoneyAmount] = None
    hourly_rate_min: Optional[MoneyAmount] = None
    hourly_rate_max: Optional[MoneyAmount] = None

    # Project details
    complexity: Optional[ProjectComplexity] = None
    estimated_duration: Optional[int] = Field(None, ge=1, le=365)  # days
    deadline: Optional[date] = None

    # Categories and skills
    category: Optional[str] = Field(None, max_length=100)
    subcategory: Optional[str] = Field(None, max_length=100)
    required_skills: List[SkillSchema] = Field(default_factory=list)

    # Settings
    status: ProjectStatus = ProjectStatus.open
    allows_proposals: bool = True
    max_proposals: int = Field(50, ge=1, le=200)
    tags: List[str] = Field(default_factory=list, max_length=10)
    attachments: List[AttachmentSchema] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validate_ranges_and_deadline(self):
        if self.budget_min is not None and self.budget_max is not None:
            if self.budget_max < self.budget_min:
                raise ValueError("budget_max must be greater than or equal to budget_min")
        if self.hourly_rate_min is not None and self.hourly_rate_max is not None:
            if self.hourly_rate_max < self.hourly_rate_min:
                raise ValueError("hourly_rate_max must be greater than or equal to hourly_rate_min")
        if self.deadline is not None and self.deadline <= date.today():
            raise ValueError("deadline must be in the future")
        return self

class ProjectUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=10, max_length=200)
    description: Optional[str] = Field(None, min_length=50, max_length=5000)
    budget_min: Optional[MoneyAmount] = None
    budget_max: Optional[MoneyAmount] = None
    hourly_rate_min: Optional[MoneyAmount] = None
    hourly_rate_max: Optional[MoneyAmount] = None
    complexity: Optional[ProjectComplexity] = None
    estimated_duration: Optional[int] = Field(None, ge=1, le=365)
    deadline: Optional[date] = None
    category: Optional[str] = Field(None, max_length=100)
    subcategory: Optional[str] = Field(None, max_length=100)
    required_skills: Optional[List[SkillSchema]] = None
    status: Optional[ProjectStatus] = None
    allows_proposals: Optional[bool] = None
    max_proposals: Optional[int] = Field(None, ge=1, le=200)
    tags: Optional[List[str]] = Field(None, max_length=10)
    attachments: Optional[List[AttachmentSchema]] = None

    @model_validator(mode="after")
    def _validate_ranges_and_deadline(self):
        if self.budget_min is not None and self.budget_max is not None:
            if self.budget_max < self.budget_min:
                raise ValueError("budget_max must be greater than or equal to budget_min")
        if self.hourly_rate_min is not None and self.hourly_rate_max is not None:
            if self.hourly_rate_max < self.hourly_rate_min:
                raise ValueError("hourly_rate_max must be greater than or equal to hourly_rate_min")
        if self.deadline is not None and self.deadline <= date.today():
            raise ValueError("deadline must be in the future")
        return self

class ProjectResponse(ProjectBase):
    id: int
    customer_id: int
    status: ProjectStatus
    budget_min: Optional[MoneyAmount]
    budget_max: Optional[MoneyAmount]
    hourly_rate_min: Optional[MoneyAmount]
    hourly_rate_max: Optional[MoneyAmount]
    complexity: Optional[ProjectComplexity]
    estimated_duration: Optional[int]
    deadline: Optional[date]
    category: Optional[str]
    subcategory: Optional[str]
    required_skills: List[SkillSchema]
    is_featured: bool = False
    allows_proposals: bool
    max_proposals: int
    attachments: List[AttachmentSchema]
    slug: Optional[str]
    tags: List[str]
    view_count: int
    proposal_count: int
    created_at: datetime
    updated_at: datetime

    # Related data (optional)
    customer: Optional[dict] = None
    budget_display: Optional[str] = None

    class Config:
        from_attributes = True

class ProjectListResponse(BaseModel):
    id: int
    title: str
    description: str
    customer_id: int
    budget_type: ProjectBudgetType
    budget_min: Optional[MoneyAmount]
    budget_max: Optional[MoneyAmount]
    hourly_rate_min: Optional[MoneyAmount]
    hourly_rate_max: Optional[MoneyAmount]
    currency: str
    complexity: Optional[ProjectComplexity]
    deadline: Optional[date]
    status: ProjectStatus
    category: Optional[str]
    required_skills: List[SkillSchema]
    proposal_count: int
    created_at: datetime
    customer_name: Optional[str] = None
    budget_display: Optional[str] = None

    class Config:
        from_attributes = True

class ProjectSearchRequest(BaseModel):
    q: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    budget_type: Optional[ProjectBudgetType] = None
    budget_min: Optional[MoneyAmount] = None
    budget_max: Optional[MoneyAmount] = None
    complexity: Optional[ProjectComplexity] = None
    skills: Optional[List[str]] = None
    sort_by: str = Field("created_at", pattern=r"^(created_at|budget_max|deadline|proposal_count)$")
    sort_order: str = Field("desc", pattern=r"^(asc|desc)$")
