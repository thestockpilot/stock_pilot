// src/context/AuthContext.jsx
import React, { createContext, useState, useContext, useEffect } from 'react';
import api from '../api/client';

// In-memory store for mock mode
let mockUsers = [
  { id: 1, email: 'demo@stocksense.com', full_name: 'Demo User', risk_profile: 'Moderate', time_horizon: 'Medium' }
];
const mockToken = 'mock-jwt-token';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true';

  // On mount: check for stored token and restore session
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      if (USE_MOCK) {
        const storedUser = JSON.parse(localStorage.getItem('mock_user'));
        if (storedUser) {
          setUser(storedUser);
        } else {
          localStorage.removeItem('access_token');
        }
        setLoading(false);
      } else {
        api
          .get('/users/me')
          .then((res) => setUser(res.data))
          .catch(() => {
            localStorage.removeItem('access_token');
            setUser(null);
          })
          .finally(() => setLoading(false));
      }
    } else {
      setLoading(false);
    }
  }, [USE_MOCK]);

  // ---------- Mock implementations ----------
  const mockLogin = (email, password) => {
    // For demo, accept any password for the demo user, else require 'password123'
    const found = mockUsers.find(u => u.email === email);
    if (!found) throw new Error('User not found');
    if (password !== 'password123' && email !== 'demo@stocksense.com') {
      throw new Error('Invalid password');
    }
    localStorage.setItem('access_token', mockToken);
    localStorage.setItem('mock_user', JSON.stringify(found));
    return found;
  };

  const mockRegister = (fullName, email, password) => {
    if (mockUsers.find(u => u.email === email)) {
      throw new Error('Email already registered');
    }
    const newUser = {
      id: mockUsers.length + 1,
      full_name: fullName,
      email,
      risk_profile: 'Moderate',
      time_horizon: 'Medium',
    };
    mockUsers.push(newUser);
    localStorage.setItem('access_token', mockToken);
    localStorage.setItem('mock_user', JSON.stringify(newUser));
    return newUser;
  };

  // ---------- Public functions ----------
  const login = async (email, password) => {
    if (USE_MOCK) {
      return new Promise((resolve, reject) => {
        try {
          const user = mockLogin(email, password);
          setUser(user);
          resolve(user);
        } catch (err) {
          reject({ response: { data: { detail: err.message } } });
        }
      });
    }
    const response = await api.post('/auth/login', { email, password });
    const { access_token, user } = response.data;
    localStorage.setItem('access_token', access_token);
    setUser(user);
    return user;
  };

  const register = async (fullName, email, password) => {
    if (USE_MOCK) {
      return new Promise((resolve, reject) => {
        try {
          const user = mockRegister(fullName, email, password);
          setUser(user);
          resolve(user);
        } catch (err) {
          reject({ response: { data: { detail: err.message } } });
        }
      });
    }
    const response = await api.post('/auth/register', {
      full_name: fullName,
      email,
      password,
    });
    const { access_token, user } = response.data;
    localStorage.setItem('access_token', access_token);
    setUser(user);
    return user;
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('mock_user');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);