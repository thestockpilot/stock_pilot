import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import api from '../../api/client';
import Toggle from '../ui/Toggle';
import { MOCK_BILLING_HISTORY } from '../../data/mock';

const TABS = [
  { key: 'profile', label: 'Profile' },
  { key: 'security', label: 'Security' },
  { key: 'notifications', label: 'Notifications' },
  { key: 'preferences', label: 'Preferences' },
  { key: 'subscription', label: 'Subscription' },
  { key: 'api', label: 'API access' },
];

export default function Settings() {
  const [searchParams] = useSearchParams();
  const { user, updateUser } = useAuth();
  const [activeTab, setActiveTab] = useState(searchParams.get('tab') || 'profile');
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');

  const [profileForm, setProfileForm] = useState({
    first_name: '', last_name: '', email: '', phone: '', bio: '',
  });

  const [passwordForm, setPasswordForm] = useState({
    current: '', new_password: '', confirm: '',
  });

  const [notifPrefs, setNotifPrefs] = useState({
    verdict_changes: true, news_sentiment: true, price_alerts: true,
    marketplace_updates: false, weekly_report: true, product_news: false,
  });

  const [securityToggles, setSecurityToggles] = useState({
    authenticator: false, sms_backup: false, sign_in_alerts: true,
  });

  useEffect(() => {
    if (user) {
      const names = (user.full_name || '').split(' ');
      setProfileForm({
        first_name: names[0] || '',
        last_name: names.slice(1).join(' ') || '',
        email: user.email || '',
        phone: user.phone || '',
        bio: user.bio || '',
      });
    }
  }, [user]);

  useEffect(() => {
    const tab = searchParams.get('tab');
    if (tab && TABS.some((t) => t.key === tab)) setActiveTab(tab);
  }, [searchParams]);

  const handleSaveProfile = async () => {
    setSaving(true);
    setMessage('');
    try {
      const { data } = await api.put('/api/v1/users/me', {
        full_name: `${profileForm.first_name} ${profileForm.last_name}`.trim(),
        email: profileForm.email,
        phone: profileForm.phone,
        bio: profileForm.bio,
      });
      updateUser(data);
      setMessage('Profile saved successfully.');
    } catch (err) {
      setMessage(err.response?.data?.detail || 'Failed to save profile.');
    } finally {
      setSaving(false);
    }
  };

  const handleUpdatePassword = async () => {
    if (passwordForm.new_password !== passwordForm.confirm) {
      setMessage('Passwords do not match.');
      return;
    }
    setSaving(true);
    setMessage('');
    try {
      await api.put('/api/v1/users/me/password', {
        current_password: passwordForm.current,
        new_password: passwordForm.new_password,
      });
      setMessage('Password updated successfully.');
      setPasswordForm({ current: '', new_password: '', confirm: '' });
    } catch (err) {
      setMessage(err.response?.data?.detail || 'Failed to update password.');
    } finally {
      setSaving(false);
    }
  };

  const initials = user?.full_name
    ? user.full_name.split(' ').map((w) => w[0]).join('').toUpperCase().slice(0, 2)
    : 'SP';

  return (
    <div className="view-enter">
      <div className="eyebrow">Account</div>
      <h1 className="page">Settings</h1>
      <p className="lede">Manage your profile, security, notifications and subscription.</p>

      {message && (
        <div style={{ marginTop: 12, padding: '10px 14px', borderRadius: 8, background: 'rgba(212,168,83,.08)', border: '1px solid rgba(212,168,83,.25)', color: 'var(--accent)', fontSize: 13, fontFamily: 'var(--mono)' }}>
          {message}
        </div>
      )}

      <div className="settings-layout">
        <div className="settings-nav">
          {TABS.map((tab) => (
            <div key={tab.key} className={`s-item${activeTab === tab.key ? ' on' : ''}`} onClick={() => setActiveTab(tab.key)}>
              {tab.label}
            </div>
          ))}
        </div>

        <div>
          {/* Profile */}
          {activeTab === 'profile' && (
            <div className="s-card">
              <h3>Profile</h3>
              <div className="s-sub">Your public information and account details.</div>
              <div className="avatar-row">
                <div className="avatar-circle">{initials}</div>
                <div>
                  <button className="btn primary">Upload new photo</button>
                  <button className="btn" style={{ marginLeft: 6 }}>Remove</button>
                  <div className="mini-note">JPG or PNG, up to 2 MB.</div>
                </div>
              </div>
              <div className="s-form" style={{ marginTop: 22 }}>
                <div><label>First name</label><input value={profileForm.first_name} onChange={(e) => setProfileForm({ ...profileForm, first_name: e.target.value })} /></div>
                <div><label>Last name</label><input value={profileForm.last_name} onChange={(e) => setProfileForm({ ...profileForm, last_name: e.target.value })} /></div>
                <div><label>Email address</label><input value={profileForm.email} onChange={(e) => setProfileForm({ ...profileForm, email: e.target.value })} /></div>
                <div><label>Phone number</label><input value={profileForm.phone} onChange={(e) => setProfileForm({ ...profileForm, phone: e.target.value })} /></div>
                <div className="full"><label>Bio</label><textarea value={profileForm.bio} onChange={(e) => setProfileForm({ ...profileForm, bio: e.target.value })} /></div>
              </div>
              <div className="s-actions">
                <button className="btn primary" onClick={handleSaveProfile} disabled={saving}>{saving ? 'Saving...' : 'Save changes'}</button>
                <button className="btn">Cancel</button>
              </div>
            </div>
          )}

          {/* Security */}
          {activeTab === 'security' && (
            <>
              <div className="s-card">
                <h3>Password</h3>
                <div className="s-sub">Set a strong password to keep your account secure.</div>
                <div className="s-form">
                  <div className="full"><label>Current password</label><input type="password" value={passwordForm.current} onChange={(e) => setPasswordForm({ ...passwordForm, current: e.target.value })} /></div>
                  <div><label>New password</label><input type="password" placeholder="At least 8 characters" value={passwordForm.new_password} onChange={(e) => setPasswordForm({ ...passwordForm, new_password: e.target.value })} /></div>
                  <div><label>Confirm new password</label><input type="password" value={passwordForm.confirm} onChange={(e) => setPasswordForm({ ...passwordForm, confirm: e.target.value })} /></div>
                </div>
                <div className="s-actions"><button className="btn primary" onClick={handleUpdatePassword} disabled={saving}>Update password</button></div>
              </div>
              <div className="s-card">
                <h3>Two-factor authentication</h3>
                <div className="s-sub">Add an extra layer of security to your sign-in.</div>
                <div className="s-toggle-row">
                  <div><div className="s-t-title">Authenticator app</div><div className="s-t-desc">Use an app like Google Authenticator to generate one-time codes.</div></div>
                  <Toggle on={securityToggles.authenticator} onToggle={(v) => setSecurityToggles({ ...securityToggles, authenticator: v })} />
                </div>
                <div className="s-toggle-row">
                  <div><div className="s-t-title">SMS backup codes</div><div className="s-t-desc">Receive a verification code by text as a fallback method.</div></div>
                  <Toggle on={securityToggles.sms_backup} onToggle={(v) => setSecurityToggles({ ...securityToggles, sms_backup: v })} />
                </div>
                <div className="s-toggle-row">
                  <div><div className="s-t-title">Sign-in email alerts</div><div className="s-t-desc">Get notified whenever a new device signs in to your account.</div></div>
                  <Toggle on={securityToggles.sign_in_alerts} onToggle={(v) => setSecurityToggles({ ...securityToggles, sign_in_alerts: v })} />
                </div>
              </div>
            </>
          )}

          {/* Notifications */}
          {activeTab === 'notifications' && (
            <div className="s-card">
              <h3>Notification preferences</h3>
              <div className="s-sub">Choose how you want to be notified about activity on your account.</div>
              {[
                { key: 'verdict_changes', title: 'Verdict changes', desc: 'When the AI switches Buy, Hold or Sell on a watched stock.' },
                { key: 'news_sentiment', title: 'News sentiment alerts', desc: 'Strongly positive or negative headlines on your holdings.' },
                { key: 'price_alerts', title: 'Price alerts', desc: 'Stop-loss triggers and price target breaches.' },
                { key: 'marketplace_updates', title: 'Marketplace updates', desc: 'New verified strategies and analyst publications.' },
                { key: 'weekly_report', title: 'Weekly performance report', desc: 'Email summary of portfolio performance every Sunday.' },
                { key: 'product_news', title: 'Product news', desc: 'Occasional emails about new features and improvements.' },
              ].map((item) => (
                <div key={item.key} className="s-toggle-row">
                  <div><div className="s-t-title">{item.title}</div><div className="s-t-desc">{item.desc}</div></div>
                  <Toggle on={notifPrefs[item.key]} onToggle={(v) => setNotifPrefs({ ...notifPrefs, [item.key]: v })} />
                </div>
              ))}
            </div>
          )}

          {/* Preferences */}
          {activeTab === 'preferences' && (
            <div className="s-card">
              <h3>Display and locale</h3>
              <div className="s-sub">Personalise how the interface looks and behaves.</div>
              <div className="s-form">
                <div><label>Theme</label><select defaultValue="dark"><option value="dark">Dark (default)</option><option value="light">Light</option><option value="system">System</option></select></div>
                <div><label>Base currency</label><select defaultValue="USD"><option value="USD">USD ($)</option><option value="EUR">EUR (€)</option><option value="GBP">GBP (£)</option><option value="JPY">JPY (¥)</option></select></div>
                <div><label>Timezone</label><select defaultValue="utc-8"><option value="utc-8">UTC−08:00 Pacific Time</option><option value="utc">UTC±00:00 UTC</option><option value="utc+1">UTC+01:00 Central Europe</option><option value="utc+5.5">UTC+05:30 India Standard</option></select></div>
                <div><label>Number format</label><select defaultValue="us"><option value="us">1,234.56 (US)</option><option value="eu">1.234,56 (EU)</option><option value="fr">1 234,56 (FR)</option></select></div>
                <div><label>Default landing tab</label><select defaultValue="dashboard"><option value="dashboard">Dashboard</option><option value="portfolio">Portfolio</option><option value="advisor">Advisor</option><option value="marketplace">Marketplace</option></select></div>
                <div><label>Chart style</label><select defaultValue="line"><option value="line">Line</option><option value="candlestick">Candlestick</option><option value="area">Area</option></select></div>
              </div>
              <div className="s-actions"><button className="btn primary">Save preferences</button></div>
            </div>
          )}

          {/* Subscription */}
          {activeTab === 'subscription' && (
            <>
              <div className="s-card">
                <h3>Current plan</h3>
                <div className="s-sub">Manage your subscription and payment method.</div>
                <div className="plan-card">
                  <div className="plan-name">Pro plan</div>
                  <div className="plan-price">$19<small>/ month</small></div>
                  <ul>
                    <li>Live AI verdicts on unlimited tickers</li>
                    <li>Full marketplace strategy access</li>
                    <li>Advanced backtesting and factor analytics</li>
                    <li>Priority email support</li>
                  </ul>
                  <div className="s-actions">
                    <button className="btn primary">Manage billing</button>
                    <button className="btn">Change plan</button>
                    <button className="btn danger">Cancel subscription</button>
                  </div>
                </div>
              </div>
              <div className="s-card">
                <h3>Billing history</h3>
                <div className="s-sub">Recent invoices and payments.</div>
                <div className="journal-table-wrap">
                  <table className="journal-table">
                    <thead>
                      <tr>
                        <th>Date</th>
                        <th>Description</th>
                        <th>Amount</th>
                        <th>Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {MOCK_BILLING_HISTORY.map((b) => (
                        <tr key={b.id}>
                          <td className="mono" style={{ fontSize: 12 }}>{new Date(b.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}</td>
                          <td>{b.description}</td>
                          <td className="mono">${b.amount.toFixed(2)}</td>
                          <td><span className="pill win">{b.status.toUpperCase()}</span></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </>
          )}

          {/* API access */}
          {activeTab === 'api' && (
            <>
              <div className="s-card">
                <h3>API access</h3>
                <div className="s-sub">Programmatic access to your account and StockPilot data.</div>
                <div className="s-form">
                  <div className="full"><label>API key</label><input readOnly value="sp_live_k8x2mQ9vR4wL7nP1tY6jB3hF0cD5aE8g" style={{ fontFamily: 'var(--mono)', letterSpacing: '.5px' }} /></div>
                  <div><label>Created</label><input readOnly value="Jun 15, 2026" /></div>
                  <div><label>Last used</label><input readOnly value="Jul 7, 2026 — 142 calls today" /></div>
                </div>
                <div className="s-actions">
                  <button className="btn primary">Regenerate key</button>
                  <button className="btn">Copy</button>
                  <button className="btn danger">Revoke</button>
                </div>
              </div>
              <div className="s-card">
                <h3>Rate limits</h3>
                <div className="s-sub">Requests permitted under your current plan.</div>
                <div className="s-form">
                  <div><label>Requests per minute</label><input readOnly value="60" /></div>
                  <div><label>Requests per day</label><input readOnly value="10,000" /></div>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
