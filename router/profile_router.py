from fastapi import Depends, HTTPException, APIRouter, UploadFile, File, status, Response
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from botocore.exceptions import BotoCoreError, ClientError
import os
import boto3


from models.user import User
from database import get_db
from services.security import SECRET_KEY, ALGORITHM
from services.auth_deps import get_current_user
from models.user_experience import UserExperience
from schemas.user import UserOut, UserExperienceCreate, UserExperienceOut, UserUpdate

S3_BUCKET_NAME = os.getenv("CV_S3_BUCKET", "monova-s3-bucket")
S3_REGION = os.getenv("AWS_REGION", "us-east-1")  # adjust if needed

s3_client = boto3.client("s3", region_name=S3_REGION)

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

@profile_router.get("/profile/cv")
def get_cv(
    current_user: User = Depends(get_current_user),
):
    if not current_user.cv_s3_key:
        raise HTTPException(status_code=404, detail="No CV uploaded")

    url = s3_client.generate_presigned_url(
        "get_object",
        Params={"Bucket": S3_BUCKET_NAME, "Key": current_user.cv_s3_key},
        ExpiresIn=3600,
    )
    return {
        "original_name": current_user.cv_original_name,
        "url": url,
    }

@profile_router.post("/profile/cv/upload", status_code=201)
async def upload_cv(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # 1) Basic validation
    allowed_types = {
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    }

    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type. Please upload a PDF or Word document.",
        )

    # 2) Generate S3 key, grouped by userId
    _, ext = os.path.splitext(file.filename or "")
    ext = ext or ".pdf"
    key = f"cvs/{current_user.userId}/{uuid.uuid4().hex}{ext}"

    if current_user.cv_s3_key:
        try:
            s3_client.delete_object(
                Bucket=S3_BUCKET_NAME,
                Key=current_user.cv_s3_key,
            )
        except Exception as e:
            print("Failed to delete old CV:", repr(e))

    try:
        # 3) Upload to S3
        s3_client.upload_fileobj(
            file.file,
            S3_BUCKET_NAME,
            key,
            ExtraArgs={"ContentType": file.content_type or "application/octet-stream"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload CV: {e}",
        )

    # 4) Save metadata on the user (or in a separate table if you prefer)
    current_user.cv_s3_key = key
    current_user.cv_original_name = file.filename

    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    # 5) Optionally generate a short-lived presigned URL for immediate access
    try:
        presigned_url = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": S3_BUCKET_NAME, "Key": key},
            ExpiresIn=3600,  # 1 hour
        )
    except Exception:
        presigned_url = None

    return {
        "key": key,
        "original_name": file.filename,
        "url": presigned_url,
    }

@profile_router.delete("/profile/cv", status_code=204)
async def delete_cv(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # If user has no CV, return 404
    if not current_user.cv_s3_key:
      raise HTTPException(status_code=404, detail="No CV to delete.")

    key = current_user.cv_s3_key

    # Try to delete from S3 – but even if this fails, we still clear DB
    try:
        s3_client.delete_object(Bucket=S3_BUCKET_NAME, Key=key)
    except (BotoCoreError, ClientError) as e:
        print("S3 delete error:", repr(e))
        # You can either still continue, or raise 500 if you want strict behavior

    # Clear metadata on the user
    current_user.cv_s3_key = None
    current_user.cv_original_name = None

    db.add(current_user)
    db.commit()

    # 204 No Content – nothing in body
    return Response(status_code=204)