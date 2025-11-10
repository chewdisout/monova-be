import os

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import timedelta

from database import engine, get_db
# schemas
from schemas.user import UserCreate, UserOut, LoginRequest
# models
from models.user import User
# services
from services.security import hash_password, verify_password, create_access_token
# routes
from router.jobs_router import jobs_router
from router.profile_router import profile_router
from router.applications_router import application_router
from router.admin_router import admin_router

app = FastAPI(title="Monova Auth API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_ORIGIN", "http://localhost:4200")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jobs_router, prefix="/jobs", tags=["job"])
app.include_router(application_router, prefix="/applications", tags=["Applications"])
app.include_router(admin_router, prefix="/admin", tags=["Admin"])
app.include_router(profile_router)

@app.on_event("startup")
def on_startup():
    from database import Base
    Base.metadata.create_all(bind=engine)

ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 240

@app.post("/login", status_code=201)
def login_user(form_data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.userEmail == form_data.email).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Account not found.")
    if not verify_password(form_data.password, user.userPasswordEncrypted):
        raise HTTPException(status_code=401, detail="Invalid password.")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(data={"sub": str(user.userId), "isAdmin": user.isAdmin}, expires_delta=access_token_expires)

    return {"access_token": token, "token_type": "bearer"}


@app.post("/createUser", response_model=UserOut, status_code=201)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    email = payload.userEmail.lower().strip()

    existing = db.execute(
        select(User).where(User.userEmail == email)
    ).scalar_one_or_none()

    if existing:
        raise HTTPException(status_code=400, detail="User with this email already exists")

    password_hashed = hash_password(payload.password)

    user = User(
        userEmail=email,
        userPasswordEncrypted=password_hashed,
        userName=payload.userName,
        userSurname=payload.userSurname,
        userAge=payload.userAge,
        userGender=payload.userGender,
        userPhoneNumber=payload.userPhoneNumber,
        userCitizenship=payload.userCitizenship,
        userEmploymentStatus = payload.userEmploymentStatus,
        isAdmin = False 
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


