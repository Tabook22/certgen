from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.dependencies import get_db
from app.models.template import CertificateTemplate
from app.schemas.template import TemplateRead, TemplateUploadResponse
from app.services.template_service import TemplateService

router = APIRouter(tags=["templates"])


@router.post("/templates", response_model=TemplateUploadResponse, status_code=201)
@router.post("/templates/upload", response_model=TemplateUploadResponse, status_code=201, include_in_schema=False)
async def upload_template(
    file: UploadFile = File(...),
    name: str | None = Form(default=None),
    description: str | None = Form(default=None),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> TemplateUploadResponse:
    service = TemplateService(settings)
    try:
        template = await service.create_template(db, file, name, description)
    except Exception:
        db.rollback()
        raise
    return TemplateUploadResponse(template=template, message="Template uploaded successfully.")


@router.get("/templates", response_model=list[TemplateRead])
def list_templates(db: Session = Depends(get_db)) -> list[CertificateTemplate]:
    return list(db.scalars(select(CertificateTemplate).order_by(CertificateTemplate.created_at.desc())).all())


@router.get("/templates/{template_id}", response_model=TemplateRead)
def get_template(template_id: int, db: Session = Depends(get_db)) -> CertificateTemplate:
    template = db.get(CertificateTemplate, template_id)
    if template is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found.")
    return template


@router.get("/templates/{template_id}/preview")
def get_template_preview(
    template_id: int,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> FileResponse:
    template = db.get(CertificateTemplate, template_id)
    if template is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found.")

    preview_path = template.preview_image_path or template.file_path
    file_path = settings.storage_root / preview_path
    if not file_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template preview not found.")
    return FileResponse(file_path)
