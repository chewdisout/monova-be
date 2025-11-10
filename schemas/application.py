from pydantic import BaseModel
from datetime import datetime

class ApplicationCreate(BaseModel):
    job_id: int

class ApplicationJobShort(BaseModel):
    id: int
    title: str
    country: str
    city: str | None = None
    category: str

    class Config:
        from_attributes = True

class ApplicationOut(BaseModel):
    id: int
    job_id: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class ApplicationWithJobOut(BaseModel):
    id: int
    status: str
    created_at: datetime
    job: ApplicationJobShort

    class Config:
        from_attributes = True
