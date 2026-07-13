import { useState, useEffect, useCallback } from 'react';
import api from '../api/client';
import { MOCK_WATCHLIST } from '../data/mock';

export function useWatchlist() {
  const [watchlist, setWatchlist] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchWatchlist = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const { data } = await api.get('/api/v1/watchlist');
      const items = Array.isArray(data) ? data : data.items || [];
      setWatchlist(items.length > 0 ? items : MOCK_WATCHLIST);
    } catch (err) {
      setWatchlist(MOCK_WATCHLIST);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchWatchlist(); }, [fetchWatchlist]);

  const addToWatchlist = async (ticker) => {
    await api.post('/api/v1/watchlist', { ticker });
    await fetchWatchlist();
  };

  const removeFromWatchlist = async (ticker) => {
    await api.delete(`/api/v1/watchlist/${ticker}`);
    await fetchWatchlist();
  };

  return { watchlist, loading, error, refetch: fetchWatchlist, addToWatchlist, removeFromWatchlist };
}
