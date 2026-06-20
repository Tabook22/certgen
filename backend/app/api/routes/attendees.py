from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.dependencies import get_db
from app.models.attendee import Attendee, AttendeeImport
from app.schemas.attendee import AttendeeImportRead, AttendeeImportUploadResponse, AttendeeRead
from app.services.excel_service import ExcelService

router = APIRouter(tags=["attendee-imports"])


@router.post("/attendee-imports", response_model=AttendeeImportUploadResponse, status_code=201)
@router.post("/attendees/upload", response_model=AttendeeImportUploadResponse, status_code=201, include_in_schema=False)
async def upload_attendees(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> AttendeeImportUploadResponse:
    service = ExcelService(settings)
    try:
        attendee_import, attendees = await service.create_attendee_import(db, file)
    except Exception:
        db.rollback()
        raise
    return AttendeeImportUploadResponse(
        attendee_import=attendee_import,
        attendees=attendees[:25],
        message="Attendee import uploaded and validated successfully.",
    )


@router.get("/attendee-imports", response_model=list[AttendeeImportRead])
def list_attendee_imports(db: Session = Depends(get_db)) -> list[AttendeeImport]:
    return list(db.scalars(select(AttendeeImport).order_by(AttendeeImport.created_at.desc())).all())


@router.get("/attendee-imports/{import_id}/attendees", response_model=list[AttendeeRead])
def list_attendees(import_id: int, db: Session = Depends(get_db)) -> list[Attendee]:
    query = select(Attendee).where(Attendee.attendee_import_id == import_id).order_by(Attendee.original_row_number)
    return list(db.scalars(query).all())
