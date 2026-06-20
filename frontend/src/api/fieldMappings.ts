import { apiClient } from "./client";
import type { FieldMapping } from "../types/fieldMapping";

export async function listFieldMappings(templateId: number): Promise<FieldMapping[]> {
  const response = await apiClient.get<FieldMapping[]>(`/templates/${templateId}/field-mappings`);
  return response.data;
}

export async function saveFieldMappings(templateId: number, mappings: FieldMapping[]): Promise<FieldMapping[]> {
  const response = await apiClient.put<FieldMapping[]>(`/templates/${templateId}/field-mappings`, { mappings });
  return response.data;
}
