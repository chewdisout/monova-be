# schemas.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserCreate(BaseModel):
    userEmail: EmailStr
    password: str = Field(min_length=6, max_length=36)

    userName: Optional[str] = None
    userSurname: Optional[str] = None
    userAge: Optional[int] = None
    userGender: Optional[str] = None
    userPhoneNumber: Optional[str] = None
    userCitizenship: Optional[str] = None


class UserOut(BaseModel):
    userId: int
    userEmail: EmailStr
    userName: Optional[str] = None
    userSurname: Optional[str] = None
    userAge: Optional[int] = None
    userGender: Optional[str] = None
    userPhoneNumber: Optional[str] = None
    userCitizenship: Optional[str] = None

    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    email: EmailStr
    password: str