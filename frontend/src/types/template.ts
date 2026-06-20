export interface CertificateTemplate {
  id: number;
  name: string;
  description: string | null;
  original_filename: string;
  file_type: string;
  preview_image_path: string | null;
  page_width: number | null;
  page_height: number | null;
  created_at: string;
  updated_at: string;
}

export interface TemplateUploadResponse {
  template: CertificateTemplate;
  message: string;
}
