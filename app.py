import streamlit as st
from PIL import Image

# Page configuration
st.set_page_config(
    page_title="JCN Financial Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for white theme
st.markdown("""
    <style>
    .main {
        background-color: white;
    }
    .stApp {
        background-color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# Header with logo and title
col1, col2 = st.columns([1, 4])
with col1:
    try:
        logo = Image.open("jcn_logo.jpg")
        st.image(logo, width=200)
    except:
        st.write("")

with col2:
    st.title("JCN Financial & Tax Advisory Group, LLC")
    st.markdown("### Investment Dashboard")

st.markdown("---")

# Welcome section
st.markdown("""
## Welcome to Your Investment Dashboard

Select a portfolio or analysis tool from the sidebar to get started.

### Available Portfolios:
- **📊 Persistent Value** - Value-focused investment strategy with long-term growth potential
- **🌱 Olivia Growth** - Growth-focused investment strategy
- **⚡ Pure Alpha** - Alpha-generating investment strategy

### Analysis Tools:
- **📈 Stock Analysis** - Individual stock research and analysis
- **🌍 Market Analysis** - Broad market trends and sector analysis
- **🛡️ Risk Management** - Portfolio risk assessment and management

### About:
- **ℹ️ About** - Learn more about JCN Financial services
""")

st.markdown("---")

# Quick stats or info section
col1, col2, col3 = st.columns(3)

with col1:
    st.info("**Real-time Data**\n\nAll portfolio data is updated in real-time using market feeds")

with col2:
    st.info("**Comprehensive Analysis**\n\nDetailed performance metrics and risk assessments")

with col3:
    st.info("**Multi-Portfolio**\n\nTrack multiple investment strategies simultaneously")

st.markdown("---")
st.caption("JCN Financial & Tax Advisory Group, LLC - Built with Streamlit")
