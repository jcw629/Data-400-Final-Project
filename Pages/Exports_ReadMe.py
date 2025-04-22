"""
11. Exports
"""
import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from fpdf import FPDF
from io import BytesIO
import tempfile
import zipfile
import plotly.io as pio

def render_export_tab(ticker_df):
    # === Dark Theme and Full White Styling ===
    st.markdown("""
    <style>
    html, body, [class*="stApp"] {
        background-color: #1E1E2F;
        color: white;
        font-family: 'Montserrat', sans-serif;
    }
    section[data-testid="stSidebar"] {
        background-color: #262637;
    }
    section[data-testid="stSidebar"] * {
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

    st.title("Export Full Portfolio Report")

    # Extract the tickers from the DataFrame
    tickers = ticker_df["ticker"].dropna().unique().tolist()

    # === Function to Collect Stock Data ===
    @st.cache_data
    def collect_data(tickers):
        fundamentals = []  # List to store fundamental data
        technicals = []  # List to store technical data
        for t in tickers:
            try:
                stock = yf.Ticker(t)  # Fetch stock data from Yahoo Finance
                info = stock.info  # Retrieve stock info
                hist = stock.history(period="1y", auto_adjust=True)  # Fetch historical data for the last year

                # Calculate technical indicators
                hist["SMA_50"] = hist["Close"].rolling(50).mean()  # 50-day Simple Moving Average (SMA)
                hist["SMA_200"] = hist["Close"].rolling(200).mean()  # 200-day SMA
                hist["Volatility"] = hist["Close"].pct_change().rolling(30).std() * np.sqrt(252)  # 30-day rolling volatility, annualized
                hist["RSI"] = 100 - (100 / (1 + hist["Close"].pct_change().rolling(14).apply(
                    lambda x: (x[x > 0].sum() / abs(x[x < 0].sum())) if abs(x[x < 0].sum()) > 0 else 0)))  # 14-day Relative Strength Index (RSI)
                hist["Ticker"] = t
                hist.reset_index(inplace=True)
                # Make datetime columns timezone-naive
                for col in hist.select_dtypes(include=["datetime64[ns, UTC]"]).columns:
                    hist[col] = hist[col].dt.tz_localize(None)
                technicals.append(hist)

                # Append fundamental data
                fundamentals.append({
                    "Ticker": t,
                    "Sector": info.get("sector"),
                    "Industry": info.get("industry"),
                    "Exchange": info.get("exchange"),
                    "Market Cap": info.get("marketCap"),
                    "P/E": info.get("trailingPE"),
                    "Forward EPS": info.get("forwardEps"),
                    "Dividend Yield": info.get("dividendYield"),
                    "Beta": info.get("beta"),
                    "Price to Book": info.get("priceToBook"),
                    "52W High": info.get("fiftyTwoWeekHigh"),
                    "52W Low": info.get("fiftyTwoWeekLow")
                })
            except Exception:
                continue

        return pd.DataFrame(fundamentals), pd.concat(technicals, ignore_index=True)

    # Fetch the fundamental and technical data for the tickers
    fundamentals_df, technicals_df = collect_data(tickers)

    # Check if valid data is retrieved
    if fundamentals_df.empty or technicals_df.empty:
        st.warning("No valid financial data could be retrieved. Please check your ticker symbols.")
        return None, None

    # === Export to Excel ===
    excel_buffer = BytesIO()  # Create an in-memory buffer for Excel file
    with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
        fundamentals_df.to_excel(writer, index=False, sheet_name="Fundamentals")
        technicals_df.to_excel(writer, index=False, sheet_name="Technicals")
        ticker_df.to_excel(writer, index=False, sheet_name="Original Input")

    excel_buffer.seek(0)  # Reset buffer position to the start

    # === Export to PDF ===
    def generate_pdf(fundamentals):
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(200, 10, "Portfolio Summary Report", ln=True, align='C')
        pdf.ln(10)

        pdf.set_font("Arial", "B", 14)
        pdf.cell(200, 10, "Fundamentals Overview", ln=True)
        pdf.set_font("Arial", size=11)
        # Add each stock's fundamental data to the PDF
        for _, row in fundamentals.iterrows():
            line = f"{row['Ticker']} | Sector: {row['Sector']} | P/E: {row['P/E']} | Yield: {(row['Dividend Yield'] or 0) * 100:.2f}%"
            pdf.multi_cell(0, 8, line)
        pdf.ln(5)

        # Save the PDF in memory
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpfile:
            pdf.output(tmpfile.name)
            tmpfile.seek(0)
            pdf_bytes = tmpfile.read()

        return BytesIO(pdf_bytes)

    pdf_buffer = generate_pdf(fundamentals_df)

    # === ZIP All Files ===
    zip_buffer = BytesIO()  # Create an in-memory buffer for the ZIP file
    with zipfile.ZipFile(zip_buffer, "w") as zf:
        zf.writestr("portfolio_report.xlsx", excel_buffer.getvalue())  # Add the Excel file to the ZIP
        zf.writestr("portfolio_summary.pdf", pdf_buffer.getvalue())  # Add the PDF file to the ZIP
    zip_buffer.seek(0)  # Reset buffer position to the start

    # === Download the ZIP Package ===
    st.markdown("### Download Portfolio Package")
    st.download_button(
        label="Download ZIP (Excel + PDF)",
        data=zip_buffer,
        file_name="full_portfolio_export.zip",
        mime="application/zip"
    )
