from database import engine, Base
from models.user import User
from models.user_experience import UserExperience
from models.job import Job
from models.application import Application

def create_all_tables():
    print("Creating tables if not exist...")
    Base.metadata.create_all(bind=engine)
    print("Done.")

if __name__ == "__main__":
    create_all_tables()
