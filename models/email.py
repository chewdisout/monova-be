from sqlalchemy import Column, Integer, String, Text, Boolean
from database import Base

class EmailContact(Base):
    __tablename__ = "email_contact"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    userEmail = Column(String(255), unique=True, index=True, nullable=False)
    message = Column(Text, nullable=True)