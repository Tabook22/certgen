from pathlib import Path

from fastapi import UploadFile
from PIL import Image
from sqlalchemy.orm import Session

from app.config import Settings
from app.models.template import CertificateTemplate
from app.services.storage_service import StorageService
from app.utils.filenames import file_extension, sanitize_filename
from app.utils.validation import validate_upload_extension

try:
    import fitz
except ImportError:  # pragma: no cover - dependency is declared for runtime use.
    fitz = None


ALLOWED_TEMPLATE_EXTENSIONS = {"pdf", "png", "jpg", "jpeg"}


class TemplateService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.storage = StorageService(settings)

    async def create_template(
        self,
        db: Session,
        upload: UploadFile,
        name: str | None,
        description: str | None,
    ) -> CertificateTemplate:
        extension = validate_upload_extension(upload, ALLOWED_TEMPLATE_EXTENSIONS, "template")
        original_filename = sanitize_filename(upload.filename or f"template.{extension}")

        template = CertificateTemplate(
            name=name or Path(original_filename).stem,
            description=description,
            original_filename=original_filename,
            file_path="pending",
            file_type=extension,
        )
        db.add(template)
        db.flush()

        stored_filename = f"original.{extension}"
        target_dir = self.settings.template_storage_path / str(template.id)
        relative_path = await self.storage.save_upload(upload, target_dir, stored_filename)
        absolute_path = self.settings.storage_root / relative_path

        width, height = self._read_template_dimensions(absolute_path, extension)
        preview_path = self._create_preview_image(absolute_path, target_dir, extension)
        template.file_path = relative_path
        template.preview_image_path = preview_path
        template.page_width = width
        template.page_height = height

        db.commit()
        db.refresh(template)
        return template

    def _read_template_dimensions(self, path: Path, extension: str) -> tuple[float | None, float | None]:
        if extension in {"png", "jpg", "jpeg"}:
            with Image.open(path) as image:
                return float(image.width), float(image.height)

        if extension == "pdf" and fitz is not None:
            with fitz.open(path) as document:
                if document.page_count == 0:
                    return None, None
                rect = document[0].rect
                return float(rect.width), float(rect.height)

        return None, None

    def _create_preview_image(self, path: Path, target_dir: Path, extension: str) -> str | None:
        if extension in {"png", "jpg", "jpeg"}:
            return path.relative_to(self.settings.storage_root).as_posix()

        if extension == "pdf" and fitz is not None:
            preview_path = target_dir / "preview.png"
            with fitz.open(path) as document:
                if document.page_count == 0:
                    return None
                page = document[0]
                pixmap = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
                pixmap.save(preview_path)
            return preview_path.relative_to(self.settings.storage_root).as_posix()

        return None
