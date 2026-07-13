import { useState, useEffect, useCallback } from 'react';
import api from '../api/client';
import { MOCK_MARKETPLACE } from '../data/mock';

export function useMarketplace() {
  const [listings, setListings] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchListings = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const { data } = await api.get('/api/v1/marketplace');
      const items = Array.isArray(data) ? data : data.items || [];
      setListings(items.length > 0 ? items : MOCK_MARKETPLACE);
    } catch (err) {
      setListings(MOCK_MARKETPLACE);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchListings(); }, [fetchListings]);

  const purchaseListing = async (listingId) => {
    const { data } = await api.post(`/api/v1/marketplace/${listingId}/purchase`);
    return data;
  };

  const rateListing = async (listingId, rating, review) => {
    const { data } = await api.post(`/api/v1/marketplace/${listingId}/rate`, { rating, review });
    await fetchListings();
    return data;
  };

  return { listings, loading, error, refetch: fetchListings, purchaseListing, rateListing };
}
