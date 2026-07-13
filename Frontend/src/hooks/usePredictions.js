import { useState, useEffect, useCallback } from 'react';
import api from '../api/client';
import { MOCK_PREDICTIONS } from '../data/mock';

export function usePredictions() {
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchPredictions = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const { data } = await api.get('/api/v1/predictions');
      const items = Array.isArray(data) ? data : data.items || [];
      setPredictions(items.length > 0 ? items : MOCK_PREDICTIONS);
    } catch (err) {
      setPredictions(MOCK_PREDICTIONS);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchPredictions(); }, [fetchPredictions]);

  return { predictions, loading, error, refetch: fetchPredictions };
}

export function usePrediction(ticker) {
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchPrediction = useCallback(async () => {
    if (!ticker) return;
    setLoading(true);
    try {
      const { data } = await api.get(`/api/v1/predictions/${ticker}`);
      setPrediction(data);
    } catch {
      setPrediction(null);
    } finally {
      setLoading(false);
    }
  }, [ticker]);

  useEffect(() => { fetchPrediction(); }, [fetchPrediction]);

  return { prediction, loading, refetch: fetchPrediction };
}
