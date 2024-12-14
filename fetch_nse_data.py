import yfinance as yf
import pandas as pd
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

# Function to fetch historical data
def fetch_historical_data(symbols, start_date, end_date):
    historical_data = {}
    for symbol in symbols:
        full_symbol = f"{symbol}.NS"
        print(f"Fetching historical data for {full_symbol}...")
        try:
            data = yf.download(full_symbol, start=start_date, end=end_date, progress=False)
            if not data.empty:
                historical_data[symbol] = data
            else:
                print(f"No data found for {symbol}")
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
    return historical_data

# Function to fetch live stock data
def fetch_live_data(symbols):
    live_data = []
    for symbol in symbols:
        full_symbol = f"{symbol}.NS"
        try:
            stock = yf.Ticker(full_symbol)
            current_price = stock.info.get("currentPrice", "N/A")
            previous_close = stock.info.get("previousClose", "N/A")
            live_data.append({
                "Stock": symbol,
                "Current Price": current_price,
                "Previous Close": previous_close
            })
        except Exception as e:
            print(f"Error fetching live data for {symbol}: {e}")
    return pd.DataFrame(live_data)

# Main function
if __name__ == "__main__":
    # User input for date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)  # Last 30 days

    print("\n--- Fetching Historical Data for NIFTY 50 Stocks ---")
    nifty_50_symbols = nifty_indices["NIFTY_50"]
    historical_data_nifty50 = fetch_historical_data(nifty_50_symbols, start_date, end_date)
    
    # Save historical data to CSV files
    for symbol, data in historical_data_nifty50.items():
        filename = f"{symbol}_historical_data.csv"
        data.to_csv(filename)
        print(f"Saved historical data for {symbol} to {filename}")
    
    print("\n--- Fetching Live Data for NIFTY 50 Stocks ---")
    live_data_nifty50 = fetch_live_data(nifty_50_symbols)
    print(live_data_nifty50)
    live_data_nifty50.to_csv("nifty50_live_data.csv", index=False)
    print("Live data saved to nifty50_live_data.csv")

    # Similarly, you can fetch for other indices
    print("\n--- Fetching Live Data for NIFTY BANK Stocks ---")
    nifty_bank_symbols = nifty_indices["NIFTY_BANK"]
    live_data_nifty_bank = fetch_live_data(nifty_bank_symbols)
    print(live_data_nifty_bank)
    live_data_nifty_bank.to_csv("niftybank_live_data.csv", index=False)
    print("Live data saved to niftybank_live_data.csv")
