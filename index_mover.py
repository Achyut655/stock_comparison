import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# App title
st.title("NSE Index Movers")

# Sidebar for user inputs
st.sidebar.header("Index Movers Settings")
index_name = st.sidebar.selectbox("Select NSE Index", ["NIFTY_50", "NIFTY_BANK"])
timeframe = st.sidebar.radio("Select Timeframe", ["Daily", "Weekly", "Monthly"])
end_date = st.sidebar.date_input("End Date", pd.Timestamp.now())

if timeframe == "Daily":
    start_date = end_date - pd.Timedelta(days=1)
elif timeframe == "Weekly":
    start_date = end_date - pd.Timedelta(days=7)
else:  # Monthly
    start_date = end_date - pd.Timedelta(days=30)

start_date = st.sidebar.date_input("Start Date", start_date)




# Index-wise stocks
nse_indices = {
    "NIFTY_50": [
        "RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "HINDUNILVR", "KOTAKBANK", "SBIN",
        "ITC", "BHARTIARTL", "WIPRO", "AXISBANK", "MARUTI", "LT", "SUNPHARMA", "TITAN",
        "BAJFINANCE", "ONGC", "NTPC", "POWERGRID", "HCLTECH", "ULTRACEMCO", "ASIANPAINT",
        "BAJAJFINSV", "COALINDIA", "M&M", "TECHM", "HDFCLIFE", "INDUSINDBK", "TATASTEEL",
        "NESTLEIND", "JSWSTEEL", "DRREDDY", "ADANIPORTS", "GRASIM", "CIPLA", "BPCL", "DIVISLAB",
        "SBILIFE", "BRITANNIA", "EICHERMOT", "UPL", "SHREECEM", "HEROMOTOCO", "TATAMOTORS",
        "IOC", "BAJAJ-AUTO", "HINDALCO"
    ],
    "NIFTY_BANK": ["HDFCBANK", "ICICIBANK", "KOTAKBANK", "AXISBANK", "SBIN", "INDUSINDBK", "BANDHANBNK"]
}

def fetch_stock_data(ticker, start, end):
    """Fetch historical stock data from Yahoo Finance."""
    try:
        data = yf.download(f"{ticker}.NS", start=start, end=end, progress=False)
        return data
    except Exception as e:
        st.warning(f"Could not fetch data for {ticker}: {e}")
        return pd.DataFrame()

def calculate_changes(data, timeframe):
    """Calculate percentage changes based on historical data."""
    if data.empty or len(data) <= 1:
        return None, None

    if timeframe == "Daily":
        reference_price = data["Close"].iloc[-2]
        reference_volume = data["Volume"].iloc[-2]
    elif timeframe == "Weekly":
        if len(data) < 5:
            return None, None
        reference_price = data["Close"].iloc[-5:].mean()
        reference_volume = data["Volume"].iloc[-5:].mean()
    else:  # Monthly
        if len(data) < 21:
            return None, None
        reference_price = data["Close"].iloc[-21:].mean()
        reference_volume = data["Volume"].iloc[-21:].mean()

    current_price = data["Close"].iloc[-1]
    current_volume = data["Volume"].iloc[-1]

    price_change_pct = ((current_price - reference_price) / reference_price) * 100
    volume_change_pct = (
        ((current_volume - reference_volume) / reference_volume) * 100
        if reference_volume != 0
        else 0
    )
    return price_change_pct, volume_change_pct

def create_heatmap(data, title, cmap="RdYlGn"):
    """Generate a 2D heatmap with stock names and values."""
    n_rows, n_cols = 6, 9  # Adjust grid dimensions as needed
    heatmap_data = np.full((n_rows, n_cols), np.nan)
    heatmap_labels = np.full((n_rows, n_cols), "", dtype=object)

    for i, row in enumerate(data):
        row_index, col_index = divmod(i, n_cols)
        if row_index < n_rows:
            heatmap_data[row_index, col_index] = row["Value"]
            heatmap_labels[row_index, col_index] = f"{row['Stock']}\n{row['Value']:.2f}%"

    fig, ax = plt.subplots(figsize=(12, 8))
    sns.heatmap(
        heatmap_data,
        annot=heatmap_labels,
        fmt="",
        cmap=cmap,
        cbar=True,
        linewidths=0.5,
        linecolor="gray",
        ax=ax,
        annot_kws={"size": 8, "weight": "bold"}
    )
    plt.title(title, fontsize=16)
    st.pyplot(fig)

# Fetch and process data
if st.sidebar.button("Analyze"):
    stocks = nse_indices.get(index_name, [])
    results = {"Price": [], "Volume": []}

    for stock in stocks:
        data = fetch_stock_data(stock, start_date, end_date)
        if not data.empty:
            price_change, volume_change = calculate_changes(data, timeframe)
            if price_change is not None:
                results["Price"].append({"Stock": stock, "Value": price_change})
            if volume_change is not None:
                results["Volume"].append({"Stock": stock, "Value": volume_change})

    # Sort results in descending order
    for key in results:
        results[key].sort(key=lambda x: x["Value"], reverse=True)

    # Create heatmaps
    st.subheader(f"{timeframe} Price Change Heatmap")
    create_heatmap(results["Price"], f"{timeframe} Price Change Heatmap")

    st.subheader(f"{timeframe} Volume Change Heatmap")
    create_heatmap(results["Volume"], f"{timeframe} Volume Change Heatmap")
