"""Contract-related schemas"""

from typing import List, Optional
from datetime import datetime, date
from decimal import Decimal

from pydantic import BaseModel, Field, model_validator

from app.models import ContractStatus, ContractType, MilestoneStatus
from .common import MoneyAmount

# -------------------- Contracts --------------------

class ContractBase(BaseModel):
    title: str = Field(..., min_length=10, max_length=200)
    description: str = Field(..., min_length=50, max_length=2000)
    contract_type: ContractType
    total_amount: MoneyAmount
    currency: str = Field("USD", pattern=r"^[A-Z]{3}$")

class ContractCreate(ContractBase):
    project_id: int
    freelancer_id: int
    winning_proposal_id: Optional[int] = None
    hourly_rate: Optional[MoneyAmount] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    estimated_hours: Optional[int] = Field(None, ge=1)
    terms: dict = Field(default_factory=dict)
    deliverables: List[dict] = Field(default_factory=list)

    @model_validator(mode="after")
    def _end_after_start(self):
        if self.end_date and self.start_date and self.end_date <= self.start_date:
            raise ValueError("end_date must be after start_date")
        return self

class ContractUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=10, max_length=200)
    description: Optional[str] = Field(None, min_length=50, max_length=2000)
    hourly_rate: Optional[MoneyAmount] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    estimated_hours: Optional[int] = Field(None, ge=1)
    status: Optional[ContractStatus] = None
    terms: Optional[dict] = None
    deliverables: Optional[List[dict]] = None

    @model_validator(mode="after")
    def _end_after_start(self):
        if self.end_date and self.start_date and self.end_date <= self.start_date:
            raise ValueError("end_date must be after start_date")
        return self

# -------------------- Milestones --------------------

class MilestoneBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    amount: MoneyAmount
    currency: str = Field("USD", pattern=r"^[A-Z]{3}$")
    due_date: Optional[date] = None
    estimated_hours: Optional[int] = Field(None, ge=1)

class MilestoneCreate(MilestoneBase):
    contract_id: int
    order_index: int = Field(0, ge=0)

class MilestoneUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=5, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    due_date: Optional[date] = None
    estimated_hours: Optional[int] = Field(None, ge=1)
    status: Optional[MilestoneStatus] = None
    deliverable_url: Optional[str] = Field(None, max_length=500)
    submission_notes: Optional[str] = Field(None, max_length=2000)
    approval_notes: Optional[str] = Field(None, max_length=2000)

class MilestoneResponse(MilestoneBase):
    id: int
    contract_id: int
    order_index: int
    status: MilestoneStatus
    funded_at: Optional[datetime]
    started_at: Optional[datetime]
    submitted_at: Optional[datetime]
    approved_at: Optional[datetime]
    released_at: Optional[datetime]
    deliverable_url: Optional[datetime]
    submission_notes: Optional[str]
    approval_notes: Optional[str]
    is_overdue: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# -------------------- Responses --------------------

class ContractResponse(ContractBase):
    id: int
    project_id: int
    customer_id: int
    freelancer_id: int
    winning_proposal_id: Optional[int]
    hourly_rate: Optional[MoneyAmount]
    start_date: Optional[date]
    end_date: Optional[date]
    estimated_hours: Optional[int]
    status: ContractStatus
    terms: dict
    deliverables: List[dict]
    payment_schedule: Optional[dict]
    approved_hours: Decimal  # saat; para değil
    billed_amount: MoneyAmount
    paid_amount: MoneyAmount
    signed_by_customer_at: Optional[datetime]
    signed_by_freelancer_at: Optional[datetime]
    completed_at: Optional[datetime]
    is_signed: bool
    remaining_amount: float
    completion_percentage: float
    created_at: datetime
    updated_at: datetime

    # Related data (optional)
    project: Optional[dict] = None
    customer: Optional[dict] = None
    freelancer: Optional[dict] = None
    milestones: List[MilestoneResponse] = []

    class Config:
        from_attributes = True

class ContractListResponse(BaseModel):
    id: int
    title: str
    project_id: int
    project_title: Optional[str]
    customer_id: int
    customer_name: Optional[str]
    freelancer_id: int
    freelancer_name: Optional[str]
    contract_type: ContractType
    total_amount: MoneyAmount
    currency: str
    status: ContractStatus
    completion_percentage: float
    created_at: datetime

    class Config:
        from_attributes = True
