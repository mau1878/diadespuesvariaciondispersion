import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import datetime

# Function to fetch stock data
def fetch_stock_data(ticker, start_date, end_date):
    stock = yf.download(ticker, start=start_date, end=end_date)
    
    # If no data is available for the given date, take the previous available value
    stock = stock.asfreq('B', method='pad')
    return stock

# Function to calculate price variations
def calculate_variations(stock_data):
    stock_data['Previous_Close'] = stock_data['Adj Close'].shift(1)
    stock_data['Next_Close'] = stock_data['Adj Close'].shift(-1)

    # Calculate the percentage variations
    stock_data['Price_Var_Y'] = (stock_data['Adj Close'] - stock_data['Previous_Close']) / stock_data['Previous_Close'] * 100
    stock_data['Price_Var_X'] = (stock_data['Next_Close'] - stock_data['Adj Close']) / stock_data['Adj Close'] * 100

    # Drop rows where percentage change cannot be computed (e.g., at the start or end)
    stock_data.dropna(subset=['Price_Var_Y', 'Price_Var_X'], inplace=True)

    return stock_data

# Function to plot the data
def plot_scatter(stock_data, ticker):
    fig = px.scatter(stock_data, x='Price_Var_X', y='Price_Var_Y',
                     labels={
                         'Price_Var_X': 'Next Day Price Variation (%)',
                         'Price_Var_Y': 'Previous Day Price Variation (%)'
                     },
                     title=f'Scatter Plot of {ticker} Price Variations',
                     template='plotly_dark')
    fig.update_traces(marker=dict(size=10, color='LightSkyBlue', line=dict(width=1, color='DarkSlateGrey')))
    fig.show()

# Main script
if __name__ == "__main__":
    ticker = input("Enter the Yfinance ticker symbol: ").upper()
    start_date = input("Enter the start date (YYYY-MM-DD): ")
    end_date = input(f"Enter the end date (YYYY-MM-DD, default is today): ") or datetime.today().strftime('%Y-%m-%d')

    # Fetch the data
    stock_data = fetch_stock_data(ticker, start_date, end_date)
    
    # Calculate the price variations
    stock_data = calculate_variations(stock_data)
    
    # Plot the data
    plot_scatter(stock_data, ticker)
