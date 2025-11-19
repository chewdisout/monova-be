from pydantic import BaseModel, EmailStr

class EmailContactCreate(BaseModel):
    userEmail: EmailStr
    message: str

class EmailContactResponse(EmailContactCreate):
    id: int

    class Config:
        orm_mode = True
