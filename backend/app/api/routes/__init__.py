from fastapi import APIRouter

from app.api.routes import attendees, certificates, email, field_mappings, generation, templates

api_router = APIRouter()
api_router.include_router(templates.router)
api_router.include_router(attendees.router)
api_router.include_router(field_mappings.router)
api_router.include_router(generation.router)
api_router.include_router(certificates.router)
api_router.include_router(email.router)

__all__ = ["api_router"]
