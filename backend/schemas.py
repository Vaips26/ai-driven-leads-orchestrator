from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class LeadBase(BaseModel):
    name: str
    email: str
    phone: str
    raw_message: str
    budget: Optional[float] = None
    budget_tier: Optional[str] = None
    lead_score: Optional[int] = None
    status: Optional[str] = "New"

class LeadCreate(LeadBase):
    pass

class LeadResponse(LeadBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
