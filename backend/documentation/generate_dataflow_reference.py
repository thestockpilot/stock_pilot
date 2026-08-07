"""StockPilot — Data Flow Reference.
Every user-facing functionality traced step by step across all layers.
Generated from verified source code."""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, white
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_JUSTIFY, TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether,
)

NAVY = HexColor("#1b2a4a"); BLUE = HexColor("#2E5496"); ACCENT = HexColor("#b8801f")
GREEN = HexColor("#1E7E45"); RED = HexColor("#b03a2e"); GREY = HexColor("#5a5a64")
LIGHTB = HexColor("#eef2f9"); LIGHTG = HexColor("#eaf6ee"); LIGHTGOLD = HexColor("#fbf6e9")
LIGHTRED = HexColor("#fbeeec"); LIGHTGREY = HexColor("#f4f4f6"); BORDER = HexColor("#c9d3e6")
TEXT = HexColor("#16161a")

PAGE_W, PAGE_H = A4
MARGIN = 44
CW = PAGE_W - 2 * MARGIN
OUT = os.path.join(os.path.dirname(__file__), "StockPilot_DataFlow_Reference.pdf")

doc = SimpleDocTemplate(OUT, pagesize=A4, leftMargin=MARGIN, rightMargin=MARGIN,
                        topMargin=MARGIN, bottomMargin=MARGIN,
                        title="StockPilot - Data Flow Reference", author="Group 13 - CSE5015")

S = getSampleStyleSheet()
S.add(ParagraphStyle("T1", fontName="Helvetica-Bold", fontSize=23, leading=27, textColor=NAVY, spaceAfter=3))
S.add(ParagraphStyle("T2", fontName="Helvetica-Bold", fontSize=13, leading=17, textColor=ACCENT, spaceAfter=9))
S.add(ParagraphStyle("Sub", fontName="Helvetica-Oblique", fontSize=10, leading=14, textColor=GREY, spaceAfter=12))
S.add(ParagraphStyle("H1", fontName="Helvetica-Bold", fontSize=14.5, leading=18, textColor=NAVY, spaceBefore=16, spaceAfter=7))
S.add(ParagraphStyle("FT", fontName="Helvetica-Bold", fontSize=10.5, leading=13.5, textColor=BLUE, spaceBefore=11, spaceAfter=4))
S.add(ParagraphStyle("Body", fontName="Helvetica", fontSize=9.3, leading=13.5, textColor=TEXT, alignment=TA_JUSTIFY, spaceAfter=6))
S.add(ParagraphStyle("Bul", fontName="Helvetica", fontSize=9.3, leading=13, textColor=TEXT, alignment=TA_JUSTIFY, spaceAfter=2, leftIndent=13, bulletIndent=3))
S.add(ParagraphStyle("Steps", fontName="Courier", fontSize=7.7, leading=10.4, textColor=HexColor("#14141a"),
                     backColor=LIGHTGREY, borderPadding=7, spaceBefore=3, spaceAfter=6, leftIndent=4, rightIndent=4))
S.add(ParagraphStyle("Cell", fontName="Helvetica", fontSize=8, leading=10.5, textColor=TEXT))
S.add(ParagraphStyle("CellC", fontName="Courier", fontSize=7.4, leading=10, textColor=HexColor("#14141a")))
S.add(ParagraphStyle("Head", fontName="Helvetica-Bold", fontSize=8.1, leading=10.5, textColor=white))
S.add(ParagraphStyle("CoTitle", fontName="Helvetica-Bold", fontSize=9.3, leading=12, textColor=TEXT))
S.add(ParagraphStyle("CoBody", fontName="Helvetica", fontSize=8.8, leading=12.5, textColor=TEXT, alignment=TA_JUSTIFY))

def P(t, s="Body"): return Paragraph(t, S[s])
def _p(t): return Paragraph(str(t), S["Cell"])
def _pc(t): return Paragraph(str(t), S["CellC"])
def _ph(t): return Paragraph(str(t), S["Head"])
def bullet(t): return Paragraph(t, S["Bul"], bulletText="•")

def rule(color=ACCENT, w=1.1, after=9):
    t = Table([[""]], colWidths=[CW])
    t.setStyle(TableStyle([("LINEBELOW",(0,0),(-1,-1),w,color),("BOTTOMPADDING",(0,0),(-1,-1),after)]))
    return t

def callout(title, body, bg=LIGHTB, ac=BLUE):
    t = Table([[Paragraph(f"<b>{title}</b>", S["CoTitle"])],[Paragraph(body, S["CoBody"])]], colWidths=[CW-14])
    t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),bg),("LEFTPADDING",(0,0),(-1,-1),11),("RIGHTPADDING",(0,0),(-1,-1),9),
        ("TOPPADDING",(0,0),(0,0),7),("BOTTOMPADDING",(-1,-1),(-1,-1),8),
        ("LINEBEFORE",(0,0),(0,-1),3,ac),("VALIGN",(0,0),(-1,-1),"TOP")]))
    return t

def table(headers, rows, widths, code_cols=()):
    data=[[_ph(h) for h in headers]]
    for r in rows:
        data.append([_pc(c) if i in code_cols else _p(c) for i,c in enumerate(r)])
    t=Table(data,colWidths=widths,repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),NAVY),("GRID",(0,0),(-1,-1),0.4,BORDER),
        ("VALIGN",(0,0),(-1,-1),"TOP"),("ROWBACKGROUNDS",(0,1),(-1,-1),[white,HexColor("#f7f8fb")]),
        ("LEFTPADDING",(0,0),(-1,-1),5),("RIGHTPADDING",(0,0),(-1,-1),4),
        ("TOPPADDING",(0,0),(-1,-1),3.5),("BOTTOMPADDING",(0,0),(-1,-1),3.5)]))
    return t

def steps(txt):
    e = txt.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
    return Paragraph(e.replace("\n","<br/>"), S["Steps"])

def flow(fid, name, meta_rows, step_text, errors=None, keep=False):
    """One functionality block: header, metadata table, numbered steps, error paths."""
    els = [P(f"{fid} &nbsp; {name}", "FT"),
           table(["Aspect","Detail"], meta_rows, [0.82*inch, CW-0.82*inch], code_cols=(1,)),
           steps(step_text)]
    if errors:
        els.append(table(["Error path","Result"], errors, [2.15*inch, CW-2.15*inch]))
        els.append(Spacer(1,4))
    return KeepTogether(els) if keep else els

st = []

# ─────────── COVER ───────────
st.append(P("StockPilot", "T1"))
st.append(P("Data Flow Reference &mdash; Every User Functionality, Step by Step", "T2"))
st.append(P("A complete trace of all 52 user-facing functionalities through every layer of the system: "
            "UI event &rarr; React hook &rarr; HTTP request &rarr; authentication &rarr; endpoint logic &rarr; database / "
            "external API &rarr; response &rarr; UI update. Every branch and error path is included. "
            "Companion volume to the System Context Document.", "Sub"))
st.append(rule())
st.append(callout("Notation used throughout",
    "<font face='Courier'>[UI]</font> browser/React &nbsp;&middot;&nbsp; <font face='Courier'>[HOOK]</font> custom React hook &nbsp;&middot;&nbsp; "
    "<font face='Courier'>[HTTP]</font> network request &nbsp;&middot;&nbsp; <font face='Courier'>[AUTH]</font> token/permission check &nbsp;&middot;&nbsp; "
    "<font face='Courier'>[API]</font> FastAPI handler &nbsp;&middot;&nbsp; <font face='Courier'>[DB]</font> PostgreSQL &nbsp;&middot;&nbsp; "
    "<font face='Courier'>[EXT]</font> external service (Yahoo Finance) &nbsp;&middot;&nbsp; <font face='Courier'>[ML]</font> AI/analytics computation. "
    "Steps are numbered in execution order; indented sub-steps are internal detail.", LIGHTGOLD, ACCENT))
st.append(Spacer(1,8))

st.append(table(["Group","Functionalities","IDs"], [
    ["Authentication &amp; Session","Register, login, session restore, token refresh, logout, route guarding","F-01 &ndash; F-06"],
    ["Profile &amp; Settings","View/update profile, change password, upload/delete avatar","F-07 &ndash; F-11"],
    ["Dashboard","Batch load, market indices, sector breakdown, portfolio history, watchlist navigation","F-12 &ndash; F-16"],
    ["Advisor (AI core)","Ticker select, live quote, chart, factor verdict, weights, presets, save/delete strategy, backtest, CSV export, bull/bear, fundamentals, sentiment","F-17 &ndash; F-28"],
    ["Portfolio","List with live prices, add, update, delete holding","F-29 &ndash; F-32"],
    ["Watchlist","List, add, remove","F-33 &ndash; F-35"],
    ["Journal","List, log trade, delete, client-side statistics","F-36 &ndash; F-39"],
    ["Marketplace","Browse, thresholds, filter/sort, publish dialog, auto-backtest, submit request","F-40 &ndash; F-45"],
    ["Notifications","Load, mark one read, mark all read","F-46 &ndash; F-48"],
    ["Administration","Dashboard load, users, listings approval lifecycle, strategies, thresholds","F-49 &ndash; F-52"],
], [1.5*inch, CW-2.45*inch, 0.95*inch]))

# ═══════════ A. AUTH ═══════════
st.append(P("A. Authentication &amp; Session", "H1"))

st.extend(flow("F-01","Register a new account",
 [["Trigger","User submits the Create Account form on /auth"],
  ["Path","POST /api/v1/auth/register"],
  ["Auth","None (public)"],
  ["Tables","users (SELECT, INSERT)"]],
"""1  [UI]   AuthPage form collects full_name, email, password; submit handler fires.
2  [UI]   AuthContext.register(full_name, email, password) is called.
3  [HTTP] api.post('/api/v1/auth/register', {full_name, email, password})
          - request interceptor runs but finds no token in localStorage -> no Authorization header
4  [API]  FastAPI validates the body against RegisterRequest (Pydantic).
5  [DB]   SELECT * FROM users WHERE email = :email        (duplicate check)
6         - if a row exists -> raise HTTPException 409 "Email already registered"  [STOP]
7  [API]  hash_password(password)  -> bcrypt hash
8  [DB]   INSERT INTO users (email, password_hash, full_name)   role defaults to 'investor'
9  [DB]   await db.flush()  then  db.refresh(user)   -> populates id, created_at
10 [API]  create_access_token(str(user.id))   JWT {sub, exp}
11 [API]  create_refresh_token(str(user.id))  JWT {sub, exp, type:'refresh'}
12 [API]  Return TokenResponse {access_token, refresh_token, user}
13 [DB]   get_db() commits the transaction on successful return.
14 [UI]   AuthContext stores both tokens in localStorage (sp_access_token, sp_refresh_token),
          sets token state and user state.
15 [UI]   If the response omitted the user object -> calls fetchUser() (GET /users/me).
16 [UI]   AuthRoute sees a session and redirects to / (Dashboard).""",
 [["Duplicate email","409 Conflict; nothing is written; form shows the error"],
  ["Validation failure","422 Unprocessable Entity from Pydantic before any DB access"]]))

st.extend(flow("F-02","Log in",
 [["Trigger","User submits the Sign In form on /auth"],
  ["Path","POST /api/v1/auth/login"],
  ["Auth","None (public)"],
  ["Tables","users (SELECT)"]],
"""1  [UI]   AuthPage submits email + password -> AuthContext.login().
2  [HTTP] api.post('/api/v1/auth/login', {email, password})
3  [API]  Body validated against LoginRequest.
4  [DB]   SELECT * FROM users WHERE email = :email
5  [API]  Branch:
          - no user found            -> 401 "Invalid email or password"  [STOP]
          - verify_password() fails  -> 401 "Invalid email or password"  [STOP]
            (identical message for both, so the API does not reveal whether the email exists)
6  [API]  Issue access token + refresh token from user.id.
7  [API]  Serialise the user via UserOut and return TokenResponse.
8  [UI]   Tokens persisted to localStorage; user state set; loading cleared.
9  [UI]   Navigate to / ; Layout + Header render with the user's initials and role.
10 [UI]   If role === 'admin', Header appends the Admin nav tab (AdminRoute allows /admin).""",
 [["Wrong password / unknown email","401 Unauthorized, generic message"],
  ["Inactive account","Login succeeds here, but every later request fails at get_current_user (is_active check) -> 401"]]))

st.extend(flow("F-03","Session restore on page load",
 [["Trigger","Browser loads or refreshes the app"],
  ["Path","GET /api/v1/users/me"],
  ["Auth","Bearer access token from localStorage"],
  ["Tables","users (SELECT)"]],
"""1  [UI]   main.jsx mounts App -> AuthProvider initialises:
          token state = localStorage.getItem('sp_access_token'), loading = true
2  [UI]   useEffect calls fetchUser().
3  [HTTP] api.get('/api/v1/users/me'); interceptor attaches Authorization: Bearer <token>.
4  [AUTH] HTTPBearer extracts the credential; decode_token() verifies signature + expiry.
5  [AUTH] Extract payload['sub'] -> UUID.
6  [DB]   SELECT * FROM users WHERE id = :sub
7  [AUTH] If user is None OR user.is_active is False -> 401 "User not found".
8  [API]  Return the User serialised as UserOut.
9  [UI]   setUser(data); setLoading(false); ProtectedRoute now renders the requested page.
10        If step 4 or 7 raised 401 -> the response interceptor takes over (see F-04).""",
 [["No token at all","Request fails 401 -> tokens cleared -> redirect to /auth"],
  ["Expired access token","401 triggers the refresh-and-retry flow (F-04)"]]))

st.extend(flow("F-04","Automatic token refresh and retry",
 [["Trigger","Any API call returns 401 while a refresh token exists"],
  ["Path","POST /api/v1/auth/refresh"],
  ["Auth","Refresh token in the request body"],
  ["Tables","users (SELECT)"]],
"""1  [HTTP] Response interceptor in api/client.js catches status 401.
2  [UI]   Guard: if originalRequest._retry is already true -> give up, reject.  [STOP]
3  [UI]   Concurrency guard: if isRefreshing is true, the request is pushed onto failedQueue
          and awaits the in-flight refresh instead of starting a second one.
4  [UI]   Set _retry = true and isRefreshing = true.
5  [UI]   Read sp_refresh_token from localStorage.
          - missing -> clear both tokens, window.location.href = '/auth'  [STOP]
6  [HTTP] Plain axios.post('/api/v1/auth/refresh', {refresh_token})   (bypasses the interceptor)
7  [API]  decode_token(refresh_token); reject if payload is None or payload['type'] != 'refresh'.
8  [DB]   SELECT * FROM users WHERE id = :sub    -> 401 if the user no longer exists.
9  [API]  Mint a fresh access token and refresh token; return both.
10 [UI]   Store the new access token (and refresh token if returned).
11 [UI]   processQueue(null, newToken) -> every queued request resumes with the new token.
12 [UI]   Re-issue the original request with the new Authorization header; return its result.
13 [UI]   finally -> isRefreshing = false.""",
 [["Refresh token invalid/expired","processQueue rejects all queued calls, tokens cleared, hard redirect to /auth"],
  ["Two 401s on a cold load","Normal: /users/me and /auth/refresh both probe before a session exists"]]))

st.extend(flow("F-05","Log out",
 [["Trigger","User menu -> Sign out"],["Path","(client only &mdash; no request)"],
  ["Auth","n/a"],["Tables","none"]],
"""1  [UI]   Header calls handleSignOut(): closes the dropdown, calls AuthContext.logout().
2  [UI]   localStorage.removeItem('sp_access_token'); removeItem('sp_refresh_token').
3  [UI]   setToken(null); setUser(null).
4  [UI]   navigate('/auth'); ProtectedRoute now fails and the auth page renders.
NOTE: the JWT is stateless, so no server call is made and the token remains
      technically valid until it expires. Server-side revocation is not implemented."""))

st.extend(flow("F-06","Route guarding",
 [["Trigger","Any navigation"],["Path","(client only)"],
  ["Auth","AuthContext state"],["Tables","none"]],
"""1  [UI]   AppRouter wraps routes in three guards:
          ProtectedRoute - renders children only when a session exists, else <Navigate to='/auth'>
          AdminRoute     - additionally requires user.role === 'admin', else redirects
          AuthRoute      - inverse: if already signed in, redirects away from /auth
2  [UI]   While AuthContext.loading is true a spinner renders, preventing a flash of
          the login page during session restore.
3  [UI]   Unknown paths (*) redirect to /.
NOTE: guards are UX only. Real enforcement is server-side - every protected endpoint
      depends on get_current_user, and admin routes on require_role(UserRole.admin)."""))

# ═══════════ B. PROFILE ═══════════
st.append(PageBreak())
st.append(P("B. Profile &amp; Settings", "H1"))

st.extend(flow("F-07","View profile",
 [["Trigger","Open /settings, or any page load"],["Path","GET /api/v1/users/me"],
  ["Auth","Bearer"],["Tables","users (SELECT)"]],
"""1  [UI]   Settings reads the user object already held in AuthContext (no new call needed).
2  [API]  When fetched: get_current_user has already loaded the row, so the handler
          simply returns it - no additional query is issued by the route body itself."""))

st.extend(flow("F-08","Update profile details",
 [["Trigger","Settings -> Profile -> Save"],["Path","PUT /api/v1/users/me"],
  ["Auth","Bearer"],["Tables","users (UPDATE)"]],
"""1  [UI]   Settings collects full_name, email, phone, bio into a payload.
2  [HTTP] api.put('/api/v1/users/me', body)
3  [AUTH] get_current_user resolves the User ORM object (already attached to the session).
4  [API]  Body validated as UserUpdate; each field applied only if not None:
          if body.full_name is not None -> user.full_name = ...
          if body.email     is not None -> user.email     = ...
          if body.phone     is not None -> user.phone     = ...
          if body.bio       is not None -> user.bio       = ...
5  [DB]   await db.flush() -> SQLAlchemy emits UPDATE for the changed columns only.
          The onupdate=func.now() rule refreshes users.updated_at.
6  [DB]   db.refresh(user); get_db() commits on return.
7  [UI]   Response replaces the user in AuthContext via updateUser(); header initials update.""",
 [["Duplicate email","Unique constraint violation -> 500/IntegrityError; the session rolls back"]]))

st.extend(flow("F-09","Change password",
 [["Trigger","Settings -> Security -> Update password"],["Path","PUT /api/v1/users/me/password"],
  ["Auth","Bearer"],["Tables","users (UPDATE)"]],
"""1  [UI]   Form supplies current_password and new_password.
2  [API]  verify_password(current_password, user.password_hash)
          - mismatch -> 400 "Current password is incorrect."  [STOP]
3  [API]  Length rule: len(new_password) < 8 -> 400 "New password must be at least 8 characters."
4  [API]  user.password_hash = hash_password(new_password)   (bcrypt, new salt)
5  [DB]   flush + commit.
6  [API]  Return {"detail": "Password updated successfully."}
NOTE: existing JWTs remain valid after a password change - sessions are not invalidated."""))

st.extend(flow("F-10","Upload avatar",
 [["Trigger","Settings -> Profile -> choose image"],["Path","POST /api/v1/users/me/avatar"],
  ["Auth","Bearer"],["Tables","users (UPDATE)"]],
"""1  [UI]   File input produces a File; sent as multipart/form-data.
2  [API]  Validate content type against ALLOWED_TYPES {image/jpeg, image/png, image/webp}.
3  [API]  Validate size against MAX_SIZE (2 MB).
4  [API]  Write the file into backend/uploads/avatars/ with a generated unique name.
5  [DB]   user.avatar_url = '/uploads/avatars/<file>' ; flush + commit.
6  [UI]   The new URL is served by the StaticFiles mount configured in main.py.""",
 [["Wrong type or oversize","400 with the reason; no file written and no DB change"]]))

st.extend(flow("F-11","Remove avatar",
 [["Trigger","Settings -> Profile -> Remove photo"],["Path","DELETE /api/v1/users/me/avatar"],
  ["Auth","Bearer"],["Tables","users (UPDATE)"]],
"""1  [API]  Resolve the stored path from user.avatar_url; unlink the file if present.
2  [DB]   user.avatar_url = NULL ; flush + commit.
3  [UI]   Avatar falls back to the generated initials chip."""))

# ═══════════ C. DASHBOARD ═══════════
st.append(P("C. Dashboard", "H1"))

st.extend(flow("F-12","Load the dashboard (batch)",
 [["Trigger","Navigate to /"],["Path","GET /api/v1/dashboard/batch"],
  ["Auth","Bearer"],["Tables","holdings, stocks, trades"]],
"""1  [UI]   Dashboard mounts; useEffect issues one batch request instead of three.
2  [API]  get_dashboard_batch runs the three sub-functions concurrently:
          asyncio.gather(get_market_indices(), get_sector_breakdown(), get_portfolio_history())
3         Each sub-flow is detailed in F-13, F-14, F-15.
4  [API]  Returns {market_indices, sector_breakdown, portfolio_history} in one payload.
5  [UI]   Three setState calls populate the indices strip, sector bars and performance chart.
6  [UI]   In parallel the page also runs usePortfolio, useWatchlist, useTrades,
          usePredictions and useMarketplace hooks for the remaining panels.
7  [UI]   Client-side derivations (no server call):
          totalMV       = SUM(quantity * (current_price or avg_cost))
          totalCost     = SUM(quantity * avg_cost)
          unrealisedPL  = totalMV - totalCost
          buyCount      = holdings whose matching prediction.signal === 'BUY'
          recentTrades  = trades sorted by closed_at desc, sliced to 5
          topListing    = listings sorted by avg_rating desc, first item
8  [UI]   Stat cards, watchlist rows, allocation doughnut and activity feed render."""))

st.extend(flow("F-13","Market indices strip",
 [["Trigger","Part of the batch call"],["Path","GET /api/v1/dashboard/market-indices"],
  ["Auth","Bearer"],["Tables","none (external only)"]],
"""1  [API]  Check the in-process _indices_cache; if still fresh, return it immediately.  [FAST PATH]
2  [EXT]  Otherwise loop over INDEX_TICKERS (S&P 500, Nasdaq, Dow, VIX):
          yf.Ticker(symbol) -> read last price and previous close
3  [API]  change % = (last - prev) / prev * 100 ; NaN/Inf values coerced to a safe default.
4  [API]  Store the result in the cache with a timestamp; return the list.
5  [UI]   Each entry renders as a chip; positive values green, negative red."""))

st.extend(flow("F-14","Sector breakdown",
 [["Trigger","Part of the batch call"],["Path","GET /api/v1/dashboard/sector-breakdown"],
  ["Auth","Bearer"],["Tables","holdings (SELECT), stocks (SELECT)"]],
"""1  [DB]   SELECT * FROM holdings WHERE user_id = :me AND closed_at IS NULL
2  [API]  If there are no holdings -> return []  (UI hides the card).  [STOP]
3  [DB]   SELECT * FROM stocks WHERE ticker IN (:tickers)   -> build ticker -> sector map
4  [API]  For each holding: value = quantity * (current_price or avg_cost);
          accumulate into sector_totals[sector], defaulting to 'Unknown' when the
          ticker is absent from the stocks catalogue.
5  [API]  Sort sectors by value descending; compute each weight as a percentage of the total.
6  [UI]   Renders one labelled gradient bar per sector."""))

st.extend(flow("F-15","Portfolio performance history",
 [["Trigger","Part of the batch call"],["Path","GET /api/v1/dashboard/portfolio-history"],
  ["Auth","Bearer"],["Tables","trades (SELECT), holdings (SELECT)"]],
"""1  [DB]   SELECT * FROM trades   WHERE user_id = :me ORDER BY closed_at ASC
2  [DB]   SELECT * FROM holdings WHERE user_id = :me AND closed_at IS NULL
3  [API]  current_mv = SUM(quantity * (current_price or avg_cost))
4  [API]  If there are no trades -> return a flat single-point series from current_mv.  [STOP]
5  [API]  Walk the trades in chronological order, bucketing realised P/L by month.
6  [API]  initial_cost = SUM(quantity * avg_cost) is the baseline for the curve.
7  [API]  Build two aligned series: 'portfolio' (cumulative) and 'benchmark'.
8  [UI]   Chart.js line chart: gold filled area for the portfolio, dashed grey for the benchmark."""))

st.extend(flow("F-16","Open a watchlist row in the Advisor",
 [["Trigger","Click a watchlist row on the Dashboard"],["Path","(client-side navigation)"],
  ["Auth","n/a"],["Tables","none"]],
"""1  [UI]   The row's onClick calls navigate('/advisor').
2  [UI]   React Router unmounts Dashboard and mounts Advisor.
3  [UI]   Advisor initialises with its default ticker and immediately begins F-17."""))

# ═══════════ D. ADVISOR ═══════════
st.append(PageBreak())
st.append(P("D. Advisor &mdash; the AI core", "H1"))

st.extend(flow("F-17","Select a ticker",
 [["Trigger","Type in the search box or click a ticker chip"],["Path","(triggers F-18 to F-21)"],
  ["Auth","n/a"],["Tables","none"]],
"""1  [UI]   setTicker(value.toUpperCase()) updates component state.
2  [UI]   Every dependent hook has `ticker` in its dependency array, so changing it
          cancels any in-flight request (AbortController) and refetches:
          useLiveQuote, useChartData, useFactorAnalysis, useBullBear,
          useFundamentals, useSentiment, useBacktest
3  [UI]   Each panel independently shows its own loading state while its request resolves."""))

st.extend(flow("F-18","Live quote",
 [["Trigger","Ticker change; optional polling"],["Path","GET /api/v1/live/{ticker}/quote"],
  ["Auth","Bearer"],["Tables","none (external only)"]],
"""1  [HOOK] useLiveQuote(ticker, pollMs) fetches, then optionally sets an interval to refetch.
2  [EXT]  Backend calls yfinance for last price, previous close, day range and volume.
3  [API]  Derives absolute and percentage change; sanitises NaN/Inf.
4  [UI]   Price header updates; the change value is colour-coded.
5  [UI]   On unmount the hook aborts the request and clears the interval."""))

st.extend(flow("F-19","Price chart",
 [["Trigger","Ticker or timeframe change"],["Path","GET /api/v1/live/{ticker}/chart"],
  ["Auth","Bearer"],["Tables","none (external only)"]],
"""1  [HOOK] useChartData(ticker, interval, period)
2  [EXT]  yfinance history for the requested period/interval.
3  [API]  Returns an OHLC series (plus moving averages where applicable).
4  [UI]   TradingChart renders it with lightweight-charts / Chart.js."""))

st.extend(flow("F-20","Generate the verdict (six-factor analysis)",
 [["Trigger","Ticker or weight change"],["Path","GET /api/v1/analysis/{ticker}/factors"],
  ["Auth","Bearer"],["Tables","none &mdash; fully live"]],
"""1  [UI]   Weights object {sentiment, momentum, valuation, volatility, volume, growth}.
2  [HOOK] useFactorAnalysis(ticker, weights, pollMs) builds query params w_sentiment=..&w_momentum=..
3  [HTTP] GET /api/v1/analysis/AAPL/factors?w_sentiment=14&w_momentum=22&...
4  [EXT]  DataFetcher.fetch_historical(ticker, period='6mo')  -> raw OHLCV DataFrame
5  [ML]   FeatureEngine.calculate_all_features(raw) -> 23 indicator columns
          (RSI_14, MACD_Histogram, Price_Position, Volatility_20, ATR_14, Volume_Ratio,
           MFI_14, BB_Position, Price_to_SMA_20/50, ROC_10, Price_Above_SMA_20, OBV, ...)
6  [ML]   latest = df.iloc[-1]; compute each factor from the latest row:
          momentum   = RSI/100*0.4 + (0.5 + clip(MACD_hist/2,-0.5,0.5))*0.3 + Price_Position*0.3
          volatility = mean(1 - clip(Volatility_20*100/5,0,1),
                            1 - clip(ATR_14/Close/0.05,0,1))          -> lower vol scores higher
          volume     = clip(Volume_Ratio/2,0,1)*0.5 + MFI_14/100*0.5
          valuation  = mean(1 - BB_Position,
                            1 - clip((P/SMA20 + P/SMA50 - 2)/0.2,-1,1)*0.5)
          growth     = (clip(ROC_10/20,-1,1)*0.5 + 0.5 + Price_Above_SMA_20*0.3) / 1.8
          each result is clipped to 0-100
7  [ML]   Sentiment factor:
          a. finbert_analyze(ticker, max_headlines=10)
             - yfinance .news -> up to 10 headlines
             - FinBERT classifies each (positive/negative/neutral probabilities)
             - aggregate to a single 0-100 score
          b. If zero headlines or any exception -> FALLBACK: OBV trend over the last 20 rows
             sent = clip(0.5 + (OBV[-1]-OBV[0])/(|OBV[0]|+1) * 5, 0, 1) * 100
          c. If both fail -> 50.0 (neutral)
8  [ML]   composite = SUM(score[k] * weight[k] / SUM(weights))
9  [ML]   Verdict band + confidence from the consensus strength across the six factors.
10 [API]  Respond with per-factor {score,label}, composite, verdict, confidence, as_of.
11 [UI]   Hero card shows BUY/HOLD/SELL, the confidence bar, and one bar per factor.
NOTE: nothing is written to the database - the verdict is not persisted (see Gaps).""",
 [["Insufficient data / bad ticker","Empty score set -> the panel shows an empty state"],
  ["yfinance unreachable","Exception is logged; the factors call returns {} and the UI degrades gracefully"]]))

st.extend(flow("F-21","Adjust factor weights",
 [["Trigger","Drag any of the six sliders"],["Path","re-runs F-20"],
  ["Auth","n/a"],["Tables","none"]],
"""1  [UI]   onChange -> setWeights({...weights, [key]: +value}) and setStrategyId(null)
          (clearing the id marks the configuration as 'custom' rather than a saved preset).
2  [UI]   The weights object identity changes -> useFactorAnalysis dependency array fires.
3  [HTTP] A new /factors request is issued with the updated w_* parameters.
4  [UI]   The verdict, composite score and factor bars re-render with the new result.
5  [UI]   The Save-strategy preview chips update to mirror the new weights."""))

st.extend(flow("F-22","Apply a preset strategy",
 [["Trigger","Click a preset card"],["Path","(client only, then F-20)"],
  ["Auth","n/a"],["Tables","none"]],
"""1  [UI]   The preset's weight object is copied into state via setWeights({...preset.w}).
2  [UI]   setStrategyId(preset.id) marks the tuner as 'preset' rather than 'custom'.
3         Downstream this behaves exactly like F-21 - the analysis refetches."""))

st.extend(flow("F-23","Save the current weights as a strategy",
 [["Trigger","Advisor -> Save as Strategy"],["Path","POST /api/v1/strategies"],
  ["Auth","Bearer"],["Tables","strategies (INSERT)"]],
"""1  [UI]   User enters a name; handler posts {name, description:'Custom strategy', weights}.
2  [API]  Body validated as StrategyCreate.
3  [DB]   INSERT INTO strategies (owner_id=:me, name, description, weights)
          weights is stored as JSONB; is_preset and is_published default to false.
4  [DB]   flush + refresh + commit.
5  [UI]   useStrategies refetches so the new entry appears under 'Your saved strategies'.
6         The strategy is now selectable in the Marketplace publish dialog (F-43)."""))

st.extend(flow("F-24","Delete a saved strategy",
 [["Trigger","Advisor -> saved strategy -> delete"],["Path","DELETE /api/v1/strategies/{id}"],
  ["Auth","Bearer"],["Tables","strategies (SELECT, DELETE)"]],
"""1  [DB]   SELECT * FROM strategies WHERE id = :id AND owner_id = :me
          - ownership is part of the WHERE clause, so another user's strategy simply
            returns no row -> 404 (never 403, and never leaks existence)
2  [API]  If None -> 404 "Strategy not found".  [STOP]
3  [DB]   await db.delete(strategy); commit on return.
4  [UI]   List refetches; the row disappears.
NOTE: if a marketplace_listing references the strategy the FK is RESTRICT, so the
      delete fails - the listing must be removed first (admins can do both, F-52)."""))

st.extend(flow("F-25","Run a backtest",
 [["Trigger","Advisor -> Run Backtest"],["Path","GET /api/v1/analysis/{ticker}/backtest"],
  ["Auth","Bearer"],["Tables","none &mdash; fully live"]],
"""1  [UI]   User picks a period tab (6mo | 1y | 2y | 5y); risk and horizon come from the profile.
2  [HOOK] useBacktest(ticker, period, weights, risk, horizon) -> refetch()
3  [HTTP] GET /analysis/{t}/backtest?period=1y&risk=Moderate&horizon=Medium&w_*=..
4  [API]  Resolve configuration:
          rc = RISK_CONFIG[risk]        -> buy threshold, sl_mult, tp_mult
          hc = HORIZON_CONFIG[horizon]  -> band, base stop, base take-profit
          buy_thresh  = rc.buy
          sell_thresh = rc.buy - hc.band
          sl_stop     = hc.sl * rc.sl_mult
          tp_stop     = hc.tp * rc.tp_mult      (0 disables the take-profit)
5  [EXT]  DataFetcher.fetch_historical(ticker, period)
6  [ML]   FeatureEngine.calculate_all_features(raw)
7  [API]  Guard: if df is empty or len(df) < 60 -> 400 "Insufficient data for backtest".  [STOP]
8  [API]  run_in_threadpool(_run_vectorbt_backtest, ...)   - the sim is CPU-bound, so it
          must not block the async event loop.
9  [ML]   _compute_daily_composite(df, weights) -> a composite score for EVERY row.
          (Here the sentiment factor uses the OBV proxy, not FinBERT - historical
           per-day news sentiment is not stored.)
10 [ML]   entries = composite >= buy_thresh ;  exits = composite <= sell_thresh
11 [ML]   vbt.Portfolio.from_signals(close, entries, exits,
                sl_stop, sl_trail=True, tp_stop, upon_opposite_entry='close',
                fees=0.001, slippage=0.0005, init_cash=10_000, freq='1D')
12 [ML]   Extract metrics; guard every value against NaN/Inf:
          total_return, buy&hold, edge, win_rate, sharpe, max_drawdown,
          profit_factor (capped at 99.99), trade count
13 [ML]   Equity curve normalised to start at 1.0 and down-sampled to ~100 points.
14 [ML]   Build trades_log from portfolio.trades.records_readable - one row per trade:
          entry_date, entry_price, exit_date, exit_price, size, pnl, return_pct, status
15 [API]  Return BacktestMetrics (metrics + equity_curve + dates + trades_log).
16 [UI]   Stat panel, equity chart and the Download-log button render.
NOTE: the first backtest after a server start takes ~20s while numba compiles
      vectorbt's kernels; later runs are fast.""",
 [["Fewer than 60 rows of data","400 Bad Request, 'Insufficient data for backtest'"],
  ["Any other failure","502 'Backtest failed for {ticker}'; the exception is logged server-side"]]))

st.extend(flow("F-26","Download the backtest log (CSV)",
 [["Trigger","Advisor -> Download log"],["Path","(client only &mdash; no request)"],
  ["Auth","n/a"],["Tables","none"]],
"""1  [UI]   downloadBacktestLog(backtest, ticker, period, profile) runs entirely in the browser.
2  [UI]   Build rows: header block (ticker, period, risk, horizon, generated timestamp),
          then the summary metrics, then the full trade ledger with a column header row.
3  [UI]   Each value is CSV-escaped (quotes doubled; fields containing , " or newline quoted).
4  [UI]   new Blob([...], {type:'text/csv;charset=utf-8;'}) -> URL.createObjectURL
5  [UI]   A temporary <a download="backtest_{TICKER}_{period}_{YYYY-MM-DD}.csv"> is clicked,
          then removed, and the object URL is revoked.
6         The file is the audit evidence that the backtest ran on real dated prices."""))

st.extend(flow("F-27","Bull / bear case and fundamentals",
 [["Trigger","Ticker change"],["Path","GET /analysis/{t}/bull-bear, GET /analysis/{t}/fundamentals"],
  ["Auth","Bearer"],["Tables","none (external only)"]],
"""1  [ML]   bull-bear: _generate_bull_bear(ticker, scores) converts the factor scores plus
          market context into human-readable bullet points for each side.
2  [EXT]  fundamentals: yfinance info -> P/E, market cap, margins, growth, etc.
3  [API]  Values are sanitised (NaN/Inf -> None) before serialisation.
4  [UI]   Two lists and a metrics grid render beneath the verdict."""))

st.extend(flow("F-28","News sentiment panel",
 [["Trigger","Ticker change"],["Path","GET /api/v1/sentiment/{ticker}"],
  ["Auth","Bearer"],["Tables","none (external only)"]],
"""1  [EXT]  fetch_news_headlines(ticker, max_headlines=15) via yfinance .news
          - each item's 'title' is extracted; failures are caught and logged, returning []
2  [ML]   analyze_headline(text) for each -> FinBERT probabilities {positive, negative, neutral}
3  [ML]   Aggregate into overall_score 0-100 (100 = all strongly positive, 50 = neutral).
4  [API]  Return the score, headline_count and the per-headline breakdown.
5  [UI]   Each headline renders with a coloured sentiment chip.
6         If headline_count is 0 the UI shows 'no recent news'."""))

# ═══════════ E. PORTFOLIO ═══════════
st.append(PageBreak())
st.append(P("E. Portfolio", "H1"))

st.extend(flow("F-29","List holdings with live valuation",
 [["Trigger","Open /portfolio or the Dashboard"],["Path","GET /api/v1/portfolio"],
  ["Auth","Bearer"],["Tables","holdings (SELECT), stocks (SELECT)"]],
"""1  [DB]   SELECT * FROM holdings
          WHERE user_id = :me AND closed_at IS NULL
          ORDER BY opened_at DESC
2  [API]  tickers = unique set of holding tickers.
3  [DB]   SELECT * FROM stocks WHERE ticker IN (:tickers)  -> ticker -> Stock map (name, sector)
4  [EXT]  _fetch_live_prices(tickers):
          - one _fetch_price task per ticker, dispatched to a ThreadPoolExecutor(max_workers=4)
            via loop.run_in_executor, then awaited together with asyncio.gather
          - each task reads yf.Ticker(t).fast_info -> last_price, falling back to previous_close
          - any failure returns (ticker, None) and is silently dropped from the map
5  [API]  For each holding: serialise with HoldingOut, attach `name` from the stocks map
          (falling back to the raw ticker), and overwrite current_price when a live
          price was obtained.
6  [UI]   Table renders; the client derives market value, cost basis, unrealised P/L and
          percentage per row and in aggregate. Verdict badges come from usePredictions.""",
 [["Ticker missing from stocks","`name` falls back to the ticker symbol; no error"],
  ["yfinance failure for a ticker","current_price stays at its stored value; the row still renders"]]))

st.extend(flow("F-30","Add a holding",
 [["Trigger","Portfolio -> Add position"],["Path","POST /api/v1/portfolio"],
  ["Auth","Bearer"],["Tables","holdings (INSERT)"]],
"""1  [UI]   Form supplies ticker, quantity, avg_cost.
2  [API]  Body validated as HoldingCreate; ticker normalised with .upper().
3  [EXT]  _fetch_live_prices([ticker]) -> seeds current_price at creation time
          (None if the lookup fails - the row is still created).
4  [DB]   INSERT INTO holdings (user_id, ticker, quantity, avg_cost, current_price)
          opened_at defaults to now(); closed_at stays NULL, marking the position open.
5  [DB]   await db.commit() - this route commits explicitly, then refreshes the object.
6  [API]  201 Created with the serialised holding.
7  [UI]   List refetches; stat cards and the allocation chart recalculate."""))

st.extend(flow("F-31","Update a holding",
 [["Trigger","Portfolio -> edit a row"],["Path","PUT /api/v1/portfolio/{holding_id}"],
  ["Auth","Bearer"],["Tables","holdings (SELECT, UPDATE)"]],
"""1  [DB]   SELECT * FROM holdings WHERE id = :id AND user_id = :me   (ownership scoped)
2  [API]  If None -> 404.  [STOP]
3  [API]  Apply the supplied fields (quantity and/or avg_cost) from HoldingUpdate.
4  [DB]   flush; commit on return.
5  [UI]   Row and totals update."""))

st.extend(flow("F-32","Close / delete a holding",
 [["Trigger","Portfolio -> remove a row"],["Path","DELETE /api/v1/portfolio/{holding_id}"],
  ["Auth","Bearer"],["Tables","holdings (SELECT, DELETE)"]],
"""1  [DB]   SELECT * FROM holdings WHERE id = :id AND user_id = :me
2  [API]  If None -> 404.  [STOP]
3  [DB]   DELETE the row (the schema also supports soft-closing by setting closed_at).
4  [UI]   204 No Content; the list refetches and the position disappears."""))

# ═══════════ F. WATCHLIST ═══════════
st.append(P("F. Watchlist", "H1"))

st.extend(flow("F-33","List the watchlist",
 [["Trigger","Dashboard or Portfolio load"],["Path","GET /api/v1/watchlist"],
  ["Auth","Bearer"],["Tables","watchlist (SELECT)"]],
"""1  [DB]   SELECT * FROM watchlist WHERE user_id = :me ORDER BY added_at DESC
2  [UI]   Each ticker is matched against usePredictions to attach a BUY/HOLD/SELL badge;
          rows without a prediction default to HOLD."""))

st.extend(flow("F-34","Add a ticker to the watchlist",
 [["Trigger","Add ticker control"],["Path","POST /api/v1/watchlist"],
  ["Auth","Bearer"],["Tables","watchlist (SELECT, INSERT)"]],
"""1  [API]  ticker normalised with .upper().
2  [DB]   SELECT ... WHERE user_id = :me AND ticker = :ticker      (application-level check)
3  [API]  If a row exists -> 409 "Already on watchlist".  [STOP]
4  [DB]   INSERT INTO watchlist (user_id, ticker); added_at defaults to now().
5  [DB]   flush + refresh; commit on return.
6  [UI]   201 Created; the list refetches.
NOTE: a UNIQUE(user_id, ticker) constraint also guards this at the database level,
      so a race between two simultaneous requests still cannot create a duplicate."""))

st.extend(flow("F-35","Remove a ticker",
 [["Trigger","Row -> remove"],["Path","DELETE /api/v1/watchlist/{ticker}"],
  ["Auth","Bearer"],["Tables","watchlist (SELECT, DELETE)"]],
"""1  [DB]   SELECT ... WHERE user_id = :me AND ticker = UPPER(:ticker)
2  [API]  If None -> 404 "Ticker not on watchlist".  [STOP]
3  [DB]   await db.delete(item); commit on return -> 204 No Content."""))

# ═══════════ G. JOURNAL ═══════════
st.append(P("G. Trading Journal", "H1"))

st.extend(flow("F-36","List journal entries",
 [["Trigger","Open /journal"],["Path","GET /api/v1/trades"],
  ["Auth","Bearer"],["Tables","trades (SELECT)"]],
"""1  [DB]   SELECT * FROM trades WHERE user_id = :me ORDER BY closed_at DESC
2  [UI]   Table renders; client-side filters (symbol, result, strategy) narrow the view
          without any further request."""))

st.extend(flow("F-37","Log a trade",
 [["Trigger","Journal -> submit the trade form"],["Path","POST /api/v1/trades"],
  ["Auth","Bearer"],["Tables","trades (INSERT)"]],
"""1  [UI]   Form collects ticker, side, entry_price, exit_price, stop_loss, take_profit,
          quantity, strategy_label, opened_at, closed_at, notes.
2  [UI]   A live preview computes P/L and the risk-reward multiple before submission.
3  [API]  Body validated as TradeCreate; ticker upper-cased; side coerced to the TradeSide enum.
4  [DB]   INSERT INTO trades (...); created_at defaults to now().
5  [DB]   flush + refresh; commit on return -> 201 Created.
6  [UI]   List refetches and every statistic in F-39 recomputes."""))

st.extend(flow("F-38","Delete a journal entry",
 [["Trigger","Journal -> delete a row"],["Path","DELETE /api/v1/trades/{trade_id}"],
  ["Auth","Bearer"],["Tables","trades (SELECT, DELETE)"]],
"""1  [DB]   SELECT * FROM trades WHERE id = :id AND user_id = :me
2  [API]  If None -> 404 "Trade not found".  [STOP]
3  [DB]   delete; commit -> 204 No Content.
4  [UI]   Statistics and the equity curve recompute."""))

st.extend(flow("F-39","Journal statistics (client-side)",
 [["Trigger","Whenever the trade list changes"],["Path","(no request)"],
  ["Auth","n/a"],["Tables","none"]],
"""1  [UI]   For each trade:  pnl = (side==='buy' ? 1 : -1) * (exit_price - entry_price) * quantity
2  [UI]   wins = trades with pnl > 0 ; losses = trades with pnl < 0
3  [UI]   winRate      = wins / (wins + losses)
          netPL        = SUM(pnl)
          profitFactor = SUM(win pnl) / |SUM(loss pnl)|
          equityCurve  = running cumulative sum of pnl ordered by closed_at
4  [UI]   Stat cards, the equity line chart and the win/loss doughnut render from these values.
NOTE: these figures are computed in the browser - the API returns raw trades only."""))

# ═══════════ H. MARKETPLACE ═══════════
st.append(PageBreak())
st.append(P("H. Marketplace", "H1"))

st.extend(flow("F-40","Browse marketplace listings",
 [["Trigger","Open /marketplace"],["Path","GET /api/v1/marketplace"],
  ["Auth","Bearer"],["Tables","marketplace_listings, strategies, users (SELECT, eager)"]],
"""1  [DB]   SELECT * FROM marketplace_listings
          .options(selectinload(MarketplaceListing.strategy)
                   .selectinload(Strategy.owner))
          ORDER BY created_at DESC
          -> selectinload issues batched IN queries instead of N+1 lookups
2  [API]  For each listing build a flat DTO:
          id, strategy_id, price_cents, status, avg_rating, rating_count, sales_count,
          all six backtest_* metrics (each cast to float or None),
          listed_at, and a nested strategy {id, name, description, weights, is_preset,
          owner:{full_name}}
3  [UI]   Cards render with the weight chips, metrics, star rating and price."""))

st.extend(flow("F-41","Load approval thresholds",
 [["Trigger","Marketplace mount"],["Path","GET /api/v1/marketplace/thresholds"],
  ["Auth","Bearer (any signed-in user)"],["Tables","platform_settings (SELECT/INSERT)"]],
"""1  [DB]   get_settings(db): db.get(PlatformSettings, 1)
2  [API]  If the singleton row is absent it is CREATED with the defaults
          (100 trades, 0.65 win rate, 1.0 Sharpe, 0.15 drawdown, 1.5 profit factor)
          and flushed - so the endpoint is self-healing on a fresh database.
3  [API]  thresholds_dict(settings) casts the Numeric columns to float.
4  [UI]   The five threshold cards render from the live values (not hard-coded), and the
          same object is passed into the publish dialog for its checklist (F-45)."""))

st.extend(flow("F-42","Search, sort and filter listings",
 [["Trigger","Toolbar interaction"],["Path","(client only)"],
  ["Auth","n/a"],["Tables","none"]],
"""1  [UI]   useMemo recomputes on every change of listings, search, sortBy or filterStatus.
2  [UI]   search  -> case-insensitive match on strategy name OR owner full name
3  [UI]   filter  -> 'verified' keeps status in {verified, listed}; 'free' keeps price_cents falsy
4  [UI]   sort    -> rating | return | sharpe | price_low | newest
5  [UI]   The grid re-renders; an empty result shows a contextual empty state."""))

st.extend(flow("F-43","Open the publish dialog",
 [["Trigger","Marketplace -> Request Publish"],["Path","GET /api/v1/strategies"],
  ["Auth","Bearer"],["Tables","strategies (SELECT)"]],
"""1  [UI]   PublishDialog mounts and fetches the user's strategies.
2  [DB]   SELECT * FROM strategies
          WHERE owner_id = :me OR is_preset = true
          ORDER BY created_at DESC
3  [UI]   Client-side filter keeps only  !is_preset && !is_published  -> selectable candidates.
4  [UI]   If none remain, the dialog shows guidance to create one in the Advisor first.  [STOP]
5  [UI]   The first candidate is preselected and its factor weights render as chips."""))

st.extend(flow("F-44","Auto-fill metrics by running a real backtest",
 [["Trigger","Publish dialog -> Run Backtest"],["Path","GET /api/v1/analysis/{ticker}/backtest"],
  ["Auth","Bearer"],["Tables","none &mdash; live"]],
"""1  [UI]   User types a ticker (Enter also submits).
2  [UI]   The selected strategy's stored weights are read from its JSONB column and
          converted into w_* query parameters.
3  [HTTP] GET /analysis/{TICKER}/backtest?period=1y&risk=Moderate&horizon=Medium&w_*=..
4         The full engine of F-25 executes.
5  [UI]   The six form fields are populated from the response:
          trades, win_rate*100, sharpe, max_drawdown_pct, profit_factor, total_return_pct
6  [UI]   A confirmation label shows 'auto-filled for {TICKER}'; the threshold checklist
          re-evaluates immediately.
7         Manual entry remains possible - the fields stay editable.""",
 [["Bad ticker or engine failure","Inline error under the runner; the form keeps its previous values"]]))

st.extend(flow("F-45","Submit a publish request",
 [["Trigger","Publish dialog -> Submit for Review"],["Path","POST /api/v1/strategies/{id}/publish"],
  ["Auth","Bearer + role IN (analyst, admin)"],["Tables","strategies, platform_settings, marketplace_listings"]],
"""0  [UI]   Role gate: investors never see this dialog. The Marketplace shows them a
          disabled 'Analyst role required' card instead of the publish CTA.
1  [UI]   Client-side gate: the button stays disabled until all five checks pass.
          trades >= min_trades ; win_rate >= min_winrate ; sharpe >= min_sharpe ;
          0 < drawdown <= max_drawdown ; profit_factor >= min_profit_factor
2  [HTTP] POST body: price_cents (dollars*100), backtest_trades, backtest_winrate,
          backtest_sharpe, backtest_max_drawdown, backtest_profit_factor, backtest_return
2a [AUTH] require_role(analyst, admin) runs BEFORE the handler.
          An investor is rejected here with 403 "Insufficient permissions",
          regardless of what the browser displays.                        [STOP]
3  [DB]   SELECT * FROM strategies WHERE id = :id AND owner_id = :me
          - not found or not owned -> 404 "Strategy not found"  [STOP]
4  [DB]   get_settings(db) -> the live thresholds (server-side re-validation; the client
          check is convenience only and cannot be trusted)
5  [API]  Evaluate each metric, collecting a message per failure:
          trades < min          -> "Min trades: X/Y"
          winrate < min         -> "Win rate: X%/Y%"
          sharpe < min          -> "Sharpe: X/Y"
          drawdown > max        -> "Max drawdown: X%/Y%"
          profit factor < min   -> "Profit factor: X/Y"
6  [API]  If any failures -> 400 "Backtest thresholds not met: ..." and NOTHING is stored. [STOP]
7  [DB]   SELECT * FROM marketplace_listings WHERE strategy_id = :id
8  [API]  Branch on the existing listing:
          - status == review    -> 400 "Already pending review"   [STOP]
          - status == verified  -> 400 "Already published"        [STOP]
          - other status        -> UPDATE it: status=review, price and all six metrics
          - no listing          -> INSERT a new row with status=review and the metrics
9  [DB]   flush; get_db() commits on return.
10 [API]  Respond {"status":"review", "listing_id": "..."}
11 [UI]   Dialog closes and the marketplace refetches - the strategy now shows 'In Review'.
12        It is invisible to buyers until an administrator approves it (F-51).""",
 [["Investor attempts the call directly","403 Insufficient permissions &mdash; blocked before any database access"],
  ["Any threshold not met","400 with a per-metric breakdown; no listing is created or modified"],
  ["Already in review / already verified","400; the existing listing is left untouched"]]))

# ═══════════ I. NOTIFICATIONS ═══════════
st.append(P("I. Notifications", "H1"))

st.extend(flow("F-46","Load notifications",
 [["Trigger","Header mount / open the bell"],["Path","GET /api/v1/notifications"],
  ["Auth","Bearer"],["Tables","notifications (SELECT)"]],
"""1  [DB]   SELECT * FROM notifications WHERE user_id = :me
          ORDER BY created_at DESC LIMIT 50
2  [UI]   useNotifications derives unreadCount = items.filter(n => !n.is_read).length
3  [UI]   The bell shows a badge with the count; each row renders an icon chosen from
          `kind` and a relative timestamp ("Just now", "5m ago", "3h ago", "2d ago")."""))

st.extend(flow("F-47","Mark one notification read",
 [["Trigger","Click a notification row"],["Path","PUT /api/v1/notifications/{id}/read"],
  ["Auth","Bearer"],["Tables","notifications (SELECT, UPDATE)"]],
"""1  [DB]   SELECT ... WHERE id = :id AND user_id = :me     (ownership scoped)
2  [API]  If None -> 404 "Notification not found".  [STOP]
3  [API]  notif.is_read = True   (no explicit flush - get_db() commits the dirty object)
4  [UI]   Local state updates optimistically; the badge count decrements."""))

st.extend(flow("F-48","Mark all read",
 [["Trigger","Bell dropdown -> Mark all as read"],["Path","PUT /api/v1/notifications/read-all"],
  ["Auth","Bearer"],["Tables","notifications (bulk UPDATE)"]],
"""1  [DB]   UPDATE notifications SET is_read = true
          WHERE user_id = :me AND is_read = false
          - a single set-based statement; rows are never loaded into Python
2  [API]  Return {"ok": true}; commit on return.
3  [UI]   The badge clears and every row loses its unread styling."""))

# ═══════════ J. ADMIN ═══════════
st.append(PageBreak())
st.append(P("J. Administration", "H1"))
st.append(P("Every route in this group depends on <font face='Courier'>require_role(UserRole.admin)</font>, "
            "which runs <font face='Courier'>get_current_user</font> first and then returns "
            "<b>403 Insufficient permissions</b> if the role does not match. The client-side "
            "<font face='Courier'>AdminRoute</font> guard is convenience only."))

st.extend(flow("F-49","Load the admin dashboard",
 [["Trigger","Navigate to /admin"],["Path","7 parallel GET requests"],
  ["Auth","Bearer + role=admin"],["Tables","users, strategies, listings, platform_settings"]],
"""1  [UI]   Admin.fetchData() issues seven requests together with Promise.all:
          /admin/stats  /admin/revenue  /admin/pending  /admin/listings
          /admin/strategies  /admin/users  /admin/thresholds
2  [API]  stats - four aggregate queries, none of which load rows into memory:
          SELECT count(users.id)
          SELECT count(strategies.id)
          SELECT count(listings.id) WHERE status = 'review'      -> pending badge
          SELECT count(listings.id) WHERE status = 'verified'
          SELECT coalesce(sum(price_cents * sales_count), 0)
                 WHERE status IN ('verified','listed')            -> total revenue
          SELECT coalesce(sum(sales_count), 0)  (same filter)     -> total sales
3  [API]  revenue - listings with sales_count > 0, eager-loading strategy and owner,
          ordered by (price_cents * sales_count) DESC; the top 10 become top_strategies
          with strategy_name, creator, price, sales and revenue.
4  [API]  pending - listings WHERE status='review', eager-loaded, newest first, each
          serialised by _listing_dict() including all six backtest metrics and the
          strategy's factor weights.
5  [UI]   Six stat tiles render; the Pending Reviews tab shows a badge with its count.
6  [UI]   Any failure is caught and logged; loading is cleared so the page still renders."""))

st.extend(flow("F-50","Manage users",
 [["Trigger","Admin -> Users tab"],["Path","GET/PATCH/DELETE /api/v1/admin/users..."],
  ["Auth","Bearer + role=admin"],["Tables","users (SELECT, UPDATE, DELETE)"]],
"""LIST      1 [DB] SELECT * FROM users ORDER BY created_at DESC
          2 [API] Serialise id, email, full_name, role.value, is_active, created_at.

CHANGE    1 [API] PATCH /admin/users/{id}/role?role=analyst
ROLE      2 [API] Self-guard: if user_id == admin.id -> 400 "Cannot change your own role" [STOP]
          3 [API] UserRole(role) -> ValueError yields 400 "Invalid role: X"           [STOP]
          4 [DB]  SELECT the target; None -> 404.
          5 [DB]  user.role = new_role; flush; commit. Effect is immediate: the user's
                  next request re-reads the row in get_current_user.

TOGGLE    1 [API] PATCH /admin/users/{id}/status
STATUS    2 [API] Self-guard: cannot deactivate yourself -> 400                        [STOP]
          3 [DB]  user.is_active = NOT user.is_active; flush; commit.
          4        A suspended user's very next request fails get_current_user -> 401.

DELETE    1 [API] DELETE /admin/users/{id}
          2 [API] Self-guard: cannot delete yourself -> 400                            [STOP]
          3 [DB]  SELECT; None -> 404.
          4 [DB]  DELETE the row. ON DELETE CASCADE removes that user's holdings,
                  watchlist, trades, strategies, notifications and ratings.""",
 [["Acting on your own account","400 for role change, status toggle and delete alike"]]))

st.extend(flow("F-51","Review and approve a listing (the approval lifecycle)",
 [["Trigger","Admin -> Pending Reviews"],["Path","GET /admin/pending then POST .../approve|reject|remove"],
  ["Auth","Bearer + role=admin"],["Tables","marketplace_listings, strategies"]],
"""1  [UI]   Each pending card renders the full backtest report:
          six metric tiles + a checklist ticking each metric against its threshold,
          the strategy's factor weights, the author, and the submission date.
2  [UI]   Admin clicks one of four actions; doAction() sets a per-row loading flag,
          awaits the call, then refetches every admin dataset.

APPROVE   1 [DB]  SELECT the listing WITH selectinload(strategy).
          2 [API] Guard: status must be 'review', else 400 "Only listings in review
                  can be approved".                                                    [STOP]
          3 [DB]  listing.status = verified
                  listing.listed_at = now(UTC)
                  listing.strategy.is_published = True
          4 [DB]  flush; commit -> the listing is now publicly visible in /marketplace.

REJECT    1 [DB]  Same load + the same 'review' guard.
          2 [DB]  listing.status = removed ; strategy.is_published = False; commit.

REMOVE    1        Same as reject but WITHOUT the status guard - it can delist an
                   already-verified/listed strategy.

DELETE    1 [DB]  Load the listing; None -> 404.
          2 [DB]  strategy.is_published = False, then DELETE the listing row permanently.
                  (This also frees the strategy, whose FK is otherwise RESTRICT.)""",
 [["Listing not in 'review'","approve/reject return 400; use Remove for live listings"],
  ["Listing id unknown","404 Listing not found"]]))

st.extend(flow("F-52","Strategies tab and threshold configuration",
 [["Trigger","Admin -> Strategies / Thresholds"],["Path","GET|DELETE /admin/strategies, GET|PUT /admin/thresholds"],
  ["Auth","Bearer + role=admin"],["Tables","strategies, marketplace_listings, platform_settings"]],
"""LIST      1 [DB] SELECT * FROM strategies .options(selectinload(owner)) ORDER BY created_at DESC
STRATEGIES2 [API] Each row exposes name, description, weights, is_preset, is_published,
                  owner_name ('System' when owner_id is NULL) and owner_email.

DELETE    1 [DB] SELECT the strategy WITH selectinload(listing).
STRATEGY  2 [API] None -> 404.
          3 [DB] If a listing exists, DELETE it first (satisfying the RESTRICT FK),
                 then DELETE the strategy; flush; commit.

READ      1 [DB] get_settings(db) -> the singleton row (created with defaults if absent).
THRESHOLDS2 [UI] The editor converts stored fractions to friendly units for display:
                 win rate and drawdown are shown as percentages (0.65 -> 65).

UPDATE    1 [UI] Save converts back to fractions (65 -> 0.65) and PUTs all five values.
THRESHOLDS2 [API] Bounds validation, each failure returning 400 with a specific message:
                 0 <= min_trades <= 100000 ; 0 <= min_winrate <= 1 ;
                 0 <= min_sharpe <= 20 ; 0 < max_drawdown <= 1 ;
                 0 <= min_profit_factor <= 100
          3 [DB] Assign the five columns on the singleton row; flush; commit.
          4      Effect is immediate and global, with no redeploy:
                 - F-45 reads the row on every publish attempt
                 - F-41 feeds the marketplace cards and the publish checklist"""))

# ═══════════ CROSS-CUTTING ═══════════
st.append(P("K. Cross-Cutting Behaviour", "H1"))
st.append(P("These mechanisms apply to every flow above and are the reason individual handlers stay small."))

st.append(table(["Mechanism","Where","Behaviour"], [
 ["Transaction boundary","db/session.py &mdash; get_db()",
  "One AsyncSession per request. It yields to the handler, commits if the handler returns normally, rolls back on any exception, and always closes. A request therefore applies all of its writes or none."],
 ["Authentication","core/dependencies.py &mdash; get_current_user",
  "Runs before every protected handler: decode the JWT, parse sub as a UUID, load the user, and reject with 401 if the token is invalid or the account is inactive."],
 ["Authorisation","core/dependencies.py &mdash; require_role",
  "A dependency factory used by admin routes; returns 403 when user.role is not in the allowed set."],
 ["Ownership scoping","every user-data route",
  "Queries filter by user_id/owner_id in the WHERE clause, so another user's row returns 404 rather than 403 &mdash; existence is never leaked."],
 ["Input validation","Pydantic schemas",
  "Bodies are validated before the handler runs; a malformed payload returns 422 without touching the database."],
 ["Eager loading","selectinload(...)",
  "Marketplace and admin queries preload nested strategy/owner objects with batched IN queries, avoiding N+1."],
 ["CPU offloading","run_in_threadpool",
  "The vectorbt simulation is CPU-bound, so it runs in a worker thread and never blocks the async event loop."],
 ["External-call fan-out","ThreadPoolExecutor + asyncio.gather",
  "Portfolio price lookups run up to 4 yfinance calls concurrently; dashboard sub-flows are gathered in parallel."],
 ["Numeric sanitisation","_safe_float helpers",
  "NaN and Infinity are coerced to safe defaults before serialisation, because JSON cannot represent them."],
 ["Token attach &amp; retry","api/client.js interceptors",
  "Every outgoing request gains the bearer token; a 401 triggers one refresh-and-retry, with concurrent calls queued behind a single refresh."],
], [1.25*inch, 1.55*inch, CW-2.8*inch]))

st.append(Spacer(1,8))
st.append(callout("Flows that never touch the database",
    "The entire AI path is live: <font face='Courier'>/analysis/*</font>, <font face='Courier'>/live/*</font>, "
    "<font face='Courier'>/sentiment/*</font> and <font face='Courier'>/dashboard/market-indices</font> read from "
    "Yahoo Finance on every request and return without persisting. Verdicts computed in F-20 and backtests in F-25 "
    "are <b>not</b> written to <font face='Courier'>predictions</font> or <font face='Courier'>price_history</font> &mdash; "
    "those tables are populated by the seed script and serve the badge/reference endpoints only.",
    LIGHTRED, RED))

def footer(canvas, d):
    canvas.saveState()
    canvas.setFont("Helvetica", 7.4)
    canvas.setFillColor(GREY)
    canvas.drawCentredString(PAGE_W/2, 25,
        f"StockPilot - Data Flow Reference  |  Group 13, CSE5015  |  Page {d.page}")
    canvas.restoreState()

doc.build(st, onFirstPage=footer, onLaterPages=footer)
print("Generated:", OUT)
