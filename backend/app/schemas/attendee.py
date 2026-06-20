from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AttendeeRead(BaseModel):
    id: int
    original_row_number: int
    full_name: str | None = None
    email: str | None = None
    workshop_title: str | None = None
    certificate_date: str | None = None
    is_valid: bool
    validation_error: str | None = None

    model_config = ConfigDict(from_attributes=True)


class AttendeeImportRead(BaseModel):
    id: int
    original_filename: str
    total_rows: int
    valid_rows: int
    invalid_rows: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AttendeeImportUploadResponse(BaseModel):
    attendee_import: AttendeeImportRead
    attendees: list[AttendeeRead]
    message: str
