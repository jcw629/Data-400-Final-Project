"""
3. Dashboard

"""
# Import necessary libraries
import streamlit as st
import pandas as pd
import plotly.express as px
import yfinance as yf
import sys
import os

# Add the project root to sys.path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from stock_dashboard.overview_tab import render_overview_tab
from stock_dashboard.price_change_tab import render_price_change_tab
from stock_dashboard.value_over_time_tab import render_value_over_time_tab
from stock_dashboard.summary_tab import render_summary_tab
from stock_dashboard.export_tab import render_export_tab

# -------------------- PAGE CONFIG --------------------
st.set_page_config(page_title="Portfolio Dashboard", layout="wide")

# -------------------- STYLING --------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600&display=swap');

/* Global Reset */
html, body, [class*="css"] {
    font-family: 'Montserrat', sans-serif;
    background-color: #2E3B4E; /* Greyish-blue background */
    color: white; /* White text */
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #34495E;  /* Lighter sidebar */
    color: white;
}
[data-testid="stSidebar"] .css-1v0mbdj, .css-1v0mbdj {
    color: white !important;
}

/* Inputs */
input, textarea {
    background-color: #34495E;
    color: white;
    border: 1px solid #1ABC9C;
    border-radius: 8px;
}
.stNumberInput input {
    background-color: #34495E !important;
    color: white !important;
}

/* Buttons */
button[kind="primary"] {
    background-color: #1ABC9C;
    border: none;
    border-radius: 8px;
    font-size: 16px;
    font-weight: 600;
}
button[kind="primary"]:hover {
    background-color: #16A085;
}

/* Titles */
h1 {
    font-size: 2.5rem;
    font-weight: 600;
    color: white; /* White text */
    margin-bottom: 1rem;
    text-align: center;
}
h3 {
    font-size: 1.5rem;
    font-weight: 500;
    color: white; /* White text */
    margin-bottom: 0.75rem;
}

/* View Options Styling */
.view-options-header {
    font-size: 1.5rem;
    font-weight: 600;
    color: white;
    margin-bottom: 1rem;
    text-align: left;
}

/* Messages */
[data-testid="stSuccess"], [data-testid="stWarning"] {
    background-color: #3B4A59; /* Slightly darker background for messages */
    border-radius: 10px;
    padding: 15px;
    font-size: 16px;
    font-weight: 500;
}
</style>
""", unsafe_allow_html=True)

# -------------------- SHARED DATA PREPARATION --------------------
# Initialize portfolio
portfolio = st.session_state.get("portfolio", [])
if not portfolio:
    st.warning("No portfolio found. Using sample data.")
    portfolio = [
        {"ticker": "AAPL", "quantity": 10}, {"ticker": "MSFT", "quantity": 5},
        {"ticker": "TSLA", "quantity": 3}, {"ticker": "AMZN", "quantity": 8},
        {"ticker": "GOOGL", "quantity": 6}, {"ticker": "NESN.SW", "quantity": 12},
        {"ticker": "ASML.AS", "quantity": 4}, {"ticker": "MC.PA", "quantity": 2},
        {"ticker": "SIE.DE", "quantity": 7}, {"ticker": "ULVR.L", "quantity": 9},
        {"ticker": "7203.T", "quantity": 15}, {"ticker": "005930.KS", "quantity": 1},
        {"ticker": "9988.HK", "quantity": 10}, {"ticker": "TCS.NS", "quantity": 5},
        {"ticker": "0700.HK", "quantity": 8}
    ]

# Create portfolio DataFrame
df = pd.DataFrame(portfolio)
df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
df.dropna(subset=["quantity"], inplace=True)

# Fetch prices and calculate values
@st.cache_data(show_spinner=True)
def fetch_price(ticker):
    try:
        stock_info = yf.Ticker(ticker).info
        return stock_info.get("regularMarketPrice", 0)
    except:
        return 0

df["price"] = df["ticker"].apply(fetch_price)
df["value"] = df["price"] * df["quantity"]
df = df[df["price"] > 0]
total_value = df["value"].sum()

# Generate charts
fig_alloc = px.pie(df, values="value", names="ticker", title="Portfolio Allocation")
fig_region = None  # Placeholder for regional diversification chart (if applicable)

# -------------------- VIEW OPTIONS --------------------
st.sidebar.markdown('<div class="view-options-header">View Options</div>', unsafe_allow_html=True)

# Use radio buttons for vertical navigation
selected_tab = st.sidebar.radio(
    label="",
    options=["Overview", "Price Change", "Value Over Time", "Summary", "Export"],
    index=0
)

# -------------------- RENDER SELECTED TAB --------------------
if selected_tab == "Overview":
    render_overview_tab(df, fig_alloc, fig_region, total_value)
elif selected_tab == "Price Change":
    render_price_change_tab(df)
elif selected_tab == "Value Over Time":
    render_value_over_time_tab(df)
elif selected_tab == "Summary":
    render_summary_tab(df)
elif selected_tab == "Export":
    render_export_tab(df, fig_alloc, fig_region, total_value)
