# schemas.py
from pydantic import BaseModel, EmailStr, Field, constr, conint
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
    userEmploymentStatus: str


class UserOut(BaseModel):
    userId: int
    userEmail: EmailStr
    userName: Optional[str] = None
    userSurname: Optional[str] = None
    userAge: Optional[int] = None
    userGender: Optional[str] = None
    userPhoneNumber: Optional[str] = None
    userCitizenship: Optional[str] = None
    userEmploymentStatus: str
    userPrefferedJob: Optional[str] = None
    userSecondPrefferedJob: Optional[str] = None
    userPrefferedJobLocation: Optional[str] = None
    userSecondPrefferedJobLocation: Optional[str] = None
    userTellAboutYourSelf: Optional[str] = None

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    userName: constr(strip_whitespace=True, min_length=1, max_length=100)
    userSurname: constr(strip_whitespace=True, min_length=1, max_length=100)
    userAge: conint(ge=16, le=75)
    userGender: constr(strip_whitespace=True, min_length=1, max_length=50)
    userPhoneNumber: constr(strip_whitespace=True, min_length=5, max_length=32)
    userCitizenship: constr(strip_whitespace=True, min_length=2, max_length=100)

    userPrefferedJob: Optional[constr(strip_whitespace=True, min_length=2, max_length=255)] = None
    userSecondPrefferedJob: Optional[constr(strip_whitespace=True, min_length=2, max_length=255)] = None
    userPrefferedJobLocation: Optional[constr(strip_whitespace=True, min_length=2, max_length=255)] = None
    userSecondPrefferedJobLocation: Optional[constr(strip_whitespace=True, min_length=2, max_length=255)] = None

    userTellAboutYourSelf: Optional[str] = None  # the only optional text field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserExperienceBase(BaseModel):
    userExperience: str = Field(..., min_length=2, max_length=2000)

class UserExperienceCreate(UserExperienceBase):
    pass

class UserExperienceOut(UserExperienceBase):
    UserExperienceId: int

    class Config:
        from_attributes = True

