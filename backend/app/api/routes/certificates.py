from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.dependencies import get_db
from app.models.generated_certificate import GeneratedCertificate
from app.schemas.generation import GeneratedCertificateRead

router = APIRouter(prefix="/certificates", tags=["certificates"])


@router.get("", response_model=list[GeneratedCertificateRead])
def list_certificates(db: Session = Depends(get_db)) -> list[GeneratedCertificate]:
    return list(db.scalars(select(GeneratedCertificate).order_by(GeneratedCertificate.created_at.desc())).all())


@router.get("/{certificate_id}", response_model=GeneratedCertificateRead)
def get_certificate(certificate_id: int, db: Session = Depends(get_db)) -> GeneratedCertificate:
    certificate = db.get(GeneratedCertificate, certificate_id)
    if certificate is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Certificate not found.")
    return certificate


@router.get("/{certificate_id}/download")
def download_certificate(
    certificate_id: int,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> FileResponse:
    certificate = db.get(GeneratedCertificate, certificate_id)
    if certificate is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Certificate not found.")
    if certificate.status != "generated":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Certificate was not generated successfully.")

    file_path = settings.storage_root / certificate.file_path
    if not file_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Certificate file not found.")
    return FileResponse(file_path, media_type="application/pdf", filename=file_path.name)
