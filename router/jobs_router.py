from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import select

from database import get_db
from models.job import Job
from schemas.job import JobOut

from .jobs_router_utils import job_to_dict, resolve_lang

jobs_router = APIRouter()

@jobs_router.get("", response_model=List[JobOut])
def list_jobs(
    db: Session = Depends(get_db),
    country: str | None = Query(None),
    lang: str | None = Query(None),
):
    q = select(Job).where(Job.is_active == True)
    if country:
        q = q.where(Job.country == country.upper())

    jobs = db.execute(q).scalars().all()
    lang_resolved = resolve_lang(lang)
    return [job_to_dict(j, lang_resolved) for j in jobs]


@jobs_router.get("/{job_id}", response_model=JobOut)
def get_job(
    job_id: int,
    lang: str | None = Query(None),
    db: Session = Depends(get_db),
):
    job = db.get(Job, job_id)
    if not job or not job.is_active:
        raise HTTPException(status_code=404, detail="Job not found")

    return job_to_dict(job, resolve_lang(lang))
