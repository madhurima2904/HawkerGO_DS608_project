import re
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from src.theme import apply_theme, render_hero, style_chart

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "processed" / "hawker_centres_final.csv"

apply_theme()


def short_name(name: str) -> str:
    """Use the text in the last brackets as a short display name."""
    matches = re.findall(r"\(([^)]+)\)", str(name))
    return matches[-1].strip() if matches else str(name).strip()


@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_FILE)
    df["total_stalls"] = (
        df["no_of_market_stalls"].fillna(0)
        + df["no_of_food_stalls"].fillna(0)
    )
    df["stall_type"] = df.apply(
        lambda r: "Wet-market heavy"
        if r["no_of_market_stalls"] >= r["no_of_food_stalls"]
        else "Food-court style",
        axis=1,
    )
    df["short_name"] = df["name"].apply(short_name)
    return df


st.markdown("""
<style>
.hg-insight-note {background:#F0F5EF;border:1px solid #DCE8DD;border-radius:16px;
  padding:15px 19px;color:#476153;margin:10px 0 22px;font-size:.92rem;}
.hg-insight-section {font-size:.76rem;letter-spacing:.13em;font-weight:800;
  color:#246C53;margin:12px 0 5px;}
[data-testid="stPlotlyChart"], [data-testid="stPlotlyChart"] > div {
  background:transparent !important;box-shadow:none !important;}
</style>
""", unsafe_allow_html=True)

render_hero(
    section="Stall Insights",
    headline="Beyond the food.",
    description=(
        "Discover the numbers behind Singapore's hawker centres, "
        "from stall capacity to food and market stall patterns."
    ),
)

try:
    df = load_data()
except (FileNotFoundError, KeyError, ValueError) as exc:
    st.error(f"Unable to load the hawker-centre dataset: {exc}")
    st.stop()

if df.empty:
    st.warning("No hawker centres found in the dataset.")
    st.stop()

st.markdown('<div class="hg-insight-section">HAWKER CENTRES AT A GLANCE</div>', unsafe_allow_html=True)
metric_a, metric_b, metric_c = st.columns(3)
with metric_a:
    st.metric("Hawker centres", f"{len(df):,}")
with metric_b:
    st.metric("Food stalls", f"{df['no_of_food_stalls'].fillna(0).sum():,.0f}")
with metric_c:
    st.metric("Market stalls", f"{df['no_of_market_stalls'].fillna(0).sum():,.0f}")

st.markdown(
    '<div class="hg-insight-note">Capacity figures describe the number of recorded stalls, '
    'not real-time occupancy or whether individual stalls are operating.</div>',
    unsafe_allow_html=True,
)

st.subheader("Largest hawker centres")
st.caption("Top 10 centres by combined food and market stall capacity.")

top10 = df.nlargest(10, "total_stalls").sort_values("total_stalls", ascending=True)
fig_top = px.bar(
    top10,
    y="short_name",
    x=["no_of_food_stalls", "no_of_market_stalls"],
    orientation="h",
    barmode="stack",
    color_discrete_map={
        "no_of_food_stalls": "#246C53",
        "no_of_market_stalls": "#E6A26F",
    },
    hover_name="name",
    labels={"short_name": "Hawker centre", "value": "Number of stalls"},
)
trace_names = {
    "no_of_food_stalls": "Food stalls",
    "no_of_market_stalls": "Market stalls",
}
fig_top.for_each_trace(lambda t: t.update(name=trace_names.get(t.name, t.name)))
fig_top = style_chart(fig_top, height=480)
fig_top.update_layout(barmode="stack", legend_title_text="")
st.plotly_chart(fig_top, use_container_width=True, theme=None)

with st.expander("View the top 10 centres as a table"):
    st.dataframe(
        top10.sort_values("total_stalls", ascending=False)[
            ["name", "no_of_market_stalls", "no_of_food_stalls", "total_stalls", "address_myenv"]
        ],
        use_container_width=True,
        hide_index=True,
    )

st.divider()
st.subheader("Food stalls and market stalls")
st.caption("Compare how individual centres allocate capacity between cooked food and wet-market stalls.")
fig_dist = px.scatter(
    df,
    x="no_of_food_stalls",
    y="no_of_market_stalls",
    color="stall_type",
    color_discrete_map={
        "Wet-market heavy": "#246C53",
        "Food-court style": "#E46C45",
    },
    hover_name="short_name",
    labels={
        "no_of_food_stalls": "Food stalls",
        "no_of_market_stalls": "Market stalls",
        "stall_type": "",
    },
)
fig_dist.update_traces(marker=dict(size=10, opacity=0.8))
fig_dist = style_chart(fig_dist, height=420)
fig_dist.update_layout(legend_title_text="")
st.plotly_chart(fig_dist, use_container_width=True, theme=None)

st.markdown(
    '<div class="hg-insight-note"><strong>How to read the chart:</strong> '
    'Green points represent wet-market-heavy centres (market stalls are at least as numerous '
    'as food stalls). Coral points represent food-court-style centres '
    '(more food stalls than market stalls).</div>',
    unsafe_allow_html=True,
)
