import streamlit as st
from utils.data import get_top5

st.set_page_config(layout="wide", page_title="Stock Analyzer")

st.title("📈 Stock Analyzer")
st.markdown("Welcome to Stock Analyzer. Use the sidebar to navigate between pages.")
st.divider()

st.subheader("Top 5 by Price:")
df = get_top5()
st.dataframe(df, hide_index=True, use_container_width=True)