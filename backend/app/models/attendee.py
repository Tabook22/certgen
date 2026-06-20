from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class AttendeeImport(Base):
    __tablename__ = "attendee_imports"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    total_rows: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    valid_rows: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    invalid_rows: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    attendees: Mapped[list["Attendee"]] = relationship(back_populates="attendee_import", cascade="all, delete-orphan")


class Attendee(Base):
    __tablename__ = "attendees"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    attendee_import_id: Mapped[int] = mapped_column(ForeignKey("attendee_imports.id", ondelete="CASCADE"), nullable=False)
    original_row_number: Mapped[int] = mapped_column(Integer, nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    workshop_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    certificate_date: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_valid: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    validation_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    attendee_import: Mapped[AttendeeImport] = relationship(back_populates="attendees")
