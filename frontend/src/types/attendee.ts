export interface Attendee {
  id: number;
  original_row_number: number;
  full_name: string | null;
  email: string | null;
  workshop_title: string | null;
  certificate_date: string | null;
  is_valid: boolean;
  validation_error: string | null;
}

export interface AttendeeImport {
  id: number;
  original_filename: string;
  total_rows: number;
  valid_rows: number;
  invalid_rows: number;
  created_at: string;
}

export interface AttendeeImportUploadResponse {
  attendee_import: AttendeeImport;
  attendees: Attendee[];
  message: string;
}
