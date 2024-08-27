import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

# Función para obtener datos de las acciones
@st.cache_data(show_spinner=False)
def fetch_stock_data(ticker, start_date, end_date, interval):
    data = yf.download(ticker, start=start_date, end=end_date, interval=interval)
    data.ffill(inplace=True)  # Rellenar fechas faltantes
    return data

# Función para calcular variaciones porcentuales
def calculate_percentage_variations(data):
    data['Cierre_Previo'] = data['Adj Close'].shift(1)
    data['Variación'] = (data['Adj Close'] - data['Cierre_Previo']) / data['Cierre_Previo'] * 100
    return data[['Variación']]

# Interfaz de Streamlit
st.title("Gráfico de Dispersión de Variaciones de Precios")

# Barra lateral para entradas del usuario
st.sidebar.header("Entrada del Usuario")
ticker1 = st.sidebar.text_input("Ingrese el Primer Ticker:", "AAPL").upper()
ticker2 = st.sidebar.text_input("Ingrese el Segundo Ticker:", "MSFT").upper()

# Selección de fechas
start_date = st.sidebar.date_input("Fecha de Inicio:", pd.to_datetime("2000-01-01"), min_value=pd.to_datetime("1980-01-01"))
end_date = st.sidebar.date_input("Fecha de Fin:", pd.to_datetime("today"), min_value=pd.to_datetime("1980-01-01"))

# Selección de frecuencia
interval = st.sidebar.radio("Seleccionar Frecuencia de Datos:", ['1d', '1wk', '1mo'], index=0)

# Determinar la etiqueta de intervalo
interval_labels = {'1d': 'diarios', '1wk': 'semanales', '1mo': 'mensuales'}
interval_label = interval_labels.get(interval, 'desconocido')

# Obtener datos para ambos tickers
if 'data1' not in st.session_state:
    st.session_state.data1 = None
    st.session_state.data2 = None
    st.session_state.years = []

if st.sidebar.button("Generar Gráfico de Dispersión") or st.session_state.data1 is None:
    data1 = fetch_stock_data(ticker1, start_date, end_date, interval)
    data2 = fetch_stock_data(ticker2, start_date, end_date, interval)
    
    if not data1.empty and not data2.empty:
        # Calcular variaciones porcentuales
        data1 = calculate_percentage_variations(data1)
        data2 = calculate_percentage_variations(data2)

        # Combinar datos según fechas
        combined_data = pd.merge(data1, data2, left_index=True, right_index=True, suffixes=('_1', '_2'))
        combined_data.dropna(inplace=True)

        if not combined_data.empty:
            # Añadir columnas de año, intervalo y fecha formateada para filtro y visualización
            combined_data['Año'] = combined_data.index.year
            combined_data['Intervalo'] = interval
            combined_data['Fecha Formateada'] = combined_data.index.strftime('%d-%m-%Y') if interval == '1d' else \
                                                combined_data.index.strftime('%d-%m-%Y') if interval == '1wk' else \
                                                combined_data.index.strftime('%m-%Y')
            
            st.session_state.data1 = data1
            st.session_state.data2 = data2
            st.session_state.combined_data = combined_data
            st.session_state.years = combined_data['Año'].unique().tolist()
        else:
            st.error("No hay datos combinados disponibles después de fusionar los dos tickers.")
    else:
        st.error("Uno de los tickers devolvió un conjunto de datos vacío. Por favor, revise los tickers o el rango de fechas.")

if st.session_state.combined_data is not None:
    combined_data = st.session_state.combined_data
    
    # Filtro de año con opciones de activar/desactivar todo
    st.sidebar.write("Filtro de Años")
    if st.sidebar.button("Seleccionar Todos los Años"):
        selected_years = st.session_state.years
    elif st.sidebar.button("Deseleccionar Todos los Años"):
        selected_years = []
    else:
        selected_years = st.sidebar.multiselect("Seleccionar Años para Mostrar:", st.session_state.years, default=st.session_state.years)
    
    # Filtrar según los años seleccionados
    filtered_data = combined_data[combined_data['Año'].isin(selected_years)]
    
    if not filtered_data.empty:
        # Crear gráfico de dispersión
        fig = px.scatter(filtered_data, 
                         x='Variación_1', 
                         y='Variación_2', 
                         color='Año',
                         symbol='Intervalo',
                         title=f"Gráfico de Dispersión de Variaciones de Precios para {ticker1} y {ticker2} ({interval_label})",
                         labels={f'Variación_1': f'Variación de {ticker1} (%)', 
                                 f'Variación_2': f'Variación de {ticker2} (%)'},
                         trendline="ols",
                         template="plotly_white",
                         hover_data={'Fecha Formateada': True, 'Año': False})
        
        fig.update_layout(showlegend=True)
        fig.update_traces(marker=dict(size=10, line=dict(width=2, color='DarkSlateGrey')))
        fig.add_hline(y=0, line_dash="dash", line_color="red")
        fig.add_vline(x=0, line_dash="dash", line_color="red")
        
        # Añadir marca de agua
        fig.add_annotation(
            text="MTaurus - X:@mtaurus_ok",
            xref="paper", yref="paper",
            x=0.99, y=0.01,
            showarrow=False,
            font=dict(size=10, color="rgba(150,150,150,0.5)"),
            align="right"
        )
        
        # Mostrar el gráfico
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("No hay datos disponibles para los años seleccionados.")
else:
    st.warning("Por favor, genere el gráfico de dispersión primero.")
