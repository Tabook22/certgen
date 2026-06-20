from pathlib import Path
from typing import Any

import pandas as pd
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.config import Settings
from app.models.attendee import Attendee, AttendeeImport
from app.services.storage_service import StorageService
from app.utils.filenames import sanitize_filename
from app.utils.validation import validate_upload_extension


ALLOWED_ATTENDEE_EXTENSIONS = {"csv", "xls", "xlsx"}
REQUIRED_ATTENDEE_COLUMNS = {"full_name"}


class ExcelService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.storage = StorageService(settings)

    async def create_attendee_import(self, db: Session, upload: UploadFile) -> tuple[AttendeeImport, list[Attendee]]:
        extension = validate_upload_extension(upload, ALLOWED_ATTENDEE_EXTENSIONS, "attendee import")
        original_filename = sanitize_filename(upload.filename or f"attendees.{extension}")

        attendee_import = AttendeeImport(original_filename=original_filename, file_path="pending")
        db.add(attendee_import)
        db.flush()

        target_dir = self.settings.import_storage_path / str(attendee_import.id)
        relative_path = await self.storage.save_upload(upload, target_dir, f"attendees.{extension}")
        rows = self._read_attendee_rows(self.settings.storage_root / relative_path, extension)

        attendees = [self._build_attendee(attendee_import.id, row_number, row) for row_number, row in rows]
        attendee_import.file_path = relative_path
        attendee_import.total_rows = len(attendees)
        attendee_import.valid_rows = sum(1 for attendee in attendees if attendee.is_valid)
        attendee_import.invalid_rows = attendee_import.total_rows - attendee_import.valid_rows

        db.add_all(attendees)
        db.commit()
        db.refresh(attendee_import)
        for attendee in attendees:
            db.refresh(attendee)

        return attendee_import, attendees

    def _read_attendee_rows(self, path: Path, extension: str) -> list[tuple[int, dict[str, Any]]]:
        try:
            dataframe = pd.read_csv(path) if extension == "csv" else pd.read_excel(path)
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unable to parse attendee import file.",
            ) from exc

        normalized_columns = {str(column).strip().lower(): column for column in dataframe.columns}
        missing_columns = REQUIRED_ATTENDEE_COLUMNS - set(normalized_columns)
        if missing_columns:
            missing = ", ".join(sorted(missing_columns))
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required attendee column(s): {missing}.",
            )

        dataframe = dataframe.rename(columns={original: normalized for normalized, original in normalized_columns.items()})
        rows: list[tuple[int, dict[str, Any]]] = []
        for index, row in dataframe.iterrows():
            rows.append((int(index) + 2, {key: self._clean_value(value) for key, value in row.to_dict().items()}))
        return rows

    def _build_attendee(self, import_id: int, row_number: int, row: dict[str, Any]) -> Attendee:
        full_name = self._clean_text(row.get("full_name"))
        validation_error = None if full_name else "full_name is required."

        return Attendee(
            attendee_import_id=import_id,
            original_row_number=row_number,
            full_name=full_name,
            email=self._clean_text(row.get("email")),
            workshop_title=self._clean_text(row.get("workshop_title")),
            certificate_date=self._clean_text(row.get("certificate_date")),
            is_valid=validation_error is None,
            validation_error=validation_error,
            raw_metadata=row,
        )

    def _clean_value(self, value: Any) -> str | None:
        if pd.isna(value):
            return None
        return str(value).strip()

    def _clean_text(self, value: Any) -> str | None:
        cleaned = self._clean_value(value)
        return cleaned or None
