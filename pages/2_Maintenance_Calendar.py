
import calendar
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from src.theme import apply_theme, style_chart
from src.wrangle import load_closure_data


# ==================================================
# SETUP
# ==================================================

apply_theme()

GREEN = "#246C53"
ORANGE = "#E46C45"
TEXT = "#25342F"
MUTED = "#607267"

st.markdown("""
<style>
/* Simple, understated closure cards */
[data-testid="stVerticalBlockBorderWrapper"] {
    box-shadow: none !important;
}

/* Soft, natural filter colours */
[data-testid="stMultiSelect"] [data-baseweb="tag"] {
    background-color: #E4EEE5 !important;
}

[data-testid="stMultiSelect"] [data-baseweb="tag"] span {
    color: #246C53 !important;
}

/* Transparent Plotly backgrounds */
[data-testid="stPlotlyChart"],
[data-testid="stPlotlyChart"] > div {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}
</style>
""", unsafe_allow_html=True)


# ==================================================
# LOAD DATA
# ==================================================

@st.cache_data
def get_data():
    return load_closure_data()


try:
    df = get_data()
except (FileNotFoundError, ValueError) as error:
    st.error(str(error))
    st.stop()

if df.empty:
    st.warning("No closure records found.")
    st.stop()


# ==================================================
# AREA CLASSIFICATION
# ==================================================
# Approximate grouping based on centre names
# and addresses, not official planning boundaries.

AREA_KEYWORDS = {
    "Ang Mo Kio": [
        "ang mo kio", "chong boon", "cheng san"
    ],
    "Bedok": [
        "bedok", "changi village", "east coast lagoon"
    ],
    "Bishan": ["bishan", "shunfu"],
    "Bukit Batok": ["bukit batok"],
    "Bukit Merah": [
        "bukit merah", "tiong bahru",
        "redhill", "alexandra", "telok blangah",
        "henderson", "beo crescent"
    ],
    "Bukit Panjang": ["bukit panjang"],
    "Central Area": [
        "maxwell", "amoy", "chinatown",
        "hong lim", "people's park",
        "tekka", "berseh", "golden mile",
        "newton", "market street",
        "tanjong pagar", "lavender"
    ],
    "Clementi": ["clementi", "west coast"],
    "Geylang": [
        "geylang", "aljunied",
        "old airport road", "sims"
    ],
    "Hougang": ["hougang", "kovan"],
    "Jurong East": [
        "jurong east", "yuhua", "teban"
    ],
    "Jurong West": [
        "jurong west", "boon lay"
    ],
    "Kallang": [
        "kallang", "whampoa", "bendemeer"
    ],
    "Marine Parade": [
        "marine parade", "marine terrace"
    ],
    "Pasir Ris": ["pasir ris"],
    "Punggol": ["punggol"],
    "Queenstown": [
        "queenstown", "commonwealth",
        "ghim moh", "holland drive",
        "tanglin halt", "mei ling"
    ],
    "Sembawang": ["sembawang"],
    "Sengkang": ["sengkang", "anchorvale"],
    "Serangoon": ["serangoon", "chomp chomp"],
    "Tampines": ["tampines"],
    "Toa Payoh": ["toa payoh"],
    "Woodlands": ["woodlands", "marsiling"],
    "Yishun": ["yishun", "chong pang"],
}


def identify_area(row):
    name = str(row["Hawker Centre"]).lower()
    address = str(row.get("Address", "")).lower()

    for area, keywords in AREA_KEYWORDS.items():
        if any(keyword in name for keyword in keywords):
            return area

    for area, keywords in AREA_KEYWORDS.items():
        if any(keyword in address for keyword in keywords):
            return area

    return "Other areas"


df["Area"] = df.apply(identify_area, axis=1)

dated_df = df[
    df["Schedule Status"] == "Dated"
].copy()

review_df = df[
    df["Schedule Status"] == "Needs review"
].copy()

if dated_df.empty:
    st.warning("No valid closure date ranges found.")
    st.stop()


# ==================================================
# HERO
# ==================================================

st.markdown("""
<div class="hero">
    <div class="section-label">
        HAWKERGO / MAINTENANCE CALENDAR
    </div>
    <h1>Know before you go.</h1>
    <p>
        Explore scheduled cleaning and maintenance
        closures across Singapore's hawker centres.
    </p>
</div>
""", unsafe_allow_html=True)

st.caption(
    "Source: Uploaded hawker-centre closure dataset. "
    "Area groupings are approximate and dates "
    "may change."
)


# ==================================================
# KEEP ORIGINAL AREA SELECTOR
# ==================================================

st.subheader("Choose your area")

area_options = sorted(df["Area"].unique())

default_area = (
    "Serangoon"
    if "Serangoon" in area_options
    else area_options[0]
)

selected_area = st.selectbox(
    "Where would you like to visit?",
    options=area_options,
    index=area_options.index(default_area),
)

area_df = df[
    df["Area"] == selected_area
].copy()

area_centres = sorted(
    area_df["Hawker Centre"].unique()
)

st.caption(
    f"{len(area_centres)} hawker centres "
    f"found in {selected_area}."
)


# ==================================================
# KEEP ORIGINAL FILTERS
# ==================================================

st.subheader("Filter closures")

col1, col2 = st.columns(2)

with col1:
    selected_centres = st.multiselect(
        "Hawker centres",
        options=area_centres,
        default=area_centres,
    )

with col2:
    type_options = sorted(
        area_df["Closure Type"].unique()
    )

    selected_types = st.multiselect(
        "Closure type",
        options=type_options,
        default=type_options,
    )

area_dated = dated_df[
    dated_df["Area"] == selected_area
].copy()

if area_dated.empty:
    st.info("No dated closure records for this area.")
    st.stop()

min_date = area_dated["Start Date"].min().date()
max_date = area_dated["End Date"].max().date()

selected_dates = st.date_input(
    "Select date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

if len(selected_dates) != 2:
    st.info("Please select both dates.")
    st.stop()

filter_start = pd.Timestamp(selected_dates[0])
filter_end = pd.Timestamp(selected_dates[1])

filtered_df = dated_df[
    dated_df["Hawker Centre"].isin(selected_centres)
    & dated_df["Closure Type"].isin(selected_types)
    & (dated_df["Area"] == selected_area)
    & (dated_df["Start Date"] <= filter_end)
    & (dated_df["End Date"] >= filter_start)
].copy()

reviews = review_df[
    review_df["Area"].eq(selected_area)
    & review_df["Hawker Centre"].isin(selected_centres)
    & review_df["Closure Type"].isin(selected_types)
].copy()


# ==================================================
# KEEP ORIGINAL SUMMARY CARDS
# ==================================================

st.markdown(
    f"### Closure overview — {selected_area}"
)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Scheduled closure events",
        len(filtered_df)
    )

with col2:
    st.metric(
        "Hawker centres affected",
        filtered_df["Hawker Centre"].nunique()
    )

with col3:
    median_duration = (
        filtered_df["Duration"].median()
        if not filtered_df.empty
        else 0
    )

    st.metric(
        "Median closure duration",
        f"{median_duration:g} days"
    )

st.divider()


# ==================================================
# MONTHLY CLOSURE CALENDAR
# ==================================================

st.subheader("Closure calendar")

st.caption(
    "Choose a month to see scheduled closure days. "
    "Darker squares indicate more overlapping events."
)

available_months = pd.period_range(
    start=filter_start,
    end=filter_end,
    freq="M"
)

month_labels = [
    period.strftime("%B %Y")
    for period in available_months
]

current_period = pd.Timestamp.today().to_period("M")

default_month_index = (
    list(available_months).index(current_period)
    if current_period in available_months
    else 0
)

selected_month_label = st.selectbox(
    "Month to display",
    options=month_labels,
    index=default_month_index,
)

selected_index = month_labels.index(
    selected_month_label
)

selected_period = available_months[selected_index]

month_start = selected_period.start_time.normalize()
month_end = selected_period.end_time.normalize()

visible_start = max(month_start, filter_start)
visible_end = min(month_end, filter_end)

month_df = filtered_df[
    (filtered_df["Start Date"] <= visible_end)
    & (filtered_df["End Date"] >= visible_start)
].copy()

year = selected_period.year
month = selected_period.month

month_calendar = calendar.Calendar(
    firstweekday=0
).monthdatescalendar(year, month)

# Every calendar cell contains a count of
# closure events active on that day.
z_values = []
hover_values = []
day_labels = []

for week in month_calendar:

    z_row = []
    hover_row = []
    label_row = []

    for day in week:

        day_timestamp = pd.Timestamp(day)

        if (
            day.month != month
            or day_timestamp < visible_start
            or day_timestamp > visible_end
        ):
            z_row.append(None)
            hover_row.append("")
            label_row.append("")
            continue

        active = month_df[
            (month_df["Start Date"] <= day_timestamp)
            & (month_df["End Date"] >= day_timestamp)
        ]

        count = len(active)

        z_row.append(count)
        label_row.append(str(day.day))

        if count:
            centre_names = sorted(
                active["Hawker Centre"].unique()
            )

            details = "<br>".join(centre_names)

            hover_row.append(
                f"{day.strftime('%d %b %Y')}"
                f"<br>{count} scheduled event(s)"
                f"<br>{details}"
            )
        else:
            hover_row.append(
                f"{day.strftime('%d %b %Y')}"
                "<br>No recorded closure events"
            )

    z_values.append(z_row)
    hover_values.append(hover_row)
    day_labels.append(label_row)

max_count = max(
    [len(month_df), 1]
)

calendar_fig = go.Figure()

calendar_fig.add_trace(
    go.Heatmap(
        z=z_values,
        x=[
            "Mon", "Tue", "Wed", "Thu",
            "Fri", "Sat", "Sun"
        ],
        y=list(range(len(month_calendar))),
        text=day_labels,
        customdata=hover_values,
        texttemplate="%{text}",
        textfont=dict(
            size=15,
            color=TEXT
        ),
        colorscale=[
            [0.0, "#F0F2EA"],
            [0.001, "#F0F2EA"],
            [0.15, "#F8D7C6"],
            [0.6, "#F0A27D"],
            [1.0, ORANGE],
        ],
        zmin=0,
        zmax=max_count,
        showscale=False,
        xgap=6,
        ygap=6,
        hovertemplate="%{customdata}<extra></extra>",
    )
)

calendar_fig = style_chart(
    calendar_fig,
    height=90 * len(month_calendar) + 65
)

calendar_fig.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=10, r=10, t=20, b=10),
)

calendar_fig.update_xaxes(
    side="top",
    showgrid=False,
    showline=False,
    ticks="",
    tickfont=dict(
        color=MUTED,
        size=13
    ),
)

calendar_fig.update_yaxes(
    autorange="reversed",
    showticklabels=False,
    showgrid=False,
    showline=False,
    zeroline=False,
)

st.plotly_chart(
    calendar_fig,
    use_container_width=True,
    theme=None,
)

st.caption(
    "Colour intensity shows the number of "
    "scheduled events affecting each day, "
    "not the number of stalls closed."
)

st.divider()


# ==================================================
# CLOSURE DETAILS
# ==================================================

st.subheader("Scheduled closures")

st.caption(
    f"Closure details for {selected_month_label} "
    f"in {selected_area}."
)

if month_df.empty:
    st.info(
        "No dated closures are recorded for this "
        "month and your selected filters. "
        "This does not guarantee every stall is open."
    )

else:
    month_df = month_df.sort_values(
        ["Start Date", "Hawker Centre"]
    )

    for _, row in month_df.iterrows():

        centre = str(row["Hawker Centre"])
        closure_type = str(row["Closure Type"])

        start_date = row["Start Date"].strftime(
            "%d %B %Y"
        )

        end_date = row["End Date"].strftime(
            "%d %B %Y"
        )

        remarks = str(row["Remarks"]).strip()

        with st.container(border=True):

            left, right = st.columns([4, 1])

            with left:
                st.markdown(f"**{centre}**")

            with right:
                st.caption(closure_type)

            st.markdown(
                f"{start_date} – {end_date}"
            )

            if remarks and remarks.lower() not in [
                "nan", "nil", "none", "-"
            ]:
                with st.expander("Additional details"):
                    st.write(remarks)


# ==================================================
# ADDITIONAL YEARLY GRAPH
# ==================================================

st.divider()

with st.expander("Explore closure patterns"):

    st.markdown("#### Closures by month")

    st.caption(
        "Each event is counted in the month "
        "when it starts. The graph follows "
        "your area, centre, type, and date filters."
    )

    if filtered_df.empty:
        st.info("No data available for these filters.")

    else:
        monthly = filtered_df.copy()

        monthly["Month"] = (
            monthly["Start Date"]
            .dt.to_period("M")
            .dt.to_timestamp()
        )

        monthly_counts = (
            monthly.groupby(
                ["Month", "Closure Type"]
            )
            .size()
            .reset_index(name="Events")
        )

        monthly_fig = go.Figure()

        for closure_type, colour in [
            ("Cleaning", ORANGE),
            ("Other works", GREEN),
        ]:

            subset = monthly_counts[
                monthly_counts["Closure Type"]
                == closure_type
            ]

            if subset.empty:
                continue

            monthly_fig.add_trace(
                go.Bar(
                    x=subset["Month"],
                    y=subset["Events"],
                    name=closure_type,
                    marker_color=colour,
                    hovertemplate=(
                        "%{x|%b %Y}"
                        "<br>%{y} events"
                        "<extra></extra>"
                    ),
                )
            )

        monthly_fig = style_chart(
            monthly_fig,
            height=350
        )

        monthly_fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            barmode="stack",
            bargap=0.35,
            xaxis_title="",
            yaxis_title="Scheduled events",
            legend_title_text="Closure type",
        )

        monthly_fig.update_xaxes(
            tickformat="%b %Y"
        )

        st.plotly_chart(
            monthly_fig,
            use_container_width=True,
            theme=None,
        )


# ==================================================
# RECORDS NEEDING CONFIRMATION
# ==================================================

with st.expander(
    f"Dates requiring confirmation ({len(reviews)})"
):

    st.caption(
        "Some records have missing or uncertain "
        "dates. These are excluded from the graphs."
    )

    if reviews.empty:
        st.write(
            "No records require review "
            "for the selected centres and types."
        )

    else:
        for _, row in reviews.iterrows():

            st.markdown(
                f"**{row['Hawker Centre']}**"
            )

            st.caption(
                f"{row['Period']} / "
                f"{row['Closure Type']}"
            )

            remarks = str(
                row["Remarks"]
            ).strip()

            if remarks and remarks.lower() not in [
                "nan", "nil", "none", "-"
            ]:
                st.write(remarks)
            else:
                st.write(
                    "The date information "
                    "requires confirmation."
                )

            st.divider()


# ==================================================
# FOOTNOTE
# ==================================================

st.caption(
    "Schedules are based on the uploaded dataset. "
    "Some records may refer to partial closures. "
    "Please check official notices before visiting."
)
