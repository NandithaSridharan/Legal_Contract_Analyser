import { apiClient } from './apiClient';
import type { Obligation } from './types';
export const obligationApi = { extract: async (text: string) => (await apiClient.post<{ obligations: Obligation[] }>('/extract-obligations', { text })).data, update: async (id: number, completed: boolean) => (await apiClient.patch<{ obligation: Obligation }>(`/obligations/${id}`, { completed })).data }; 
