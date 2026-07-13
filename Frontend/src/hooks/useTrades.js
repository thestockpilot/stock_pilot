import { useState, useEffect, useCallback } from 'react';
import api from '../api/client';
import { MOCK_TRADES } from '../data/mock';

export function useTrades() {
  const [trades, setTrades] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchTrades = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const { data } = await api.get('/api/v1/trades');
      const items = Array.isArray(data) ? data : data.items || [];
      setTrades(items.length > 0 ? items : MOCK_TRADES);
    } catch (err) {
      setTrades(MOCK_TRADES);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchTrades(); }, [fetchTrades]);

  const createTrade = async (trade) => {
    const { data } = await api.post('/api/v1/trades', trade);
    await fetchTrades();
    return data;
  };

  const deleteTrade = async (id) => {
    await api.delete(`/api/v1/trades/${id}`);
    await fetchTrades();
  };

  return { trades, loading, error, refetch: fetchTrades, createTrade, deleteTrade };
}
