"""
4. Home Page

"""

# Home Page:
import streamlit as st
from nextpage import nav_page

# -------------------- PAGE CONFIG --------------------
st.set_page_config(page_title="Stock Portfolio Builder", layout="wide")
# Configures the page layout to wide and sets the title for the Streamlit app.

# -------------------- STYLING --------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600&family=Roboto+Mono&display=swap');

/* General styling for app */
html, body, [class*="stApp"] {
    font-family: 'Montserrat', sans-serif !important;
    background-color: #0D1B2A !important;
    color: #F1F1F1 !important;
}

/* Styling for Sidebar */
section[data-testid="stSidebar"] {
    background-color: #132A3E !important;
    color: #F1F1F1 !important;
}

section[data-testid="stSidebar"] * {
    color: #F1F1F1 !important;
}

/* Input fields */
input, textarea, .stTextInput input, .stNumberInput input {
    background-color: #1B263B !important;
    color: #FFFFFF !important;
    border: 1px solid #00C9A7 !important;
    border-radius: 8px !important;
    font-family: 'Roboto Mono', monospace !important;
}

/* Buttons */
button[kind="primary"], .stButton button {
    background-color: #00C9A7 !important;
    color: #0D1B2A !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 16px !important;
}
button[kind="primary"]:hover, .stButton button:hover {
    background-color: #00B894 !important;
    color: #0D1B2A !important;
}

/* General text and labels */
h1, h2, h3, h4, h5, h6, p, label, span, div {
    color: #F1F1F1 !important;
}

/* Styling for success/warning messages */
[data-testid="stSuccess"], [data-testid="stWarning"] {
    background-color: #1B2A41 !important;
    color: #F1F1F1 !important;
    border-radius: 10px;
    padding: 15px;
    font-size: 16px;
    font-weight: 500;
}

/* Optional: scrollbar */
::-webkit-scrollbar {
    width: 8px;
}
::-webkit-scrollbar-thumb {
    background: #00C9A7;
    border-radius: 10px;
}

/* Lottie container (for animation, if used) */
.lottie-wrapper {
    display: flex;
    justify-content: center;
    margin-top: 2rem;
    margin-bottom: 2rem;
}
</style>
""", unsafe_allow_html=True)
# This section applies custom CSS for styling the page, including fonts, background colors, input fields, buttons, and message styles.

# -------------------- PAGE CONTENT --------------------
# The main content of the home page
st.title("Build Your Portfolio")
st.write("Input your stock holdings to analyze them on the dashboard.")
# Title and description for the page.

# Initialize session state to keep track of portfolio
if "portfolio" not in st.session_state:
    st.session_state.portfolio = []
# If no portfolio is saved in the session state, initialize an empty portfolio.

# Function to add a new stock to the portfolio
def add_stock():
    st.session_state.portfolio.append({"ticker": "", "quantity": 0.0})

# Card-style container for adding stocks
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown("### Add Stocks")
# Card-style UI for better layout

# Create input fields for each stock in the portfolio
for i, stock in enumerate(st.session_state.portfolio):
    col1, col2 = st.columns(2)
    stock["ticker"] = col1.text_input(
        f"Stock Ticker {i+1}", stock["ticker"], key=f"ticker_{i}"
    )
    stock["quantity"] = col2.number_input(
        f"Quantity", value=float(stock["quantity"]), min_value=0.0, step=1.0, key=f"quantity_{i}"
    )
st.markdown("</div>", unsafe_allow_html=True)
# Loop through the portfolio and create input fields for stock tickers and quantities.
# Each stock is represented by a `ticker` and `quantity`, and a unique key is used to identify the input elements.

# Add button to allow users to add another stock to the portfolio
if st.button("Add Another"):
    add_stock()

# Validation: Ensure that there is at least one valid stock in the portfolio before proceeding
valid_stocks = [s for s in st.session_state.portfolio if s["ticker"].strip() and s["quantity"] > 0]

if valid_stocks:
    st.success("Portfolio ready.")
    if st.button("Go to Dashboard"):
        nav_page("Dashboard")
else:
    st.warning("Add at least one valid stock with a positive quantity to proceed.")
# This section checks that each stock in the portfolio has a valid ticker and quantity before allowing users to proceed to the dashboard.

