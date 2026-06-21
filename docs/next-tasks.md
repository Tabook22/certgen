# Next Tasks for Cursor

This is a prioritized implementation backlog based on the project review in `docs/review-report.md`. Tasks are written for Cursor to execute incrementally. Prefer small PRs/commits and verify each task with tests or a manual acceptance step before moving on.

## Priority 0: Make the project runnable and testable

### P0.1 Add backend setup documentation and remove reliance on local venv

Files to touch:
- `README.md` or `docs/development.md`
- `.env.example`
- `backend/pyproject.toml`
- `requirements.txt` if keeping it

Recommendations:
- Document a clean setup flow:
  - `python3 -m venv .venv`
  - `source .venv/bin/activate`
  - `pip install -e ./backend` or `pip install -r requirements.txt`
  - `uvicorn app.main:app --reload` from `backend/`
  - `npm install && npm run dev` from `frontend/`
- Decide whether `backend/pyproject.toml` or root `requirements.txt` is the source of truth. Avoid maintaining two divergent dependency manifests.
- Add `.env.example` with at least:
  - `CERTGEN_DATABASE_URL=sqlite:///./app.db`
  - `CERTGEN_STORAGE_ROOT=storage`
  - `CERTGEN_CORS_ORIGINS=["http://localhost:5173"]`
  - `CERTGEN_MAX_UPLOAD_SIZE_BYTES=10485760`
- Ensure `backend/venv/` is not committed or required.

Acceptance criteria:
- A fresh clone can start the backend and frontend using only documented commands.
- `python -c "from app.main import app; print(app.title)"` works inside the documented backend environment.

### P0.2 Add backend tests foundation

Files to create:
- `backend/tests/conftest.py`
- `backend/tests/test_health.py`
- `backend/tests/test_upload_validation.py`
- `backend/tests/test_field_mappings.py`
- `backend/tests/test_generation.py`

Recommendations:
- Use pytest and FastAPI `TestClient`.
- Use temporary SQLite database files and temporary storage roots per test.
- Override `get_settings()` and `get_db()` dependencies where needed.
- Add `pytest` and `httpx` to backend dependencies.

Acceptance criteria:
- `pytest` runs from `backend/` and passes.
- Tests do not write to real `backend/app.db` or real `backend/storage/`.

## Priority 1: Database migrations and schema hardening

### P1.1 Add Alembic environment and initial migration

Files to create/update:
- `backend/alembic/env.py`
- `backend/alembic/script.py.mako`
- `backend/alembic/versions/<revision>_initial_schema.py`
- `backend/alembic.ini`
- `backend/app/database.py`

Recommendations:
- Import `Base.metadata` and all models in Alembic `env.py`.
- Configure Alembic to read `CERTGEN_DATABASE_URL` or app settings instead of hardcoding only `sqlite:///./app.db`.
- Generate an initial migration for current tables.
- Stop relying on unconditional `Base.metadata.create_all()` at startup. Either remove it or guard it behind a setting such as `CERTGEN_AUTO_CREATE_TABLES=true` for local-only development.

Acceptance criteria:
- `alembic upgrade head` creates all tables in a blank SQLite database.
- Backend startup does not silently mutate production schemas outside migrations.

### P1.2 Add constraints for field mappings and statuses

Files to touch:
- `backend/app/models/field_mapping.py`
- `backend/app/models/generation_job.py`
- `backend/app/models/generated_certificate.py`
- `backend/app/models/template.py`
- New Alembic migration

Recommendations:
- Add unique constraint on `(template_id, field_key)` in `field_mappings`.
- Add unique constraint on `(template_id, asset_type)` if only one `stamp` and one `signature` are supported per template.
- Add check constraints or enums for known statuses.
- Add indexes where listing/filtering occurs frequently, e.g. `attendees.attendee_import_id`, `generated_certificates.generation_job_id`.
- Enable SQLite foreign key enforcement on connection.

Acceptance criteria:
- Duplicate field mappings for the same template/field cannot be inserted.
- Cascades work under SQLite with `PRAGMA foreign_keys=ON`.
- Tests cover duplicate field mappings and cascades.

## Priority 2: File upload and storage security

### P2.1 Replace extension-only upload validation with content validation

Files to touch:
- `backend/app/utils/validation.py`
- `backend/app/services/template_service.py`
- `backend/app/services/excel_service.py`
- `backend/app/services/storage_service.py`
- Tests under `backend/tests/`

Recommendations:
- Keep extension checks as the first filter, but add parser-level validation after saving to a temporary/quarantine path.
- For images, use Pillow to open and `verify()`, then reopen to read dimensions.
- For PDFs, use PyMuPDF to open, reject encrypted PDFs, reject zero-page PDFs, and consider rejecting multi-page PDFs for MVP.
- For `.xlsx`, check it is a valid zip/openpyxl workbook before parsing.
- If validation fails, delete the uploaded file and roll back the DB transaction.
- Restrict attendee import formats to `.xlsx` unless CSV/XLS support is intentionally accepted and documented.

Acceptance criteria:
- A renamed non-image/non-PDF file is rejected as a template.
- A malformed workbook is rejected as an attendee import.
- Failed validation leaves no orphaned file in storage.

### P2.2 Use safe storage path resolution for all reads/downloads

Files to touch:
- `backend/app/api/routes/templates.py`
- `backend/app/api/routes/certificates.py`
- `backend/app/services/generation_service.py`
- `backend/app/services/storage_service.py`

Recommendations:
- Use `StorageService.resolve_storage_path()` for template previews, certificate downloads, and ZIP creation input files.
- Make `resolve_storage_path()` the only approved way to turn stored relative paths into filesystem paths.
- Add tests that manually insert a `../` path in the DB and verify downloads reject it.

Acceptance criteria:
- No route directly joins `settings.storage_root / db_file_path`.
- Path traversal attempts from stored paths return 400 and do not read files outside storage root.

### P2.3 Stop exposing internal storage paths through public API schemas

Files to touch:
- `backend/app/schemas/template.py`
- `backend/app/schemas/generation.py`
- `frontend/src/types/template.ts`
- `frontend/src/types/generation.ts`
- Frontend pages that consume those fields

Recommendations:
- Remove `file_path` and internal `preview_image_path` from public API responses.
- Add explicit URL fields only if useful, e.g. `preview_url`, `download_url`, `zip_download_url`.
- Alternatively keep URLs generated only in frontend API helpers using resource IDs.

Acceptance criteria:
- API responses do not expose filesystem layout.
- Frontend still displays previews and download links via endpoint URLs.

## Priority 3: Complete MVP feature gaps

### P3.1 Implement template asset upload/list/delete

Files to touch/create:
- `backend/app/api/routes/templates.py` or new `backend/app/api/routes/template_assets.py`
- `backend/app/services/template_service.py` or new `backend/app/services/asset_service.py`
- `backend/app/schemas/template.py`
- `backend/app/models/template.py`
- `frontend/src/api/templates.ts`
- `frontend/src/types/template.ts`
- `frontend/src/pages/TemplateDesignerPage.tsx` or a dedicated assets component

Recommendations:
- Implement:
  - `POST /api/v1/templates/{template_id}/assets`
  - `GET /api/v1/templates/{template_id}/assets`
  - `DELETE /api/v1/templates/{template_id}/assets/{asset_id}`
- Restrict `asset_type` to `stamp` and `signature` for MVP.
- Validate asset content as PNG/JPG/JPEG.
- Store assets under `storage/templates/<template_id>/stamp.<ext>` and `signature.<ext>` or similar.
- Decide whether uploading a new asset replaces the old one or creates a new version. For MVP, replacement is simpler.

Acceptance criteria:
- Admin can upload a stamp and signature for a template.
- Assets are listed in the API and visible in the frontend designer.
- Invalid asset files are rejected.

### P3.2 Add stamp/signature field support in frontend and backend

Files to touch:
- `frontend/src/types/fieldMapping.ts`
- `frontend/src/pages/TemplateDesignerPage.tsx`
- `frontend/src/components/TemplateCanvas.tsx`
- `frontend/src/components/FieldControlPanel.tsx`
- `backend/app/schemas/field_mapping.py`
- `backend/app/services/certificate_renderer.py`
- `backend/app/services/generation_service.py`

Recommendations:
- Extend field keys to include `stamp` and `signature`.
- Treat text and image fields differently in controls:
  - Text fields need font family/size/color/alignment.
  - Image fields need x/y/width/height/visible only.
- In `CertificateRenderer`, load template assets and insert them using PyMuPDF `page.insert_image()` with the saved rectangle.
- Make missing optional image assets non-fatal when their mapping is hidden; decide whether visible-but-missing assets should fail the job or skip with warning.

Acceptance criteria:
- Manual acceptance test can position attendee name, workshop title, date, stamp, and signature.
- Generated PDF contains stamp and signature images when assets are present and fields are visible.

### P3.3 Fix designer drag coordinate calculation

Files to touch:
- `frontend/src/components/TemplateCanvas.tsx`
- Possibly `frontend/src/styles/index.css`

Problem:
- `handlePointerMove()` uses the field button bounds to calculate template scaling. It should use the full template stage/image bounds.

Recommendations:
- Add a `ref` to the `.template-stage` container.
- Compute `scaleX = templateWidth / stageBounds.width` and `scaleY = templateHeight / stageBounds.height`.
- Capture pointer on pointer down for smoother dragging.
- Clamp `x` and `y` so fields cannot move outside template bounds.

Acceptance criteria:
- Dragging a field tracks pointer movement accurately at different viewport sizes.
- Saved coordinates match the visual preview and backend PDF output.

### P3.4 Implement missing MVP endpoints

Files to touch:
- `backend/app/api/routes/templates.py`
- `backend/app/api/routes/attendees.py`
- `backend/app/api/routes/field_mappings.py`
- Services as needed

Implement:
- `DELETE /api/v1/templates/{template_id}`
- `PATCH /api/v1/templates/{template_id}/field-mappings/{field_key}`
- `GET /api/v1/attendee-imports/{import_id}`
- `DELETE /api/v1/attendee-imports/{import_id}`

Recommendations:
- For delete endpoints, delete database rows and associated storage directories/files safely.
- Return 404 for child collection routes when the parent import/template/job does not exist.
- Add tests for all missing endpoints.

Acceptance criteria:
- API endpoint list matches `docs/architecture.md` for MVP endpoints, or docs are updated to match intentional scope.

## Priority 4: Generation reliability and downloads

### P4.1 Improve generation record lifecycle

Files to touch:
- `backend/app/services/generation_service.py`
- `backend/app/services/certificate_renderer.py`
- Tests

Recommendations:
- Create `GeneratedCertificate` records with `pending` status.
- Render to a temporary path first.
- Move/rename to final path only after successful render.
- Set `status="generated"` only after the final PDF exists and has non-zero size.
- Set `job.status="failed"` if job-level setup fails after job creation.

Acceptance criteria:
- Failed renders produce failed records with clear error messages.
- Successful records always point to existing non-empty PDF files.

### P4.2 Make ZIP creation strict and transparent

Files to touch:
- `backend/app/services/generation_service.py`
- `backend/app/api/routes/generation.py`
- Tests

Recommendations:
- Count how many files are added to the ZIP.
- If no files are added, raise 404/409 instead of returning an empty ZIP.
- If some generated files are missing, either fail with a clear 409 or include a manifest warning file in the ZIP.
- Consider regenerating ZIP only when inputs changed, or always generating fresh with clear semantics.

Acceptance criteria:
- ZIP contains exactly generated certificate PDFs for the job.
- Missing files are surfaced clearly.

### P4.3 Add attendee details to certificate listings

Files to touch:
- `backend/app/models/generated_certificate.py`
- `backend/app/schemas/generation.py`
- `backend/app/api/routes/certificates.py`
- `backend/app/api/routes/generation.py`
- `frontend/src/types/generation.ts`
- `frontend/src/pages/CertificatesPage.tsx`

Recommendations:
- Add relationship from `GeneratedCertificate` to `Attendee`.
- Return attendee name/email in certificate list response or add a dedicated list view schema.
- Avoid returning raw file paths.

Acceptance criteria:
- Certificates page shows meaningful recipient names instead of only IDs.

## Priority 5: Frontend workflow polish

### P5.1 Replace placeholder pages with real workflows

Files to touch:
- `frontend/src/pages/TemplatesPage.tsx`
- `frontend/src/pages/AttendeeImportPage.tsx`
- `frontend/src/pages/EmailPage.tsx` if kept visible
- `frontend/src/App.tsx`
- `frontend/src/components/Layout.tsx`

Recommendations:
- Templates page: list templates, upload new template, open designer, delete template.
- Attendee imports page: upload import, list imports, view all rows/validation errors, delete import.
- Hide Email page from navigation until implemented, or clearly mark it as future only.

Acceptance criteria:
- The full MVP workflow can be completed without relying only on the dashboard.

### P5.2 Add frontend API support for attendee row browsing

Files to touch:
- `frontend/src/api/attendees.ts`
- `frontend/src/pages/AttendeeImportPage.tsx`
- `frontend/src/components/AttendeeTable.tsx`

Recommendations:
- Add `listAttendees(importId)` API function.
- Show all attendees for selected import, with validation errors.
- Add loading and empty states.

Acceptance criteria:
- User can inspect all valid and invalid rows after upload.

### P5.3 Improve frontend forms and error UX

Files to touch:
- `frontend/src/components/UploadBox.tsx`
- `frontend/src/components/FieldControlPanel.tsx`
- `frontend/src/api/client.ts`

Recommendations:
- Do not clear the selected file after a failed upload.
- Display structured FastAPI validation errors, not only string `detail` values.
- Validate numeric field controls client-side before save.
- Add `download` attributes to download links where appropriate.

Acceptance criteria:
- User can recover from failed uploads without reselecting files unnecessarily.
- Backend validation errors are understandable in the UI.

## Priority 6: Deployment readiness

### P6.1 Add Docker and local production-like compose

Files to create:
- `backend/Dockerfile` or root `Dockerfile.backend`
- `frontend/Dockerfile` or root `Dockerfile.frontend`
- `docker-compose.yml`
- `docs/deployment.md`

Recommendations:
- Backend container runs Uvicorn/Gunicorn and uses a mounted volume for SQLite and storage.
- Frontend builds static assets and serves them with nginx or another static server.
- Compose should define persistent volumes for database and storage.
- Document backup/restore for SQLite and storage together.

Acceptance criteria:
- `docker compose up --build` starts the app locally.
- Uploaded/generated files persist across container restarts.

### P6.2 Add production configuration hardening

Files to touch:
- `backend/app/config.py`
- `backend/app/main.py`
- `.env.example`
- `docs/deployment.md`

Recommendations:
- Make `storage_root` and database path absolute in production deployments.
- Document CORS origin configuration.
- Add structured logging.
- Add reverse-proxy upload size guidance matching `CERTGEN_MAX_UPLOAD_SIZE_BYTES`.
- Add optional authentication plan before public deployment.

Acceptance criteria:
- Deployment docs explain every required environment variable.
- Production startup does not depend on current working directory.

## Priority 7: Optional future improvements

### P7.1 Background generation for larger batches

Recommendations:
- Use FastAPI `BackgroundTasks` for a simple intermediate step, or Celery/RQ/Arq for a real worker queue.
- Return job immediately with `pending/running` status.
- Poll job status from frontend.

### P7.2 React Router and React Query

Recommendations:
- Add `react-router-dom` for real routes.
- Add `@tanstack/react-query` for caching, loading states, invalidation after upload/generate/delete, and retry behavior.

### P7.3 Authentication before shared deployment

Recommendations:
- If more than one trusted local admin uses the app, add authentication and authorization before exposing it on a network.
- At minimum, put the app behind an authenticated reverse proxy for internal deployments.

## Suggested implementation order

1. P0.1: Make backend setup reproducible.
2. P0.2: Add test foundation.
3. P1.1: Add Alembic and initial migration.
4. P2.1/P2.2/P2.3: Harden uploads and storage paths.
5. P3.1/P3.2/P3.3: Complete stamp/signature and designer correctness.
6. P3.4: Fill endpoint gaps.
7. P4.1/P4.2/P4.3: Improve generation/download reliability.
8. P5.1/P5.2/P5.3: Polish frontend workflow.
9. P6.1/P6.2: Prepare deployment.

## Cursor guidance

When implementing these tasks:
- Keep changes scoped to one task at a time.
- Add or update tests with every backend behavior change.
- Prefer service-level functions for file/database operations; keep routes thin.
- Do not expose filesystem paths in frontend contracts.
- Use temporary files and cleanup on failure for upload/generation code.
- Run these checks before handing off:
  - Backend: `pytest`
  - Backend: `python -m compileall app`
  - Frontend: `npm run build`
  - Manual: upload template, save mappings, upload attendees, generate PDFs, download PDF and ZIP.
