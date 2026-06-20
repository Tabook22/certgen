from fastapi import HTTPException, UploadFile, status

from app.utils.filenames import file_extension


def validate_upload_extension(file: UploadFile, allowed_extensions: set[str], label: str) -> str:
    extension = file_extension(file.filename or "")
    if extension not in allowed_extensions:
        allowed = ", ".join(sorted(allowed_extensions))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported {label} type. Allowed extensions: {allowed}.",
        )
    return extension
