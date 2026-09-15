import React from 'react';
import { useNavigate } from 'react-router-dom';

const Icon = ({ d }) => (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">
    {d}
  </svg>
);

const FEATURES = [
  {
    title: 'Explainable verdicts',
    body: 'A clear BUY, HOLD or SELL for any stock — with a confidence level and the reasoning behind it, never a black box.',
    icon: <><path d="M9 11l3 3L22 4" /><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11" /></>,
  },
  {
    title: 'Six-factor scoring',
    body: 'Every stock is scored on sentiment, momentum, valuation, volatility, volume and growth — weighted to your own strategy.',
    icon: <><path d="M3 3v18h18" /><path d="M7 15l3-4 3 2 5-7" /></>,
  },
  {
    title: 'AI news sentiment',
    body: 'FinBERT reads recent financial headlines and turns market mood into a signal you can actually use.',
    icon: <><path d="M4 4h16v12H8l-4 4V4z" /><path d="M8 9h8M8 12h5" /></>,
  },
  {
    title: 'Backtesting',
    body: 'See how a strategy would have performed on years of real data — return, Sharpe, win rate, drawdown and more.',
    icon: <><path d="M3 3v18h18" /><path d="M7 13l3 3 7-8" /><circle cx="7" cy="13" r="1" /><circle cx="10" cy="16" r="1" /></>,
  },
  {
    title: 'Portfolio & journal',
    body: 'Track holdings with live prices and unrealised P/L, and log trades to learn from your own win rate and equity curve.',
    icon: <><path d="M3 7h18v13H3z" /><path d="M3 7l3-4h12l3 4M8 12h8" /></>,
  },
  {
    title: 'Strategy marketplace',
    body: 'Verified analysts publish backtest-validated strategies. Browse, buy and apply the ones that fit your style.',
    icon: <><path d="M3 9l1-5h16l1 5" /><path d="M4 9v11h16V9" /><path d="M9 20v-6h6v6" /></>,
  },
];

const STEPS = [
  { n: '1', title: 'Pick a stock', body: 'Search any ticker or choose a popular one. The analysis runs instantly.' },
  { n: '2', title: 'Read the verdict', body: 'Get a BUY / HOLD / SELL call with a confidence score and a factor-by-factor breakdown.' },
  { n: '3', title: 'Validate it', body: 'Backtest the strategy on historical data before you trust it with a single decision.' },
  { n: '4', title: 'Track & improve', body: 'Manage a portfolio and keep a trading journal so you learn from every trade.' },
];

const ROLES = [
  { role: 'Investor', body: 'Get AI verdicts, manage a portfolio and watchlist, keep a journal, and buy strategies from the marketplace.' },
  { role: 'Financial Analyst', body: 'Everything an investor can do, plus design factor strategies and publish backtest-verified ones for others.' },
  { role: 'Administrator', body: 'Review and approve strategies, manage users, and configure the platform’s quality thresholds.' },
];

export default function Landing() {
  const navigate = useNavigate();
  const go = () => navigate('/auth');

  return (
    <div className="lp">
      {/* Nav */}
      <header className="lp-nav">
        <div className="lp-brand">
          <div className="lp-mark">SP</div>
          Stock<span>Pilot</span>
        </div>
        <div className="lp-nav-actions">
          <button className="lp-btn ghost" onClick={go}>Sign in</button>
          <button className="lp-btn gold" onClick={go}>Get started</button>
        </div>
      </header>

      {/* Hero */}
      <section className="lp-hero">
        <div className="lp-eyebrow">AI-powered investment advisory</div>
        <h1 className="lp-title">Invest with clarity,<br /><span>not guesswork.</span></h1>
        <p className="lp-sub">
          StockPilot turns scattered market data into one clear, explainable recommendation.
          For any stock it combines a six-factor scoring engine, an XGBoost model and FinBERT
          news sentiment into a BUY, HOLD or SELL call — with the reasoning shown, and a backtest
          to prove it.
        </p>
        <div className="lp-cta-row">
          <button className="lp-btn gold lg" onClick={go}>Get started free</button>
          <button className="lp-btn ghost lg" onClick={go}>Sign in</button>
        </div>
        <div className="lp-pills">
          <span className="lp-pill">Six-factor engine</span>
          <span className="lp-pill">XGBoost model</span>
          <span className="lp-pill">FinBERT sentiment</span>
          <span className="lp-pill">Backtesting</span>
        </div>
      </section>

      {/* Features */}
      <section className="lp-section">
        <div className="lp-sec-head">
          <div className="lp-eyebrow">What you get</div>
          <h2 className="lp-h2">Everything you need to decide with confidence</h2>
        </div>
        <div className="lp-grid">
          {FEATURES.map((f) => (
            <div key={f.title} className="lp-card">
              <div className="lp-card-icon"><Icon d={f.icon} /></div>
              <h3>{f.title}</h3>
              <p>{f.body}</p>
            </div>
          ))}
        </div>
      </section>

      {/* How it works */}
      <section className="lp-section alt">
        <div className="lp-sec-head">
          <div className="lp-eyebrow">How it works</div>
          <h2 className="lp-h2">From ticker to decision in four steps</h2>
        </div>
        <div className="lp-steps">
          {STEPS.map((s) => (
            <div key={s.n} className="lp-step">
              <div className="lp-step-n">{s.n}</div>
              <h3>{s.title}</h3>
              <p>{s.body}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Roles */}
      <section className="lp-section">
        <div className="lp-sec-head">
          <div className="lp-eyebrow">Built for everyone</div>
          <h2 className="lp-h2">One platform, three roles</h2>
        </div>
        <div className="lp-roles">
          {ROLES.map((r) => (
            <div key={r.role} className="lp-role">
              <div className="lp-role-name">{r.role}</div>
              <p>{r.body}</p>
            </div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="lp-band">
        <h2>Ready to make smarter investment decisions?</h2>
        <p>Create a free account and analyse your first stock in seconds.</p>
        <button className="lp-btn gold lg" onClick={go}>Get started</button>
      </section>

      {/* Footer */}
      <footer className="lp-footer">
        <div className="lp-brand small">
          <div className="lp-mark">SP</div>
          Stock<span>Pilot</span>
        </div>
        <p className="lp-disclaimer">
          StockPilot is an educational decision-support tool, not licensed financial advice.
          It does not execute trades or manage money. All figures are illustrative.
        </p>
        <div className="lp-copy">© 2026 StockPilot · Group 13</div>
      </footer>
    </div>
  );
}
