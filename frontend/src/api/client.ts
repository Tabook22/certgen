import axios from "axios";

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1",
  timeout: 30000,
});

export const apiBaseUrl = apiClient.defaults.baseURL ?? "http://localhost:8000/api/v1";

export function getApiErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail;
    if (typeof detail === "string") {
      return detail;
    }
    return error.message;
  }
  return "An unexpected error occurred.";
}
