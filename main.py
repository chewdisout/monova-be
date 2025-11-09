import os

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from datetime import timedelta

from database import SessionLocal, engine
from models.user import User
from models.user_experience import UserExperience
from schemas.user import UserCreate, UserOut, LoginRequest, UserExperienceCreate, UserExperienceOut, UserUpdate
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

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

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

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        sub = payload.get("sub")
        if sub is None:
            raise ValueError("Missing sub")
        user_id = int(sub)
    except (JWTError, ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    user = db.execute(
        select(User).where(User.userId == user_id)
    ).scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


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
        userEmploymentStatus = payload.userEmploymentStatus
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user

@app.put("/profile", response_model=UserOut)
def update_profile(
    payload: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    current_user.userName = payload.userName
    current_user.userSurname = payload.userSurname
    current_user.userAge = payload.userAge
    current_user.userGender = payload.userGender
    current_user.userPhoneNumber = payload.userPhoneNumber
    current_user.userCitizenship = payload.userCitizenship

    current_user.userPrefferedJob = payload.userPrefferedJob
    current_user.userSecondPrefferedJob = payload.userSecondPrefferedJob
    current_user.userPrefferedJobLocation = payload.userPrefferedJobLocation
    current_user.userSecondPrefferedJobLocation = payload.userSecondPrefferedJobLocation

    current_user.userTellAboutYourSelf = (payload.userTellAboutYourSelf or "").strip() or None

    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    return current_user

@app.get("/loadUserMeta", response_model=UserOut)
def get_user_meta(current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    return current_user

@app.get("/loadProfileData", response_model=UserOut)
def get_profile(current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    return current_user

@app.get("/profile/experience", response_model=list[UserExperienceOut])
def list_experience(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rows = db.execute(
        select(UserExperience)
        .where(UserExperience.userId == current_user.userId)
        .order_by(UserExperience.UserExperienceId.asc())
    ).scalars().all()
    return rows


@app.post("/profile/experience", response_model=UserExperienceOut, status_code=201)
def add_experience(
    payload: UserExperienceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    exp = UserExperience(
        userId=current_user.userId,
        userExperience=payload.userExperience.strip(),
    )
    db.add(exp)
    db.commit()
    db.refresh(exp)
    return exp


@app.delete("/profile/experience/{exp_id}", status_code=204)
def delete_experience(
    exp_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    exp = db.execute(
        select(UserExperience).where(
            UserExperience.UserExperienceId == exp_id,
            UserExperience.userId == current_user.userId,
        )
    ).scalar_one_or_none()

    if not exp:
        raise HTTPException(status_code=404, detail="Experience not found")

    db.delete(exp)
    db.commit()
    return