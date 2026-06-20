import { apiClient } from "./client";
import type { AttendeeImport, AttendeeImportUploadResponse } from "../types/attendee";

export async function uploadAttendees(file: File): Promise<AttendeeImportUploadResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await apiClient.post<AttendeeImportUploadResponse>("/attendee-imports", formData);
  return response.data;
}

export async function listAttendeeImports(): Promise<AttendeeImport[]> {
  const response = await apiClient.get<AttendeeImport[]>("/attendee-imports");
  return response.data;
}
