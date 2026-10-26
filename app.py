
import streamlit as st
from src.theme import apply_theme

st.set_page_config(
    page_title="HawkerGo",
    page_icon="🍜",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_theme()

pages = [
    st.Page(
        "pages/1_Explore_Hawkers.py",
        title="Explore Hawkers",
        icon="🏠"
    ),
    st.Page(
        "pages/2_Maintenance_Calendar.py",
        title="Maintenance Calendar",
        icon="📅",
        default=True
    ),
    st.Page(
        "pages/3_Stall_Insights.py",
        title="Stall Insights",
        icon="📊"
    )
]

with st.sidebar:
    st.markdown("## 🍜 HawkerGo")
    st.caption("Find your next makan spot")

navigation = st.navigation(
    pages,
    position="sidebar"
)

navigation.run()
