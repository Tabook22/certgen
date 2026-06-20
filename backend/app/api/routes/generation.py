from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.dependencies import get_db
from app.models.generated_certificate import GeneratedCertificate
from app.models.generation_job import GenerationJob
from app.schemas.generation import GeneratedCertificateRead, GenerationJobCreate, GenerationJobRead
from app.services.generation_service import GenerationService

router = APIRouter(prefix="/generation-jobs", tags=["generation-jobs"])


@router.post("", response_model=GenerationJobRead, status_code=status.HTTP_201_CREATED)
def create_generation_job(
    payload: GenerationJobCreate,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> GenerationJob:
    service = GenerationService(settings)
    return service.create_generation_job(
        db,
        payload.template_id,
        payload.attendee_import_id,
        payload.workshop_title,
        payload.certificate_date,
    )


@router.get("", response_model=list[GenerationJobRead])
def list_generation_jobs(db: Session = Depends(get_db)) -> list[GenerationJob]:
    return list(db.scalars(select(GenerationJob).order_by(GenerationJob.created_at.desc())).all())


@router.get("/{job_id}", response_model=GenerationJobRead)
def get_generation_job(job_id: int, db: Session = Depends(get_db)) -> GenerationJob:
    job = db.get(GenerationJob, job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Generation job not found.")
    return job


@router.get("/{job_id}/certificates", response_model=list[GeneratedCertificateRead])
def list_job_certificates(job_id: int, db: Session = Depends(get_db)) -> list[GeneratedCertificate]:
    query = select(GeneratedCertificate).where(GeneratedCertificate.generation_job_id == job_id)
    return list(db.scalars(query.order_by(GeneratedCertificate.created_at.desc())).all())


@router.get("/{job_id}/download-zip")
def download_job_zip(
    job_id: int,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> FileResponse:
    zip_path = GenerationService(settings).create_zip_for_job(db, job_id)
    return FileResponse(zip_path, media_type="application/zip", filename=f"certificates-job-{job_id}.zip")
