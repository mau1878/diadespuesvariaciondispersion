import yfinance as yf
import pandas as pd
import plotly.express as px
import streamlit as st

# Function to fetch the closest previous and next trading day data
def fetch_closest_data(ticker, date):
    stock_data = yf.download(ticker, start=date, end=pd.to_datetime(date) + pd.DateOffset(days=7))
    if stock_data.empty:
        return None, None, None

    # Find the closest previous, given date, and next trading days
    dates = stock_data.index
    prev_day = dates[dates < date][-1]
    next_day = dates[dates > date][0]
    given_day = dates[dates == date][0] if date in dates else prev_day

    return stock_data.loc[prev_day], stock_data.loc[given_day], stock_data.loc[next_day]

# Calculate percentage variation
def calculate_variation(price_start, price_end):
    return ((price_end - price_start) / price_start) * 100

# Streamlit app interface
st.title('Scatter Plot of Price Variation')
ticker = st.text_input('Enter the Yfinance Ticker:')
date_input = st.date_input('Select a Date:', value=pd.to_datetime('2024-08-01'))

if ticker and date_input:
    prev_data, given_data, next_data = fetch_closest_data(ticker, pd.to_datetime(date_input))

    if prev_data is not None and given_data is not None and next_data is not None:
        prev_variation = calculate_variation(prev_data['Close'], given_data['Close'])
        next_variation = calculate_variation(given_data['Close'], next_data['Close'])

        # Create scatter plot
        scatter_data = pd.DataFrame({
            'X Axis (Next Day Variation)': [next_variation],
            'Y Axis (Previous Day Variation)': [prev_variation],
            'Ticker': [ticker]
        })

        fig = px.scatter(scatter_data, x='X Axis (Next Day Variation)', y='Y Axis (Previous Day Variation)',
                         text='Ticker', size_max=15)
        fig.update_traces(marker=dict(size=20, color='blue'), textposition='top center')
        fig.update_layout(title=f'Price Variation for {ticker} on {date_input}',
                          xaxis_title='Next Day Price Variation (%)',
                          yaxis_title='Previous Day Price Variation (%)')

        st.plotly_chart(fig)
    else:
        st.write('No data available for the selected date.')
