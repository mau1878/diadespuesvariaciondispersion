import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

# Function to fetch stock data
@st.cache_data(show_spinner=False)
def fetch_stock_data(ticker, start_date, end_date, interval):
    data = yf.download(ticker, start=start_date, end=end_date, interval=interval)
    data.ffill(inplace=True)  # Fill missing dates
    return data

# Function to calculate percentage variations
def calculate_percentage_variations(data):
    data['Previous_Close'] = data['Adj Close'].shift(1)
    data['Variation'] = (data['Adj Close'] - data['Previous_Close']) / data['Previous_Close'] * 100
    return data[['Variation']]

# Streamlit interface
st.title("Scatter Plot of Stock Price Variations")

# Sidebar for user inputs
st.sidebar.header("User Input")
ticker1 = st.sidebar.text_input("Enter First Ticker:", "AAPL").upper()
ticker2 = st.sidebar.text_input("Enter Second Ticker:", "MSFT").upper()

# Date selection
start_date = st.sidebar.date_input("Start Date:", pd.to_datetime("2000-01-01"), min_value=pd.to_datetime("1980-01-01"))
end_date = st.sidebar.date_input("End Date:", pd.to_datetime("today"), min_value=pd.to_datetime("1980-01-01"))

# Frequency selection
interval = st.sidebar.radio("Select Data Frequency:", ['1d', '1wk', '1mo'], index=0)

# Button to generate the scatter plot
if st.sidebar.button("Generate Scatter Plot"):
    # Fetch data for both tickers
    data1 = fetch_stock_data(ticker1, start_date, end_date, interval)
    data2 = fetch_stock_data(ticker2, start_date, end_date, interval)

    if not data1.empty and not data2.empty:
        # Calculate percentage variations
        data1 = calculate_percentage_variations(data1)
        data2 = calculate_percentage_variations(data2)

        # Merge data on date index
        combined_data = pd.merge(data1, data2, left_index=True, right_index=True, suffixes=('_1', '_2'))
        combined_data.dropna(inplace=True)

        if not combined_data.empty:
            # Add year column for filtering
            combined_data['Year'] = combined_data.index.year

            # Select Years
            years = combined_data['Year'].unique().tolist()
            selected_years = st.sidebar.multiselect("Select Years to Display:", years, default=years)

            # Filter based on selected years
            filtered_data = combined_data[combined_data['Year'].isin(selected_years)]

            if not filtered_data.empty:
                # Create the scatter plot
                fig = px.scatter(filtered_data, 
                                 x='Variation_1', 
                                 y='Variation_2', 
                                 color='Year',
                                 title=f"Price Variation Scatter Plot for {ticker1} and {ticker2}",
                                 labels={f'Variation_1': f'{ticker1} Variation (%)', 
                                         f'Variation_2': f'{ticker2} Variation (%)'},
                                 trendline="ols",
                                 template="plotly_white")
                fig.update_layout(showlegend=True)
                fig.update_traces(marker=dict(size=10, line=dict(width=2, color='DarkSlateGrey')))
                fig.add_hline(y=0, line_dash="dash", line_color="red")
                fig.add_vline(x=0, line_dash="dash", line_color="red")
                
                # Display the plot
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.error("No data available for the selected years.")
        else:
            st.error("No overlapping data found for the specified date range and tickers.")
    else:
        st.error("Could not retrieve data for the tickers or date range provided.")
