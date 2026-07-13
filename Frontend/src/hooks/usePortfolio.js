import { useState, useEffect, useCallback } from 'react';
import api from '../api/client';
import { MOCK_HOLDINGS } from '../data/mock';

export function usePortfolio() {
  const [holdings, setHoldings] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchHoldings = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const { data } = await api.get('/api/v1/portfolio');
      const items = Array.isArray(data) ? data : data.items || [];
      setHoldings(items.length > 0 ? items : MOCK_HOLDINGS);
    } catch (err) {
      setHoldings(MOCK_HOLDINGS);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchHoldings(); }, [fetchHoldings]);

  const addHolding = async (holding) => {
    const { data } = await api.post('/api/v1/portfolio', holding);
    await fetchHoldings();
    return data;
  };

  const updateHolding = async (id, updates) => {
    const { data } = await api.put(`/api/v1/portfolio/${id}`, updates);
    await fetchHoldings();
    return data;
  };

  const deleteHolding = async (id) => {
    await api.delete(`/api/v1/portfolio/${id}`);
    await fetchHoldings();
  };

  return { holdings, loading, error, refetch: fetchHoldings, addHolding, updateHolding, deleteHolding };
}
