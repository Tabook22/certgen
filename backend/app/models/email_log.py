from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class EmailLog(Base):
    __tablename__ = "email_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    generated_certificate_id: Mapped[int] = mapped_column(
        ForeignKey("generated_certificates.id", ondelete="CASCADE"), nullable=False
    )
    recipient_email: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    generated_certificate: Mapped["GeneratedCertificate"] = relationship(back_populates="email_logs")
