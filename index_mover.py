# import streamlit as st
# import pandas as pd
# import yfinance as yf
# import numpy as np
# import seaborn as sns
# import matplotlib.pyplot as plt

# # App title
# st.title("NSE Index Movers")

# # Sidebar for user inputs
# st.sidebar.header("Index Movers Settings")
# index_name = st.sidebar.selectbox("Select NSE Index", ["NIFTY_50", "NIFTY_BANK"])
# timeframe = st.sidebar.radio("Select Timeframe", ["Daily", "Weekly", "Monthly"])
# start_date = st.sidebar.date_input("Start Date", pd.Timestamp.now() - pd.Timedelta(days=90))
# end_date = st.sidebar.date_input("End Date", pd.Timestamp.now())

# # Index-wise stocks
# nse_indices = {
#     "NIFTY_50": [
#         "RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "HINDUNILVR", "KOTAKBANK", "SBIN",
#         "ITC", "BHARTIARTL", "WIPRO", "AXISBANK", "MARUTI", "LT", "SUNPHARMA", "TITAN",
#         "BAJFINANCE", "ONGC", "NTPC", "POWERGRID", "HCLTECH", "ULTRACEMCO", "ASIANPAINT",
#         "BAJAJFINSV", "COALINDIA", "M&M", "TECHM", "HDFCLIFE", "INDUSINDBK", "TATASTEEL",
#         "NESTLEIND", "JSWSTEEL", "DRREDDY", "ADANIPORTS", "GRASIM", "CIPLA", "BPCL", "DIVISLAB",
#         "SBILIFE", "BRITANNIA", "EICHERMOT", "UPL", "SHREECEM", "HEROMOTOCO", "TATAMOTORS",
#         "IOC", "BAJAJ-AUTO", "HINDALCO"
#     ],
#     "NIFTY_BANK": ["HDFCBANK", "ICICIBANK", "KOTAKBANK", "AXISBANK", "SBIN", "INDUSINDBK", "BANDHANBNK"]
# }

# def fetch_stock_data(ticker, start, end):
#     """Fetch historical stock data from Yahoo Finance."""
#     try:
#         data = yf.download(f"{ticker}.NS", start=start, end=end, progress=False)
#         return data
#     except Exception as e:
#         st.warning(f"Could not fetch data for {ticker}: {e}")
#         return pd.DataFrame()

# def fetch_live_data(symbols):
#     """Fetch live stock data for a list of symbols."""
#     live_data = []
#     for symbol in symbols:
#         full_symbol = f"{symbol}.NS"
#         try:
#             stock = yf.Ticker(full_symbol)
#             current_price = stock.info.get("currentPrice", None)
#             if current_price is None:
#                 current_price = stock.history(period="1d")["Close"].iloc[-1]
#             previous_close = stock.info.get("previousClose", None)
#             live_data.append({
#                 "Stock": symbol,
#                 "Current Price": current_price,
#                 "Previous Close": previous_close
#             })
#         except Exception as e:
#             st.warning(f"Could not fetch live data for {symbol}: {e}")
#     return pd.DataFrame(live_data)

# def calculate_changes(data, timeframe, live_price, previous_close):
#     """Calculate percentage changes based on current price."""
#     if data.empty or len(data) <= 1 or live_price is None or previous_close is None:
#         return None, None

#     current_price = live_price

#     if timeframe == "Daily":
#         reference_price = previous_close
#         reference_volume = data["Volume"].iloc[-1]
#     elif timeframe == "Weekly":
#         if len(data) < 5:
#             return None, None
#         reference_price = data["Close"].iloc[-5:].mean()
#         reference_volume = data["Volume"].iloc[-5:].mean()
#     else:  # Monthly
#         if len(data) < 21:
#             return None, None
#         reference_price = data["Close"].iloc[-21:].mean()
#         reference_volume = data["Volume"].iloc[-21:].mean()

#     price_change_pct = ((current_price - reference_price) / reference_price) * 100
#     volume_change_pct = (
#         ((data["Volume"].iloc[-1] - reference_volume) / data["Volume"].iloc[-1]) * 100
#         if data["Volume"].iloc[-1] != 0
#         else 0
#     )
#     return price_change_pct, volume_change_pct

# def create_heatmap(data, title, cmap="RdYlGn"):
#     """Generate a 2D heatmap with stock names and values."""
#     n_rows, n_cols = 6, 9  # Adjust grid dimensions as needed
#     heatmap_data = np.full((n_rows, n_cols), np.nan)
#     heatmap_labels = np.full((n_rows, n_cols), "", dtype=object)
    
#     for i, row in enumerate(data):
#         row_index, col_index = divmod(i, n_cols)
#         if row_index < n_rows:
#             heatmap_data[row_index, col_index] = row["Value"]
#             heatmap_labels[row_index, col_index] = f"{row['Stock']}\n{row['Value']:.2f}%"

#     fig, ax = plt.subplots(figsize=(12, 8))
#     sns.heatmap(
#         heatmap_data,
#         annot=heatmap_labels,
#         fmt="",
#         cmap=cmap,
#         cbar=True,
#         linewidths=0.5,
#         linecolor="gray",
#         ax=ax,
#         annot_kws={"size": 8, "weight": "bold"}
#     )
#     plt.title(title, fontsize=16)
#     st.pyplot(fig)

# # Fetch and process data
# if st.sidebar.button("Analyze"):
#     stocks = nse_indices.get(index_name, [])
#     results = {"Price": [], "Volume": []}
    
#     live_data = fetch_live_data(stocks)
    
#     for stock in stocks:
#         data = fetch_stock_data(stock, start_date, end_date)
#         live_price_row = live_data[live_data["Stock"] == stock]
#         if not live_price_row.empty:
#             live_price = live_price_row["Current Price"].values[0]
#             previous_close = live_price_row["Previous Close"].values[0]
#         else:
#             live_price, previous_close = None, None

#         if not data.empty and len(data) > 1 and live_price is not None and previous_close is not None:
#             price_change, volume_change = calculate_changes(data, timeframe, live_price, previous_close)
#             if price_change is not None:
#                 results["Price"].append({"Stock": stock, "Value": price_change})
#             if volume_change is not None:
#                 results["Volume"].append({"Stock": stock, "Value": volume_change})

#     # Sort results in descending order
#     for key in results:
#         results[key].sort(key=lambda x: x["Value"], reverse=True)

#     # Create heatmaps
#     st.subheader(f"{timeframe} Price Change Heatmap")
#     create_heatmap(results["Price"], f"{timeframe} Price Change Heatmap")

#     st.subheader(f"{timeframe} Volume Change Heatmap")
#     create_heatmap(results["Volume"], f"{timeframe} Volume Change Heatmap")

# # Footer
# st.sidebar.info("Built with Streamlit and Yahoo Finance API")


import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import appdirs as ad
import os
os.system("streamlit run index_mover.py --server.port $PORT")

# Override appdirs cache directory for Streamlit Cloud
ad.user_cache_dir = lambda *args: "/tmp"

# App title
st.title("NSE Index Movers")

# Sidebar for user inputs
st.sidebar.header("Index Movers Settings")
index_name = st.sidebar.selectbox("Select NSE Index", ["NIFTY_50", "NIFTY_BANK"])
timeframe = st.sidebar.radio("Select Timeframe", ["Daily", "Weekly", "Monthly"])
start_date = st.sidebar.date_input("Start Date", pd.Timestamp.now() - pd.Timedelta(days=90))
end_date = st.sidebar.date_input("End Date", pd.Timestamp.now())

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

def fetch_live_data(symbols):
    """Fetch live stock data for a list of symbols."""
    live_data = []
    for symbol in symbols:
        full_symbol = f"{symbol}.NS"
        try:
            stock = yf.Ticker(full_symbol)
            current_price = stock.info.get("currentPrice", None)
            if current_price is None:
                current_price = stock.history(period="1d")["Close"].iloc[-1]
            previous_close = stock.info.get("previousClose", None)
            live_volume = stock.info.get("volume", None)  # Fetch live volume
            
            # Fallback if live volume data is unavailable
            if live_volume is None:
                live_volume = stock.history(period="1d")["Volume"].iloc[-1]
            
            live_data.append({
                "Stock": symbol,
                "Current Price": current_price,
                "Previous Close": previous_close,
                "Live Volume": live_volume  # Include live volume
            })
        except Exception as e:
            st.warning(f"Could not fetch live data for {symbol}: {e}")
    return pd.DataFrame(live_data)  # Ensure DataFrame format

def calculate_changes(data, timeframe, live_price, previous_close, live_volume=None):
    """Calculate percentage changes based on current price and volume."""
    if data.empty or len(data) <= 1 or live_price is None or previous_close is None:
        return None, None

    current_price = live_price

    if timeframe == "Daily":
        reference_price = previous_close
        reference_volume = live_volume  # Use live volume for daily timeframe
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

    price_change_pct = ((current_price - reference_price) / reference_price) * 100
    volume_change_pct = (
        ((reference_volume-data["Volume"].iloc[-1]) / data["Volume"].iloc[-1]) * 100
        if data["Volume"].iloc[-1] != 0
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
    
    live_data = fetch_live_data(stocks)
    st.write(live_data)  # Debugging: Display live data for verification
    
    for stock in stocks:
        data = fetch_stock_data(stock, start_date, end_date)
        live_price_row = live_data[live_data["Stock"] == stock]
        if live_price_row.empty:
            st.warning(f"No live data available for {stock}")
            continue

        live_price = live_price_row["Current Price"].values[0]
        previous_close = live_price_row["Previous Close"].values[0]
        live_volume = live_price_row["Live Volume"].values[0]

        if not data.empty and len(data) > 1 and live_price is not None and previous_close is not None:
            price_change, volume_change = calculate_changes(data, timeframe, live_price, previous_close, live_volume)
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
