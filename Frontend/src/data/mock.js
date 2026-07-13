export const MOCK_HOLDINGS = [
  { id: 1, ticker: 'AAPL', quantity: 25, avg_cost: 178.50, current_price: 312.56 },
  { id: 2, ticker: 'NVDA', quantity: 15, avg_cost: 480.00, current_price: 1245.80 },
  { id: 3, ticker: 'MSFT', quantity: 20, avg_cost: 310.00, current_price: 467.35 },
  { id: 4, ticker: 'GOOGL', quantity: 12, avg_cost: 135.00, current_price: 192.18 },
  { id: 5, ticker: 'AMZN', quantity: 18, avg_cost: 145.00, current_price: 213.40 },
  { id: 6, ticker: 'TSLA', quantity: 10, avg_cost: 195.00, current_price: 285.70 },
];

export const MOCK_WATCHLIST = [
  { ticker: 'META' },
  { ticker: 'AMD' },
  { ticker: 'PLTR' },
  { ticker: 'COIN' },
];

export const MOCK_PREDICTIONS = [
  { ticker: 'AAPL', signal: 'HOLD', composite_score: 63, confidence: 77, prob_up: 0.60 },
  { ticker: 'NVDA', signal: 'BUY',  composite_score: 82, confidence: 89, prob_up: 0.84 },
  { ticker: 'MSFT', signal: 'BUY',  composite_score: 74, confidence: 81, prob_up: 0.72 },
  { ticker: 'GOOGL', signal: 'BUY', composite_score: 71, confidence: 78, prob_up: 0.70 },
  { ticker: 'AMZN', signal: 'HOLD', composite_score: 58, confidence: 65, prob_up: 0.55 },
  { ticker: 'TSLA', signal: 'SELL', composite_score: 38, confidence: 72, prob_up: 0.35 },
  { ticker: 'META', signal: 'BUY',  composite_score: 76, confidence: 83, prob_up: 0.75 },
  { ticker: 'AMD',  signal: 'BUY',  composite_score: 69, confidence: 74, prob_up: 0.68 },
  { ticker: 'PLTR', signal: 'HOLD', composite_score: 55, confidence: 60, prob_up: 0.52 },
  { ticker: 'COIN', signal: 'SELL', composite_score: 34, confidence: 68, prob_up: 0.32 },
];

export const MOCK_TRADES = [
  { id: 1, ticker: 'NVDA', side: 'buy', entry_price: 420.00, exit_price: 502.30, stop_loss: 395.00, take_profit: 520.00, quantity: 10, strategy_label: 'Momentum', opened_at: '2025-12-02T09:30:00', closed_at: '2025-12-18T15:45:00', notes: 'Strong breakout above 50-day MA with rising volume. AI score 81.' },
  { id: 2, ticker: 'AAPL', side: 'buy', entry_price: 185.20, exit_price: 198.45, stop_loss: 178.00, take_profit: 205.00, quantity: 20, strategy_label: 'Balanced', opened_at: '2026-01-08T10:15:00', closed_at: '2026-01-22T14:30:00', notes: 'Earnings beat expected. Entered on pullback to support.' },
  { id: 3, ticker: 'TSLA', side: 'buy', entry_price: 265.00, exit_price: 242.80, stop_loss: 248.00, take_profit: 295.00, quantity: 8, strategy_label: 'Growth', opened_at: '2026-01-15T09:30:00', closed_at: '2026-01-28T11:00:00', notes: 'Stopped out after delivery numbers miss. Lesson: wait for confirmation.' },
  { id: 4, ticker: 'MSFT', side: 'buy', entry_price: 388.50, exit_price: 425.90, stop_loss: 375.00, take_profit: 440.00, quantity: 12, strategy_label: 'Balanced', opened_at: '2026-02-03T10:00:00', closed_at: '2026-02-20T15:00:00', notes: 'Cloud revenue growth re-accelerating. Azure momentum.' },
  { id: 5, ticker: 'AMD', side: 'buy', entry_price: 155.00, exit_price: 178.60, stop_loss: 145.00, take_profit: 185.00, quantity: 15, strategy_label: 'Momentum', opened_at: '2026-02-10T09:45:00', closed_at: '2026-03-05T14:15:00', notes: 'AI chip demand thesis. Broke resistance at 160.' },
  { id: 6, ticker: 'META', side: 'buy', entry_price: 510.00, exit_price: 485.30, stop_loss: 490.00, take_profit: 560.00, quantity: 6, strategy_label: 'Growth', opened_at: '2026-03-01T10:30:00', closed_at: '2026-03-10T09:30:00', notes: 'Stopped out on broad market sell-off. Position was oversized.' },
  { id: 7, ticker: 'GOOGL', side: 'buy', entry_price: 158.00, exit_price: 182.40, stop_loss: 150.00, take_profit: 190.00, quantity: 20, strategy_label: 'Balanced', opened_at: '2026-03-12T09:30:00', closed_at: '2026-04-02T15:30:00', notes: 'Gemini AI product launch catalyst. Strong ad revenue growth.' },
  { id: 8, ticker: 'NVDA', side: 'buy', entry_price: 780.00, exit_price: 920.50, stop_loss: 740.00, take_profit: 950.00, quantity: 8, strategy_label: 'Momentum', opened_at: '2026-03-20T10:00:00', closed_at: '2026-04-15T14:00:00', notes: 'GTC conference catalyst. Blackwell demand exceeding supply.' },
  { id: 9, ticker: 'COIN', side: 'sell', entry_price: 285.00, exit_price: 258.20, stop_loss: 305.00, take_profit: 245.00, quantity: 10, strategy_label: 'Momentum', opened_at: '2026-04-05T09:30:00', closed_at: '2026-04-18T11:00:00', notes: 'Short on crypto weakness. Regulatory headwinds.' },
  { id: 10, ticker: 'AAPL', side: 'buy', entry_price: 210.00, exit_price: 228.50, stop_loss: 200.00, take_profit: 235.00, quantity: 15, strategy_label: 'Balanced', opened_at: '2026-04-20T10:15:00', closed_at: '2026-05-08T15:00:00', notes: 'iPhone AI features driving upgrade cycle.' },
  { id: 11, ticker: 'PLTR', side: 'buy', entry_price: 24.50, exit_price: 24.50, stop_loss: 22.00, take_profit: 28.00, quantity: 50, strategy_label: 'Growth', opened_at: '2026-05-01T09:30:00', closed_at: '2026-05-10T15:00:00', notes: 'Flat. No catalyst materialized. Closed at breakeven.' },
  { id: 12, ticker: 'MSFT', side: 'buy', entry_price: 440.00, exit_price: 467.35, stop_loss: 425.00, take_profit: 480.00, quantity: 10, strategy_label: 'Balanced', opened_at: '2026-05-15T10:00:00', closed_at: '2026-06-05T14:30:00', notes: 'Copilot enterprise adoption accelerating. Strong guidance.' },
  { id: 13, ticker: 'TSLA', side: 'sell', entry_price: 310.00, exit_price: 278.90, stop_loss: 330.00, take_profit: 270.00, quantity: 12, strategy_label: 'Momentum', opened_at: '2026-05-20T09:30:00', closed_at: '2026-06-10T11:00:00', notes: 'Short on valuation concerns. Robotaxi delays.' },
  { id: 14, ticker: 'AMD', side: 'buy', entry_price: 168.00, exit_price: 152.40, stop_loss: 155.00, take_profit: 190.00, quantity: 12, strategy_label: 'Momentum', opened_at: '2026-06-01T10:00:00', closed_at: '2026-06-15T14:00:00', notes: 'Hit stop loss. Intel gaining ground in data center.' },
  { id: 15, ticker: 'NVDA', side: 'buy', entry_price: 1050.00, exit_price: 1245.80, stop_loss: 980.00, take_profit: 1300.00, quantity: 5, strategy_label: 'Momentum', opened_at: '2026-06-10T09:30:00', closed_at: '2026-06-28T15:00:00', notes: 'Earnings blowout. Data center revenue doubled YoY.' },
];

export const MOCK_MARKETPLACE = [
  {
    id: 1, status: 'verified', avg_rating: 4.6, rating_count: 128, sales_count: 342,
    price_cents: 2999, backtest_return: 0.34, backtest_sharpe: 1.82,
    strategy: {
      name: 'Alpha Momentum', owner: { full_name: 'Sarah Chen' },
      weights: { sentiment: 10, momentum: 35, valuation: 10, volatility: 15, volume: 20, growth: 10 },
    },
  },
  {
    id: 2, status: 'verified', avg_rating: 4.3, rating_count: 87, sales_count: 215,
    price_cents: 1999, backtest_return: 0.28, backtest_sharpe: 1.65,
    strategy: {
      name: 'Value Hunter', owner: { full_name: 'James Park' },
      weights: { sentiment: 5, momentum: 10, valuation: 40, volatility: 10, volume: 5, growth: 30 },
    },
  },
  {
    id: 3, status: 'verified', avg_rating: 4.8, rating_count: 64, sales_count: 178,
    price_cents: 4999, backtest_return: 0.41, backtest_sharpe: 2.10,
    strategy: {
      name: 'Sentinel Pro', owner: { full_name: 'Alex Rivera' },
      weights: { sentiment: 25, momentum: 25, valuation: 15, volatility: 20, volume: 10, growth: 5 },
    },
  },
  {
    id: 4, status: 'verified', avg_rating: 4.1, rating_count: 43, sales_count: 96,
    price_cents: 0, backtest_return: 0.22, backtest_sharpe: 1.35,
    strategy: {
      name: 'Balanced Core', owner: { full_name: 'StockPilot' },
      weights: { sentiment: 15, momentum: 20, valuation: 20, volatility: 15, volume: 15, growth: 15 },
    },
  },
  {
    id: 5, status: 'review', avg_rating: 0, rating_count: 0, sales_count: 0,
    price_cents: 3499, backtest_return: null, backtest_sharpe: null,
    strategy: {
      name: 'Volatility Edge', owner: { full_name: 'Mika Tanaka' },
      weights: { sentiment: 5, momentum: 15, valuation: 5, volatility: 45, volume: 25, growth: 5 },
    },
  },
  {
    id: 6, status: 'verified', avg_rating: 3.9, rating_count: 31, sales_count: 74,
    price_cents: 1499, backtest_return: 0.19, backtest_sharpe: 1.21,
    strategy: {
      name: 'Growth Seeker', owner: { full_name: 'David Kim' },
      weights: { sentiment: 10, momentum: 20, valuation: 5, volatility: 10, volume: 10, growth: 45 },
    },
  },
];

export const MOCK_PORTFOLIO_HISTORY = [
  { date: '2025-12', value: 18500 },
  { date: '2026-01', value: 21200 },
  { date: '2026-02', value: 24800 },
  { date: '2026-03', value: 23100 },
  { date: '2026-04', value: 28900 },
  { date: '2026-05', value: 32400 },
  { date: '2026-06', value: 38200 },
  { date: '2026-07', value: 44852 },
];

export const MOCK_BENCHMARK = [
  { date: '2025-12', value: 18500 },
  { date: '2026-01', value: 19200 },
  { date: '2026-02', value: 20100 },
  { date: '2026-03', value: 19800 },
  { date: '2026-04', value: 21400 },
  { date: '2026-05', value: 22100 },
  { date: '2026-06', value: 23500 },
  { date: '2026-07', value: 24200 },
];

export const MOCK_SECTOR_BREAKDOWN = [
  { sector: 'Technology', weight: 72.4, value: 32491 },
  { sector: 'Consumer Discretionary', weight: 14.9, value: 6698 },
  { sector: 'Communication', weight: 5.1, value: 2306 },
  { sector: 'Cash', weight: 7.6, value: 3400 },
];

export const MOCK_MARKET_INDICES = [
  { name: 'S&P 500', value: 5892.34, change: 0.68 },
  { name: 'NASDAQ', value: 19845.12, change: 1.12 },
  { name: 'DOW', value: 42156.78, change: 0.34 },
  { name: 'VIX', value: 14.82, change: -3.21 },
];

export const MOCK_NOTIFICATIONS = [
  { id: 1, title: 'NVDA verdict changed to BUY (89% conviction)', is_read: false, created_at: '2026-07-07T09:15:00' },
  { id: 2, title: 'Price alert: TSLA dropped below $280 stop-loss level', is_read: false, created_at: '2026-07-07T08:30:00' },
  { id: 3, title: 'New verified strategy "Sentinel Pro" listed on Marketplace', is_read: false, created_at: '2026-07-06T16:00:00' },
  { id: 4, title: 'AAPL sentiment shift: strong positive news detected', is_read: true, created_at: '2026-07-06T11:20:00' },
  { id: 5, title: 'Weekly report: Portfolio +3.2% vs S&P 500 +0.7%', is_read: true, created_at: '2026-07-06T08:00:00' },
  { id: 6, title: 'GOOGL verdict changed to BUY (78% conviction)', is_read: true, created_at: '2026-07-05T14:45:00' },
  { id: 7, title: 'Your strategy "Custom Momentum" backtest completed', is_read: true, created_at: '2026-07-05T10:00:00' },
  { id: 8, title: 'AMD earnings report released — sentiment score updated', is_read: true, created_at: '2026-07-04T18:30:00' },
];

export const MOCK_BILLING_HISTORY = [
  { id: 1, date: '2026-07-01', description: 'Pro plan — monthly', amount: 19.00, status: 'paid' },
  { id: 2, date: '2026-06-01', description: 'Pro plan — monthly', amount: 19.00, status: 'paid' },
  { id: 3, date: '2026-05-01', description: 'Pro plan — monthly', amount: 19.00, status: 'paid' },
  { id: 4, date: '2026-04-01', description: 'Pro plan — monthly', amount: 19.00, status: 'paid' },
  { id: 5, date: '2026-03-01', description: 'Pro plan — monthly', amount: 19.00, status: 'paid' },
];
