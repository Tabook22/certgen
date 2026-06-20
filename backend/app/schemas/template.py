from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TemplateBase(BaseModel):
    name: str
    description: str | None = None


class TemplateRead(TemplateBase):
    id: int
    original_filename: str
    file_type: str
    preview_image_path: str | None = None
    page_width: float | None = None
    page_height: float | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TemplateUploadResponse(BaseModel):
    template: TemplateRead
    message: str
