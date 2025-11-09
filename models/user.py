from sqlalchemy import Column, Integer, String, Text
from database import Base

class User(Base):
    __tablename__ = "users"

    userId = Column(Integer, primary_key=True, index=True, autoincrement=True)
    userEmail = Column(String(255), unique=True, index=True, nullable=False)
    userPasswordEncrypted = Column(String(255), nullable=False)
    userName = Column(String(100), nullable=True)
    userSurname = Column(String(100), nullable=True)
    userGender = Column(String(20), nullable=True)
    userAge = Column(Integer, nullable=True)
    userPhoneNumber = Column(String(50), nullable=True)
    userCitizenship = Column(String(100), nullable=True)

    userPrefferedJob = Column(String(255), nullable=True)
    userSecondPrefferedJob = Column(String(255), nullable=True)
    userPrefferedJobLocation = Column(String(255), nullable=True)
    userSecondPrefferedJobLocation = Column(String(255), nullable=True)

    userTellAboutYourSelf = Column(Text, nullable=True)
    userWorkExperience = Column(Text, nullable=True)
    userEmploymentStatus = Column(String(255), nullable=True)
