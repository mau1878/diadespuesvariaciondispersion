import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

# Function to fetch stock data
def fetch_stock_data(ticker, start_date, end_date):
    data = yf.download(ticker, start=start_date, end=end_date)
    
    if data.empty:
        st.error("No data found for the specified ticker and date range.")
        return None
    
    # Handle missing dates by forward-filling
    data.ffill(inplace=True)
    return data

# Function to calculate percentage variations
def calculate_percentage_variations(data):
    data['Previous_Close'] = data['Adj Close'].shift(1)
    data['Next_Close'] = data['Adj Close'].shift(-1)
    data['Y_axis'] = (data['Adj Close'] - data['Previous_Close']) / data['Previous_Close'] * 100
    data['X_axis'] = (data['Next_Close'] - data['Adj Close']) / data['Adj Close'] * 100
    
    # Drop rows with missing values in X or Y axis
    data.dropna(subset=['X_axis', 'Y_axis'], inplace=True)
    return data

# Streamlit interface
st.title("Scatter Plot of Stock Price Variations")

# User inputs
ticker = st.text_input("Enter YFinance Ticker:", "AAPL").upper()
start_date = st.date_input("Start Date:", pd.to_datetime("2020-01-01"))
end_date = st.date_input("End Date:", pd.to_datetime("today"))

if st.button("Generate Scatter Plot"):
    data = fetch_stock_data(ticker, start_date, end_date)
    
    if data is not None:
        # Calculate price variations
        data = calculate_percentage_variations(data)
        
        # Plotting the scatter plot
        fig = px.scatter(data, x='X_axis', y='Y_axis', 
                         title=f"Scatter Plot for {ticker}",
                         labels={'X_axis': 'Price Variation After (%)', 
                                 'Y_axis': 'Price Variation Before (%)'},
                         template="plotly_white")
        
        fig.update_traces(marker=dict(size=10, color='blue', line=dict(width=2, color='DarkSlateGrey')))
        fig.update_layout(showlegend=False, height=600)
        fig.add_hline(y=0, line_dash="dash", line_color="red")
        fig.add_vline(x=0, line_dash="dash", line_color="red")
        
        st.plotly_chart(fig)
