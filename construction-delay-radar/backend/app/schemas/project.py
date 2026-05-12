from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    location: str = Field(..., min_length=1, max_length=200)
    start_date: date
    duration_days: int = Field(..., gt=0)
    description: Optional[str] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[date] = None
    duration_days: Optional[int] = None
    description: Optional[str] = None
    status: Optional[str] = None
    progress_percent: Optional[int] = Field(None, ge=0, le=100)


class ProjectResponse(BaseModel):
    id: str
    name: str
    location: str
    start_date: date
    duration_days: int
    description: Optional[str] = None
    status: str = "planning"
    progress_percent: int = 0
    risk_level: str = "LOW"
    created_at: str
    updated_at: str
