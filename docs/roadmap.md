# Certificate Generator Roadmap

## Overview

This roadmap breaks the Certificate Generator application into practical implementation phases.

The goal is to build a usable MVP first, then add polish, background processing, email delivery, and production-readiness later.

## Phase 1: Project Setup

### Goals

- Create the project folder structure.
- Set up FastAPI backend.
- Set up React frontend.
- Confirm both applications run locally.

### Tasks

1. Create root project structure.
2. Create `backend/` folder.
3. Create `frontend/` folder.
4. Add FastAPI app entrypoint.
5. Add React Vite app.
6. Add backend dependency file.
7. Add frontend dependency file.
8. Add `.env.example`.
9. Add initial README.

### Backend dependencies

Recommended packages:

```text
fastapi
uvicorn[standard]
sqlmodel
alembic
pydantic-settings
python-multipart
pymupdf
pillow
pandas
openpyxl
pytest
httpx
```

### Frontend dependencies

Recommended packages:

```text
react
react-dom
vite
typescript
axios
@tanstack/react-query
react-router-dom
```

### Completion Criteria

- Backend starts successfully.
- Frontend starts successfully.
- `GET /health` returns a successful response.

## Phase 2: Database Foundation

### Goals

- Add SQLite database connection.
- Add database models.
- Add database migrations.

### Tasks

1. Implement database connection.
2. Implement session dependency.
3. Create template model.
4. Create template asset model.
5. Create field mapping model.
6. Create attendee import model.
7. Create attendee model.
8. Create generation job model.
9. Create generated certificate model.
10. Create email log model for future use.
11. Configure Alembic.
12. Create initial migration.
13. Run migration locally.

### Completion Criteria

- SQLite database is created.
- All required tables exist.
- Backend can import all models without circular import errors.

## Phase 3: Template Upload and Preview

### Goals

- Upload certificate templates.
- Save template files safely.
- Generate previews for frontend display.

### Tasks

1. Create storage service.
2. Create filename sanitization utility.
3. Implement template upload endpoint.
4. Validate uploaded file type.
5. Save original uploaded file.
6. Create database row for uploaded template.
7. Generate preview image.
8. Implement template list endpoint.
9. Implement template detail endpoint.
10. Implement template preview endpoint.
11. Add backend tests for template upload.

### Completion Criteria

- Admin can upload PNG/JPG/PDF template.
- Backend stores metadata.
- Backend stores original file.
- Backend returns a preview image.

## Phase 4: Template Field Mapping

### Goals

- Save and retrieve field positions.
- Support required certificate fields.
- Build visual designer in frontend.

### Tasks

1. Implement field mapping schemas.
2. Implement get field mappings endpoint.
3. Implement save all field mappings endpoint.
4. Implement update one field mapping endpoint.
5. Build frontend templates page.
6. Build template upload UI.
7. Build template designer page.
8. Build certificate preview canvas.
9. Add draggable field boxes.
10. Add field style controls.
11. Convert frontend pixel positions to template coordinates.
12. Save mappings to backend.
13. Reload saved mappings correctly.

### Completion Criteria

- Admin can position name, workshop title, date, stamp, and signature fields.
- Field mappings persist after page reload.
- Saved coordinates can be used by backend generation.

## Phase 5: Excel Attendee Import

### Goals

- Upload attendee Excel sheet.
- Parse attendees.
- Validate required data.
- Preview rows in frontend.

### Tasks

1. Create attendee import schemas.
2. Create Excel parsing service.
3. Validate `.xlsx` file extension and content.
4. Parse required and optional columns.
5. Store attendee import metadata.
6. Store attendee rows.
7. Mark invalid rows with error messages.
8. Implement upload attendee import endpoint.
9. Implement list attendee imports endpoint.
10. Implement attendee import detail endpoint.
11. Implement list attendees for import endpoint.
12. Build attendee import frontend page.
13. Build attendee table component.

### Required Excel columns

```text
full_name
```

### Optional Excel columns

```text
email
workshop_title
certificate_date
```

### Completion Criteria

- Admin can upload `.xlsx` file.
- Backend parses attendee rows.
- Frontend displays valid and invalid rows.
- Invalid rows do not block valid rows.

## Phase 6: Certificate PDF Generation

### Goals

- Generate one PDF certificate per valid attendee.
- Save generated PDFs.
- Track job status and output records.

### Tasks

1. Create certificate renderer service.
2. Implement rendering text onto template.
3. Implement rendering stamp image.
4. Implement rendering signature image.
5. Implement safe output filename generation.
6. Create generation service.
7. Create generation job record.
8. Load valid attendees for selected import.
9. Generate PDF for each attendee.
10. Store generated certificate records.
11. Track success and failure counts.
12. Update job status.
13. Add backend tests for rendering.
14. Add backend tests for batch generation.

### Completion Criteria

- Generation job creates one PDF per valid attendee.
- Generated files exist on disk.
- Database records match generated files.
- Failed attendee generation is recorded without stopping the whole batch.

## Phase 7: Certificate Downloads

### Goals

- List generated certificates.
- Download individual PDFs.
- Download all certificates for a job as ZIP.

### Tasks

1. Implement list generation jobs endpoint.
2. Implement generation job detail endpoint.
3. Implement list certificates for job endpoint.
4. Implement certificate detail endpoint.
5. Implement individual certificate download endpoint.
6. Implement ZIP generation helper.
7. Implement job ZIP download endpoint.
8. Build frontend generation page.
9. Build frontend certificates page.
10. Add download buttons.

### Completion Criteria

- Admin can see generated jobs.
- Admin can download one PDF.
- Admin can download ZIP file containing all PDFs for a job.

## Phase 8: Frontend Workflow Polish

### Goals

- Make the application usable end-to-end.
- Improve navigation and feedback.

### Tasks

1. Add shared layout component.
2. Add navigation menu.
3. Add dashboard page.
4. Add loading states.
5. Add error states.
6. Add success messages.
7. Add empty states.
8. Add basic form validation.
9. Add confirmation before delete actions.
10. Add job summary cards.

### Completion Criteria

- Admin can complete the full MVP workflow without using curl or direct API calls.
- UI clearly shows errors and successful actions.

## Phase 9: Optional Email Delivery

### Goals

- Send generated certificates by email.
- Track delivery status.

### Tasks

1. Add SMTP settings to backend configuration.
2. Create email service.
3. Create email request schemas.
4. Implement send one certificate endpoint.
5. Implement send whole job endpoint.
6. Store email logs.
7. Build email page.
8. Add subject/body editor.
9. Add send status display.
10. Add retry failed email option.

### Completion Criteria

- Admin can send one generated certificate to one email address.
- Admin can send all certificates from a job to attendees with email addresses.
- Email logs show sent and failed statuses.

## Phase 10: Production Readiness

### Goals

- Improve reliability, security, deployment, and maintainability.

### Tasks

1. Add upload size limits.
2. Harden file validation.
3. Add structured logging.
4. Add better error handling.
5. Add background job processing for large batches.
6. Add authentication if required.
7. Add Dockerfile.
8. Add docker-compose file.
9. Add deployment documentation.
10. Add backup strategy for SQLite and storage directory.
11. Add optional PostgreSQL support.
12. Add optional object storage support.

### Completion Criteria

- Application can be deployed reliably.
- Uploads and generated files are persisted safely.
- Large generation jobs do not block HTTP requests.

## Recommended MVP Build Order

Build in this order:

1. Backend health endpoint.
2. Database models.
3. Template upload.
4. Template preview.
5. Field mappings API.
6. Frontend template upload.
7. Frontend designer.
8. Excel import API.
9. Frontend attendee import.
10. Certificate renderer.
11. Generation API.
12. Certificate download API.
13. Frontend generation page.
14. Frontend certificates page.
15. ZIP download.

## MVP Acceptance Test

The MVP should pass this manual test:

1. Start backend.
2. Start frontend.
3. Upload a certificate template.
4. Open the template in designer.
5. Position attendee name, workshop title, date, stamp, and signature.
6. Save field mappings.
7. Upload an Excel file with at least three attendees.
8. Generate certificates.
9. Confirm three PDFs are created.
10. Download one PDF.
11. Download ZIP for the generation job.
12. Open the PDFs and confirm each attendee name appears correctly.
