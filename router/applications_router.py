from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from database import get_db
from models.application import Application
from models.job import Job
from schemas.application import ApplicationCreate, ApplicationOut, ApplicationWithJobOut
from services.auth_deps import get_current_user

application_router = APIRouter()


@application_router.post("", response_model=ApplicationOut, status_code=status.HTTP_201_CREATED)
def create_application(
    payload: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    job = db.query(Job).filter(Job.id == payload.job_id, Job.is_active == True).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found or inactive")

    # either rely on unique constraint or pre-check:
    existing = (
        db.query(Application)
        .filter(
            Application.user_id == current_user.userId,
            Application.job_id == payload.job_id,
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=400,
            detail="You already applied for this job",
        )

    app = Application(
        user_id=current_user.userId,
        job_id=payload.job_id,
        status="applied",
    )

    db.add(app)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="You already applied for this job",
        )

    db.refresh(app)
    return app


@application_router.get("/me", response_model=list[ApplicationWithJobOut])
def get_my_applications(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    apps = (
        db.query(Application)
        .join(Job, Job.id == Application.job_id)
        .filter(Application.user_id == current_user.userId)
        .order_by(Application.created_at.desc())
        .all()
    )
    return apps
