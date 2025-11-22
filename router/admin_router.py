from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from sqlalchemy import select
from database import get_db
from models.user import User
from models.job import Job
from models.job_translations import JobTranslation
from models.application import Application
from models.job_translations import JobTranslation
from schemas.admin import (
    AdminUserBase, AdminUserUpdate,
    AdminApplicationJob,
    AdminJobBase, AdminJobCreate, AdminJobUpdate,
    JobTranslationUpsert, JobTranslationBase
)
from services.auth_deps import get_current_admin

admin_router = APIRouter()

# --- Users ---

@admin_router.get("/users", response_model=list[AdminUserBase])
def list_users(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    rows = db.execute(select(User)).scalars().all()
    return rows


@admin_router.get("/users/{user_id}")
def get_user_detail(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    user = db.execute(
        select(User).where(User.userId == user_id)
    ).scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    from models.user_experience import UserExperience

    experiences = (
        db.execute(
            select(UserExperience)
            .where(UserExperience.userId == user.userId)
            .order_by(UserExperience.UserExperienceId.asc())
        )
        .scalars()
        .all()
    )

    app_count = db.query(Application).filter(Application.user_id == user_id).count()

    return {
        "userId": user.userId,
        "userEmail": user.userEmail,
        "userName": user.userName,
        "userSurname": user.userSurname,
        "userAge": user.userAge,
        "userGender": user.userGender,
        "userPhoneNumber": user.userPhoneNumber,
        "userCitizenship": user.userCitizenship,
        "userEmploymentStatus": user.userEmploymentStatus,
        "userPrefferedJob": user.userPrefferedJob,
        "userSecondPrefferedJob": user.userSecondPrefferedJob,
        "userPrefferedJobLocation": user.userPrefferedJobLocation,
        "userSecondPrefferedJobLocation": user.userSecondPrefferedJobLocation,
        "userTellAboutYourSelf": user.userTellAboutYourSelf,
        "is_admin": bool(getattr(user, "is_admin", False)),
        "experiences": [
            {
                "id": exp.UserExperienceId,
                "experience": exp.userExperience,
            }
            for exp in experiences
        ],
        "applications_count": app_count,
    }

@admin_router.patch("/users/{user_id}", response_model=AdminUserBase)
def admin_update_user(
    user_id: int,
    payload: AdminUserUpdate,
    db: Session = Depends(get_db),
):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    data = payload.dict(exclude_unset=True)

    for field, value in data.items():
        if field == "is_admin":
            user.isAdmin = value
        else:
            setattr(user, field, value)

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@admin_router.get("/users/{user_id}/applications", response_model=list[AdminApplicationJob])
def list_user_applications(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    q = (
        select(
            Application.id,
            Application.status,
            Application.created_at,
            Application.job_id,
            Job.title.label("job_title"),
            Job.country.label("job_country"),
        )
        .join(Job, Job.id == Application.job_id)
        .where(Application.user_id == user_id)
        .order_by(Application.created_at.desc())
    )
    rows = db.execute(q).all()
    return [
        {
            "id": r.id,
            "status": r.status,
            "created_at": r.created_at.isoformat(),
            "job_id": r.job_id,
            "job_title": r.job_title,
            "job_country": r.job_country,
        }
        for r in rows
    ]

@admin_router.delete("/users/{user_id}", status_code=204)
def admin_delete_user(
    user_id: int,
    db: Session = Depends(get_db),
):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    db.delete(user)
    db.commit()
    return Response(status_code=204)

# --- Jobs ---

@admin_router.get("/jobs", response_model=list[AdminJobBase])
def admin_list_jobs(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    return db.execute(select(Job)).scalars().all()


@admin_router.post("/jobs", response_model=AdminJobBase, status_code=201)
def admin_create_job(
    payload: AdminJobCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    data = payload.dict(exclude_unset=True)
    if "is_active" not in data:
        data["is_active"] = True

    job = Job(**data)
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


@admin_router.put("/jobs/{job_id}", response_model=AdminJobBase)
def admin_update_job(
    job_id: int,
    payload: AdminJobUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    for field, value in payload.dict(exclude_unset=True).items():
        setattr(job, field, value)

    db.add(job)
    db.commit()
    db.refresh(job)
    return job

@admin_router.get("/jobs/{job_id}", response_model=AdminJobBase)
def admin_get_job(
    job_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@admin_router.delete("/jobs/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(
    job_id: int,
    db: Session = Depends(get_db),
):
    job = (
        db.execute(
            select(Job).where(Job.id == job_id)
        )
        .scalar_one_or_none()
    )

    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    db.delete(job)
    db.commit()

    # DB will cascade delete job_translations + applications
    return Response(status_code=204)

# --- Translations ---

@admin_router.get(
    "/jobs/{job_id}/translations",
    response_model=list[JobTranslationBase]
)
def get_job_translations(
    job_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    rows = (
        db.execute(
            select(JobTranslation).where(JobTranslation.job_id == job_id)
        )
        .scalars()
        .all()
    )
    return rows


@admin_router.put("/jobs/{job_id}/translations/{lang_code}")
def upsert_job_translation(
    job_id: int,
    lang_code: str,
    payload: JobTranslationUpsert,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    lang = lang_code.lower()

    tr = (
        db.execute(
            select(JobTranslation).where(
                JobTranslation.job_id == job_id,
                JobTranslation.lang_code == lang,
            )
        )
        .scalar_one_or_none()
    )

    data = payload.dict(exclude_unset=True)
    data["lang_code"] = lang
    data["job_id"] = job_id

    if tr:
        for k, v in data.items():
            setattr(tr, k, v)
    else:
        tr = JobTranslation(**data)
        db.add(tr)

    db.commit()
    db.refresh(tr)
    return {"status": "ok"}
