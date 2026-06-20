from datetime import datetime

from pydantic import BaseModel, ConfigDict


class GenerationJobCreate(BaseModel):
    template_id: int
    attendee_import_id: int
    workshop_title: str | None = None
    certificate_date: str | None = None


class GenerationJobRead(BaseModel):
    id: int
    template_id: int
    attendee_import_id: int
    status: str
    total_count: int
    success_count: int
    failed_count: int
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class GeneratedCertificateRead(BaseModel):
    id: int
    generation_job_id: int
    attendee_id: int
    file_path: str
    status: str
    error_message: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
