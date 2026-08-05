from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from sqlalchemy.sql import func
from database import Base

class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    raw_message = Column(Text, nullable=False)
    budget = Column(Float, nullable=True)
    budget_tier = Column(String, nullable=True)
    lead_score = Column(Integer, nullable=True)
    status = Column(String, default="New")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
