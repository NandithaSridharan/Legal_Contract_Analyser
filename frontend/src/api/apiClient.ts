import axios from 'axios';

export const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';
export const apiClient = axios.create({ baseURL: BASE_URL, timeout: 120000 });

export function apiErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    if (error.response?.status === 429) return 'AI analysis quota temporarily unavailable. Please try again later.';
    if (error.response?.status === 404) return 'The requested contract could not be found.';
    if (error.response?.status === 429) return 'AI quota temporarily exceeded. Your saved contract data is still available.';
    if (error.response?.status === 404) return 'Contract not found.';
    if (error.response?.status === 500) return 'Something went wrong while processing this contract.';
    const detail = error.response?.data?.detail;
    if (typeof detail === 'string' && error.response?.status !== 500) return detail;
  }
  return 'Something went wrong. Please try again.';
}
