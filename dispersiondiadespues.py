import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import time

# Function to fetch stock data with retry logic
def fetch_stock_data(ticker, start_date, end_date, retries=3, delay=5):
    for attempt in range(retries):
        try:
            data = yf.download(ticker, start=start_date, end=end_date)
            
            if data.empty:
                st.error(f"No data found for ticker {ticker} within the specified date range.")
                return None
            
            # Handle missing dates by forward-filling
            data.ffill(inplace=True)
            return data
        
        except Exception as e:
            if attempt < retries - 1:
                st.warning(f"Attempt {attempt + 1} failed for ticker {ticker}: {e}. Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                st.error(f"An error occurred while fetching data for ticker {ticker}: {e}")
                return None

# Function to calculate percentage variations
def calculate_percentage_variations(data):
    data['Previous_Close'] = data['Adj Close'].shift(1)
    data['Y_axis'] = (data['Adj Close'] - data['Previous_Close']) / data['Previous_Close'] * 100
    return data[['Y_axis']]

# Streamlit interface
st.title("Scatter Plot of Stock Price Variations with Regression Line")

# Sidebar for user inputs
st.sidebar.header("User Input")
ticker1 = st.sidebar.text_input("Enter First YFinance Ticker:", "AAPL").upper()
ticker2 = st.sidebar.text_input("Enter Second YFinance Ticker:", "MSFT").upper()
start_date = st.sidebar.date_input("Start Date:", pd.to_datetime("2020-01-01"))
end_date = st.sidebar.date_input("End Date:", pd.to_datetime("today"))

# Fetch data and display plot when button is clicked
if st.sidebar.button("Generate Scatter Plot"):
    # Fetch data for both tickers
    data1 = fetch_stock_data(ticker1, start_date, end_date)
    data2 = fetch_stock_data(ticker2, start_date, end_date)
    
    if data1 is not None and data2 is not None:
        # Calculate price variations
        data1 = calculate_percentage_variations(data1)
        data2 = calculate_percentage_variations(data2)
        
        # Merge data on date index
        combined_data = pd.merge(data1, data2, left_index=True, right_index=True, suffixes=('_ticker1', '_ticker2'))
        combined_data.dropna(inplace=True)
        
        if combined_data.empty:
            st.error("No overlapping data found for the specified date range and tickers.")
        else:
            # Add a column for the year
            combined_data['Year'] = combined_data.index.year
            
            # User input for years to display
            years = sorted(combined_data['Year'].unique())
            selected_years = st.sidebar.multiselect("Select Years to Display:", options=years, default=years)
            
            # Filter data based on selected years
            filtered_data = combined_data[combined_data['Year'].isin(selected_years)]
            
            if filtered_data.empty:
                st.error("No data available for the selected years.")
            else:
                # Plotting the scatter plot with trend line
                fig = px.scatter(filtered_data, x='Y_axis_ticker1', y='Y_axis_ticker2', 
                                 color='Year',  # Color by year
                                 trendline="ols",  # Adding the trendline
                                 title=f"Scatter Plot for {ticker1} vs {ticker2} with Trend Line",
                                 labels={'Y_axis_ticker1': f'{ticker1} Price Variation (%)', 
                                         'Y_axis_ticker2': f'{ticker2} Price Variation (%)'},
                                 template="plotly_white",
                                 color_continuous_scale=px.colors.sequential.Viridis)  # Color scale
                
                fig.update_traces(marker=dict(size=10, line=dict(width=2, color='DarkSlateGrey')))
                fig.update_layout(showlegend=True, height=600)
                fig.add_hline(y=0, line_dash="dash", line_color="red")
                fig.add_vline(x=0, line_dash="dash", line_color="red")
                
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Please enter valid tickers and date range.")
