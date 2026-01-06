import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Olivia Growth - JCN Dashboard",
    page_icon="🌱",
    layout="wide"
)

# Header with logo and title
col1, col2 = st.columns([1, 4])
with col1:
    try:
        logo = Image.open("jcn_logo.jpg")
        st.image(logo, width=150)
    except:
        st.write("")

with col2:
    st.title("🌱 Olivia Growth Portfolio")
    st.markdown("Growth-focused investment strategy")

st.markdown("---")

st.info("🚧 This page is under construction. Coming soon!")

st.markdown("---")
st.caption("JCN Financial & Tax Advisory Group, LLC - Built with Streamlit")
