import { apiClient } from './apiClient';
import type { Contract, Entity, FullContract, UploadResponse } from './types';

export const contractApi = {
  list: async () => (await apiClient.get<{ contracts: Contract[] }>('/contracts')).data.contracts,
  get: async (id: number) => (await apiClient.get<{ contract: Contract }>(`/contracts/${id}`)).data.contract,
  full: async (id: number) => {
    const data = (await apiClient.get<FullContract>(`/contracts/${id}/full`)).data;
    return { ...data, entities: data.entities.map(entity => ({ ...entity, entity_type: entity.entity_type || (entity as EntityApiShape).type || 'Other', entity_value: entity.entity_value || (entity as EntityApiShape).value || 'Unspecified' })) };
  },
  remove: async (id: number) => apiClient.delete(`/contracts/${id}`),
  upload: async (file: File, onProgress?: (value: number) => void) => {
    const data = new FormData(); data.append('file', file);
    const result = (await apiClient.post<UploadResponse>('/upload', data, { headers: { 'Content-Type': 'multipart/form-data' }, onUploadProgress: e => onProgress?.(e.total ? Math.round((e.loaded / e.total) * 100) : 0) })).data;
    localStorage.setItem('activeContractId', String(result.contract_id));
    return { ...result, database_id: Number(result.contract_id) };
  },
};

type EntityApiShape = Entity & { type?: string; value?: string };
