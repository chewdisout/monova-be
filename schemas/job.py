from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class JobBase(BaseModel):
    title: str
    company_name: Optional[str] = None
    reference_code: Optional[str] = None
    country: str = Field(..., min_length=2, max_length=2)
    city: Optional[str] = None
    workplace_address: Optional[str] = None
    category: str
    employment_type: Optional[str] = None          # e.g., FULLTIME / PARTTIME
    shift_type: Optional[str] = None               # e.g., DAY / NIGHT / MIXED
    salary_from: Optional[float] = None
    salary_to: Optional[float] = None
    currency: Optional[str] = "EUR"
    salary_type: Optional[str] = None              # e.g., monthly / hourly
    is_net: Optional[bool] = False
    housing_provided: Optional[bool] = False
    housing_details: Optional[str] = None
    transport_provided: Optional[bool] = False
    bonuses: Optional[str] = None
    benefits_text: Optional[str] = None
    min_experience_years: Optional[int] = None
    language_required: Optional[str] = None
    documents_required: Optional[str] = None
    driving_license_required: Optional[bool] = False
    requirements_text: Optional[str] = None
    responsibilities: Optional[str] = None
    short_description: str
    full_description: str
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    image: Optional[str] = None

class JobCreate(JobBase):
    pass  # if you want admin create via API

class JobOut(JobBase):
    id: int

    class Config:
        from_attributes = True
