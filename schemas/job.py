from pydantic import BaseModel, Field
from typing import Optional

class JobBase(BaseModel):
    title: str
    company_name: Optional[str] = None
    country: str = Field(..., min_length=2, max_length=2)
    city: Optional[str] = None
    category: str
    employment_type: Optional[str] = None
    shift_type: Optional[str] = None
    salary_from: Optional[float] = None
    salary_to: Optional[float] = None
    currency: Optional[str] = "EUR"
    salary_type: Optional[str] = None
    is_net: Optional[bool] = False
    housing_provided: Optional[bool] = False
    transport_provided: Optional[bool] = False
    short_description: str
    full_description: str
    is_active: bool = True

class JobCreate(JobBase):
    pass  # if you want admin create via API

class JobOut(JobBase):
    id: int

    class Config:
        from_attributes = True
