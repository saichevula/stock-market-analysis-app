import html as html_lib
from datetime import datetime, timezone

import streamlit as st

from utils.data import get_top5

st.set_page_config(
    layout="wide",
    page_title="Stock Analyzer",
    page_icon="📈",
    menu_items={'Get Help': None, 'Report a bug': None, 'About': None},
)

# ---------------------------------------------------------------------------
# Styling — a ledger / trading-ticket look: ruled paper background, a serif
# headline, monospace for anything that's actually a number. No dark-mode
# neon, no gradient text, no rounded-shadow card grid.
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500;600&display=swap');

    :root{
        --paper: #F2F0E8;
        --panel: #FBFAF4;
        --ink: #1B2430;
        --ink-soft: #5B6472;
        --line: #DEDACB;
        --brass: #7C5F1E;
        --gain: #2F6F4F;
    }

    [data-testid="stAppViewContainer"], .stApp{
        background-color: var(--paper);
    }
    [data-testid="stHeader"]{ background: transparent; }
    [data-testid="stToolbar"]{ visibility: hidden; }

    html, body, [class*="css"]{
        font-family: 'Inter', sans-serif;
        color: var(--ink);
    }

    .nc-hero{
        padding: 4px 0 18px;
        border-bottom: 1px solid var(--line);
        margin-bottom: 26px;
    }
    .nc-hero h1{
        font-family: 'Fraunces', serif;
        font-weight: 600;
        font-size: clamp(2rem, 1.4rem + 2vw, 3rem);
        margin: 0 0 6px;
        letter-spacing: -0.01em;
    }
    .nc-hero p.tagline{
        font-size: 0.98rem;
        color: var(--ink-soft);
        margin: 0 0 14px;
        max-width: 54ch;
    }
    .nc-status-row{
        display: flex;
        align-items: center;
        gap: 18px;
        flex-wrap: wrap;
    }
    .nc-pill{
        display: inline-flex;
        align-items: center;
        gap: 7px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.76rem;
        padding: 5px 10px;
        border-radius: 999px;
        border: 1px solid var(--line);
        background: var(--panel);
        color: var(--ink-soft);
    }
    .nc-dot{ width: 7px; height: 7px; border-radius: 50%; }
    .nc-dot.open{ background: var(--gain); animation: nc-pulse 1.4s ease-in-out infinite; }
    .nc-dot.closed{ background: var(--ink-soft); }
    @keyframes nc-pulse{ 0%,100%{opacity:1;} 50%{opacity:0.35;} }
    @media (prefers-reduced-motion: reduce){ .nc-dot.open{ animation: none; } }

    .nc-clock{
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.76rem;
        color: var(--ink-soft);
    }

    .nc-sidebar-hint{
        display: flex;
        gap: 10px;
        align-items: flex-start;
        border: 1px solid var(--line);
        background: var(--panel);
        border-radius: 6px;
        padding: 12px 14px;
        margin-bottom: 26px;
        max-width: 480px;
    }
    .nc-sidebar-hint .arrow{
        font-family: 'JetBrains Mono', monospace;
        color: var(--brass);
        font-size: 1rem;
        line-height: 1.3;
    }
    .nc-sidebar-hint p{ margin: 0; font-size: 0.85rem; color: var(--ink-soft); line-height: 1.5; }
    .nc-sidebar-hint strong{ color: var(--ink); }

    .nc-ledger-title{
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 0.75rem;
        letter-spacing: 0.06em;
        color: var(--ink-soft);
        margin: 0 0 10px;
    }
    .nc-ledger{
        border: 1px solid var(--line);
        background: var(--panel);
        border-radius: 6px;
        overflow: hidden;
        max-width: 480px;
    }
    .nc-row{
        display: grid;
        grid-template-columns: 40px 1fr auto;
        align-items: center;
        gap: 14px;
        padding: 12px 16px;
        border-bottom: 1px solid var(--line);
        transition: background 0.12s ease;
    }
    .nc-row:last-child{ border-bottom: none; }
    .nc-row:hover{ background: rgba(156, 122, 41, 0.07); }
    .nc-rank{ font-family: 'JetBrains Mono', monospace; font-size: 0.74rem; color: var(--ink-soft); }
    .nc-ticker{ font-family: 'JetBrains Mono', monospace; font-weight: 600; font-size: 0.95rem; letter-spacing: 0.02em; }
    .nc-price{ font-family: 'JetBrains Mono', monospace; font-size: 0.95rem; font-variant-numeric: tabular-nums; }

    details.nc-about{
        margin-top: 30px;
        border-top: 1px solid var(--line);
        padding-top: 16px;
        max-width: 68ch;
    }
    details.nc-about summary{
        cursor: pointer;
        font-weight: 600;
        font-size: 0.88rem;
        list-style: none;
    }
    details.nc-about summary::-webkit-details-marker{ display: none; }
    details.nc-about summary::before{ content: '+ '; color: var(--brass); }
    details.nc-about[open] summary::before{ content: '– '; }
    details.nc-about .body{
        margin-top: 10px;
        font-size: 0.86rem;
        line-height: 1.6;
        color: var(--ink-soft);
    }
    details.nc-about .body p{ margin: 0 0 10px; }
    details.nc-about .body p:last-child{ margin-bottom: 0; }
    details.nc-about .body strong{ color: var(--ink); }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Market status — approximate NYSE hours (9:30am-4pm ET, weekdays).
# Not holiday-adjusted. Falls back gracefully if timezone data isn't
# available in the deploy environment, rather than showing wrong info.
# ---------------------------------------------------------------------------
tz_available = True
try:
    from zoneinfo import ZoneInfo
    now_et = datetime.now(ZoneInfo("America/New_York"))
except Exception:
    tz_available = False
    now_et = datetime.now(timezone.utc)

status_html = ""
if tz_available:
    is_weekday = now_et.weekday() < 5
    open_time = now_et.replace(hour=9, minute=30, second=0, microsecond=0)
    close_time = now_et.replace(hour=16, minute=0, second=0, microsecond=0)
    market_open = is_weekday and open_time <= now_et <= close_time
    status_label = "Market open" if market_open else "Market closed"
    dot_class = "open" if market_open else "closed"
    status_html = (
        f'<span class="nc-pill"><span class="nc-dot {dot_class}"></span>'
        f'{status_label} · NYSE hours, ET</span>'
        f'<span class="nc-clock">{now_et.strftime("%a %d %b · %I:%M %p %Z")}</span>'
    )

# ---------------------------------------------------------------------------
# Hero
# ---------------------------------------------------------------------------
st.markdown(
    f"""
    <div class="nc-hero">
        <h1>Stock Analyzer</h1>
        <p class="tagline">A ledger for watching prices move, and a workbench for testing
        trading strategies against real history.</p>
        <div class="nc-status-row">{status_html}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Sidebar hint
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="nc-sidebar-hint">
        <span class="arrow">&rarr;</span>
        <p><strong>Open the sidebar</strong> to pull up a ticker, chart its price
        history, and backtest four trading strategies against it.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Top 5 by price — same data source and function as before (utils.data.get_top5),
# just presented as a ledger instead of a raw dataframe. Falls back to the
# plain table if the data doesn't come back in the expected shape, so a
# formatting hiccup never breaks the page.
# ---------------------------------------------------------------------------
st.markdown('<p class="nc-ledger-title">TOP 5 BY PRICE</p>', unsafe_allow_html=True)

try:
    df = get_top5()
except Exception:
    df = None

if df is None or df.empty:
    st.info("Live prices are taking a moment to load — refresh in a few seconds.")
else:
    try:
        cols = list(df.columns)
        ticker_col = cols[0]
        price_col = cols[1] if len(cols) > 1 else cols[0]

        rows_html = ""
        for i, (_, row) in enumerate(df.iterrows(), start=1):
            ticker = html_lib.escape(str(row[ticker_col]))
            price = html_lib.escape(str(row[price_col]))
            rows_html += (
                f'<div class="nc-row">'
                f'<span class="nc-rank">{i:02d}</span>'
                f'<span class="nc-ticker">{ticker}</span>'
                f'<span class="nc-price">{price}</span>'
                f'</div>'
            )

        st.markdown(f'<div class="nc-ledger">{rows_html}</div>', unsafe_allow_html=True)
    except Exception:
        st.dataframe(df, hide_index=True, use_container_width=True)

# ---------------------------------------------------------------------------
# About
# ---------------------------------------------------------------------------
st.markdown(
    """
    <details class="nc-about">
        <summary>What's inside this app</summary>
        <div class="body">
            <p><strong>Analysis page:</strong> enter one or more tickers to see closing
            price, 50-day moving average, and daily returns over the past year, plus a
            quick read on each stock's best day, worst day, and volatility.</p>
            <p><strong>Backtesting:</strong> the same page runs four strategies —
            Moving Average Crossover, RSI, Bollinger Bands, and MACD — against five
            years of history, and lines up total return, drawdown, win rate, profit
            factor, and Sharpe ratio side by side so you can see which approach
            actually held up.</p>
        </div>
    </details>
    """,
    unsafe_allow_html=True,
)
