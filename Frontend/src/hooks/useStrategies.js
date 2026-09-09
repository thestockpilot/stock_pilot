import { useState, useEffect, useCallback } from 'react';
import api from '../api/client';
import { getCached, setCache, subscribe } from '../api/cache';

const KEY = 'strategies';

export function useStrategies() {
  const [strategies, setStrategies] = useState(() => getCached(KEY, 30000) || []);
  const [loading, setLoading] = useState(!getCached(KEY, 30000));
  const [error, setError] = useState(null);

  useEffect(() => subscribe(KEY, setStrategies), []);

  const fetchStrategies = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const { data } = await api.get('/api/v1/strategies');
      const items = Array.isArray(data) ? data : data.items || [];
      setStrategies(items);
      setCache(KEY, items);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load strategies');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchStrategies(); }, [fetchStrategies]);

  const createStrategy = async (strategy) => {
    const { data } = await api.post('/api/v1/strategies', strategy);
    await fetchStrategies();
    return data;
  };

  const updateStrategy = async (id, updates) => {
    const { data } = await api.put(`/api/v1/strategies/${id}`, updates);
    await fetchStrategies();
    return data;
  };

  const deleteStrategy = async (id) => {
    await api.delete(`/api/v1/strategies/${id}`);
    await fetchStrategies();
  };

  return { strategies, loading, error, refetch: fetchStrategies, createStrategy, updateStrategy, deleteStrategy };
}
