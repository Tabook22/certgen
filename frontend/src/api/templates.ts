import { apiBaseUrl, apiClient } from "./client";
import type { CertificateTemplate, TemplateUploadResponse } from "../types/template";

export async function uploadTemplate(file: File, name?: string, description?: string): Promise<TemplateUploadResponse> {
  const formData = new FormData();
  formData.append("file", file);
  if (name) {
    formData.append("name", name);
  }
  if (description) {
    formData.append("description", description);
  }

  const response = await apiClient.post<TemplateUploadResponse>("/templates", formData);
  return response.data;
}

export async function listTemplates(): Promise<CertificateTemplate[]> {
  const response = await apiClient.get<CertificateTemplate[]>("/templates");
  return response.data;
}

export function getTemplatePreviewUrl(templateId: number): string {
  return `${apiBaseUrl}/templates/${templateId}/preview`;
}
