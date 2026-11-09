
"""HawkerGO | Stall Insights."""

from html import escape
from pathlib import Path
import re
import textwrap

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.theme import apply_theme, render_hero


ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "processed" / "hawker_centres_final.csv"

FOREST = "#103D2D"
GREEN = "#246C53"
ORANGE = "#EDA36D"
CREAM = "#FBFAF5"
MUTED = "#66756B"

apply_theme()


# ============================================================
# PAGE STYLING
# ============================================================

st.html(
    """
    <style>
    .si-card {
        border: 1px solid #E4E7D9;
        border-radius: 19px;
        background: #FFFEFA;
        padding: 18px 20px;
        min-height: 100px;
        display: flex;
        align-items: center;
        gap: 15px;
    }

    .si-card-green {
        background: linear-gradient(125deg,#FFFEF8,#E9F3E5);
    }

    .si-card-peach {
        background: linear-gradient(125deg,#FFFEF8,#FFF0E3);
    }

    .si-card-gold {
        background: linear-gradient(125deg,#FFFEF8,#FBF2D7);
    }

    .si-icon {
        height: 50px;
        width: 50px;
        min-width: 50px;
        border-radius: 50%;
        background: #E2F0D8;
        color: #176644;
        display: flex;
        justify-content: center;
        align-items: center;
    }

    .si-card-peach .si-icon {
        background: #FFE8CF;
        color: #CB6A26;
    }

    .si-card-gold .si-icon {
        background: #F9E9AD;
        color: #8C6813;
    }

    .si-icon svg {
        height: 29px;
        width: 29px;
    }

    .si-card-label {
        font-size: 12px;
        color: #32493C;
        font-weight: 650;
    }

    .si-card-value {
        margin-top: 4px;
        color: #103D2D;
        font: 700 clamp(24px,2.0vw,34px)/1.1 Georgia,serif;
        font-variant-numeric: tabular-nums;
    }

    .si-heading {
        color: #103D2D;
        font-size: 18px;
        font-weight: 800;
        line-height: 1.25;
        margin: 0 0 4px;
    }

    .si-caption {
        color: #68776C;
        font-size: 12px;
        line-height: 1.45;
        margin: 0 0 8px;
    }

    .si-panel {
        border: 1px solid #E7E8DB;
        border-radius: 19px;
        background: rgba(255,254,249,.90);
        padding: 15px 15px 6px;
    }

    .si-mix-label {
        text-align: center;
        padding-top: 76px;
    }

    .si-mix-number {
        font-size: 25px;
        line-height: 1.2;
        font-weight: 800;
        color: #246C53;
    }

    .si-mix-number.orange {
        color: #B86931;
    }

    .si-mix-detail {
        color: #45584A;
        font-size: 12px;
        line-height: 1.4;
    }

    .si-footer {
        font-size: 11px;
        color: #65776B;
        padding: 10px 3px 3px;
    }

    [data-testid="stPlotlyChart"],
    [data-testid="stPlotlyChart"] > div {
        background: transparent !important;
        box-shadow: none !important;
    }

    @media (max-width: 950px) {
        .si-card {
            min-height: 90px;
            padding: 13px;
            gap: 9px;
        }

        .si-icon {
            min-width: 40px;
            width: 40px;
            height: 40px;
        }

        .si-icon svg {
            width: 23px;
            height: 23px;
        }

        .si-card-value {
            font-size: 23px;
        }

        .si-mix-label {
            padding-top: 55px;
        }

        .si-mix-number {
            font-size: 19px;
        }
    }
    </style>
    """
)


# ============================================================
# LOAD AND PREPARE DATA
# ============================================================

@st.cache_data(show_spinner=False)
def load_data():

    df = pd.read_csv(DATA_FILE)

    required = {
        "name",
        "no_of_food_stalls",
        "no_of_market_stalls",
    }

    missing = required.difference(df.columns)

    if missing:
        raise ValueError(
            "Missing columns: " + ", ".join(sorted(missing))
        )

    df = df.dropna(subset=["name"]).copy()

    for col in (
        "no_of_food_stalls",
        "no_of_market_stalls",
    ):
        df[col] = (
            pd.to_numeric(df[col], errors="coerce")
            .fillna(0)
            .clip(lower=0)
        )

    df["total_stalls"] = (
        df["no_of_food_stalls"]
        + df["no_of_market_stalls"]
    )

    df["stall_profile"] = "Balanced"

    df.loc[
        df["no_of_food_stalls"]
        > df["no_of_market_stalls"],
        "stall_profile",
    ] = "Food-court style"

    df.loc[
        df["no_of_market_stalls"]
        > df["no_of_food_stalls"],
        "stall_profile",
    ] = "Wet-market heavy"

    return df


# ============================================================
# CHART HELPERS
# ============================================================

def chart_label(name, max_chars=31):
    """Short labels, with full names available on hover."""

    name = str(name)

    parens = re.findall(r"\(([^)]+)\)", name)

    if parens and len(parens[-1]) >= 7:
        name = parens[-1].strip()

    if len(name) > max_chars:
        name = name[:max_chars - 1].rstrip() + "…"

    return "<br>".join(
        textwrap.wrap(
            name,
            width=17,
            break_long_words=False,
        )
    )


def plot_layout(fig, height, margin=None):

    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="Arial, sans-serif",
            size=11,
            color=FOREST,
        ),
        margin=margin or dict(
            l=8,
            r=8,
            t=14,
            b=32,
        ),
    )

    return fig


# ============================================================
# KPI ICONS
# ============================================================

ICONS = {
    "centre": (
        '<rect x="4" y="10" width="16" height="11" rx="1"/>'
        '<path d="M3 10l2-6h14l2 6M3 10h18M9 21v-7h6v7"/>'
    ),

    "food": (
        '<path d="M3 12h18c0 5-4 9-9 9s-9-4-9-9Z'
        'M9 12l9-9M13 12l8-8"/>'
    ),

    "market": (
        '<path d="M4 10h16l-2 11H6L4 10Z'
        'M3 10l3-5h12l3 5M9 14v3M15 14v3"/>'
    ),

    "total": (
        '<path d="M2 10h20l-2-5H4l-2 5Z'
        'M4 10v11h16V10M9 21v-7h6v7'
        'M2 10c2 3 4 3 6 0 2 3 4 3 6 0 '
        '2 3 4 3 6 0"/>'
    ),
}


def kpi_card(label, value, icon, tone="green"):

    paths = ICONS[icon]

    st.html(
        f'<div class="si-card si-card-{tone}">'
        f'<div class="si-icon">'
        f'<svg viewBox="0 0 24 24" fill="none" '
        f'stroke="currentColor" stroke-width="1.75" '
        f'stroke-linecap="round" stroke-linejoin="round">'
        f'{paths}'
        f'</svg>'
        f'</div>'
        f'<div>'
        f'<div class="si-card-label">{escape(label)}</div>'
        f'<div class="si-card-value">{escape(value)}</div>'
        f'</div>'
        f'</div>'
    )


def panel_title(text, subtitle):

    st.html(
        f'<div class="si-heading">{escape(text)}</div>'
        f'<div class="si-caption">{escape(subtitle)}</div>'
    )


# ============================================================
# PAGE HEADING
# ============================================================

render_hero(
    "Stall Insights",
    "Beyond the food.",
    (
        "Discover the numbers behind Singapore's hawker "
        "centres, from stall capacity to food and market "
        "stall patterns."
    ),
)


try:
    df = load_data()

except (
    FileNotFoundError,
    pd.errors.ParserError,
    ValueError,
) as exc:

    st.error(f"Unable to load the stall dataset: {exc}")
    st.stop()


if df.empty:
    st.warning(
        "There are no hawker-centre records to display."
    )
    st.stop()


# ============================================================
# CALCULATE KPI VALUES
# ============================================================

food_total = int(df["no_of_food_stalls"].sum())

market_total = int(df["no_of_market_stalls"].sum())

all_total = food_total + market_total

food_pct = (
    100 * food_total / all_total
    if all_total
    else 0
)

market_pct = (
    100 * market_total / all_total
    if all_total
    else 0
)


# ============================================================
# FOUR KPI CARDS
# ============================================================

kpi_columns = st.columns(
    4,
    gap="small",
)

with kpi_columns[0]:
    kpi_card(
        "Hawker centres",
        f"{len(df):,}",
        "centre",
    )

with kpi_columns[1]:
    kpi_card(
        "Food stalls",
        f"{food_total:,}",
        "food",
        "peach",
    )

with kpi_columns[2]:
    kpi_card(
        "Market stalls",
        f"{market_total:,}",
        "market",
    )

with kpi_columns[3]:
    kpi_card(
        "Total stalls",
        f"{all_total:,}",
        "total",
        "gold",
    )


st.write("")


# ============================================================
# MAIN DASHBOARD LAYOUT
# ============================================================

left, right = st.columns(
    [1.08, 1],
    gap="medium",
    vertical_alignment="top",
)


# ============================================================
# LEFT: LARGEST HAWKER CENTRES
# ============================================================

with left:

    with st.container(border=True):

        panel_title(
            "Largest hawker centres",
            (
                "Top 10 centres by combined food "
                "and market stall capacity."
            ),
        )

        top = (
            df.nlargest(10, "total_stalls")
            .sort_values("total_stalls")
            .copy()
        )

        top["axis_name"] = [
            f"centre_{i}"
            for i in range(len(top))
        ]

        label_map = dict(
            zip(
                top["axis_name"],
                top["name"].map(chart_label),
            )
        )

        fig_bar = go.Figure()

        # Two stacked bar components
        for col, label, color in (
            ("no_of_food_stalls", "Food stalls", GREEN),
            ("no_of_market_stalls", "Market stalls", ORANGE),
        ):

            fig_bar.add_trace(
                go.Bar(
                    x=top[col],
                    y=top["axis_name"],
                    orientation="h",
                    name=label,
                    marker_color=color,
                    marker_line_width=0,

                    customdata=top[
                        ["name", "total_stalls"]
                    ].to_numpy(),

                    hovertemplate=(
                        "<b>%{customdata[0]}</b><br>"
                        + label
                        + ": %{x:,.0f}<br>"
                        + "Total: %{customdata[1]:,.0f}"
                        + "<extra></extra>"
                    ),
                )
            )

        # Total values at the end of each bar
        fig_bar.add_trace(
            go.Scatter(
                x=(
                    top["total_stalls"]
                    + max(
                        float(top["total_stalls"].max()) * .014,
                        4,
                    )
                ),

                y=top["axis_name"],
                mode="text",

                text=[
                    f"{int(x):,}"
                    for x in top["total_stalls"]
                ],

                textposition="middle right",
                textfont=dict(
                    size=10,
                    color=FOREST,
                ),

                hoverinfo="skip",
                showlegend=False,
                cliponaxis=False,
            )
        )

        fig_bar.update_layout(
            barmode="stack",
            bargap=.34,

            legend=dict(
                orientation="h",
                y=-.12,
                x=.95,
                xanchor="right",
                yanchor="top",
                font=dict(size=10),
            ),

            xaxis=dict(
                title="Number of stalls",
                rangemode="tozero",
                range=[
                    0,
                    float(
                        top["total_stalls"].max()
                    ) * 1.15,
                ],
                showgrid=True,
                gridcolor="#EBEDE5",
                zeroline=False,
                title_font=dict(size=11),
                tickfont=dict(size=10),
            ),

            yaxis=dict(
                title="",
                automargin=True,
                tickmode="array",

                tickvals=top[
                    "axis_name"
                ].tolist(),

                ticktext=[
                    label_map[key]
                    for key in top["axis_name"]
                ],

                tickfont=dict(size=10),
                showgrid=False,
            ),
        )

        plot_layout(
            fig_bar,
            height=615,
            margin=dict(
                l=12,
                r=34,
                t=13,
                b=77,
            ),
        )

        st.plotly_chart(
            fig_bar,
            use_container_width=True,
            config={
                "displayModeBar": False
            },
        )


# ============================================================
# RIGHT TOP: STALL MIX DOUGHNUT CHART
# ============================================================

with right:

    with st.container(border=True):

        panel_title(
            "Stall mix across Singapore",
            (
                "Recorded food and market stall "
                "capacity across all centres."
            ),
        )

        label_left, doughnut_col, label_right = (
            st.columns(
                [0.85, 1.55, 0.85],
                gap="small",
                vertical_alignment="center",
            )
        )

        with label_left:

            st.html(
                '<div class="si-mix-label">'
                f'<div class="si-mix-number">'
                f'{food_pct:.0f}%'
                '</div>'
                '<div class="si-mix-detail">'
                f'Food stalls<br>({food_total:,})'
                '</div></div>'
            )

        with doughnut_col:

            fig_donut = go.Figure(
                go.Pie(
                    labels=[
                        "Food stalls",
                        "Market stalls",
                    ],

                    values=[
                        food_total,
                        market_total,
                    ],

                    hole=.68,

                    marker=dict(
                        colors=[
                            GREEN,
                            ORANGE,
                        ],
                        line=dict(width=0),
                    ),

                    sort=False,
                    textinfo="none",

                    hovertemplate=(
                        "%{label}<br>"
                        "%{value:,.0f} stalls "
                        "(%{percent})"
                        "<extra></extra>"
                    ),

                    showlegend=False,
                )
            )

            # Centre number inside doughnut
            fig_donut.add_annotation(
                text=(
                    f"<b>{all_total:,}</b><br>"
                    "<span style='font-size:11px'>"
                    "stalls</span>"
                ),

                x=.5,
                y=.5,
                xref="paper",
                yref="paper",
                showarrow=False,

                font=dict(
                    size=20,
                    color=FOREST,
                ),

                align="center",
            )

            plot_layout(
                fig_donut,
                height=225,
                margin=dict(
                    l=0,
                    r=0,
                    t=0,
                    b=0,
                ),
            )

            st.plotly_chart(
                fig_donut,
                use_container_width=True,
                config={
                    "displayModeBar": False
                },
            )

        with label_right:

            st.html(
                '<div class="si-mix-label">'
                '<div class="si-mix-number orange">'
                f'{market_pct:.0f}%'
                '</div>'
                '<div class="si-mix-detail">'
                f'Market stalls<br>({market_total:,})'
                '</div></div>'
            )


    # ========================================================
    # RIGHT BOTTOM: FOOD VS MARKET STALLS
    # ========================================================

    with st.container(border=True):

        panel_title(
            "Food stalls vs. market stalls",
            (
                "How centres allocate capacity between "
                "cooked food and wet-market stalls."
            ),
        )

        fig_scatter = go.Figure()

        profiles = (
            ("Wet-market heavy", GREEN),
            ("Food-court style", ORANGE),
            ("Balanced", "#90A795"),
        )

        for profile, color in profiles:

            group = df[
                df["stall_profile"].eq(profile)
            ]

            if group.empty:
                continue

            fig_scatter.add_trace(
                go.Scatter(
                    x=group["no_of_food_stalls"],
                    y=group["no_of_market_stalls"],

                    mode="markers",
                    name=profile,

                    marker=dict(
                        size=8,
                        color=color,
                        opacity=.76,
                        line=dict(width=0),
                    ),

                    customdata=group[
                        ["name", "total_stalls"]
                    ].to_numpy(),

                    hovertemplate=(
                        "<b>%{customdata[0]}</b><br>"
                        "Food stalls: %{x:,.0f}<br>"
                        "Market stalls: %{y:,.0f}<br>"
                        "Total: %{customdata[1]:,.0f}"
                        "<extra></extra>"
                    ),
                )
            )

        fig_scatter.update_layout(

            xaxis=dict(
                title="Food stalls",
                showgrid=True,
                gridcolor="#EAEDE5",
                zeroline=False,
                rangemode="tozero",
                title_font=dict(size=11),
            ),

            yaxis=dict(
                title="Market stalls",
                showgrid=True,
                gridcolor="#EAEDE5",
                zeroline=False,
                rangemode="tozero",
                title_font=dict(size=11),
            ),

            legend=dict(
                orientation="h",
                x=0,
                y=1.12,
                font=dict(size=10),
            ),
        )

        plot_layout(
            fig_scatter,
            height=300,

            margin=dict(
                l=44,
                r=10,
                t=36,
                b=48,
            ),
        )

        st.plotly_chart(
            fig_scatter,
            use_container_width=True,
            config={
                "displayModeBar": False
            },
        )


# ============================================================
# DATA NOTE
# ============================================================

st.html(
    '<div class="si-footer">'
    'Figures represent recorded stall capacity, '
    'not real-time occupancy or whether '
    'individual stalls are operating.'
    '</div>'
)
