from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class GenerationJob(Base):
    __tablename__ = "generation_jobs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    template_id: Mapped[int] = mapped_column(ForeignKey("certificate_templates.id"), nullable=False)
    attendee_import_id: Mapped[int] = mapped_column(ForeignKey("attendee_imports.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)
    total_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    success_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    failed_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    output_folder_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    generated_certificates: Mapped[list["GeneratedCertificate"]] = relationship(
        back_populates="generation_job", cascade="all, delete-orphan"
    )
