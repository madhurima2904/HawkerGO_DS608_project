import streamlit as st
from src.theme import apply_theme


# ============================================================
# PAGE SETTINGS
# ============================================================

st.set_page_config(
    page_title="HawkerGO",
    page_icon="🍜",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# SHARED THEME
# ============================================================

apply_theme()


# ============================================================
# PAGE NAVIGATION
# ============================================================

pages = [
    st.Page(
        "pages/1_Explore_Hawkers.py",
        title="Explore Hawkers",
        icon=":material/home:",
    ),

    st.Page(
        "pages/2_Maintenance_Calendar.py",
        title="Maintenance Calendar",
        icon=":material/calendar_month:",
        default=True,
    ),

    st.Page(
        "pages/3_Stall_Insights.py",
        title="Stall Insights",
        icon=":material/bar_chart:",
    ),
]


navigation = st.navigation(
    pages,
    position="sidebar",
)

navigation.run()
