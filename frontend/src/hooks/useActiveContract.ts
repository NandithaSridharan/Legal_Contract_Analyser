import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { apiErrorMessage } from '../api/apiClient';
import { contractApi } from '../api/contractApi';
import type { Contract, FullContract } from '../api/types';

const ACTIVE_CONTRACT_KEY = 'activeContractId';

export function useActiveContract(loadData = true) {
  const params = useParams<{ contractId?: string; id?: string }>();
  const urlId = params.contractId || params.id;
  const [contract, setContract] = useState<Contract | null>(null);
  const [full, setFull] = useState<FullContract | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const contractId = urlId || localStorage.getItem(ACTIVE_CONTRACT_KEY) || '';

  useEffect(() => {
    let cancelled = false;
    if (urlId) localStorage.setItem(ACTIVE_CONTRACT_KEY, urlId);
    if (!contractId || !loadData) {
      setLoading(false);
      return;
    }
    localStorage.setItem(ACTIVE_CONTRACT_KEY, contractId);
    setLoading(true);
    setError('');
    Promise.all([contractApi.get(Number(contractId)), contractApi.full(Number(contractId))])
      .then(([basic, complete]) => {
        if (cancelled) return;
        setContract(basic);
        setFull(complete);
      })
      .catch((reason: unknown) => {
        if (!cancelled) setError(apiErrorMessage(reason));
      })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [contractId, loadData]);

  return { contractId, contract, full, loading, error, setFull };
}

export function rememberActiveContract(id: number | string) {
  localStorage.setItem(ACTIVE_CONTRACT_KEY, String(id));
}
