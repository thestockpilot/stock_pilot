import React, { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMarketplace } from '../../hooks/useMarketplace';
import LoadingSpinner from '../ui/LoadingSpinner';
import EmptyState from '../ui/EmptyState';

const FACTORS = ['Sentiment', 'Momentum', 'Valuation', 'Volatility', 'Volume', 'Growth'];
const SORT_OPTIONS = [
  { value: 'rating', label: 'Top rated' },
  { value: 'return', label: 'Best return' },
  { value: 'sharpe', label: 'Best Sharpe' },
  { value: 'price_low', label: 'Price: low to high' },
  { value: 'newest', label: 'Newest' },
];

export default function Marketplace() {
  const navigate = useNavigate();
  const { listings, loading } = useMarketplace();
  const [search, setSearch] = useState('');
  const [sortBy, setSortBy] = useState('rating');
  const [filterStatus, setFilterStatus] = useState('all');

  const filtered = useMemo(() => {
    let items = [...listings];
    if (search) {
      const q = search.toLowerCase();
      items = items.filter(l => (l.strategy?.name || '').toLowerCase().includes(q) || (l.strategy?.owner?.full_name || '').toLowerCase().includes(q));
    }
    if (filterStatus === 'verified') items = items.filter(l => l.status === 'verified' || l.status === 'listed');
    if (filterStatus === 'free') items = items.filter(l => !l.price_cents);
    items.sort((a, b) => {
      switch (sortBy) {
        case 'return': return (b.backtest_return || 0) - (a.backtest_return || 0);
        case 'sharpe': return (b.backtest_sharpe || 0) - (a.backtest_sharpe || 0);
        case 'price_low': return (a.price_cents || 0) - (b.price_cents || 0);
        case 'newest': return b.id - a.id;
        default: return (b.avg_rating || 0) - (a.avg_rating || 0);
      }
    });
    return items;
  }, [listings, search, sortBy, filterStatus]);

  const purchased = listings.filter(l => l.status === 'verified' || l.status === 'listed').slice(0, 2);

  if (loading) return <LoadingSpinner />;

  return (
    <div className="view-enter">
      <div className="eyebrow">Marketplace</div>
      <h1 className="page">Strategy Marketplace</h1>
      <p className="lede">Verified factor weight configurations published by analysts. Every strategy must pass an objective backtest against the thresholds below before it can be listed.</p>

      <div className="thresh-grid">
        {[
          { op: '≥', val: '100', label: 'Min. trades', icon: (
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M3 3v18h18"/><path d="M7 16l4-8 4 4 6-6"/>
            </svg>
          )},
          { op: '≥', val: '65%', label: 'Win rate', icon: (
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/>
            </svg>
          )},
          { op: '≥', val: '1.0', label: 'Sharpe ratio', icon: (
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
            </svg>
          )},
          { op: '≤', val: '15%', label: 'Max drawdown', icon: (
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 2v20M2 12h20"/><path d="M2 7h5M17 7h5M2 17h5M17 17h5"/>
            </svg>
          )},
          { op: '≥', val: '1.5', label: 'Profit factor', icon: (
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 1v22M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
            </svg>
          )},
        ].map((t, i) => (
          <div key={i} className={`thresh-card${t.featured ? ' featured' : ''}`}>
            <div className={`thresh-icon${t.featured ? ' featured' : ''}`}>{t.icon}</div>
            <div className="thresh-val">{t.op} {t.val}</div>
            <div className="thresh-label">{t.label}</div>
          </div>
        ))}
      </div>

      {/* My strategies */}
      {purchased.length > 0 && (
        <>
          <div className="sec-label">My strategies</div>
          <div className="mkt-owned-grid">
            {purchased.map((l) => (
              <div key={'own-' + l.id} className="mkt-owned-card">
                <div className="mkt-owned-top">
                  <span className="mkt-owned-name">{l.strategy?.name}</span>
                  <span className="mkt-status ok">Active</span>
                </div>
                <div className="mkt-owned-stats">
                  {l.backtest_return != null && <span className="mono up">{(l.backtest_return * 100).toFixed(0)}% return</span>}
                  {l.backtest_sharpe != null && <span className="mono">{l.backtest_sharpe.toFixed(2)} Sharpe</span>}
                </div>
                <button className="btn primary" style={{ width: '100%', marginTop: 10 }} onClick={() => navigate('/advisor')}>
                  Open in Advisor
                </button>
              </div>
            ))}
          </div>
        </>
      )}

      {/* Search and filter */}
      <div className="sec-label">Available strategies</div>
      <div className="mkt-toolbar">
        <input className="mkt-search" value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search strategies or analysts..." />
        <select className="mkt-sort" value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
          {SORT_OPTIONS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
        </select>
        <div className="mkt-filter-tabs">
          {[['all', 'All'], ['verified', 'Verified'], ['free', 'Free']].map(([v, l]) => (
            <button key={v} className={`mkt-filter-tab${filterStatus === v ? ' active' : ''}`} onClick={() => setFilterStatus(v)}>{l}</button>
          ))}
        </div>
      </div>
      {filtered.length === 0 ? (
        <EmptyState icon="🏪" message={search ? 'No strategies match your search.' : 'No strategies listed yet.'} />
      ) : (
        <div className="strategy-grid">
          {filtered.map((listing) => {
            const strategy = listing.strategy || {};
            const weights = strategy.weights || {};
            const isVerified = listing.status === 'verified' || listing.status === 'listed';
            const stars = Math.round(listing.avg_rating || 0);
            const starsStr = '★'.repeat(stars) + '☆'.repeat(5 - stars);
            const price = listing.price_cents ? `$${(listing.price_cents / 100).toFixed(2)}` : 'Free';

            return (
              <div key={listing.id} className="mkt-card">
                <div className="mkt-top">
                  <div>
                    <h3>{strategy.name || 'Unnamed Strategy'}</h3>
                    <div className="mkt-by mono">by {strategy.owner?.full_name || 'StockPilot'}</div>
                    <div className="mkt-stars">{starsStr}</div>
                  </div>
                  <span className={`mkt-status ${isVerified ? 'ok' : 'review'}`}>
                    {isVerified ? 'Verified' : 'In Review'}
                  </span>
                </div>

                <div className="mkt-weights">
                  {FACTORS.map((f) => {
                    const key = f.toLowerCase();
                    const val = weights[key];
                    return val != null ? <span key={f} className="mkt-chip">{f} {val}%</span> : null;
                  })}
                </div>

                <div className="mkt-stats">
                  {listing.backtest_return != null && (
                    <div><div className="v">{(listing.backtest_return * 100).toFixed(0)}%</div><div className="k">Return</div></div>
                  )}
                  {listing.backtest_sharpe != null && (
                    <div><div className="v">{listing.backtest_sharpe.toFixed(2)}</div><div className="k">Sharpe ratio</div></div>
                  )}
                  <div><div className="v">{listing.sales_count || 0}</div><div className="k">Sales</div></div>
                  <div><div className="v">{listing.rating_count || 0}</div><div className="k">Reviews</div></div>
                </div>

                <div className="mkt-bottom">
                  <span className="mkt-price">{price}</span>
                  {isVerified ? (
                    <button className="btn primary" onClick={() => navigate('/advisor')}>Apply in Advisor</button>
                  ) : (
                    <button className="btn" disabled style={{ opacity: .5 }}>Awaiting verification</button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      <div className="sec-label">For analysts</div>
      <div className="card pad creator-cta">
        <div>
          <div className="ctitle"><span className="dot" />Publish a strategy</div>
          <div className="csub" style={{ marginBottom: 0 }}>Analysts design factor weights, submit for automatic backtesting, and earn from every sale. The underlying model is not modified.</div>
        </div>
        <button className="btn primary">Apply as analyst</button>
      </div>
    </div>
  );
}
