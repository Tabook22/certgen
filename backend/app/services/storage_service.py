from pathlib import Path

from fastapi import HTTPException, UploadFile, status

from app.config import Settings
from app.utils.filenames import sanitize_filename


class StorageService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def ensure_storage_dirs(self) -> None:
        for path in (
            self.settings.template_storage_path,
            self.settings.import_storage_path,
            self.settings.generated_storage_path,
            self.settings.zip_storage_path,
        ):
            path.mkdir(parents=True, exist_ok=True)

    def resolve_storage_path(self, relative_path: str) -> Path:
        storage_root = self.settings.storage_root.resolve()
        target = (storage_root / relative_path).resolve()
        if storage_root not in target.parents and target != storage_root:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid storage path.")
        return target

    async def save_upload(self, upload: UploadFile, target_dir: Path, stored_filename: str) -> str:
        safe_filename = sanitize_filename(stored_filename)
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / safe_filename

        written = 0
        try:
            with target_path.open("wb") as destination:
                while chunk := await upload.read(1024 * 1024):
                    written += len(chunk)
                    if written > self.settings.max_upload_size_bytes:
                        target_path.unlink(missing_ok=True)
                        raise HTTPException(
                            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                            detail="Upload exceeds the configured size limit.",
                        )
                    destination.write(chunk)
        finally:
            await upload.close()

        return target_path.relative_to(self.settings.storage_root).as_posix()
