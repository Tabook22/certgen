from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import Settings
from app.models.attendee import Attendee, AttendeeImport
from app.models.field_mapping import FieldMapping
from app.models.generated_certificate import GeneratedCertificate
from app.models.generation_job import GenerationJob
from app.models.template import CertificateTemplate
from app.services.certificate_renderer import CertificateRenderer
from app.utils.filenames import sanitize_filename


class GenerationService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.renderer = CertificateRenderer()

    def create_generation_job(
        self,
        db: Session,
        template_id: int,
        attendee_import_id: int,
        workshop_title: str | None = None,
        certificate_date: str | None = None,
    ) -> GenerationJob:
        template = db.get(CertificateTemplate, template_id)
        attendee_import = db.get(AttendeeImport, attendee_import_id)
        if template is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found.")
        if attendee_import is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attendee import not found.")

        mappings = list(
            db.scalars(select(FieldMapping).where(FieldMapping.template_id == template_id).order_by(FieldMapping.field_key)).all()
        )
        if not mappings:
            mappings = self._default_mappings(template)

        attendees = list(
            db.scalars(
                select(Attendee)
                .where(Attendee.attendee_import_id == attendee_import_id, Attendee.is_valid.is_(True))
                .order_by(Attendee.original_row_number)
            ).all()
        )
        if not attendees:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No valid attendees found for this import.")

        job = GenerationJob(
            template_id=template_id,
            attendee_import_id=attendee_import_id,
            status="running",
            total_count=len(attendees),
        )
        db.add(job)
        db.flush()

        output_dir = self.settings.generated_storage_path / str(job.id)
        job.output_folder_path = output_dir.relative_to(self.settings.storage_root).as_posix()
        template_path = self.settings.storage_root / template.file_path
        default_values = {
            "workshop_title": workshop_title or "",
            "certificate_date": certificate_date or "",
        }

        for attendee in attendees:
            safe_name = sanitize_filename(attendee.full_name or f"attendee-{attendee.id}")
            relative_output = Path("generated") / str(job.id) / f"{attendee.id}-{safe_name}.pdf"
            output_path = self.settings.storage_root / relative_output
            certificate = GeneratedCertificate(
                generation_job_id=job.id,
                attendee_id=attendee.id,
                file_path=relative_output.as_posix(),
                status="generated",
            )
            try:
                self.renderer.render(template, attendee, mappings, template_path, output_path, default_values)
                job.success_count += 1
            except Exception as exc:
                certificate.status = "failed"
                certificate.error_message = str(exc)
                job.failed_count += 1
            db.add(certificate)

        job.status = "completed" if job.failed_count == 0 else "completed_with_errors"
        db.commit()
        db.refresh(job)
        return job

    def create_zip_for_job(self, db: Session, job_id: int) -> Path:
        job = db.get(GenerationJob, job_id)
        if job is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Generation job not found.")

        certificates = list(
            db.scalars(
                select(GeneratedCertificate).where(
                    GeneratedCertificate.generation_job_id == job_id,
                    GeneratedCertificate.status == "generated",
                )
            ).all()
        )
        if not certificates:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No generated certificates found for this job.")

        zip_path = self.settings.zip_storage_path / f"{job_id}.zip"
        zip_path.parent.mkdir(parents=True, exist_ok=True)
        with ZipFile(zip_path, "w", ZIP_DEFLATED) as archive:
            for certificate in certificates:
                certificate_path = self.settings.storage_root / certificate.file_path
                if certificate_path.exists():
                    archive.write(certificate_path, arcname=certificate_path.name)
        return zip_path

    def _default_mappings(self, template: CertificateTemplate) -> list[FieldMapping]:
        width = template.page_width or 1000
        height = template.page_height or 700
        return [
            FieldMapping(
                template_id=template.id,
                field_key="attendee_name",
                x=width * 0.2,
                y=height * 0.42,
                width=width * 0.6,
                height=height * 0.12,
                font_family="helv",
                font_size=max(width * 0.04, 24),
                font_color="#111827",
                alignment="center",
                visible=True,
            ),
            FieldMapping(
                template_id=template.id,
                field_key="workshop_title",
                x=width * 0.25,
                y=height * 0.55,
                width=width * 0.5,
                height=height * 0.08,
                font_family="tahoma",
                font_size=max(width * 0.028, 20),
                font_color="#111827",
                alignment="center",
                visible=True,
            ),
            FieldMapping(
                template_id=template.id,
                field_key="certificate_date",
                x=width * 0.35,
                y=height * 0.68,
                width=width * 0.3,
                height=height * 0.06,
                font_family="tahoma",
                font_size=max(width * 0.022, 16),
                font_color="#111827",
                alignment="center",
                visible=True,
            ),
        ]
