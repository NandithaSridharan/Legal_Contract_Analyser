import { apiClient } from './apiClient';
export const reportApi = { export: async (payload: unknown) => (await apiClient.post('/export-report', payload, { responseType: 'blob' })).data as Blob, compare: async (contract_a: string, contract_b: string) => (await apiClient.post('/compare-contracts', { contract_a, contract_b })).data }; 

export function downloadBlob(blob: Blob, filename: string) {
	const url = URL.createObjectURL(blob);
	const anchor = document.createElement('a');
	anchor.href = url;
	anchor.download = filename;
	anchor.click();
	URL.revokeObjectURL(url);
}
