import { useState, useEffect, useCallback } from 'react';
import api from '../api/client';
import { MOCK_NOTIFICATIONS } from '../data/mock';

export function useNotifications() {
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(false);

  const fetchNotifications = useCallback(async () => {
    setLoading(true);
    try {
      const { data } = await api.get('/api/v1/notifications');
      const items = Array.isArray(data) ? data : data.items || [];
      const result = items.length > 0 ? items : MOCK_NOTIFICATIONS;
      setNotifications(result);
      setUnreadCount(result.filter((n) => !n.is_read).length);
    } catch {
      setNotifications(MOCK_NOTIFICATIONS);
      setUnreadCount(MOCK_NOTIFICATIONS.filter((n) => !n.is_read).length);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchNotifications(); }, [fetchNotifications]);

  const markAsRead = async (id) => {
    try {
      await api.put(`/api/v1/notifications/${id}/read`);
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, is_read: true } : n))
      );
      setUnreadCount((c) => Math.max(0, c - 1));
    } catch { /* silent */ }
  };

  const markAllRead = async () => {
    try {
      await api.put('/api/v1/notifications/read-all');
      setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
      setUnreadCount(0);
    } catch { /* silent */ }
  };

  return { notifications, unreadCount, loading, refetch: fetchNotifications, markAsRead, markAllRead };
}
