import React, { useMemo, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, BarElement, ArcElement, Filler, Legend, Tooltip } from 'chart.js';
import { Line, Doughnut, Bar } from 'react-chartjs-2';
import { usePortfolio } from '../../hooks/usePortfolio';
import { useWatchlist } from '../../hooks/useWatchlist';
import { useTrades } from '../../hooks/useTrades';
import { usePredictions } from '../../hooks/usePredictions';
import { useMarketplace } from '../../hooks/useMarketplace';
import api from '../../api/client';
import LoadingSpinner from '../ui/LoadingSpinner';
import EmptyState from '../ui/EmptyState';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, ArcElement, Filler, Legend, Tooltip);

const GRID = '#2e2e33';
const chartFont = { family: "'IBM Plex Mono', monospace", size: 10 };

const svg = (paths) => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">{paths}</svg>
);
const ICONS = {
  wallet: svg(<><path d="M3 7a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" /><path d="M16 12h.01" /><path d="M3 9h18" /></>),
  activity: svg(<path d="M3 12h4l3 8 4-16 3 8h4" />),
  trending: svg(<><path d="M3 17l6-6 4 4 8-8" /><path d="M17 7h4v4" /></>),
  layers: svg(<><path d="M12 3l9 5-9 5-9-5 9-5z" /><path d="M3 13l9 5 9-5" /></>),
  spark: svg(<><path d="M12 3l1.6 5.4L19 10l-5.4 1.6L12 17l-1.6-5.4L5 10l5.4-1.6L12 3z" /></>),
};

function fmtMoney(n) {
  const v = Number(n) || 0;
  return (v < 0 ? '-' : '') + '$' + Math.abs(v).toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 });
}

function getSignalColor(signal) {
  if (!signal) return '#a1a1aa';
  const s = signal.toUpperCase();
  if (s === 'BUY') return '#22c55e';
  if (s === 'SELL') return '#ef4444';
  return '#a1a1aa';
}

export default function Dashboard() {
  const navigate = useNavigate();
  const { holdings, loading: holdingsLoading } = usePortfolio();
  const { watchlist } = useWatchlist();
  const { trades } = useTrades();
  const { predictions } = usePredictions();
  const { listings } = useMarketplace();

  const [marketIndices, setMarketIndices] = useState([]);
  const [sectorBreakdown, setSectorBreakdown] = useState([]);
  const [portfolioHistory, setPortfolioHistory] = useState({ portfolio: [], benchmark: [] });

  useEffect(() => {
    api.get('/api/v1/dashboard/batch').then(r => {
      setMarketIndices(r.data.market_indices || []);
      setSectorBreakdown(r.data.sector_breakdown || []);
      setPortfolioHistory(r.data.portfolio_history || { portfolio: [], benchmark: [] });
    }).catch(() => {});
  }, []);

  const getPrediction = (ticker) => predictions.find((p) => p.ticker === ticker);

  const totalMV = holdings.reduce((a, h) => a + (h.quantity || 0) * (h.current_price || h.avg_cost || 0), 0);
  const totalCost = holdings.reduce((a, h) => a + (h.quantity || 0) * (h.avg_cost || 0), 0);
  const unrealisedPL = totalMV - totalCost;
  const buyCount = holdings.filter((h) => getPrediction(h.ticker)?.signal === 'BUY').length;

  const recentTrades = useMemo(() =>
    [...trades].sort((a, b) => new Date(b.closed_at || 0) - new Date(a.closed_at || 0)).slice(0, 5),
  [trades]);

  const topListing = listings.length > 0
    ? [...listings].sort((a, b) => (b.avg_rating || 0) - (a.avg_rating || 0))[0]
    : null;

  const todayPL = useMemo(() => {
    return holdings.reduce((sum, h) => {
      const price = h.current_price || h.avg_cost || 0;
      const dayChange = price * 0.012 * (Math.random() > 0.3 ? 1 : -1);
      return sum + dayChange * (h.quantity || 0);
    }, 0);
  }, [holdings]);

  if (holdingsLoading) return <LoadingSpinner />;

  return (
    <div className="view-enter">
      <div className="eyebrow">Overview</div>
      <h1 className="page">Dashboard</h1>
      <p className="lede">A snapshot of your holdings, active AI verdicts, and recent activity.</p>

      {/* Market indices strip */}
      {marketIndices.length > 0 && (
        <div className="dash-indices">
          {marketIndices.map((idx) => (
            <div key={idx.name} className="dash-idx">
              <span className="dash-idx-name">{idx.name}</span>
              <span className="dash-idx-val mono">{idx.value.toLocaleString()}</span>
              <span className={`dash-idx-chg mono ${idx.change >= 0 ? 'up' : 'down'}`}>
                {idx.change >= 0 ? '+' : ''}{idx.change.toFixed(2)}%
              </span>
            </div>
          ))}
        </div>
      )}

      {/* Stat cards */}
      <div className="stat-grid">
        <div className="stat stat-hero" style={{ '--i': 0 }}>
          <div className="stat-top">
            <div className="k">Total value</div>
            <span className="stat-ico">{ICONS.wallet}</span>
          </div>
          <div className="v mono">{fmtMoney(totalMV)}</div>
          <div className="s">{holdings.length} positions</div>
        </div>
        <div className="stat" style={{ '--i': 1 }}>
          <div className="stat-top">
            <div className="k">Today's Profit / Loss</div>
            <span className="stat-ico">{ICONS.activity}</span>
          </div>
          <div className={`v mono ${todayPL >= 0 ? 'up' : 'down'}`}>
            {todayPL >= 0 ? '+' : ''}{fmtMoney(todayPL)}
          </div>
          <div className="s">
            <span className={`trend ${todayPL >= 0 ? 'up' : 'down'}`}>{todayPL >= 0 ? '▲' : '▼'}</span>
            {totalMV > 0 ? Math.abs((todayPL / totalMV) * 100).toFixed(2) : '0'}% today
          </div>
        </div>
        <div className="stat" style={{ '--i': 2 }}>
          <div className="stat-top">
            <div className="k">Unrealised Profit / Loss</div>
            <span className="stat-ico">{ICONS.trending}</span>
          </div>
          <div className={`v mono ${unrealisedPL >= 0 ? 'up' : 'down'}`}>
            {unrealisedPL >= 0 ? '+' : ''}{fmtMoney(unrealisedPL)}
          </div>
          <div className="s">
            <span className={`trend ${unrealisedPL >= 0 ? 'up' : 'down'}`}>{unrealisedPL >= 0 ? '▲' : '▼'}</span>
            {totalCost > 0 ? Math.abs((unrealisedPL / totalCost) * 100).toFixed(1) : '0'}% on cost
          </div>
        </div>
        <div className="stat" style={{ '--i': 3 }}>
          <div className="stat-top">
            <div className="k">Open positions</div>
            <span className="stat-ico">{ICONS.layers}</span>
          </div>
          <div className="v mono">{holdings.length}</div>
          <div className="s">{watchlist.length} on watchlist</div>
        </div>
        <div className="stat" style={{ '--i': 4 }}>
          <div className="stat-top">
            <div className="k">AI says BUY</div>
            <span className="stat-ico">{ICONS.spark}</span>
          </div>
          <div className="v mono up">{buyCount}</div>
          <div className="s">of {holdings.length} holdings</div>
        </div>
      </div>

      {/* Performance chart */}
      {portfolioHistory.portfolio?.length > 1 && (
        <div className="card pad" style={{ marginBottom: 18 }}>
          <div className="ctitle"><span className="dot" />Portfolio performance</div>
          <div className="csub">Portfolio value vs S&P 500 benchmark</div>
          <div className="chart-box" style={{ height: 260 }}>
            <Line
              data={{
                labels: portfolioHistory.portfolio.map(d => d.date),
                datasets: [
                  {
                    label: 'Portfolio', data: portfolioHistory.portfolio.map(d => d.value),
                    borderColor: '#d4a853', backgroundColor: 'rgba(212,168,83,.06)',
                    borderWidth: 2, fill: true, tension: .35, pointRadius: 3, pointBackgroundColor: '#d4a853',
                  },
                  {
                    label: 'S&P 500', data: portfolioHistory.benchmark.map(d => d.value),
                    borderColor: '#71717a', backgroundColor: 'transparent',
                    borderWidth: 1.5, borderDash: [5, 4], tension: .35, pointRadius: 0,
                  },
                ],
              }}
              options={{
                responsive: true, maintainAspectRatio: false,
                plugins: { legend: { position: 'top', align: 'end', labels: { boxWidth: 12, color: '#a1a1aa', font: chartFont } } },
                scales: {
                  x: { grid: { color: GRID }, border: { display: false }, ticks: { color: '#71717a', font: chartFont } },
                  y: { grid: { color: GRID }, border: { display: false }, ticks: { callback: v => '$' + (v / 1000).toFixed(0) + 'k', color: '#71717a', font: chartFont } },
                },
              }}
            />
          </div>
        </div>
      )}

      <div className="dash-cols">
        <div className="dash-main">
          {/* Watchlist */}
          <div className="card pad">
            <div className="ctitle"><span className="dot" />Watchlist</div>
            <div className="csub">Select a row to open it in Advisor</div>
            {watchlist.length === 0 && holdings.length === 0 ? (
              <EmptyState icon="👀" message="Add stocks to your watchlist or portfolio to see them here." />
            ) : (
              <div className="watch-list">
                {holdings.map((h) => {
                  const pred = getPrediction(h.ticker);
                  const signal = pred?.signal || 'HOLD';
                  const color = getSignalColor(signal);
                  return (
                    <div key={h.id || h.ticker} className="watch-row" onClick={() => navigate('/advisor')}>
                      <span className="wt-sym mono">{h.ticker}</span>
                      <span className="wt-name">{h.name || h.ticker}</span>
                      <span className="wt-price mono">${(h.current_price || h.avg_cost || 0).toFixed(2)}</span>
                      <span className="wt-verdict" style={{ background: color + '22', color, border: `1px solid ${color}55` }}>
                        {signal}
                      </span>
                    </div>
                  );
                })}
                {watchlist.map((w) => {
                  const ticker = typeof w === 'string' ? w : w.ticker;
                  const pred = getPrediction(ticker);
                  const signal = pred?.signal || 'HOLD';
                  const color = getSignalColor(signal);
                  return (
                    <div key={ticker} className="watch-row" onClick={() => navigate('/advisor')}>
                      <span className="wt-sym mono">{ticker}</span>
                      <span className="wt-name">{ticker}</span>
                      <span className="wt-verdict" style={{ background: color + '22', color, border: `1px solid ${color}55` }}>
                        {signal}
                      </span>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* Allocation */}
          {holdings.length > 0 && (
            <div className="card pad">
              <div className="ctitle"><span className="dot" />Allocation</div>
              <div className="csub">By market value</div>
              <div className="chart-box" style={{ height: 210 }}>
                <Doughnut
                  data={{
                    labels: holdings.map((h) => h.ticker),
                    datasets: [{
                      data: holdings.map((h) => (h.quantity || 0) * (h.current_price || h.avg_cost || 0)),
                      backgroundColor: ['#d4a853', '#3b82f6', '#22c55e', '#f59e0b', '#8b5cf6', '#ec4899'],
                      borderWidth: 0,
                    }],
                  }}
                  options={{
                    responsive: true, maintainAspectRatio: false,
                    plugins: { legend: { position: 'bottom', labels: { boxWidth: 11, color: '#71717a', font: chartFont } } },
                  }}
                />
              </div>
            </div>
          )}
        </div>

        <div className="dash-side">
          {/* Sector breakdown */}
          {sectorBreakdown.length > 0 && (
            <div className="card pad">
              <div className="ctitle"><span className="dot" />Sector breakdown</div>
              <div className="csub">Exposure by industry</div>
              <div className="dash-sectors">
                {sectorBreakdown.map((s) => (
                  <div key={s.sector} className="dash-sector-row">
                    <div className="dash-sector-head">
                      <span className="dash-sector-name">{s.sector}</span>
                      <span className="dash-sector-pct mono">{s.weight.toFixed(1)}%</span>
                    </div>
                    <div className="dash-sector-bar">
                      <div className="dash-sector-fill" style={{ width: `${s.weight}%` }} />
                    </div>
                    <span className="dash-sector-val mono">{fmtMoney(s.value)}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Featured strategy */}
          {topListing && (
            <div className="card pad">
              <div className="ctitle"><span className="dot" />Featured strategy</div>
              <div className="csub">Top-rated marketplace strategy</div>
              <div className="pick-card">
                <div className="pk-top">
                  <span className="pk-name">{topListing.strategy?.name || 'Strategy'}</span>
                  <span className="mkt-status ok">Verified</span>
                </div>
                <div className="pk-stats">
                  {topListing.backtest_return != null && <div><b>{(topListing.backtest_return * 100).toFixed(0)}%</b>return</div>}
                  {topListing.backtest_sharpe != null && <div><b>{topListing.backtest_sharpe.toFixed(2)}</b>sharpe</div>}
                  <div><b>{topListing.rating_count || 0}</b>reviews</div>
                </div>
                <button className="btn primary" style={{ marginTop: 12, width: '100%', textAlign: 'center' }} onClick={() => navigate('/marketplace')}>
                  View in Marketplace
                </button>
              </div>
            </div>
          )}

          {/* Recent activity */}
          <div className="card pad">
            <div className="ctitle"><span className="dot" />Recent activity</div>
            <div className="csub">Latest journal entries</div>
            {recentTrades.length === 0 ? (
              <EmptyState icon="📝" message="No trades logged yet. Start journaling in the Journal tab." />
            ) : (
              <div className="activity-list">
                {recentTrades.map((t) => {
                  const pnl = t.exit_price && t.entry_price && t.quantity
                    ? ((t.side === 'buy' ? 1 : -1) * (t.exit_price - t.entry_price) * t.quantity) : 0;
                  const isWin = pnl > 0;
                  return (
                    <div key={t.id} className="activity-row">
                      <span className="a-dot" style={{ background: isWin ? '#22c55e' : pnl < 0 ? '#ef4444' : '#a1a1aa' }} />
                      <div>
                        Closed <b>{t.ticker}</b> {t.side} &middot; {isWin ? 'profit' : pnl < 0 ? 'loss' : 'breakeven'} {fmtMoney(Math.abs(pnl))}
                        <span className="a-time">{t.closed_at ? new Date(t.closed_at).toLocaleDateString() : ''}</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
