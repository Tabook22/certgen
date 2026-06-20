import { apiBaseUrl, apiClient } from "./client";
import type { GeneratedCertificate, GenerationJob } from "../types/generation";

export async function createGenerationJob(
  templateId: number,
  attendeeImportId: number,
  workshopTitle?: string,
  certificateDate?: string,
): Promise<GenerationJob> {
  const response = await apiClient.post<GenerationJob>("/generation-jobs", {
    template_id: templateId,
    attendee_import_id: attendeeImportId,
    workshop_title: workshopTitle || null,
    certificate_date: certificateDate || null,
  });
  return response.data;
}

export async function listGenerationJobs(): Promise<GenerationJob[]> {
  const response = await apiClient.get<GenerationJob[]>("/generation-jobs");
  return response.data;
}

export async function listJobCertificates(jobId: number): Promise<GeneratedCertificate[]> {
  const response = await apiClient.get<GeneratedCertificate[]>(`/generation-jobs/${jobId}/certificates`);
  return response.data;
}

export function getJobZipUrl(jobId: number): string {
  return `${apiBaseUrl}/generation-jobs/${jobId}/download-zip`;
}
