from pydantic import BaseModel, EmailStr
from typing import Optional, List

class AdminUserBase(BaseModel):
    userId: int
    userEmail: EmailStr
    userName: Optional[str] = None
    userSurname: Optional[str] = None
    userPhoneNumber: Optional[str] = None
    userCitizenship: Optional[str] = None
    userEmploymentStatus: Optional[str] = None
    isAdmin: bool

    class Config:
        orm_mode = True

class AdminUserUpdate(BaseModel):
    userName: Optional[str] = None
    userSurname: Optional[str] = None
    userPhoneNumber: Optional[str] = None
    userCitizenship: Optional[str] = None
    userEmploymentStatus: Optional[str] = None
    isAdmin: Optional[bool] = None  # if you want to promote/demote

class AdminApplicationJob(BaseModel):
    id: int
    status: str
    created_at: str
    job_id: int
    job_title: Optional[str] = None
    job_country: Optional[str] = None

class AdminJobBase(BaseModel):
    id: int
    title: str

    company_name: Optional[str] = None
    reference_code: Optional[str] = None

    country: str
    city: Optional[str] = None
    workplace_address: Optional[str] = None

    category: Optional[str] = None
    employment_type: Optional[str] = None
    shift_type: Optional[str] = None

    salary_from: Optional[float] = None
    salary_to: Optional[float] = None
    currency: Optional[str] = None          # e.g. EUR
    salary_type: Optional[str] = None       # e.g. "hourly", "monthly"
    is_net: Optional[bool] = None           # net salary flag

    housing_provided: Optional[bool] = None
    housing_details: Optional[str] = None
    transport_provided: Optional[bool] = None
    bonuses: Optional[str] = None

    min_experience_years: Optional[int] = None
    language_required: Optional[str] = None
    documents_required: Optional[str] = None
    driving_license_required: Optional[bool] = None

    short_description: Optional[str] = None
    full_description: Optional[str] = None
    responsibilities: Optional[str] = None
    requirements_text: Optional[str] = None
    benefits_text: Optional[str] = None

    is_active: bool

    class Config:
        orm_mode = True


class AdminJobCreate(BaseModel):
    # required minimal
    title: str
    country: str

    # everything else optional
    company_name: Optional[str] = None
    reference_code: Optional[str] = None
    city: Optional[str] = None
    workplace_address: Optional[str] = None
    category: Optional[str] = None
    employment_type: Optional[str] = None
    shift_type: Optional[str] = None
    salary_from: Optional[float] = None
    salary_to: Optional[float] = None
    currency: Optional[str] = None
    salary_type: Optional[str] = None
    is_net: Optional[bool] = None
    housing_provided: Optional[bool] = None
    housing_details: Optional[str] = None
    transport_provided: Optional[bool] = None
    bonuses: Optional[str] = None
    min_experience_years: Optional[int] = None
    language_required: Optional[str] = None
    documents_required: Optional[str] = None
    driving_license_required: Optional[bool] = None
    short_description: Optional[str] = None
    full_description: Optional[str] = None
    responsibilities: Optional[str] = None
    requirements_text: Optional[str] = None
    benefits_text: Optional[str] = None
    is_active: Optional[bool] = True


class AdminJobUpdate(BaseModel):
    # all fields optional for partial updates
    title: Optional[str] = None
    company_name: Optional[str] = None
    reference_code: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    workplace_address: Optional[str] = None
    category: Optional[str] = None
    employment_type: Optional[str] = None
    shift_type: Optional[str] = None
    salary_from: Optional[float] = None
    salary_to: Optional[float] = None
    currency: Optional[str] = None
    salary_type: Optional[str] = None
    is_net: Optional[bool] = None
    housing_provided: Optional[bool] = None
    housing_details: Optional[str] = None
    transport_provided: Optional[bool] = None
    bonuses: Optional[str] = None
    min_experience_years: Optional[int] = None
    language_required: Optional[str] = None
    documents_required: Optional[str] = None
    driving_license_required: Optional[bool] = None
    short_description: Optional[str] = None
    full_description: Optional[str] = None
    responsibilities: Optional[str] = None
    requirements_text: Optional[str] = None
    benefits_text: Optional[str] = None
    is_active: Optional[bool] = None

class JobTranslationBase(BaseModel):
    id: int
    job_id: int
    lang_code: str
    title: Optional[str] = None
    short_description: Optional[str] = None
    full_description: Optional[str] = None
    responsibilities: Optional[str] = None
    requirements_text: Optional[str] = None
    benefits_text: Optional[str] = None
    housing_details: Optional[str] = None
    documents_required: Optional[str] = None
    bonuses: Optional[str] = None
    language_required: Optional[str] = None

    class Config:
        from_attributes = True


class JobTranslationUpsert(BaseModel):
    # lang_code comes from path, but we allow it so FE can reuse the type
    lang_code: Optional[str] = None
    title: Optional[str] = None
    short_description: Optional[str] = None
    full_description: Optional[str] = None
    responsibilities: Optional[str] = None
    requirements_text: Optional[str] = None
    benefits_text: Optional[str] = None
    housing_details: Optional[str] = None
    documents_required: Optional[str] = None
    bonuses: Optional[str] = None
    language_required: Optional[str] = None
