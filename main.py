import os

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from datetime import timedelta

from database import SessionLocal, engine
from models.user import User
from schemas.user import UserCreate, UserOut, LoginRequest
from jose import jwt, JWTError
from services.security import hash_password, verify_password, create_access_token
from services.security import SECRET_KEY, ALGORITHM



app = FastAPI(title="Monova Auth API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_ORIGIN", "http://localhost:4200")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    from database import Base
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 240

@app.post("/login", status_code=201)
def login_user(form_data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.userEmail == form_data.email).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Account not found.")
    if not verify_password(form_data.password, user.userPasswordEncrypted):
        raise HTTPException(status_code=401, detail="Invalid password.")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(data={"sub": str(user.userId)}, expires_delta=access_token_expires)

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
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")
@app.get("/profile", response_model=UserOut)
def get_profile(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
    except (JWTError, ValueError, TypeError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = db.execute(select(User).where(User.userId == user_id)).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return user