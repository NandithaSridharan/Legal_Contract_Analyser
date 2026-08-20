import { apiClient } from './apiClient';
import type { AnalysisResponse, ChatResponse, Clause, Entity, Risk } from './types';

export const analysisApi = {
  analyze: async (id: number) => (await apiClient.post<AnalysisResponse>(`/analyze-contract/${id}`)).data,
  summary: async (id: string) => (await apiClient.get<{ summary: string }>(`/summary/${id}`)).data,
  clauses: async (id: string) => (await apiClient.get<{ clauses: Clause[] }>(`/extract-clauses/${id}`)).data,
  risks: async (clauses: Record<string, string>) => (await apiClient.post<{ risks: Risk[] }>('/risk-analysis', { clauses })).data,
  entities: async (text: string) => (await apiClient.post<{ entities: Entity[] }>('/extract-entities', { text })).data,
  chat: async (contract_id: number | string, question: string) => (await apiClient.post<ChatResponse>('/chat', { contract_id: Number(contract_id), question })).data,
};
