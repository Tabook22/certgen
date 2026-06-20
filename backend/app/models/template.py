from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class CertificateTemplate(Base):
    __tablename__ = "certificate_templates"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_type: Mapped[str] = mapped_column(String(50), nullable=False)
    preview_image_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    page_width: Mapped[float | None] = mapped_column(Float, nullable=True)
    page_height: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    assets: Mapped[list["TemplateAsset"]] = relationship(back_populates="template", cascade="all, delete-orphan")
    field_mappings: Mapped[list["FieldMapping"]] = relationship(back_populates="template", cascade="all, delete-orphan")


class TemplateAsset(Base):
    __tablename__ = "template_assets"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    template_id: Mapped[int] = mapped_column(ForeignKey("certificate_templates.id", ondelete="CASCADE"), nullable=False)
    asset_type: Mapped[str] = mapped_column(String(50), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    template: Mapped[CertificateTemplate] = relationship(back_populates="assets")
