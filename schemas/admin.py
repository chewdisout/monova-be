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
    country: str
    city: Optional[str] = None
    category: Optional[str] = None
    is_active: bool

    class Config:
        orm_mode = True

class AdminJobCreate(BaseModel):
    title: str
    country: str
    city: Optional[str] = None
    category: Optional[str] = None
    short_description: Optional[str] = None
    full_description: Optional[str] = None
    is_active: bool = True

class AdminJobUpdate(AdminJobCreate):
    is_active: Optional[bool] = None

class JobTranslationUpsert(BaseModel):
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
