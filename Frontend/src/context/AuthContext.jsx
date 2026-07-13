import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import api from '../api/client';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(() => localStorage.getItem('sp_access_token'));
  const [loading, setLoading] = useState(true);

  const fetchUser = useCallback(async () => {
    const stored = localStorage.getItem('sp_access_token');
    if (stored === 'demo_token_offline') {
      setUser({ id: 0, full_name: 'Demo Trader', email: 'demo@stockpilot.io' });
      return;
    }
    try {
      const { data } = await api.get('/api/v1/users/me');
      setUser(data);
    } catch (err) {
      if (err.response?.status === 401 || err.response?.status === 403) {
        setUser(null);
        setToken(null);
        localStorage.removeItem('sp_access_token');
        localStorage.removeItem('sp_refresh_token');
      }
    }
  }, []);

  useEffect(() => {
    if (token) {
      fetchUser().finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, [token, fetchUser]);

  const login = async (email, password) => {
    try {
      const { data } = await api.post('/api/v1/auth/login', { email, password });
      localStorage.setItem('sp_access_token', data.access_token);
      if (data.refresh_token) {
        localStorage.setItem('sp_refresh_token', data.refresh_token);
      }
      setToken(data.access_token);
      setUser(data.user || null);
      if (!data.user) {
        await fetchUser();
      }
      return data;
    } catch (err) {
      if (email === 'demo@stockpilot.io' && password === 'demo1234') {
        const demoToken = 'demo_token_offline';
        const demoUser = { id: 0, full_name: 'Demo Trader', email: 'demo@stockpilot.io' };
        localStorage.setItem('sp_access_token', demoToken);
        setToken(demoToken);
        setUser(demoUser);
        return { access_token: demoToken, user: demoUser };
      }
      throw err;
    }
  };

  const register = async (full_name, email, password) => {
    const { data } = await api.post('/api/v1/auth/register', { full_name, email, password });
    localStorage.setItem('sp_access_token', data.access_token);
    if (data.refresh_token) {
      localStorage.setItem('sp_refresh_token', data.refresh_token);
    }
    setToken(data.access_token);
    setUser(data.user || null);
    if (!data.user) {
      await fetchUser();
    }
    return data;
  };

  const logout = () => {
    localStorage.removeItem('sp_access_token');
    localStorage.removeItem('sp_refresh_token');
    setToken(null);
    setUser(null);
  };

  const updateUser = (updatedUser) => {
    setUser(updatedUser);
  };

  return (
    <AuthContext.Provider value={{ user, token, loading, login, register, logout, updateUser, fetchUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
