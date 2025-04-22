"""
5. GetInfoOnStockFunction

"""
import logging
import yfinance as yf
from typing import Optional, Dict, Any
import pandas as pd
import streamlit as st

def get_info_on_stock(ticker: str) -> Dict[str, Any]:
    """
    Fetch stock information for a given ticker using yfinance.

    Args:
        ticker (str): The stock ticker symbol.

    Returns:
        dict: A dictionary containing stock information.
    """
    try:
        # Initialize the yfinance Ticker object for the given ticker symbol
        stock = yf.Ticker(ticker)
        
        # Fetch the stock information
        stock_info = stock.info
        
        # Return the stock info
        return stock_info
    except Exception as e:
        # If an error occurs during data fetching, display the error message in Streamlit
        st.error(f"Error fetching data for {ticker}: {e}")
        # Return an empty dictionary in case of error
        return {}

# Configure logging
logging.basicConfig(filename='stock_data.log', level=logging.INFO, format='%(asctime)s - %(message)s')

"""
6. GetStockRegionFunction

"""
import yfinance as yf
from typing import Dict

def get_stock_region(ticker: str) -> str:
    """
    Fetch the region of a stock based on its exchange.
    
    Args:
        ticker (str): The stock ticker symbol.
        
    Returns:
        str: The region (e.g., "American Stock", "European Stock", "Asian Stock", "Other/Unknown Region").
    """
    try:
        # Fetch stock info using yfinance
        stock = yf.Ticker(ticker)
        info = stock.info
        exchange = info.get("exchange", "").lower()

        # Region mapping based on exchange abbreviations
        region_map = {
            "American Stock": [
                "nasdaq", "nyse", "amex", "arca", "pcx", "nms", "nyq", "snp", "cboe", "bats", "tsx", "tsxv", "cse", "ne"
            ],
            "European Stock": [
                "lse", "euronext", "xetra", "bme", "six", "fra", "ams", "par", "mil", "lis", "vse", "omx", "wse", "prague",
                "athens", "budapest", "bvx", "micex", "moex", "hel", "sto", "oslo", "dublin", "bolsa-madrid","ger","ebs"
            ],
            "Asian Stock": [
                "tse", "sse", "hkex", "kospi", "kosdaq", "nse", "bse", "szse", "taiex", "jpxt", "hsi", "idx", "pse",
                "bursa-malaysia", "set", "hkg", "jpx", "tky", "sto", "shanghai", "shenzhen", "taipei", "karachi", "dhaka","ksc","nsi"
            ],
            "Other/Unknown Region": [
                "asx", "nzx", "jse", "bvc", "bmv", "b3", "bovespa", "safex", "adx", "dfm", "tadawul", "qse", "egx", "casablanca",
                "nairobi", "lagos", "muscat", "doha", "kuwait", "manama", "colombia", "peru", "chile", "argentina"
            ]
        }

        # Match the exchange with the appropriate region
        for region, exchanges in region_map.items():
            if any(ex in exchange for ex in exchanges):
                return region

        # If no match found, return Unknown region with exchange info
        return f"Other/Unknown Region (Exchange: {exchange})"

    except Exception as e:
        return f"Error fetching data for {ticker}: {e}"


def stock_region_diversification(tickers_with_quantity: Dict[str, int]) -> Dict[str, float]:
    """
    Calculates the portfolio diversification by region based on the stock tickers and quantities.
    
    Args:
        tickers_with_quantity (Dict[str, int]): A dictionary where keys are stock tickers and values are quantities.
        
    Returns:
        Dict[str, float]: A dictionary with regions as keys and the percentage of the total portfolio investment in each region.
    """
    try:
        # Check if the input dictionary is empty
        if not tickers_with_quantity:
            raise ValueError("Input tickers_with_quantity is empty.")

        # Initialize the region totals and total investment
        region_totals = {}
        total_investment = 0

        # Loop through each stock in the portfolio
        for ticker, quantity in tickers_with_quantity.items():
            stock = yf.Ticker(ticker)
            current_price = stock.info.get("regularMarketPrice", 0)
            
            # Skip the stock if the price is zero or invalid
            if current_price <= 0:
                continue

            # Calculate the investment in this stock
            investment = current_price * quantity
            total_investment += investment

            # Get the region for the stock
            region = get_stock_region(ticker)
            
            # Add investment to the corresponding region
            if region not in region_totals:
                region_totals[region] = 0
            region_totals[region] += investment

        # If no valid investments, return an error message
        if total_investment == 0:
            return {"Error": "Total investment is zero. Cannot calculate diversification."}

        # Calculate the percentage of total investment for each region
        region_percentages = {
            region: (amount / total_investment) * 100
            for region, amount in region_totals.items()
        }

        return region_percentages

    except Exception as e:
        return {"Error": f"Error calculating diversification: {e}"}

"""
7. NextPageFunction

"""
def nav_page(page_name):
    """
    Navigate to a different page in the Streamlit app.

    Args:
        page_name (str): The name of the page to navigate to. This should match the expected query parameter value.

    Raises:
        ValueError: If the page_name is invalid (e.g., empty or not a string).
    """
    if not page_name or not isinstance(page_name, str):
        raise ValueError("Invalid page name. It must be a non-empty string.")
    
    # Set the query parameter to navigate to the desired page
    st.experimental_set_query_params(page=page_name)



