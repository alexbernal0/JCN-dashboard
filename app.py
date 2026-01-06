import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="JCN Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title and description
st.title("📊 JCN Dashboard")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("Dashboard Controls")
    st.markdown("Configure your dashboard settings here.")
    
    # Example filter
    date_range = st.date_input(
        "Select Date Range",
        value=(pd.Timestamp.now() - pd.Timedelta(days=30), pd.Timestamp.now())
    )
    
    st.markdown("---")
    st.info("💡 This is a starter template. Customize it based on your needs!")

# Main content area
col1, col2, col3 = st.columns(3)

# Example metrics
with col1:
    st.metric(
        label="Total Records",
        value="1,234",
        delta="12%"
    )

with col2:
    st.metric(
        label="Active Users",
        value="567",
        delta="-3%"
    )

with col3:
    st.metric(
        label="Revenue",
        value="$89,432",
        delta="8%"
    )

st.markdown("---")

# Example chart section
col1, col2 = st.columns(2)

with col1:
    st.subheader("Sample Line Chart")
    # Generate sample data
    dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
    values = np.cumsum(np.random.randn(30)) + 100
    
    df = pd.DataFrame({'Date': dates, 'Value': values})
    
    fig = px.line(df, x='Date', y='Value', title='Trend Over Time')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Sample Bar Chart")
    # Generate sample data
    categories = ['Category A', 'Category B', 'Category C', 'Category D', 'Category E']
    values = np.random.randint(10, 100, size=5)
    
    df_bar = pd.DataFrame({'Category': categories, 'Value': values})
    
    fig_bar = px.bar(df_bar, x='Category', y='Value', title='Distribution by Category')
    st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")

# Data table section
st.subheader("Sample Data Table")
# Generate sample data
sample_data = pd.DataFrame({
    'ID': range(1, 11),
    'Name': [f'Item {i}' for i in range(1, 11)],
    'Value': np.random.randint(100, 1000, size=10),
    'Status': np.random.choice(['Active', 'Inactive', 'Pending'], size=10)
})

st.dataframe(sample_data, use_container_width=True)

# Footer
st.markdown("---")
st.caption("JCN Dashboard - Built with Streamlit and orchestrated by Manus AI")
