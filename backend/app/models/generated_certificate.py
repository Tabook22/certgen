from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class GeneratedCertificate(Base):
    __tablename__ = "generated_certificates"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    generation_job_id: Mapped[int] = mapped_column(ForeignKey("generation_jobs.id", ondelete="CASCADE"), nullable=False)
    attendee_id: Mapped[int] = mapped_column(ForeignKey("attendees.id"), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    generation_job: Mapped["GenerationJob"] = relationship(back_populates="generated_certificates")
    email_logs: Mapped[list["EmailLog"]] = relationship(back_populates="generated_certificate", cascade="all, delete-orphan")
