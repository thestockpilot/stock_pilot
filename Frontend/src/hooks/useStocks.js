import { useState, useEffect, useCallback } from 'react';
import api from '../api/client';

export function useStocks() {
  const [stocks, setStocks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchStocks = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const { data } = await api.get('/api/v1/stocks');
      setStocks(Array.isArray(data) ? data : data.items || []);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load stocks');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchStocks(); }, [fetchStocks]);

  return { stocks, loading, error, refetch: fetchStocks };
}

export function useStockDetail(ticker) {
  const [stock, setStock] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchStock = useCallback(async () => {
    if (!ticker) return;
    setLoading(true);
    setError(null);
    try {
      const { data } = await api.get(`/api/v1/stocks/${ticker}`);
      setStock(data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load stock');
    } finally {
      setLoading(false);
    }
  }, [ticker]);

  useEffect(() => { fetchStock(); }, [fetchStock]);

  return { stock, loading, error, refetch: fetchStock };
}

export function usePriceHistory(ticker, days = 60) {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchHistory = useCallback(async () => {
    if (!ticker) return;
    setLoading(true);
    try {
      const { data } = await api.get(`/api/v1/stocks/${ticker}/history`, {
        params: { days },
      });
      setHistory(Array.isArray(data) ? data : data.items || []);
    } catch {
      setHistory([]);
    } finally {
      setLoading(false);
    }
  }, [ticker, days]);

  useEffect(() => { fetchHistory(); }, [fetchHistory]);

  return { history, loading, refetch: fetchHistory };
}
