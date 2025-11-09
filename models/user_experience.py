from sqlalchemy import Column, Integer, Text, ForeignKey
from database import Base

class UserExperience(Base):
    __tablename__ = "user_experience"

    UserExperienceId = Column(Integer, primary_key=True, index=True, autoincrement=True)
    userId = Column(Integer, ForeignKey("users.userId"), index=True, nullable=False)
    userExperience = Column(Text, nullable=False)
