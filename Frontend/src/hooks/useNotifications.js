import { useState, useEffect, useCallback } from 'react';
import api from '../api/client';
import { getCached, setCache, subscribe } from '../api/cache';

const KEY = 'notifications';

const withUnread = (items) => ({ items, unread: items.filter((n) => !n.is_read).length });

export function useNotifications() {
  const cached = getCached(KEY, 30000);
  const [notifications, setNotifications] = useState(() => cached?.items || []);
  const [unreadCount, setUnreadCount] = useState(() => cached?.unread || 0);
  const [loading, setLoading] = useState(!cached);

  useEffect(() => subscribe(KEY, (payload) => {
    setNotifications(payload?.items || []);
    setUnreadCount(payload?.unread || 0);
  }), []);

  const fetchNotifications = useCallback(async () => {
    try {
      const { data } = await api.get('/api/v1/notifications');
      const items = Array.isArray(data) ? data : data.items || [];
      setCache(KEY, withUnread(items)); // notifies all subscribers
    } catch {
      setCache(KEY, { items: [], unread: 0 });
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (cached) { setLoading(false); return; }
    fetchNotifications();
  }, [fetchNotifications]);

  const markAsRead = async (id) => {
    try {
      await api.put(`/api/v1/notifications/${id}/read`);
      const items = (getCached(KEY, 1e12)?.items || notifications)
        .map((n) => (n.id === id ? { ...n, is_read: true } : n));
      setCache(KEY, withUnread(items));
    } catch { /* silent */ }
  };

  const markAllRead = async () => {
    try {
      await api.put('/api/v1/notifications/read-all');
      const items = (getCached(KEY, 1e12)?.items || notifications)
        .map((n) => ({ ...n, is_read: true }));
      setCache(KEY, withUnread(items));
    } catch { /* silent */ }
  };

  return { notifications, unreadCount, loading, refetch: fetchNotifications, markAsRead, markAllRead };
}
