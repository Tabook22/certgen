export interface GenerationJob {
  id: number;
  template_id: number;
  attendee_import_id: number;
  status: string;
  total_count: number;
  success_count: number;
  failed_count: number;
  error_message: string | null;
  created_at: string;
  updated_at: string;
}

export interface GeneratedCertificate {
  id: number;
  generation_job_id: number;
  attendee_id: number;
  file_path: string;
  status: string;
  error_message: string | null;
  created_at: string;
}
