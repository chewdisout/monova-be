from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import select
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status


from models.user import User
from database import get_db
from services.security import SECRET_KEY, ALGORITHM
from services.auth_deps import get_current_user
from models.user_experience import UserExperience
from schemas.user import UserOut, UserExperienceCreate, UserExperienceOut, UserUpdate

profile_router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

@profile_router.get("/loadProfileData", response_model=UserOut)
def get_profile(current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    return current_user

@profile_router.get("/profile/experience", response_model=list[UserExperienceOut])
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


@profile_router.post("/profile/experience", response_model=UserExperienceOut, status_code=201)
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


@profile_router.delete("/profile/experience/{exp_id}", status_code=204)
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

@profile_router.put("/profile", response_model=UserOut)
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

@profile_router.get("/loadUserMeta", response_model=UserOut)
def get_user_meta(current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    return current_user