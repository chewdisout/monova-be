from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from models.job import Job
from schemas.job import JobOut

jobs_router = APIRouter()

@jobs_router.get("", response_model=List[JobOut])
def list_jobs(
    country: Optional[str] = Query(None, description="Country code, e.g. DE"),
    category: Optional[str] = Query(None),
    q: Optional[str] = Query(None, description="Search in title/description"),
    db: Session = Depends(get_db),
):
    query = db.query(Job).filter(Job.is_active == True)

    if country:
        query = query.filter(Job.country == country.upper())
    if category:
        query = query.filter(Job.category == category)
    if q:
        like = f"%{q.lower()}%"
        query = query.filter(
            (Job.title.ilike(like)) | (Job.short_description.ilike(like))
        )

    query = query.order_by(Job.created_at.desc())
    return query.limit(200).all()


@jobs_router.get("/{job_id}", response_model=JobOut)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id, Job.is_active == True).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
