from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class FieldMapping(Base):
    __tablename__ = "field_mappings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    template_id: Mapped[int] = mapped_column(ForeignKey("certificate_templates.id", ondelete="CASCADE"), nullable=False)
    field_key: Mapped[str] = mapped_column(String(100), nullable=False)
    x: Mapped[float] = mapped_column(Float, nullable=False)
    y: Mapped[float] = mapped_column(Float, nullable=False)
    width: Mapped[float] = mapped_column(Float, nullable=False)
    height: Mapped[float] = mapped_column(Float, nullable=False)
    font_family: Mapped[str | None] = mapped_column(String(100), nullable=True)
    font_size: Mapped[float | None] = mapped_column(Float, nullable=True)
    font_color: Mapped[str | None] = mapped_column(String(20), nullable=True)
    font_weight: Mapped[str | None] = mapped_column(String(50), nullable=True)
    alignment: Mapped[str | None] = mapped_column(String(50), nullable=True)
    visible: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    template: Mapped["CertificateTemplate"] = relationship(back_populates="field_mappings")
