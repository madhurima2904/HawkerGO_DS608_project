
import base64
from html import escape
from pathlib import Path

import streamlit as st


ROOT = Path(__file__).resolve().parent.parent


# ============================================================
# IMAGE LOADER
# ============================================================

def _image_url(filename):
    image = ROOT / "assets" / filename

    if not image.is_file():
        return "none"

    suffix = image.suffix.lower()
    mime = "image/png" if suffix == ".png" else "image/jpeg"

    encoded = base64.b64encode(
        image.read_bytes()
    ).decode("ascii")

    return f'url("data:{mime};base64,{encoded}")'


# ============================================================
# SHARED HAWKERGO THEME
# ============================================================

def apply_theme():

    logo_url = _image_url("sidebar_logo.png")
    scenery_url = _image_url("sidebar_scenery.png")
    hero_url = _image_url("hawker_hero_art.jpg")

    css = """
    <style>

    /* COLOURS */

    :root {
        --hg-forest: #103D2D;
        --hg-green: #246C53;
        --hg-cream: #FBFAF5;
        --hg-sage: #E3F0D1;
        --hg-text: #25342F;
    }

    .stApp,
    [data-testid="stAppViewContainer"] {
        background-color: var(--hg-cream) !important;
        color: var(--hg-text);
    }

    /* MAIN CONTENT */

    [data-testid="stMainBlockContainer"] {
        width: 100% !important;
        max-width: 1700px !important;
        padding: 0.65rem 1.6rem 2.5rem !important;
    }


    /* =====================================================
       STATIC ILLUSTRATED SIDEBAR
       ===================================================== */

    [data-testid="stSidebar"],
    [data-testid="stSidebarContent"] {
        background-color: var(--hg-forest) !important;
        width: 230px !important;
        min-width: 230px !important;
        max-width: 230px !important;
    }

    [data-testid="stSidebarContent"] {
        height: 100dvh !important;
        min-height: 100dvh !important;

        overflow-x: hidden !important;
        overflow-y: hidden !important;

        background-image:
            __LOGO__,
            __SCENERY__ !important;

        background-position:
            center 10px,
            center bottom !important;

        background-repeat:
            no-repeat,
            no-repeat !important;

        background-size:
            176px auto,
            100% min(61dvh, 610px) !important;

        background-attachment:
            scroll,
            scroll !important;
    }

    /* HIDE NATIVE SMALL STREAMLIT LOGO */

    [data-testid="stLogo"] {
        display: none !important;
    }

    [data-testid="stSidebarHeader"] {
        min-height: 4px !important;
        height: 4px !important;
        padding: 0 !important;
    }


    /* =====================================================
       SIDEBAR NAVIGATION
       ===================================================== */

    [data-testid="stSidebarNav"] {
        position: relative !important;
        z-index: 2 !important;

        padding: 144px 11px 0 !important;
        margin: 0 !important;

        background: transparent !important;
    }

    [data-testid="stSidebarNav"] a {
        display: flex !important;
        align-items: center !important;

        min-height: 45px !important;

        margin: 4px 0 !important;
        padding: 8px 10px !important;

        border-radius: 14px !important;
    }

    [data-testid="stSidebarNav"] a span,
    [data-testid="stSidebarNav"] a p {
        color: #F8F8EB !important;

        font-size: 12px !important;
        font-weight: 550 !important;
        line-height: 1.25 !important;

        white-space: normal !important;
        text-overflow: clip !important;
        overflow: visible !important;
    }

    /* ACTIVE NAVIGATION */

    [data-testid="stSidebarNav"]
    a[aria-current="page"] {
        background: var(--hg-sage) !important;
    }

    [data-testid="stSidebarNav"]
    a[aria-current="page"] span,
    [data-testid="stSidebarNav"]
    a[aria-current="page"] p {
        color: var(--hg-forest) !important;
        font-weight: 750 !important;
    }


    /* =====================================================
       ILLUSTRATED HEADING
       ===================================================== */

    .hg-hero {
        box-sizing: border-box !important;
        isolation: isolate !important;

        position: relative !important;
        width: 100% !important;

        min-height: 200px !important;

        margin: 0 0 12px !important;
        padding: 25px 26px !important;

        overflow: hidden !important;

        border: 0 !important;
        border-radius: 0 !important;
        box-shadow: none !important;

        background-color: var(--hg-cream) !important;
        background-image: __HERO__ !important;

        background-position: right center !important;
        background-repeat: no-repeat !important;
        background-size: auto 100% !important;
    }

    /* GRADIENT OVER BACKGROUND IMAGE */

    .hg-hero::before {
        content: "";

        position: absolute;
        inset: 0;
        z-index: 0;

        background: linear-gradient(
            90deg,
            #FBFAF5 0%,
            rgba(251,250,245,.98) 28%,
            rgba(251,250,245,.86) 44%,
            rgba(251,250,245,.14) 70%,
            transparent 90%
        );

        pointer-events: none;
    }

    .hg-hero::after {
        content: none !important;
    }

    .hg-hero-content {
        position: relative !important;
        z-index: 1 !important;

        max-width: 510px !important;
        width: 56% !important;
    }


    /* HEADING LABEL */

    .hg-hero-label {
        color: #176344 !important;

        font-size: 10px !important;
        font-weight: 800 !important;
        letter-spacing: 1px !important;
        text-transform: uppercase !important;

        margin-bottom: 10px !important;
    }


    /* MAIN HEADING - SMALLER */

    .hg-hero-title {
        font-family: Georgia, serif !important;

        font-size: clamp(
            26px,
            2.25vw,
            38px
        ) !important;

        font-weight: 700 !important;
        color: var(--hg-forest) !important;

        line-height: 1.1 !important;
        letter-spacing: -.7px !important;

        margin: 0 0 12px !important;
    }


    /* HEADING DESCRIPTION */

    .hg-hero-description {
        max-width: 420px !important;

        font-size: 13px !important;
        line-height: 1.5 !important;

        color: #35483D !important;
    }


    /* =====================================================
       SMALLER FONTS ACROSS ALL PAGES
       ===================================================== */

    [data-testid="stMainBlockContainer"] h1 {
        font-size: 1.85rem !important;
        line-height: 1.2 !important;
    }

    [data-testid="stMainBlockContainer"] h2 {
        font-size: 1.35rem !important;
        line-height: 1.25 !important;
    }

    [data-testid="stMainBlockContainer"] h3 {
        font-size: 1.12rem !important;
        line-height: 1.28 !important;
    }

    [data-testid="stMainBlockContainer"] .stMarkdown p,
    [data-testid="stMainBlockContainer"] .stCaption p {
        font-size: .88rem !important;
        line-height: 1.5 !important;
    }

    /* FILTER LABELS */

    [data-testid="stMainBlockContainer"]
    [data-testid="stWidgetLabel"] p,

    [data-testid="stMainBlockContainer"] label {
        font-size: .80rem !important;
    }


    /* METRIC LABELS */

    [data-testid="stMainBlockContainer"]
    [data-testid="stMetricLabel"] p {
        font-size: .77rem !important;
    }

    /* METRIC VALUES */

    [data-testid="stMainBlockContainer"]
    [data-testid="stMetricValue"] {
        font-size: 1.65rem !important;
        color: var(--hg-forest) !important;
    }

    /* BUTTONS AND SELECTBOXES */

    [data-testid="stMainBlockContainer"] button,
    [data-testid="stMainBlockContainer"]
    [data-baseweb="select"] {
        font-size: .84rem !important;
    }


    /* MAINTENANCE CALENDAR ELEMENTS */

    .hg-section {
        font-size: 18px !important;
    }

    .hg-kpi-value {
        font-size: 30px !important;
    }

    .hg-kpi-label {
        font-size: 12px !important;
    }

    .hg-spotlight-title {
        font-size: 22px !important;
    }

    .hg-filter-head {
        font-size: 16px !important;
    }

    .hg-muted,
    .hg-upcoming,
    .hg-fact {
        font-size: 12px !important;
    }


    /* CARDS */

    [data-testid="stMetric"] {
        background: linear-gradient(
            145deg,
            #FFFFFF,
            #F0F5EF
        );

        border: 1px solid #DCE8D9;
        border-radius: 15px;
        padding: 14px;
    }


    /* TRANSPARENT CHARTS */

    [data-testid="stPlotlyChart"],
    [data-testid="stPlotlyChart"] > div {
        background: transparent !important;
        box-shadow: none !important;
    }


    /* TABLES */

    [data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
    }


    /* =====================================================
       RESPONSIVE LAYOUT
       ===================================================== */

    @media (max-width: 850px) {

        .hg-hero-content {
            width: 80% !important;
        }

        .hg-hero {
            background-size: cover !important;
        }

        .hg-hero::before {
            background: linear-gradient(
                90deg,
                rgba(251,250,245,.98),
                rgba(251,250,245,.72)
            );
        }
    }

    @media (max-height: 650px) {

        [data-testid="stSidebarContent"] {
            background-size:
                150px auto,
                100% 48% !important;
        }

        [data-testid="stSidebarNav"] {
            padding-top: 115px !important;
        }
    }

    </style>
    """

    css = css.replace("__LOGO__", logo_url)
    css = css.replace("__SCENERY__", scenery_url)
    css = css.replace("__HERO__", hero_url)

    st.html(css)


# ============================================================
# CHART STYLING
# ============================================================

def style_chart(fig, height=380):

    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="Arial, sans-serif",
            color="#25342F",
        ),
        margin=dict(
            l=20,
            r=20,
            t=35,
            b=20,
        ),
        legend_title_text="",
    )

    return fig


# ============================================================
# SHARED HERO FUNCTION
# ============================================================

def render_hero(section, headline, description):

    safe_section = escape(str(section).upper())

    safe_title = escape(
        str(headline)
    ).replace("\n", "<br>")

    safe_description = escape(str(description))

    st.html(
        '<div class="hg-hero">'
        '<div class="hg-hero-content">'
        f'<div class="hg-hero-label">HAWKERGO / {safe_section}</div>'
        f'<div class="hg-hero-title">{safe_title}</div>'
        f'<div class="hg-hero-description">{safe_description}</div>'
        '</div></div>'
    )
