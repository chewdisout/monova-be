# routers/email.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database import get_db
from models.email import EmailContact
from schemas.email import EmailContactCreate, EmailContactResponse

email_router = APIRouter()

@email_router.post(
    "/add",
    response_model=EmailContactResponse,
    status_code=status.HTTP_201_CREATED
)
def create_email_contact(
    payload: EmailContactCreate,
    db: Session = Depends(get_db)
):
    contact_info = EmailContact(
        userEmail=payload.userEmail,
        message=payload.message
    )

    db.add(contact_info)
    db.commit()
    db.refresh(contact_info)

    print(payload.message)

    return contact_info
