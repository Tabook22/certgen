from fastapi import APIRouter, HTTPException, status

router = APIRouter(prefix="/email", tags=["email"])


@router.post("/send", status_code=status.HTTP_501_NOT_IMPLEMENTED)
def send_email() -> None:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Email delivery is planned for a later phase.",
    )
