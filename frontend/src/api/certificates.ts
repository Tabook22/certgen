import { apiBaseUrl, apiClient } from "./client";
import type { GeneratedCertificate } from "../types/generation";

export async function listCertificates(): Promise<GeneratedCertificate[]> {
  const response = await apiClient.get<GeneratedCertificate[]>("/certificates");
  return response.data;
}

export function getCertificateDownloadUrl(certificateId: number): string {
  return `${apiBaseUrl}/certificates/${certificateId}/download`;
}
