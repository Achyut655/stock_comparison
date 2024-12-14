import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
from datetime import datetime, timedelta

# Nifty index stock symbols
nifty_indices = {
    "NIFTY_50": [
        "RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "HINDUNILVR", "KOTAKBANK", "SBIN",
        "ITC", "BHARTIARTL", "WIPRO", "AXISBANK", "MARUTI", "LT", "SUNPHARMA", "TITAN",
        "BAJFINANCE", "ONGC", "NTPC", "POWERGRID", "HCLTECH", "ULTRACEMCO", "ASIANPAINT",
        "BAJAJFINSV", "COALINDIA", "M&M", "TECHM", "HDFC", "INDUSINDBK", "TATASTEEL",
        "NESTLEIND", "JSWSTEEL", "DRREDDY", "ADANIPORTS", "GRASIM", "CIPLA", "BPCL", "DIVISLAB",
        "SBILIFE", "BRITANNIA", "EICHERMOT", "UPL", "SHREECEM", "HEROMOTOCO", "TATAMOTORS",
        "IOC", "BAJAJ-AUTO", "HINDALCO"
    ],
    "NIFTY_BANK": ["HDFCBANK", "ICICIBANK", "KOTAKBANK", "AXISBANK", "SBIN", "INDUSINDBK", "BANDHANBNK"]
}

# App title
st.title("NSE Stock Analysis: Current vs Weekly/Monthly Averages")

# Sidebar for user inputs
st.sidebar.header("Stock Input Parameters")

# User inputs
selected_index = st.sidebar.selectbox("Select NSE Index:", list(nifty_indices.keys()))
start_date = st.sidebar.date_input("Start Date", datetime.now() - timedelta(days=30))
end_date = st.sidebar.date_input("End Date", datetime.now())

# Validate date inputs
if start_date >= end_date:
    st.sidebar.error("End Date must be greater than Start Date")

# Function to fetch historical data
def fetch_historical_data(symbol, start_date, end_date):
    try:
        full_symbol = f"{symbol}.NS"
        data = yf.download(full_symbol, start=start_date, end=end_date, progress=False)
        return data
    except Exception as e:
        st.error(f"Error fetching historical data for {symbol}: {e}")
        return pd.DataFrame()

# Function to fetch live data
def fetch_live_data(symbol):
    try:
        stock = yf.Ticker(f"{symbol}.NS")
        current_price = stock.info.get("currentPrice", None)
        volume = stock.info.get("volume", None)
        return current_price, volume
    except Exception as e:
        st.error(f"Error fetching live data for {symbol}: {e}")
        return None, None

# Function to calculate percentage change
def calculate_percentage_change(current, average):
    if average is None or average == 0:
        return None
    return ((current - average) / average) * 100

# Main analysis logic
if st.sidebar.button("Run Analysis"):
    st.subheader(f"Analysis for {selected_index}")

    # Initialize results list
    results = []

    # Get symbols for the selected index
    stock_symbols = nifty_indices[selected_index]

    # Fetch data for each stock
    for symbol in stock_symbols:
        st.text(f"Processing {symbol}...")
        
        # Fetch historical data
        data = fetch_historical_data(symbol, start_date, end_date)
        if data.empty:
            continue

        # Calculate weekly and monthly averages
        data['Weekly_Avg_Price'] = data['Close'].rolling(window=5).mean()
        data['Monthly_Avg_Price'] = data['Close'].rolling(window=20).mean()
        data['Weekly_Avg_Volume'] = data['Volume'].rolling(window=5).mean()
        data['Monthly_Avg_Volume'] = data['Volume'].rolling(window=20).mean()

        # Get the latest weekly and monthly averages
        weekly_avg_price = data['Weekly_Avg_Price'].iloc[-1]
        monthly_avg_price = data['Monthly_Avg_Price'].iloc[-1]
        weekly_avg_volume = data['Weekly_Avg_Volume'].iloc[-1]
        monthly_avg_volume = data['Monthly_Avg_Volume'].iloc[-1]

        # Fetch live data
        current_price, current_volume = fetch_live_data(symbol)
        if current_price is None or current_volume is None:
            continue

        # Calculate percentage changes
        price_change_weekly = calculate_percentage_change(current_price, weekly_avg_price)
        price_change_monthly = calculate_percentage_change(current_price, monthly_avg_price)
        volume_change_weekly = calculate_percentage_change(current_volume, weekly_avg_volume)
        volume_change_monthly = calculate_percentage_change(current_volume, monthly_avg_volume)

        # Append results
        results.append({
            "Stock": symbol,
            "Current Price": current_price,
            "Weekly Avg Price": weekly_avg_price,
            "Monthly Avg Price": monthly_avg_price,
            "Price Change (Weekly %)": price_change_weekly,
            "Price Change (Monthly %)": price_change_monthly,
            "Current Volume": current_volume,
            "Weekly Avg Volume": weekly_avg_volume,
            "Monthly Avg Volume": monthly_avg_volume,
            "Volume Change (Weekly %)": volume_change_weekly,
            "Volume Change (Monthly %)": volume_change_monthly
        })

    # Convert results to DataFrame
    results_df = pd.DataFrame(results)

    if not results_df.empty:
        # Sort stocks by largest price change (weekly)
        results_df = results_df.sort_values(by="Price Change (Weekly %)", ascending=False)

        # Display results
        st.subheader("Results: Sorted by Price Change (Weekly %)")
        st.dataframe(results_df)

        # Plot the top 10 stocks with the highest price change
        st.subheader("Top 10 Stocks by Price Change (Weekly %)")
        top_10 = results_df.head(10)
        plt.figure(figsize=(10, 6))
        plt.bar(top_10['Stock'], top_10['Price Change (Weekly %)'], color='skyblue')
        plt.xlabel("Stock")
        plt.ylabel("Price Change (Weekly %)")
        plt.title("Top 10 Stocks by Weekly Price Change")
        st.pyplot(plt)

    else:
        st.error("No data available for the selected index and date range.")

# Footer
st.sidebar.info("Built with Streamlit and yfinance")
