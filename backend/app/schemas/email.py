from datetime import datetime

from pydantic import BaseModel, ConfigDict


class EmailLogRead(BaseModel):
    id: int
    generated_certificate_id: int
    recipient_email: str
    status: str
    error_message: str | None = None
    sent_at: datetime | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
