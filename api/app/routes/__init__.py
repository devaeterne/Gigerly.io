"""Admin-related schemas"""

from pydantic import BaseModel
from datetime import datetime

class AdminSummary(BaseModel):
    users: int
    projects: int
    proposals: int
    contracts: int
    revenue_total: float
    generated_at: datetime
