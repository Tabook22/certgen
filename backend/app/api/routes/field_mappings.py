from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models.field_mapping import FieldMapping
from app.models.template import CertificateTemplate
from app.schemas.field_mapping import FieldMappingRead, FieldMappingUpdate

router = APIRouter(prefix="/templates/{template_id}/field-mappings", tags=["field-mappings"])


@router.get("", response_model=list[FieldMappingRead])
def list_field_mappings(template_id: int, db: Session = Depends(get_db)) -> list[FieldMapping]:
    query = select(FieldMapping).where(FieldMapping.template_id == template_id).order_by(FieldMapping.field_key)
    return list(db.scalars(query).all())


@router.put("", response_model=list[FieldMappingRead])
def save_field_mappings(
    template_id: int,
    payload: FieldMappingUpdate,
    db: Session = Depends(get_db),
) -> list[FieldMapping]:
    if db.get(CertificateTemplate, template_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found.")

    existing = db.scalars(select(FieldMapping).where(FieldMapping.template_id == template_id)).all()
    for mapping in existing:
        db.delete(mapping)

    mappings = [FieldMapping(template_id=template_id, **mapping.model_dump()) for mapping in payload.mappings]
    db.add_all(mappings)
    db.commit()
    for mapping in mappings:
        db.refresh(mapping)
    return mappings
