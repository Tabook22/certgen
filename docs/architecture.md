# Certificate Generator Architecture

## 1. Overview

The Certificate Generator is a full-stack web application with a React frontend and a FastAPI backend.

The backend is responsible for file uploads, database persistence, Excel parsing, certificate rendering, and download endpoints.

The frontend is responsible for the user workflow, including template upload, field placement, attendee import, certificate generation, and certificate downloads.

## 2. High-Level Architecture

```text
Browser / React Frontend
        |
        | HTTP REST API / multipart uploads
        v
FastAPI Backend
        |
        |-- API Routes
        |-- Services
        |-- SQLite Database
        |-- Local File Storage
        |
        v
Certificate Renderer
        |
        v
Generated PDF Certificates
```

## 3. Backend Architecture

## 3.1 Backend Responsibilities

The backend handles:

- Template upload and metadata storage
- Template preview generation
- Stamp/signature asset uploads
- Field mapping persistence
- Excel attendee import
- Attendee validation
- Certificate PDF generation
- Generated certificate metadata
- PDF and ZIP downloads
- Future email delivery

## 3.2 Backend Folder Structure

```text
backend/
  pyproject.toml
  alembic.ini
  app/
    __init__.py
    main.py
    config.py
    database.py
    dependencies.py

    models/
      __init__.py
      template.py
      field_mapping.py
      attendee.py
      generation_job.py
      generated_certificate.py
      email_log.py

    schemas/
      __init__.py
      template.py
      field_mapping.py
      attendee.py
      generation.py
      email.py

    api/
      __init__.py
      routes/
        __init__.py
        templates.py
        field_mappings.py
        attendees.py
        generation.py
        certificates.py
        email.py

    services/
      __init__.py
      storage_service.py
      template_service.py
      excel_service.py
      certificate_renderer.py
      generation_service.py
      email_service.py

    utils/
      __init__.py
      filenames.py
      coordinates.py
      validation.py

  alembic/
    versions/

  tests/
    test_templates.py
    test_field_mappings.py
    test_attendee_import.py
    test_certificate_generation.py

  storage/
    templates/
    imports/
    generated/
```

## 3.3 Backend Layers

### API Routes

API route files receive HTTP requests, validate request data, call service functions, and return responses.

Route modules:

- `templates.py`
- `field_mappings.py`
- `attendees.py`
- `generation.py`
- `certificates.py`
- `email.py`, later phase

### Schemas

Schemas define request and response contracts using Pydantic/SQLModel models.

They should not contain business logic.

### Models

Models define database tables and relationships.

Main models:

- CertificateTemplate
- TemplateAsset
- FieldMapping
- AttendeeImport
- Attendee
- GenerationJob
- GeneratedCertificate
- EmailLog

### Services

Services contain business logic.

Main services:

- `storage_service.py`: safe file storage, folder creation, file path handling
- `template_service.py`: template validation, preview generation
- `excel_service.py`: Excel parsing and attendee validation
- `certificate_renderer.py`: PDF rendering for one certificate
- `generation_service.py`: batch certificate generation
- `email_service.py`: future email sending

### Utilities

Utilities contain shared helper functions.

Examples:

- Filename sanitization
- Coordinate conversion
- Validation helpers

## 4. Frontend Architecture

## 4.1 Frontend Responsibilities

The frontend handles:

- Navigation
- Template uploads
- Template listing
- Visual field mapping
- Excel uploads
- Attendee preview
- Generation job creation
- Certificate listing
- Certificate downloads
- Future email UI

## 4.2 Frontend Folder Structure

```text
frontend/
  package.json
  vite.config.ts
  index.html
  src/
    main.tsx
    App.tsx

    api/
      client.ts
      templates.ts
      attendees.ts
      generation.ts
      certificates.ts

    components/
      Layout.tsx
      UploadBox.tsx
      TemplateCanvas.tsx
      FieldControlPanel.tsx
      AttendeeTable.tsx
      JobStatusCard.tsx

    pages/
      DashboardPage.tsx
      TemplatesPage.tsx
      TemplateDesignerPage.tsx
      AttendeeImportPage.tsx
      GeneratePage.tsx
      CertificatesPage.tsx
      EmailPage.tsx

    types/
      template.ts
      attendee.ts
      generation.ts

    styles/
      index.css
```

## 4.3 Frontend Pages

### DashboardPage

Shows application summary and quick links.

### TemplatesPage

Allows template upload and template management.

### TemplateDesignerPage

Displays the uploaded certificate preview and lets the user position fields.

### AttendeeImportPage

Allows Excel upload and attendee validation preview.

### GeneratePage

Allows the user to choose a template and attendee import, then generate PDFs.

### CertificatesPage

Lists generated certificates and supports downloads.

### EmailPage

Future page for sending certificates by email.

## 5. Storage Architecture

Binary files should be stored on disk, not inside SQLite.

Recommended storage layout:

```text
backend/storage/
  templates/
    <template_id>/
      original.pdf
      preview.png
      stamp.png
      signature.png

  imports/
    <import_id>/
      attendees.xlsx

  generated/
    <job_id>/
      <attendee_id>-<safe-name>.pdf

  zips/
    <job_id>.zip
```

SQLite stores metadata and relative paths.

## 6. Database Architecture

## 6.1 Tables

The database contains these main tables:

- `certificate_templates`
- `template_assets`
- `field_mappings`
- `attendee_imports`
- `attendees`
- `generation_jobs`
- `generated_certificates`
- `email_logs`

## 6.2 Relationships

```text
certificate_templates
  |-- template_assets
  |-- field_mappings
  |-- attendee_imports, optional association
  |-- generation_jobs

attendee_imports
  |-- attendees
  |-- generation_jobs

generation_jobs
  |-- generated_certificates

attendees
  |-- generated_certificates

generated_certificates
  |-- email_logs, later phase
```

## 7. API Architecture

Base path:

```text
/api/v1
```

Main API groups:

```text
GET    /health

POST   /api/v1/templates
GET    /api/v1/templates
GET    /api/v1/templates/{template_id}
DELETE /api/v1/templates/{template_id}
GET    /api/v1/templates/{template_id}/preview

POST   /api/v1/templates/{template_id}/assets
GET    /api/v1/templates/{template_id}/assets
DELETE /api/v1/templates/{template_id}/assets/{asset_id}

GET    /api/v1/templates/{template_id}/field-mappings
PUT    /api/v1/templates/{template_id}/field-mappings
PATCH  /api/v1/templates/{template_id}/field-mappings/{field_key}

POST   /api/v1/attendee-imports
GET    /api/v1/attendee-imports
GET    /api/v1/attendee-imports/{import_id}
GET    /api/v1/attendee-imports/{import_id}/attendees
DELETE /api/v1/attendee-imports/{import_id}

POST   /api/v1/generation-jobs
GET    /api/v1/generation-jobs
GET    /api/v1/generation-jobs/{job_id}
GET    /api/v1/generation-jobs/{job_id}/certificates
GET    /api/v1/generation-jobs/{job_id}/download-zip

GET    /api/v1/certificates
GET    /api/v1/certificates/{certificate_id}
GET    /api/v1/certificates/{certificate_id}/download
```

## 8. Certificate Rendering Architecture

## 8.1 Rendering Flow

```text
Generation Request
  |
  v
Load template
  |
  v
Load field mappings
  |
  v
Load attendees
  |
  v
For each valid attendee:
  - Create output PDF path
  - Render text fields
  - Render image fields
  - Save PDF
  - Store generated certificate record
```

## 8.2 Coordinate System

The application should use a single backend coordinate system based on the actual template dimensions.

The frontend designer may display a scaled preview image, but it must convert browser pixel positions to template coordinates before saving.

Example:

```text
template_x = browser_x / display_scale_x
template_y = browser_y / display_scale_y
```

The backend renderer should use the saved template coordinates directly.

## 8.3 Recommended Rendering Library

PyMuPDF is recommended for MVP because it can:

- Open PDFs
- Render PDF previews
- Draw text
- Insert images
- Save PDFs

Pillow can be used for image validation and resizing.

ReportLab can be introduced later if overlay PDFs become necessary.

## 9. Future Email Architecture

Email should be implemented as a separate service so it does not complicate MVP certificate generation.

Future `email_service.py` should support:

- SMTP configuration from environment variables
- Email body templates
- PDF attachments
- Email status tracking
- Error tracking in `email_logs`

## 10. Deployment Architecture, MVP

For local MVP:

```text
React dev server: http://localhost:5173
FastAPI server:   http://localhost:8000
SQLite database:  backend/app.db
File storage:     backend/storage/
```

For later production:

- Serve frontend as static files through a web server.
- Run FastAPI with Uvicorn/Gunicorn.
- Use persistent storage volume for generated files.
- Consider PostgreSQL if concurrent usage grows.
- Consider S3-compatible storage for cloud deployments.
