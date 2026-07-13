import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

export default function AuthPage() {
  const navigate = useNavigate();
  const { login, register } = useAuth();
  const [mode, setMode] = useState('signin');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const [signInForm, setSignInForm] = useState({ email: '', password: '' });
  const [signUpForm, setSignUpForm] = useState({ full_name: '', email: '', password: '', confirm: '' });

  const handleSignIn = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(signInForm.email, signInForm.password);
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.detail || 'Invalid email or password. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSignUp = async (e) => {
    e.preventDefault();
    setError('');
    if (signUpForm.password !== signUpForm.confirm) {
      setError('Passwords do not match.');
      return;
    }
    if (signUpForm.password.length < 8) {
      setError('Password must be at least 8 characters.');
      return;
    }
    setLoading(true);
    try {
      await register(signUpForm.full_name, signUpForm.email, signUpForm.password);
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-view">
      <div className="auth-card">
        <div className="auth-brand">
          <div className="mark">SP</div>
          Stock<span>Pilot</span>
        </div>
        <div className="auth-tag">
          {mode === 'signin' ? 'Sign in to your account' : 'Create your StockPilot account'}
        </div>

        <div className="auth-tabs">
          <button className={mode === 'signin' ? 'on' : ''} onClick={() => { setMode('signin'); setError(''); }}>
            Sign in
          </button>
          <button className={mode === 'signup' ? 'on' : ''} onClick={() => { setMode('signup'); setError(''); }}>
            Create account
          </button>
        </div>

        {error && <div className="auth-error">{error}</div>}

        {mode === 'signin' ? (
          <form className="auth-form" onSubmit={handleSignIn}>
            <div className="a-field">
              <label>Email address</label>
              <input
                type="email"
                required
                autoComplete="email"
                value={signInForm.email}
                onChange={(e) => setSignInForm({ ...signInForm, email: e.target.value })}
              />
            </div>
            <div className="a-field">
              <label>Password</label>
              <input
                type="password"
                required
                autoComplete="current-password"
                value={signInForm.password}
                onChange={(e) => setSignInForm({ ...signInForm, password: e.target.value })}
              />
            </div>
            <div className="a-row">
              <label className="a-check">
                <input type="checkbox" defaultChecked /> Keep me signed in
              </label>
              <span className="a-link">Forgot password?</span>
            </div>
            <button className="a-submit" type="submit" disabled={loading}>
              {loading ? 'Signing in...' : 'Sign in'}
            </button>
          </form>
        ) : (
          <form className="auth-form" onSubmit={handleSignUp}>
            <div className="a-field">
              <label>Full name</label>
              <input
                type="text"
                required
                placeholder="Your name"
                autoComplete="name"
                value={signUpForm.full_name}
                onChange={(e) => setSignUpForm({ ...signUpForm, full_name: e.target.value })}
              />
            </div>
            <div className="a-field">
              <label>Email address</label>
              <input
                type="email"
                required
                placeholder="you@example.com"
                autoComplete="email"
                value={signUpForm.email}
                onChange={(e) => setSignUpForm({ ...signUpForm, email: e.target.value })}
              />
            </div>
            <div className="a-field">
              <label>Password</label>
              <input
                type="password"
                required
                placeholder="At least 8 characters"
                autoComplete="new-password"
                value={signUpForm.password}
                onChange={(e) => setSignUpForm({ ...signUpForm, password: e.target.value })}
              />
            </div>
            <div className="a-field">
              <label>Confirm password</label>
              <input
                type="password"
                required
                placeholder="Repeat password"
                autoComplete="new-password"
                value={signUpForm.confirm}
                onChange={(e) => setSignUpForm({ ...signUpForm, confirm: e.target.value })}
              />
            </div>
            <button className="a-submit" type="submit" disabled={loading}>
              {loading ? 'Creating account...' : 'Create account'}
            </button>
          </form>
        )}

        <div className="a-divider">or continue with</div>
        <div className="oauth-btns">
          <button className="oauth-btn" type="button">
            <svg viewBox="0 0 24 24">
              <path d="M22.5 12.25c0-.79-.07-1.55-.2-2.28H12v4.32h5.9a5.04 5.04 0 0 1-2.19 3.3v2.74h3.54c2.08-1.92 3.28-4.75 3.28-8.08z" fill="#4285F4" />
              <path d="M12 22.5c2.97 0 5.46-.98 7.28-2.65l-3.54-2.74c-.98.66-2.24 1.05-3.74 1.05-2.87 0-5.3-1.94-6.17-4.54H2.18v2.86A10.5 10.5 0 0 0 12 22.5z" fill="#34A853" />
              <path d="M5.83 13.62A6.31 6.31 0 0 1 5.5 12c0-.56.1-1.11.24-1.62V7.52H2.18a10.5 10.5 0 0 0 0 8.96l3.65-2.86z" fill="#FBBC05" />
              <path d="M12 6.94c1.62 0 3.06.56 4.21 1.65l3.14-3.14A10.4 10.4 0 0 0 12 1.5C7.86 1.5 4.29 3.88 2.18 7.52l3.65 2.86c.86-2.6 3.3-4.44 6.17-4.44z" fill="#EA4335" />
            </svg>
            Google
          </button>
          <button className="oauth-btn" type="button">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M17.05 20.28c-.98.95-2.05.8-3.08.35-1.09-.46-2.09-.48-3.24 0-1.44.62-2.2.44-3.06-.35C2.79 15.25 3.51 7.59 9.05 7.31c1.35.07 2.29.74 3.08.8 1.18-.24 2.31-.93 3.57-.84 1.51.12 2.65.72 3.4 1.8-3.12 1.87-2.38 5.98.48 7.13-.57 1.5-1.31 2.99-2.54 4.09zM12.03 7.25c-.15-2.23 1.66-4.07 3.74-4.25.29 2.58-2.34 4.5-3.74 4.25z" />
            </svg>
            Apple
          </button>
        </div>

        <div className="auth-switch">
          {mode === 'signin' ? "Don't have an account? " : 'Already have an account? '}
          <a onClick={() => { setMode(mode === 'signin' ? 'signup' : 'signin'); setError(''); }}>
            {mode === 'signin' ? 'Create one' : 'Sign in'}
          </a>
        </div>
      </div>
    </div>
  );
}
