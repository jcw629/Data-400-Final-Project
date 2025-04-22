"""
2. Stock Price Performance Over Time
This chart shows how the stock prices have evolved over time for the selected portfolio.

"""
# Import necessary libraries
import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import numpy as np

# Caching data to improve performance and reduce API calls
@st.cache_data
def get_ticker_currencies(tickers):
    """
    Fetches the currency of each ticker. Defaults to USD if unavailable.
    
    Parameters:
        tickers (list): List of stock tickers (symbols).
        
    Returns:
        dict: A dictionary mapping tickers to their respective currencies.
    """
    currencies = {}
    for ticker in tickers:
        try:
            info = yf.Ticker(ticker).info
            currencies[ticker] = info.get("currency", "USD")
        except:
            currencies[ticker] = "USD"
    return currencies

@st.cache_data
def fetch_fx_rates(currencies):
    """
    Fetches the exchange rates for all currencies in the portfolio (converting to USD).
    
    Parameters:
        currencies (set): A set of unique currencies in the portfolio.
        
    Returns:
        dict: A dictionary mapping each currency to its exchange rate against USD.
    """
    fx_rates = {}
    for curr in currencies:
        if curr == "USD":
            fx_rates[curr] = 1.0
        else:
            fx_symbol = f"{curr}USD=X"
            try:
                fx_data = yf.download(fx_symbol, period="7d", interval="1d", progress=False)
                if not fx_data.empty:
                    fx_rates[curr] = fx_data["Adj Close"].iloc[-1]
                else:
                    fx_rates[curr] = None
            except:
                fx_rates[curr] = None
    return fx_rates

@st.cache_data(show_spinner=True)
def fetch_price_history(tickers, start):
    """
    Fetches the historical stock price data for the specified tickers.
    
    Parameters:
        tickers (list): List of stock tickers.
        start (datetime): The start date for fetching historical data.
        
    Returns:
        pd.DataFrame: A DataFrame with stock price data.
    """
    try:
        data = yf.download(tickers, start=start, auto_adjust=True, progress=False)["Close"]
        return data.dropna(axis=1, how="all") if not data.empty else pd.DataFrame()
    except:
        return pd.DataFrame()

@st.cache_data(show_spinner=True)
def calculate_returns(prices):
    """
    Calculates returns over different periods (1 month, 6 months, 1 year, 5 years).
    
    Parameters:
        prices (pd.DataFrame): DataFrame of historical stock prices.
        
    Returns:
        pd.DataFrame: A DataFrame of the calculated returns for each stock.
    """
    returns = pd.DataFrame(index=prices.columns)
    today = prices.index[-1]

    def calc_return(days):
        try:
            past = prices.index[-1] - pd.Timedelta(days=days)
            past_idx = prices.index[prices.index >= past][0]
            return ((prices.loc[today] - prices.loc[past_idx]) / prices.loc[past_idx]) * 100
        except:
            return pd.Series(np.nan, index=prices.columns)

    # Calculating returns for 1M, 6M, 1Y, and 5Y
    returns["1M"] = calc_return(30)
    returns["6M"] = calc_return(180)
    returns["1Y"] = calc_return(365)
    returns["5Y"] = calc_return(1825)
    
    # Calculating maximum drawdown
    returns["Max Drawdown %"] = (
        prices.apply(lambda x: ((x / x.cummax()) - 1).min() * 100)
    )
    return returns.round(2)

def render_value_over_time_tab(df):
    """
    Renders the Stock Price Performance Over Time tab in the Streamlit app.
    
    Parameters:
        df (pd.DataFrame): A DataFrame containing the stock tickers, quantities, and prices.
        
    Displays:
        - Price performance charts over time
        - Return metrics for different periods
        - Portfolio's volatility and maximum drawdown
    """
    # Set custom styles for the app interface
    st.markdown("""
    <style>
    /* General background and font */
    html, body, [class*="stApp"] {
        background-color: #1E1E2F !important;
        color: white !important;
        font-family: 'Montserrat', sans-serif !important;
    }

    /* Sidebar background and font */
    section[data-testid="stSidebar"] {
        background-color: #262637 !important;
    }
    section[data-testid="stSidebar"] * {
        color: white !important;
    }

    /* Force labels and inputs in main area to be white */
    label, .stRadio > div > label, .stCheckbox > div > label {
        color: white !important;
    }

    /* Fix radio and checkbox text */
    div[role="radiogroup"] > label, div[data-testid="stVerticalBlock"] label {
        color: white !important;
    }

    /* Multiselect dropdown and options */
    .stMultiSelect div[role="button"], .stMultiSelect label {
        color: white !important;
    }
    div[data-baseweb="select"] {
        background-color: #1E1E2F !important;
        color: white !important;
    }
    ul[role="listbox"] > li {
        color: white !important;
        background-color: #1E1E2F !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Add a title to the tab
    st.title("Stock Price Performance Over Time")

    # Sidebar Inputs
    start_date = st.sidebar.date_input("Select Start Date", value=pd.to_datetime("2020-01-01"))

    tickers = df["ticker"].unique().tolist()
    st.sidebar.subheader("Benchmark Comparison")
    benchmark_input = st.sidebar.text_input("Add Benchmark Symbols (comma-separated)", value="^GSPC")
    benchmarks = [t.strip().upper() for t in benchmark_input.split(",") if t.strip()]

    all_tickers = list(set(tickers + benchmarks))
    price_data = fetch_price_history(all_tickers, start=start_date)

    if price_data.empty:
        st.error("No price data found.")
        return

    benchmark_data = price_data[benchmarks].dropna(axis=1, how="all") if benchmarks else pd.DataFrame()
    stock_data = price_data.drop(columns=benchmarks, errors="ignore")

    # FX Conversion (silent)
    currencies = get_ticker_currencies(stock_data.columns.tolist())
    fx_rates = fetch_fx_rates(set(currencies.values()))
    for ticker in stock_data.columns:
        fx = fx_rates.get(currencies.get(ticker, "USD"), 1.0) or 1.0
        stock_data[ticker] *= fx

    # Chart Controls
    st.subheader("Chart Options")
    selected_tickers = st.multiselect("Select Tickers", stock_data.columns.tolist(), default=stock_data.columns.tolist())
    view_type = st.radio("View Type", ["Normalized", "Actual Prices"], horizontal=True)
    log_y = st.checkbox("Logarithmic Y-Axis", value=False)

    chart_data = stock_data[selected_tickers]
    if view_type == "Normalized":
        chart_data = chart_data.divide(chart_data.iloc[0]) * 100
        if not benchmark_data.empty:
            benchmark_data = benchmark_data.divide(benchmark_data.iloc[0]) * 100

    # Create the plot
    fig = go.Figure()

    for ticker in chart_data.columns:
        fig.add_trace(go.Scatter(
            x=chart_data.index,
            y=chart_data[ticker],
            name=ticker,
            line=dict(width=2),
            opacity=0.9,
            hovertemplate=f"{ticker}<br>Date=%{{x|%Y-%m-%d}}<br>Price=%{{y:.2f}}"
        ))

    for bm in benchmark_data.columns:
        fig.add_trace(go.Scatter(
            x=benchmark_data.index,
            y=benchmark_data[bm],
            name=f"{bm} (Benchmark)",
            line=dict(width=3, dash="dash"),
            hovertemplate=f"{bm}<br>Date=%{{x|%Y-%m-%d}}<br>Price=%{{y:.2f}}"
        ))

    # Set layout for the chart
    fig.update_layout(
        title=dict(text=f"{view_type} Performance", font=dict(color='white')),
        xaxis=dict(title="Date", color='white'),
        yaxis=dict(title="Price" if view_type == "Actual Prices" else "Normalized (Start = 100)", type="log" if log_y else "linear", color='white'),
        plot_bgcolor="#1E1E2F",
        paper_bgcolor="#1E1E2F",
        font=dict(color='white'),
        legend=dict(font=dict(color='white')),
        hoverlabel=dict(bgcolor='black', font_color='white')
    )

    # Display the plot
    st.plotly_chart(fig, use_container_width=True)

    # Returns Table
    st.subheader("Performance Summary and Max Drawdown")
    returns_df = calculate_returns(stock_data[selected_tickers])

    def colorize(val):
        if pd.isna(val):
            return "color: lightgray"
        elif val > 0:
            return "color: #00C851"
        elif val < 0:
            return "color: #ff4444"
        return "color: white"

    # Styling the returns table
    styled_df = returns_df.style.format("{:.2f}%").applymap(colorize)
    st.dataframe(styled_df, use_container_width=True)

    # Rolling Volatility Chart
    st.subheader("30-Day Rolling Volatility")
    vol_fig = go.Figure()
    for ticker in selected_tickers:
        returns = stock_data[ticker].pct_change().dropna()
        rolling_vol = returns.rolling(30).std() * 100
        vol_fig.add_trace(go.Scatter(
            x=rolling_vol.index,
            y=rolling_vol,
            name=ticker,
            line=dict(width=2),
            hovertemplate=f"{ticker}<br>Date=%{{x|%Y-%m-%d}}<br>30d Volatility=%{{y:.2f}}%"
        ))

    vol_fig.update_layout(
        title=dict(text="Rolling 30-Day Volatility (Annualized %)", font=dict(color='white')),
        xaxis=dict(title="Date", color='white'),
        yaxis=dict(title="Volatility (%)", color='white'),
        plot_bgcolor="#1E1E2F",
        paper_bgcolor="#1E1E2F",
        font=dict(color='white'),
        legend=dict(font=dict(color='white')),
        hoverlabel=dict(bgcolor='black', font_color='white')
    )

    # Display volatility chart
    st.plotly_chart(vol_fig, use_container_width=True)
