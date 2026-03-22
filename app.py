import streamlit as st
import pandas as pd

# Sample DataFrame for historical data
@st.cache_data
def load_data():
    data = {
        'Year': [2020, 2021, 2022, 2023, 2024, 2025],
        'Votes': [150, 200, 250, 300, 350, 400]
    }
    return pd.DataFrame(data)

# Load the data
historical_data = load_data()

# Initialize session state if not already done
if 'chart_data' not in st.session_state:
    st.session_state.chart_data = historical_data

# Title of the app
st.title('Vote Evolution Chart')

# Evolution Chart
st.subheader('Votes Over the Years')

# Plotting the evolution chart
st.line_chart(st.session_state.chart_data.set_index('Year'))
