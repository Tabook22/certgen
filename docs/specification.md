# Certificate Generator Application Specification

## 1. Purpose

The Certificate Generator application is a web-based tool for creating personalized certificate PDFs from a reusable certificate design/template and an Excel list of attendees.

The application should allow an administrator to:

1. Upload a certificate design/template.
2. Define where dynamic fields appear on the certificate.
3. Upload an Excel sheet of attendees.
4. Generate one certificate PDF per attendee.
5. Save and download generated certificates.
6. Optionally email certificates in a later phase.

## 2. Preferred Technology Stack

### Backend

- Python
- FastAPI
- SQLite
- SQLModel or SQLAlchemy
- Alembic for database migrations
- PyMuPDF, Pillow, and/or ReportLab for certificate rendering
- pandas and openpyxl for Excel parsing

### Frontend

- React
- TypeScript
- Vite
- Axios or Fetch API
- React Query, optional but recommended
- Tailwind CSS or Material UI, optional

### Storage

- SQLite stores metadata.
- Local filesystem stores uploaded templates, uploaded Excel sheets, stamp/signature images, generated PDFs, and generated ZIP files.

## 3. Main Users

### Administrator

The administrator manages certificate templates, uploads attendee lists, configures field positions, generates certificates, and downloads the results.

### Future Email Sender

In a later phase, the administrator can send generated certificates to attendees by email.

## 4. Core Functional Requirements

## 4.1 Template Upload

The system must allow the administrator to upload a certificate template.

Supported MVP formats:

- PNG
- JPG/JPEG
- PDF, single page preferred for MVP

For each uploaded template, the system must store:

- Template name
- Optional description
- Original filename
- File path
- File type
- Preview image path
- Page width
- Page height
- Created timestamp
- Updated timestamp

The system must generate or store a preview image for the frontend designer.

## 4.2 Template Assets

The system must allow optional upload of:

- Stamp image
- Signature image

Supported MVP formats:

- PNG
- JPG/JPEG

Each asset must be associated with a certificate template.

## 4.3 Field Mapping Designer

The system must allow the administrator to define where each certificate field appears.

Required dynamic fields:

- Attendee name
- Workshop title
- Certificate date
- Stamp
- Signature

For text fields, the system should store:

- Field key
- X coordinate
- Y coordinate
- Width
- Height
- Font family
- Font size
- Font color
- Font weight
- Alignment
- Visibility

For image fields, the system should store:

- Field key
- X coordinate
- Y coordinate
- Width
- Height
- Visibility

The frontend designer must display the certificate preview and allow fields to be positioned visually.

Coordinate mapping must be consistent between the frontend preview and backend PDF generation.

## 4.4 Excel Attendee Upload

The system must allow the administrator to upload an Excel sheet of attendees.

Supported MVP format:

- .xlsx

Expected columns:

- full_name, required
- email, optional for MVP, required for future email sending
- workshop_title, optional
- certificate_date, optional

The system must parse the Excel file and store attendee records.

Rows with missing required data must be marked invalid rather than silently ignored.

The system should store:

- Original row number
- Full name
- Email
- Workshop title
- Certificate date
- Validation status
- Validation error
- Optional raw metadata JSON

## 4.5 Certificate Generation

The system must generate one PDF certificate for each valid attendee in an import batch.

Generation must:

1. Load the selected template.
2. Load saved field mappings.
3. Load stamp/signature assets if configured.
4. For each valid attendee:
   - Draw attendee name.
   - Draw workshop title.
   - Draw certificate date.
   - Draw stamp image if visible and available.
   - Draw signature image if visible and available.
   - Save a PDF file.
5. Store a generated certificate database record.

Generated certificates must be saved under a job-specific output folder.

## 4.6 Generated Certificate Management

The system must allow the administrator to:

- List generation jobs.
- View job status.
- View generated certificates for a job.
- Download an individual PDF certificate.
- Download all PDFs for a job as a ZIP file.

## 4.7 Optional Email Delivery, Later Phase

The system should be designed so email delivery can be added later.

Future email functionality should support:

- Sending one certificate to one attendee.
- Sending all certificates from a generation job.
- Configurable subject and message body.
- Attachment of generated PDF.
- Tracking send status.
- Tracking errors.

## 5. Non-Functional Requirements

## 5.1 Security

The system must:

- Validate uploaded file types.
- Prevent path traversal attacks.
- Store files using sanitized names.
- Avoid exposing arbitrary filesystem paths through the API.
- Limit upload size.
- Avoid executing uploaded files.

## 5.2 Reliability

The system should:

- Preserve uploaded source files.
- Record generation errors per attendee.
- Not fail the whole batch if one attendee certificate fails.
- Keep job status and counts accurate.

## 5.3 Performance

For MVP, synchronous certificate generation is acceptable for small batches.

If batch sizes grow, generation should move to background tasks or a worker queue.

## 5.4 Maintainability

The backend should separate responsibilities into:

- API routes
- Schemas
- Models
- Services
- Utilities

The frontend should separate responsibilities into:

- Pages
- Components
- API client modules
- Type definitions

## 6. MVP Scope

The MVP should include:

1. Upload template.
2. Generate template preview.
3. Save field mappings.
4. Upload Excel attendee sheet.
5. Parse and validate attendees.
6. Generate PDF certificates.
7. List and download generated certificates.
8. Download ZIP per generation job.

## 7. Out of Scope for MVP

The following should be deferred:

- User authentication.
- Multi-tenant support.
- Payment/billing.
- Email sending.
- Cloud object storage.
- Multiple-page certificates.
- Custom font upload.
- Advanced design editor features.

## 8. Acceptance Criteria

The MVP is complete when an administrator can:

1. Upload a certificate template.
2. Open the template designer.
3. Position name, workshop title, date, stamp, and signature fields.
4. Save the field mapping.
5. Upload an Excel file with at least three attendees.
6. Generate certificates.
7. Confirm one PDF exists per valid attendee.
8. Download an individual certificate PDF.
9. Download all certificates in a ZIP file.
