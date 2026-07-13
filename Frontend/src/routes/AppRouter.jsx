import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Layout from '../components/layout/Layout';
import AuthPage from '../components/auth/AuthPage';
import Dashboard from '../components/dashboard/Dashboard';
import Advisor from '../components/advisor/Advisor';
import Marketplace from '../components/marketplace/Marketplace';
import Portfolio from '../components/portfolio/Portfolio';
import Journal from '../components/journal/Journal';
import Settings from '../components/settings/Settings';
import LoadingSpinner from '../components/ui/LoadingSpinner';

function ProtectedRoute({ children }) {
  const { token, loading } = useAuth();
  if (loading) return <LoadingSpinner />;
  if (!token) return <Navigate to="/auth" replace />;
  return children;
}

function AuthRoute({ children }) {
  const { token, loading } = useAuth();
  if (loading) return <LoadingSpinner />;
  if (token) return <Navigate to="/" replace />;
  return children;
}

export default function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/auth" element={<AuthRoute><AuthPage /></AuthRoute>} />
        <Route element={<ProtectedRoute><Layout /></ProtectedRoute>}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/advisor" element={<Advisor />} />
          <Route path="/marketplace" element={<Marketplace />} />
          <Route path="/portfolio" element={<Portfolio />} />
          <Route path="/journal" element={<Journal />} />
          <Route path="/settings" element={<Settings />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
