# Certificate Agent Project Review Report

Review date: 2026-06-21
Workspace: `/home/nasser/hermes-work/certificate-agent`

## Executive summary

The project has a solid early-MVP skeleton: the backend is split into FastAPI routes, SQLAlchemy models, Pydantic schemas, services, and utilities; the frontend is split into pages, components, API modules, and types; template upload, attendee import, field mapping, generation, and downloads are partially implemented.

However, the implementation is not yet deployment-ready and does not satisfy the full MVP acceptance criteria in `docs/specification.md`. The highest-risk gaps are database migrations being absent, weak upload/content validation, no template asset support for stamp/signature, no rendering of stamp/signature fields, limited endpoint coverage, no tests, no production/deployment configuration, and backend dependencies not being installed in the checked-in `backend/venv`.

## Verification performed

- Reviewed specification and architecture: `docs/specification.md`, `docs/architecture.md`, `docs/roadmap.md`.
- Reviewed tracked project files with `git ls-files`.
- Reviewed backend routes, models, schemas, services, utilities, and configuration.
- Reviewed frontend pages, components, API clients, and types.
- Ran `npm run build` in `frontend/`: passed.
- Ran `python3 -m compileall app` in `backend/`: passed syntax compilation.
- Attempted to import the backend app with both `venv/bin/python` and system `python3`: both failed with `ModuleNotFoundError: No module named 'fastapi'`, indicating dependencies are not installed in the active backend environment.
- Confirmed missing project files/directories: `backend/alembic/`, `backend/alembic/versions/`, `backend/tests/`, `Dockerfile`, `docker-compose.yml`, `.env.example`, and `README.md` do not exist.

## What is good

### Backend structure

- The backend follows the intended layered structure from `docs/architecture.md`:
  - Routes under `backend/app/api/routes/`.
  - Models under `backend/app/models/`.
  - Schemas under `backend/app/schemas/`.
  - Services under `backend/app/services/`.
  - Utilities under `backend/app/utils/`.
- `backend/app/main.py:15` uses FastAPI lifespan startup to create database tables and ensure storage directories.
- `backend/app/database.py:19` provides a conventional SQLAlchemy session dependency.
- Business logic is mostly kept out of routes and placed in services, for example `TemplateService`, `ExcelService`, and `GenerationService`.
- Storage path resolution has a path traversal guard in `backend/app/services/storage_service.py:22`.
- Upload size is streamed and limited in `backend/app/services/storage_service.py:34` instead of reading the entire upload into memory.
- Basic Pydantic request/response schemas exist and use `ConfigDict(from_attributes=True)` for ORM serialization.
- Generation failures are captured per certificate in `backend/app/services/generation_service.py:81`, which aligns with the reliability requirement to avoid failing an entire batch because one attendee fails.

### Frontend structure

- The frontend follows the intended separation in `docs/architecture.md`:
  - API modules under `frontend/src/api/`.
  - Components under `frontend/src/components/`.
  - Pages under `frontend/src/pages/`.
  - Types under `frontend/src/types/`.
- `frontend/src/api/client.ts:3` centralizes Axios configuration and supports `VITE_API_BASE_URL`.
- The dashboard provides the basic upload workflow for templates and attendee imports in `frontend/src/pages/DashboardPage.tsx`.
- The designer page has a usable first-pass visual field positioning workflow in `frontend/src/pages/TemplateDesignerPage.tsx` and `frontend/src/components/TemplateCanvas.tsx`.
- The frontend TypeScript production build passes.

### Database model coverage

- Models exist for the tables called out in the architecture: templates/assets, field mappings, attendee imports/attendees, generation jobs, generated certificates, and email logs.
- Metadata fields called out in the specification are mostly represented:
  - Template metadata: `backend/app/models/template.py:12`.
  - Attendee import and rows: `backend/app/models/attendee.py:12` and `backend/app/models/attendee.py:26`.
  - Generation jobs and outputs: `backend/app/models/generation_job.py:12` and `backend/app/models/generated_certificate.py:12`.

## Critical findings

### 1. Alembic migrations are configured but absent

Severity: Critical

Evidence:
- `backend/alembic.ini` exists.
- `backend/alembic/` and `backend/alembic/versions/` do not exist.
- Runtime table creation uses `Base.metadata.create_all(bind=engine)` in `backend/app/database.py:27`.

Why this matters:
- The specification explicitly prefers Alembic migrations (`docs/specification.md:24`).
- The roadmap Phase 2 requires Alembic configuration and an initial migration (`docs/roadmap.md:89`).
- `create_all()` hides schema drift during development and is not a safe production migration strategy.

Recommendation:
- Add a real Alembic environment under `backend/alembic/`.
- Generate an initial migration for all current models.
- Replace startup `create_all()` with migrations for deployed environments, or gate `create_all()` behind a local-development setting only.

### 2. Backend environment is not runnable from the checked-in setup

Severity: Critical

Evidence:
- `requirements.txt` and `backend/pyproject.toml` list FastAPI and related dependencies.
- Attempting to import `app.main` failed with `ModuleNotFoundError: No module named 'fastapi'` under both `backend/venv/bin/python` and system `python3`.
- The checked-in `backend/venv` exists in the workspace but does not contain FastAPI.

Why this matters:
- A new developer or deployment process cannot reliably start the backend without undocumented setup steps.
- `backend/venv` should not be committed or relied on; `.gitignore` ignores `venv/`, but the working tree still contains a local venv directory.

Recommendation:
- Remove local virtualenv artifacts from the workspace/repo if tracked or accidentally copied.
- Add setup documentation and `.env.example`.
- Standardize on one dependency source, preferably `backend/pyproject.toml`, and document `python -m venv .venv && pip install -e backend` or equivalent.

### 3. Upload validation trusts file extension and does not validate content type or file signatures

Severity: High

Evidence:
- `backend/app/utils/validation.py:6` validates only the filename extension.
- Template upload allows `pdf`, `png`, `jpg`, `jpeg` based only on extension in `backend/app/services/template_service.py:19`.
- Attendee import allows `csv`, `xls`, and `xlsx` based only on extension in `backend/app/services/excel_service.py:15`, while the MVP specification only requires `.xlsx` (`docs/specification.md:136`).

Why this matters:
- A malicious or malformed file can be uploaded with a safe extension.
- The backend later passes files to Pillow, PyMuPDF, pandas, and openpyxl. Those parsers should only receive files that pass stricter validation.
- The implementation goes beyond MVP by accepting CSV/XLS without a matching spec update or security review.

Recommendation:
- Validate file content after saving, not just extension:
  - Use Pillow `Image.verify()` for image templates/assets.
  - Use PyMuPDF open/page-count validation for PDFs and reject encrypted/multi-page PDFs if not supported.
  - Use `zipfile.is_zipfile()` and openpyxl for `.xlsx` validation.
- Decide whether CSV/XLS are intentionally supported. If not, restrict attendee imports to `.xlsx`.
- Return a clear 400 error and remove saved files when validation fails.

### 4. Missing template asset upload/list/delete endpoints and rendering support

Severity: High

Evidence:
- The spec requires stamp and signature assets (`docs/specification.md:79`).
- The architecture lists asset endpoints (`docs/architecture.md:356`).
- `TemplateAsset` model exists in `backend/app/models/template.py:30`.
- No backend routes implement `/templates/{template_id}/assets`.
- Frontend `FieldKey` only includes `attendee_name`, `workshop_title`, and `certificate_date` in `frontend/src/types/fieldMapping.ts:1`.
- Backend renderer only renders text fields defined in `TEXT_FIELD_VALUES` in `backend/app/services/certificate_renderer.py:21`; image fields are skipped in `backend/app/services/certificate_renderer.py:69`.

Why this matters:
- Required MVP fields `stamp` and `signature` cannot be uploaded, positioned, or rendered.
- The app cannot meet acceptance criteria requiring positioning name, workshop title, date, stamp, and signature (`docs/specification.md:280`).

Recommendation:
- Add asset routes to upload/list/delete `stamp` and `signature` images.
- Add frontend controls for asset upload and image field placement.
- Extend `FieldKey` and backend field mapping validation to include `stamp` and `signature`.
- Extend `CertificateRenderer` to insert visible image assets using saved field rectangles.

### 5. Public API exposes storage paths in response schemas

Severity: High

Evidence:
- `TemplateRead` includes `preview_image_path` in `backend/app/schemas/template.py:15`.
- `GeneratedCertificateRead` includes `file_path` in `backend/app/schemas/generation.py:32`.
- The security requirements say to avoid exposing arbitrary filesystem paths through the API (`docs/specification.md:214`).

Why this matters:
- Even relative storage paths leak internal layout and may become absolute or sensitive if storage configuration changes.
- Clients should use download/preview endpoints rather than relying on filesystem path metadata.

Recommendation:
- Remove `file_path` and internal storage paths from public schemas.
- Return opaque IDs and explicit URLs such as `preview_url`, `download_url`, or `zip_download_url`.
- Keep storage paths server-side only.

### 6. Download endpoints do not use the storage traversal guard

Severity: High

Evidence:
- `StorageService.resolve_storage_path()` provides safe path resolution in `backend/app/services/storage_service.py:22`.
- `get_template_preview()` directly joins `settings.storage_root / preview_path` in `backend/app/api/routes/templates.py:56`.
- `download_certificate()` directly joins `settings.storage_root / certificate.file_path` in `backend/app/api/routes/certificates.py:39`.
- `create_zip_for_job()` directly joins `settings.storage_root / certificate.file_path` in `backend/app/services/generation_service.py:115`.

Why this matters:
- Today the paths are database-controlled, but if an attacker or bug writes a path like `../../...` into the database, download code can escape storage root.
- The project already has a safe helper but does not consistently use it.

Recommendation:
- Use `StorageService.resolve_storage_path()` for every read/download path.
- Store and validate only relative paths under the configured storage root.
- Consider a database constraint or model-level validator for path fields.

### 7. Field mapping API does not validate field keys or bounds

Severity: High

Evidence:
- `FieldMappingBase.field_key` is an unconstrained string in `backend/app/schemas/field_mapping.py:5`.
- `save_field_mappings()` deletes and recreates all mappings without validating required fields or duplicates in `backend/app/api/routes/field_mappings.py:28`.
- Coordinates only require non-negative x/y and positive width/height in `backend/app/schemas/field_mapping.py:6`, but there is no check against template dimensions.

Why this matters:
- Invalid field keys are accepted and silently ignored by rendering.
- Duplicate mappings can be saved for the same field key.
- Out-of-bounds mappings can generate broken PDFs or confusing frontend behavior.

Recommendation:
- Introduce an enum for allowed field keys.
- Require exactly one mapping per required field or clearly support optional hidden mappings.
- Enforce `x + width <= page_width` and `y + height <= page_height` when template dimensions are known.
- Add a uniqueness constraint on `(template_id, field_key)`.

### 8. Generation marks certificate records as generated before rendering succeeds

Severity: Medium

Evidence:
- `GeneratedCertificate(status="generated")` is constructed before render in `backend/app/services/generation_service.py:75`.
- The status is changed to `failed` only if an exception is raised.

Why this matters:
- The code works for exceptions, but the lifecycle is misleading and fragile.
- If future code commits mid-loop, streams output, or returns early, records may be incorrectly marked generated.

Recommendation:
- Create certificate records with `status="pending"` or create records only after successful render.
- Set `status="generated"` after the file exists and passes a file existence/size check.

### 9. ZIP download can return an empty ZIP even when database records say certificates exist

Severity: Medium

Evidence:
- `create_zip_for_job()` filters generated certificate rows in `backend/app/services/generation_service.py:100`.
- It silently skips missing files in `backend/app/services/generation_service.py:116`.
- It returns the ZIP path even if every expected file was missing.

Why this matters:
- Users can download an empty archive without knowing files are missing.
- This hides data loss and storage consistency problems.

Recommendation:
- Count added files and raise a 404/409 if no files were added.
- Add missing-file details to job/certificate errors or logs.

### 10. Endpoint coverage is incomplete against the architecture

Severity: Medium

Missing or partial endpoints:
- `DELETE /api/v1/templates/{template_id}` is listed in `docs/architecture.md:353` but not implemented.
- `POST/GET/DELETE /api/v1/templates/{template_id}/assets` are listed in `docs/architecture.md:356` but not implemented.
- `PATCH /api/v1/templates/{template_id}/field-mappings/{field_key}` is listed in `docs/architecture.md:362` but not implemented.
- `GET /api/v1/attendee-imports/{import_id}` and `DELETE /api/v1/attendee-imports/{import_id}` are listed in `docs/architecture.md:366` but not implemented.
- `GET /api/v1/attendee-imports/{import_id}/attendees` exists but does not 404 when the import is missing; it returns an empty list.

Recommendation:
- Implement the missing MVP endpoints or update `docs/architecture.md` if intentionally deferred.
- Return 404 for child collection routes when parent resources do not exist.

### 11. No backend tests are present

Severity: High

Evidence:
- `backend/tests/` does not exist.
- `backend/pyproject.toml:21` configures pytest to look for `tests`, but no tests are checked in.

Why this matters:
- File upload, path validation, migrations, rendering, and ZIP generation are all high-risk areas.
- Refactoring toward stricter validation will need regression coverage.

Recommendation:
- Add pytest coverage for upload validation, storage path traversal, attendee parsing, field mapping validation, generation, and downloads.
- Use temporary SQLite databases and temporary storage directories in fixtures.

## Backend detailed review

### FastAPI practices

Good:
- Uses routers and dependency injection consistently.
- Uses response models for most endpoints.
- Uses `HTTPException` with appropriate status codes for many not-found and validation cases.

Needs improvement:
- `backend/app/main.py:38` includes the same router under `/api/v1` and again under `/api`. This was noted as a Phase 1 compatibility alias in `backend/app/main.py:40`, but it doubles the public surface area and can confuse API docs and clients. Keep it only if there is a real backward-compatibility requirement.
- `backend/app/main.py:22` does not configure version, description, contact, or OpenAPI metadata beyond the title.
- There is no global exception handling or structured logging.
- Long-running certificate generation is synchronous inside the request in `backend/app/api/routes/generation.py:16`. This is acceptable for small MVP batches per `docs/specification.md:229`, but it is not production-ready.
- There is no request ID/correlation ID logging to trace upload/generation failures.

### Error handling

Good:
- Template and generation routes return 404 for missing template/job/certificate in many places.
- Excel parsing wraps parser exceptions into a 400 in `backend/app/services/excel_service.py:51`.

Needs improvement:
- `upload_template()` and `upload_attendees()` catch `Exception`, roll back, and re-raise in routes, but service methods also perform file writes before later validation. If dimension/preview parsing fails after saving a file, the database rolls back but the uploaded file remains orphaned.
- `ExcelService.create_attendee_import()` saves the upload before parsing. If parse or required-column validation fails, the saved file remains orphaned and the flushed DB row is rolled back.
- `TemplateService._read_template_dimensions()` and `_create_preview_image()` can raise parser exceptions that will bubble as 500s for malformed uploads.
- `CertificateRenderer._hex_to_rgb()` can raise `ValueError` for non-hex 6-character strings because it only checks length, not hex validity.

### Security

Good:
- Uploads are streamed and capped by size.
- Filenames are sanitized with `Path(filename).name` and a restricted character regex.
- `StorageService.resolve_storage_path()` exists and correctly guards resolved paths.

Risks:
- No authentication. This is explicitly out of MVP scope in `docs/specification.md:267`, but it must be addressed before any shared or public deployment.
- CORS allows credentials with configured origins in `backend/app/main.py:24`; keep production origins explicit and avoid wildcards with credentials.
- Upload validation is extension-only.
- Internal paths are exposed via API schemas.
- Download code bypasses storage path guard.
- Generated ZIP files are overwritten per job ID without cache invalidation or concurrency protection.

## Frontend detailed review

### Component organization

Good:
- Components are small and readable.
- API calls are isolated from rendering components.
- Types are centralized.

Needs improvement:
- `TemplatesPage.tsx`, `AttendeeImportPage.tsx`, and `EmailPage.tsx` are placeholders, so key workflows are collapsed into the dashboard rather than having complete pages.
- `App.tsx` uses string-based manual page state instead of React Router. This is acceptable for a tiny MVP but prevents deep links such as `/templates/1/designer`.
- There is no React Query or equivalent caching/error retry layer, though it was recommended as optional in `docs/specification.md:34`.
- Parent callback props in `DashboardPage.tsx` are passed raw `setState` functions from `App.tsx`. Because React state setters are stable this works, but the effect dependencies in `DashboardPage.tsx:31` and `TemplateDesignerPage.tsx:29` are easy to make chatty if those callbacks later change.

### State management and UX

Good:
- Uploads and generation show loading states.
- API errors are displayed via `getApiErrorMessage()`.
- Build passes under TypeScript.

Needs improvement:
- Upload errors do not preserve selected files for retry in `UploadBox.tsx:19` because the selected file is cleared after every upload call, even when the upload fails.
- The attendee preview only shows the first 25 rows returned by the upload response and there is no frontend call to fetch all attendees for an import. `frontend/src/api/attendees.ts` has no `listAttendees(importId)` function even though the backend route exists.
- The UI cannot show attendee names on the Certificates page because `GeneratedCertificateRead` lacks attendee details and the frontend table only displays IDs/status.
- Download links do not set `download` attributes and do not handle errors from failed downloads.
- No user confirmation or cleanup exists for destructive operations because delete endpoints are missing.

### Designer/coordinate handling

Good:
- `TemplateCanvas.tsx:30` converts displayed preview pointer positions back to template coordinate space.
- The field boxes are sized proportionally to the template dimensions.

Risks:
- Dragging uses `onPointerMove` on each field button and `event.currentTarget.getBoundingClientRect()` in `frontend/src/components/TemplateCanvas.tsx:30`. That bounding box is the field box, not the full template stage. As a result, scale is computed from the field's rendered size rather than the preview/stage size, which can produce incorrect coordinate movement. The coordinate calculation should use the containing stage/image bounds.
- The frontend only supports three text fields. It does not support stamp/signature fields required by the spec.
- Field controls can set invalid numeric values: `Number("")` becomes `0`, and width/height can become invalid until the backend rejects the save.
- Font preview sizing divides font size by 3 in `TemplateCanvas.tsx:59`, which is a rough heuristic and may not match PDF rendering.

## Database design review

Good:
- Tables cover the broad entities from the architecture.
- Relationships are defined where needed for cascade delete on ORM relationships.

Risks and gaps:
- No Alembic migrations.
- No uniqueness constraint on field mappings per template/field key.
- No enum/check constraints for statuses (`pending`, `running`, `completed`, `completed_with_errors`, `generated`, `failed`) or field keys.
- Foreign keys use `ondelete="CASCADE"` in some places but SQLite foreign key enforcement is not explicitly enabled. SQLAlchemy/SQLite requires `PRAGMA foreign_keys=ON` per connection for DB-level cascades to work reliably.
- `GenerationJob` lacks relationships to `CertificateTemplate` and `AttendeeImport`, which limits ORM navigation and schema expansion.
- `GeneratedCertificate` has no relationship to `Attendee`, so certificate listings cannot easily include attendee names without manual joins.
- `TemplateAsset.asset_type` is a free string with no uniqueness constraint preventing multiple stamps/signatures unless intentionally supported.

## File upload and storage handling review

Good:
- Storage is under `backend/storage/` by default, matching the architecture.
- Files are grouped by template/import/job ID.
- Filenames are sanitized and generated outputs include attendee ID.

Risks:
- Relative storage root defaults to `Path("storage")` in `backend/app/config.py:13`, making behavior dependent on process working directory. Running Uvicorn from repository root versus `backend/` changes where files and `app.db` are created.
- Failed uploads can leave orphaned files.
- File content validation is too weak.
- Internal paths are leaked in public API responses.
- Download paths do not use the safe resolver.
- Generated file names include attendee names. This is user-friendly but leaks PII into filesystem paths and ZIP member names. Decide if that is acceptable for the application context.

## API implementation and documentation review

Good:
- Core route groups are present for templates, field mappings, attendees, generation jobs, certificates, and placeholder email.
- Response models make OpenAPI docs usable for implemented endpoints.

Needs improvement:
- API docs are incomplete because several spec/architecture endpoints are missing.
- There is no README documenting how to start backend/frontend, install dependencies, configure environment, or run migrations.
- There is no `.env.example` documenting `CERTGEN_DATABASE_URL`, `CERTGEN_CORS_ORIGINS`, `CERTGEN_MAX_UPLOAD_SIZE_BYTES`, or `CERTGEN_STORAGE_ROOT`.
- Compatibility aliases under `/api` are included with the same router; the canonical API base path should be clear.

## Missing features compared to specification

Missing from MVP acceptance criteria:
- Stamp/signature asset upload and rendering.
- Field designer support for stamp/signature.
- Template asset endpoints.
- Full attendee import detail and deletion endpoints.
- Template deletion endpoint.
- Migration-based database setup.
- Backend tests.
- End-to-end manual acceptance flow documentation.

Partially implemented:
- Template upload and preview are present, but validation is weak and malformed files can create orphaned files.
- Attendee import parses files and marks missing names invalid, but accepts CSV/XLS beyond MVP and lacks full frontend import browsing.
- Certificate generation creates PDFs for text fields but not image fields.
- ZIP download exists but can silently omit missing files.
- Frontend workflow is usable for a happy path but important pages are placeholders.

## Deployment readiness review

The project is not production/deployment-ready yet.

Missing deployment essentials:
- No Dockerfile or docker-compose.
- No README.
- No `.env.example`.
- No migration environment.
- No production static frontend serving plan.
- No dependency lock for backend.
- No tests or CI configuration.
- No structured logging.
- No authentication or authorization for public/shared deployments.
- No backup/restore strategy for SQLite and local storage.
- No persistent volume documentation.

Configuration risks:
- `database_url` and `storage_root` are relative paths by default.
- `CORS` defaults are local-only but production documentation is absent.
- Upload size is configurable but not enforced at reverse-proxy level.

## Suggested quality gates before calling MVP complete

1. Backend dependencies install cleanly in a fresh venv.
2. `pytest` passes with tests for uploads, attendee parsing, field mappings, generation, and downloads.
3. `npm run build` passes.
4. Alembic migration upgrades a blank database successfully.
5. Manual acceptance test from `docs/roadmap.md:361` passes end-to-end.
6. Generated certificates visually confirm text and image fields in correct positions.
7. ZIP download contains exactly the generated PDFs for a job.
8. Malformed/oversized/renamed uploads are rejected and leave no orphaned files.
