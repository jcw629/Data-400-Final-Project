"""
8. PriceChangeTab

"""


import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px

def render_price_change_tab(portfolio_df):
    st.markdown("""
    <style>
    html, body, [class*="stApp"] {
        font-family: 'Montserrat', sans-serif !important;
        background-color: #1C1C24 !important;
        color: #FFFFFF !important;
    }
    section[data-testid="stSidebar"] {
        background-color: #262637 !important;
    }
    h1, h2, h3, h4, h5, h6, p, div, span {
        color: #FFFFFF !important;
    }
    /* Force dropdown font to be black for visibility */
    [data-baseweb="select"] * {
        color: black !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.title("Price Change & Volatility")

    df = portfolio_df.copy()

    # Define helper functions
    @st.cache_data
    def get_change(ticker, period):
        try:
            hist = yf.Ticker(ticker).history(period=period)
            return ((hist["Close"].iloc[-1] - hist["Close"].iloc[0]) / hist["Close"].iloc[0]) * 100
        except:
            return np.nan

    @st.cache_data
    def get_volatility(ticker):
        try:
            hist = yf.Ticker(ticker).history(period="30d")
            returns = hist["Close"].pct_change().dropna()
            return np.std(returns) * 100
        except:
            return np.nan

    @st.cache_data
    def get_max_drawdown(ticker):
        try:
            hist = yf.Ticker(ticker).history(period="90d")["Close"]
            roll_max = hist.cummax()
            drawdown = (hist - roll_max) / roll_max
            return drawdown.min() * 100
        except:
            return np.nan

    @st.cache_data
    def get_52w_high(ticker):
        try:
            return yf.Ticker(ticker).info.get("fiftyTwoWeekHigh")
        except:
            return np.nan

    # Add static metrics
    df["1D %"] = df["ticker"].apply(lambda t: get_change(t, "2d"))
    df["1W %"] = df["ticker"].apply(lambda t: get_change(t, "7d"))
    df["1M %"] = df["ticker"].apply(lambda t: get_change(t, "30d"))
    df["Volatility (30d)"] = df["ticker"].apply(get_volatility)
    df["Max Drawdown (90d)"] = df["ticker"].apply(get_max_drawdown)
    df["52W High"] = df["ticker"].apply(get_52w_high)
    df["From 52W High"] = ((df["price"] - df["52W High"]) / df["52W High"]) * 100

    # === RETURN PERIOD SELECTION ===
    period_map = {
        "1 Day": "2d",
        "1 Week": "7d",
        "1 Month": "30d",
        "6 Months": "6mo",
        "1 Year": "1y",
        "5 Years": "5y",
        "All Time": "max"
    }

    st.subheader("Select Return Period")
    selected_label = st.selectbox("Choose return period", list(period_map.keys()))
    period = period_map[selected_label]

    df["Selected %"] = df["ticker"].apply(lambda t: get_change(t, period))

    # === BAR CHART ===
    st.subheader(f"{selected_label} Returns by Ticker")
    fig_bar = px.bar(
        df,
        x="ticker",
        y="Selected %",
        text=df["Selected %"].map(lambda x: f"{x:.2f}%"),
        title=f"{selected_label} Price Change by Ticker",
        labels={"ticker": "Ticker", "Selected %": "Change (%)"},
    )
    fig_bar.update_traces(textposition="outside")
    fig_bar.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        title_font=dict(color='white'),
        xaxis=dict(color='white'),
        yaxis=dict(color='white'),
        hoverlabel=dict(bgcolor='black', font_color='white')
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    # === NORMALIZED PRICE LINE CHART ===
    st.subheader("Normalized Price History (Last 90 Days)")
    selected = st.multiselect("Compare stocks", df["ticker"].tolist(), default=df["ticker"].tolist())

    @st.cache_data
    def get_price_history(tickers):
        chart_data = pd.DataFrame()
        for ticker in tickers:
            try:
                hist = yf.Ticker(ticker).history(period="90d")["Close"]
                hist = hist / hist.iloc[0] * 100
                chart_data[ticker] = hist
            except:
                continue
        chart_data.index.name = "Date"
        return chart_data

    price_chart_df = get_price_history(selected)
    if not price_chart_df.empty:
        fig_line = px.line(
            price_chart_df,
            x=price_chart_df.index,
            y=price_chart_df.columns,
            labels={"value": "Normalized Price", "Date": "Date"},
            title="Normalized Price Over Last 90 Days"
        )
        fig_line.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            title_font=dict(color='white'),
            xaxis=dict(color='white'),
            yaxis=dict(color='white'),
            hoverlabel=dict(bgcolor='black', font_color='white')
        )
        st.plotly_chart(fig_line, use_container_width=True)

    # === METRICS TABLE ===
    st.subheader("Detailed Price & Risk Metrics")
    st.dataframe(df[[ 
        "ticker", "price", "1D %", "1W %", "1M %",
        "Volatility (30d)", "Max Drawdown (90d)", "From 52W High"
    ]], use_container_width=True, height=300)
