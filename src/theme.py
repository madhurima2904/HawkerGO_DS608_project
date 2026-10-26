
import streamlit as st


def apply_theme():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Outfit:wght@400;500;600;700;800&display=swap');

    :root {
        --hawker-bg: #FBFAF5;
        --hawker-text: #25342F;
        --hawker-green: #246C53;
        --hawker-muted: #607267;
        --hawker-line: #E3E9E1;
    }

    .stApp {
        background-color: var(--hawker-bg);
        color: var(--hawker-text);
        font-family: 'DM Sans', sans-serif;
    }

    h1, h2, h3, h4 {
        font-family: 'Outfit', sans-serif !important;
        color: var(--hawker-text) !important;
        font-weight: 700 !important;
    }

    [data-testid="stMain"] p,
    [data-testid="stMain"] label {
        color: var(--hawker-text);
    }

    [data-testid="stCaptionContainer"] p {
        color: #718078 !important;
    }

    /* SIDEBAR */
    [data-testid="stSidebar"] {
        background-color: #F0F5EF !important;
        border-right: 1px solid var(--hawker-line);
    }

    [data-testid="stSidebar"] * {
        color: var(--hawker-text) !important;
    }

    [data-testid="stSidebar"] a:hover {
        background-color: #E1EEE4 !important;
        border-radius: 10px;
    }

    [data-testid="stSidebar"] a[aria-current="page"] {
        background-color: #DCEDE2 !important;
        color: var(--hawker-green) !important;
        border-radius: 10px;
        font-weight: 700;
    }

    /* TRANSPARENT METRIC CARDS */
    div[data-testid="stMetric"] {
        background: transparent !important;
        border: 1px solid var(--hawker-line) !important;
        border-radius: 18px !important;
        padding: 22px !important;
        min-height: 135px !important;
        box-shadow: none !important;
    }

    div[data-testid="stMetricLabel"],
    div[data-testid="stMetricLabel"] * {
        color: var(--hawker-muted) !important;
        font-size: 15px !important;
        font-weight: 600 !important;
        opacity: 1 !important;
    }

    div[data-testid="stMetricValue"],
    div[data-testid="stMetricValue"] *,
    div[data-testid="stMetricValue"] > div {
        color: var(--hawker-green) !important;
        font-family: 'Outfit', sans-serif !important;
        font-size: 38px !important;
        font-weight: 800 !important;
        line-height: 1.2 !important;
    }

    /* FILTERS */
    [data-testid="stMultiSelect"] [data-baseweb="select"],
    [data-testid="stSelectbox"] [data-baseweb="select"],
    [data-testid="stMultiSelect"] [data-baseweb="select"] > div,
    [data-testid="stSelectbox"] [data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        color: var(--hawker-text) !important;
        border-radius: 12px !important;
        border-color: #DDE6DD !important;
    }

    [data-testid="stMultiSelect"] [data-baseweb="tag"] {
        background-color: #E8F3EC !important;
        border-radius: 8px !important;
    }

    [data-testid="stMultiSelect"] [data-baseweb="tag"] span {
        color: var(--hawker-green) !important;
        font-weight: 600 !important;
    }

    [data-testid="stMultiSelect"] input,
    [data-testid="stSelectbox"] input {
        color: var(--hawker-text) !important;
        background-color: transparent !important;
    }

    /* BUTTONS */
    div.stButton > button {
        background-color: transparent !important;
        color: var(--hawker-green) !important;
        border: 1px solid #DDE6DD;
        border-radius: 12px;
        font-weight: 700;
    }

    div.stButton > button:hover {
        background-color: #E8F3EC !important;
        border-color: var(--hawker-green);
    }

    /* HERO BANNER */
    .hero {
        background: linear-gradient(
            110deg,
            #E9F3E8 0%,
            #F5F5E8 55%,
            #FFF0DC 100%
        );
        padding: 34px 38px;
        border-radius: 24px;
        margin-bottom: 28px;
    }

    .hero h1 {
        font-family: 'Outfit', sans-serif !important;
        font-size: 40px !important;
        font-weight: 800 !important;
        color: var(--hawker-text) !important;
        margin: 10px 0;
    }

    .hero p {
        color: var(--hawker-muted) !important;
        font-size: 15px;
        line-height: 1.7;
    }

    .section-label {
        color: var(--hawker-green) !important;
        font-size: 12px;
        font-weight: 800;
        letter-spacing: 1.2px;
        text-transform: uppercase;
    }

    /* TRANSPARENT PLOTLY CONTAINERS */
    [data-testid="stPlotlyChart"],
    [data-testid="stPlotlyChart"] > div {
        background: transparent !important;
        border: none !important;
        border-radius: 0 !important;
        box-shadow: none !important;
    }

    [data-testid="stPlotlyChart"] {
        padding: 0 !important;
    }

    /* TRANSPARENT DATAFRAME CONTAINERS */
    [data-testid="stDataFrame"],
    [data-testid="stDataFrame"] > div {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }

    /* CUSTOM TABLE */
    .hawker-table-wrapper {
        width: 100%;
        overflow-x: auto;
        background: transparent !important;
    }

    .hawker-table {
        width: 100%;
        border-collapse: collapse;
        background: transparent !important;
        font-family: 'DM Sans', sans-serif;
        font-size: 14px;
    }

    .hawker-table th,
    .hawker-table td,
    .hawker-table thead,
    .hawker-table tbody,
    .hawker-table tr {
        background: transparent !important;
    }

    .hawker-table th {
        color: var(--hawker-green) !important;
        font-weight: 700;
        text-align: left;
        padding: 16px 14px;
        border-bottom: 2px solid #D9E4D8;
        white-space: nowrap;
    }

    .hawker-table td {
        color: var(--hawker-text) !important;
        padding: 16px 14px;
        border-bottom: 1px solid var(--hawker-line);
    }

    .hawker-table tbody tr:hover td {
        background: rgba(36,108,83,0.05) !important;
    }

    .hawker-table th:last-child,
    .hawker-table td:last-child {
        text-align: right;
    }

    .hawker-type {
        display: inline-block;
        padding: 5px 11px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 700;
    }

    .hawker-type.cleaning {
        background: #FBE9E0;
        color: #B75030;
    }

    .hawker-type.maintenance {
        background: #E3F1E8;
        color: var(--hawker-green);
    }

    hr {
        border-color: var(--hawker-line) !important;
    }

    @media (max-width: 768px) {
        .hero {
            padding: 24px;
        }

        .hero h1 {
            font-size: 30px !important;
        }

        div[data-testid="stMetric"] {
            min-height: 110px !important;
            padding: 16px !important;
        }

        div[data-testid="stMetricValue"],
        div[data-testid="stMetricValue"] * {
            font-size: 30px !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)


def style_chart(fig, height=380):
    """
    Apply a transparent theme to all Plotly charts.
    """
    fig.update_layout(
        template="plotly_white",
        height=height,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="DM Sans, Arial, sans-serif",
            size=13,
            color="#25342F"
        ),
        margin=dict(l=20, r=20, t=35, b=35),
        xaxis=dict(
            tickfont=dict(color="#25342F", size=12),
            title_font=dict(color="#25342F"),
            gridcolor="#E3E9E1",
            linecolor="#DDE6DD",
            zeroline=False
        ),
        yaxis=dict(
            tickfont=dict(color="#25342F", size=12),
            title_font=dict(color="#25342F"),
            gridcolor="#E3E9E1",
            linecolor="#DDE6DD",
            zeroline=False
        ),
        legend=dict(
            font=dict(color="#25342F"),
            title_font=dict(color="#25342F"),
            bgcolor="rgba(0,0,0,0)"
        ),
        hoverlabel=dict(
            bgcolor="#FFFFFF",
            font=dict(color="#25342F")
        )
    )
    return fig
