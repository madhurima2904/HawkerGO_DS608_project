
"""HawkerGO Maintenance Calendar."""

import calendar
from html import escape

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.theme import apply_theme, render_hero
from src.wrangle import load_closure_data


apply_theme()


# ============================================================
# PAGE STYLING
# ============================================================

st.markdown(
    """
    <style>
    .hg-summary {
        background: linear-gradient(
            130deg, #FFFEFA 55%, #E9F3E4
        );
        border: 1px solid #E3E8D9;
        border-radius: 15px;
        padding: 16px 18px;
        min-height: 90px;
    }

    .hg-summary-label {
        color: #526359;
        font-size: 12px;
        font-weight: 600;
        margin-bottom: 6px;
    }

    .hg-summary-value {
        color: #103D2D;
        font: 700 28px Georgia, serif;
    }

    .hg-panel-title {
        color: #103D2D;
        font-size: 18px;
        font-weight: 750;
        margin-bottom: 5px;
    }

    .hg-help {
        color: #637369;
        font-size: 12px;
        line-height: 1.5;
        margin-bottom: 12px;
    }

    .hg-centre-group {
        margin: 16px 0 6px;
        color: #103D2D;
        font-size: 13px;
        font-weight: 800;
    }

    .hg-centre-group span {
        color: #718076;
        font-weight: 500;
    }

    .hg-period {
        padding: 12px 0;
        border-bottom: 1px solid #E8E9DE;
    }

    .hg-period:last-child {
        border-bottom: 0;
    }

    .hg-period-date {
        display: inline-block;
        background: #FCE4D6;
        color: #624332;
        border-radius: 9px;
        font-size: 11px;
        font-weight: 700;
        padding: 5px 9px;
        margin-bottom: 6px;
    }

    .hg-period-centre {
        color: #183A2B;
        font-size: 13px;
        font-weight: 700;
        line-height: 1.4;
    }

    .hg-period-type {
        color: #627269;
        font-size: 12px;
        margin-top: 3px;
    }

    .hg-data-note {
        margin-top: 17px;
        padding: 12px 15px;
        background: #F1F6ED;
        border: 1px solid #DFEADC;
        border-radius: 12px;
        color: #536B58;
        font-size: 12px;
        line-height: 1.5;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# AREA CLASSIFICATION
# ============================================================

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
        "bukit merah", "tiong bahru", "redhill",
        "alexandra", "telok blangah", "henderson",
        "beo crescent"
    ],
    "Bukit Panjang": ["bukit panjang"],
    "Central Area": [
        "maxwell", "amoy", "chinatown", "hong lim",
        "people's park", "tekka", "berseh",
        "golden mile", "newton", "market street",
        "tanjong pagar", "lavender"
    ],
    "Clementi": ["clementi", "west coast"],
    "Geylang": [
        "geylang", "aljunied", "old airport road",
        "sims"
    ],
    "Hougang": ["hougang", "kovan"],
    "Jurong East": ["jurong east", "yuhua", "teban"],
    "Jurong West": ["jurong west", "boon lay"],
    "Kallang": [
        "kallang", "whampoa", "bendemeer"
    ],
    "Marine Parade": [
        "marine parade", "marine terrace"
    ],
    "Pasir Ris": ["pasir ris"],
    "Punggol": ["punggol"],
    "Queenstown": [
        "queenstown", "commonwealth", "ghim moh",
        "holland drive", "tanglin halt", "mei ling"
    ],
    "Sembawang": ["sembawang"],
    "Sengkang": ["sengkang", "anchorvale"],
    "Serangoon": ["serangoon", "chomp chomp"],
    "Tampines": ["tampines"],
    "Toa Payoh": ["toa payoh"],
    "Woodlands": ["woodlands", "marsiling"],
    "Yishun": ["yishun", "chong pang"],
}


def area_for(row):
    name = str(row.get("Hawker Centre", "")).lower()
    address = str(row.get("Address", "")).lower()

    for text in (name, address):
        for area, keywords in AREA_KEYWORDS.items():
            if any(word in text for word in keywords):
                return area

    return "Other areas"


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data(show_spinner=False)
def get_data():
    return load_closure_data()


try:
    data = get_data().copy()

except (FileNotFoundError, ValueError) as exc:
    st.error(
        f"Could not load the closure dataset: {exc}"
    )
    st.stop()


if data.empty:
    st.info("No closure records are available.")
    st.stop()


data["Area"] = data.apply(area_for, axis=1)

dated = data[
    data["Schedule Status"].eq("Dated")
].copy()

needs_review = data[
    data["Schedule Status"].eq("Needs review")
].copy()


if dated.empty:
    st.info("No dated closure records are available.")
    st.stop()


# ============================================================
# ILLUSTRATED PAGE HEADING
# ============================================================

render_hero(
    "Maintenance Calendar",
    "Plan the makan.\nSkip the closure.",
    (
        "Explore recorded cleaning and maintenance "
        "closures across Singapore's hawker centres."
    ),
)


# ============================================================
# FILTERS
# ============================================================

area_col, centre_col, type_col, range_col = st.columns(
    [1.15, 2.1, 1.3, 1.6],
    gap="small",
    vertical_alignment="bottom",
)


areas = sorted(
    data["Area"].dropna().unique().tolist()
)


with area_col:
    area = st.selectbox(
        "Area",
        areas,
        index=(
            areas.index("Serangoon")
            if "Serangoon" in areas
            else 0
        ),
        key="simple_area",
    )


area_data = data[data["Area"].eq(area)]

centres = sorted(
    area_data["Hawker Centre"]
    .dropna()
    .unique()
    .tolist()
)


with centre_col:
    selected_centres = st.multiselect(
        "Hawker centres",
        centres,
        default=centres,
        key="simple_centres",
    )


closure_types = sorted(
    area_data["Closure Type"]
    .dropna()
    .unique()
    .tolist()
)


with type_col:
    selected_types = st.multiselect(
        "Closure type",
        closure_types,
        default=closure_types,
        key="simple_types",
    )


area_dated = dated[
    dated["Area"].eq(area)
]

range_data = (
    area_dated
    if not area_dated.empty
    else dated
)

first_date = range_data["Start Date"].min().date()
last_date = range_data["End Date"].max().date()


with range_col:
    chosen_range = st.date_input(
        "Date range",
        (first_date, last_date),
        min_value=first_date,
        max_value=last_date,
        key=f"simple_range_{area}",
    )


if (
    not isinstance(chosen_range, (tuple, list))
    or len(chosen_range) != 2
):
    st.info("Select both start and end dates.")
    st.stop()


start, end = map(pd.Timestamp, chosen_range)


# ============================================================
# FILTERED DATA FOR CALENDAR AND SUMMARY
# ============================================================

filtered = dated[
    dated["Area"].eq(area)
    & dated["Hawker Centre"].isin(selected_centres)
    & dated["Closure Type"].isin(selected_types)
    & dated["Start Date"].le(end)
    & dated["End Date"].ge(start)
].copy()


# ============================================================
# SUMMARY METRICS
# ============================================================

st.write("")

median = (
    filtered["Duration"].median()
    if not filtered.empty
    else None
)

summary = [
    (
        "Recorded closure events",
        str(len(filtered)),
    ),
    (
        "Centres affected",
        str(filtered["Hawker Centre"].nunique()),
    ),
    (
        "Median duration",
        (
            f"{median:g} days"
            if pd.notna(median)
            else "—"
        ),
    ),
]


for col, (label, value) in zip(
    st.columns(3, gap="medium"),
    summary,
):
    with col:
        st.markdown(
            '<div class="hg-summary">'
            f'<div class="hg-summary-label">{escape(label)}</div>'
            f'<div class="hg-summary-value">{escape(value)}</div>'
            '</div>',
            unsafe_allow_html=True,
        )


st.write("")


# ============================================================
# CALENDAR
# ============================================================

months = list(
    pd.period_range(
        start=start,
        end=end,
        freq="M",
    )
)

today = pd.Timestamp.today().to_period("M")


active_months = [
    month
    for month in months
    if not filtered.empty
    and (
        filtered["Start Date"].le(
            min(month.end_time.normalize(), end)
        )
        & filtered["End Date"].ge(
            max(month.start_time.normalize(), start)
        )
    ).any()
]


initial_month = (
    min(
        active_months,
        key=lambda month: abs(
            month.ordinal - today.ordinal
        ),
    )
    if active_months
    else (
        today
        if today in months
        else months[0]
    )
)


left, right = st.columns(
    [1.08, 0.92],
    gap="medium",
    vertical_alignment="top",
)


with left:
    with st.container(border=True):

        label_col, month_col = st.columns(
            [1.5, 1],
            vertical_alignment="bottom",
        )

        with label_col:
            st.markdown(
                '<div class="hg-panel-title">'
                'Closure calendar'
                '</div>',
                unsafe_allow_html=True,
            )

        with month_col:
            month = st.selectbox(
                "Month",
                months,
                index=months.index(initial_month),
                format_func=lambda m: m.strftime(
                    "%B %Y"
                ),
                key="simple_month",
            )

        st.markdown(
            '<p class="hg-help">'
            'Darker coral means more overlapping closures. '
            'Hover over a date to see its recorded event count.'
            '</p>',
            unsafe_allow_html=True,
        )

        visible_start = max(
            month.start_time.normalize(),
            start,
        )

        visible_end = min(
            month.end_time.normalize(),
            end,
        )

        weeks = calendar.Calendar(
            firstweekday=0
        ).monthdatescalendar(
            month.year,
            month.month,
        )

        day_labels = []
        values = []
        hover = []

        for week in weeks:
            row_days = []
            row_counts = []
            row_hover = []

            for day in week:
                when = pd.Timestamp(day)

                inside = (
                    day.month == month.month
                    and visible_start <= when <= visible_end
                )

                if inside:
                    count = int(
                        (
                            filtered["Start Date"].le(when)
                            & filtered["End Date"].ge(when)
                        ).sum()
                    )
                else:
                    count = None

                row_days.append(
                    str(day.day) if inside else ""
                )

                row_counts.append(count)

                row_hover.append(
                    day.strftime("%d %b %Y")
                    if inside
                    else ""
                )

            day_labels.append(row_days)
            values.append(row_counts)
            hover.append(row_hover)

        maximum = max(
            1,
            max(
                (
                    value
                    for row in values
                    for value in row
                    if value is not None
                ),
                default=0,
            ),
        )

        fig = go.Figure(
            go.Heatmap(
                x=[
                    "Mon", "Tue", "Wed", "Thu",
                    "Fri", "Sat", "Sun"
                ],
                y=list(range(len(weeks))),
                z=values,
                text=day_labels,
                customdata=hover,
                texttemplate="%{text}",
                textfont=dict(
                    size=13,
                    color="#203A2D",
                ),
                colorscale=[
                    [0, "#FFFEFA"],
                    [0.01, "#FFE7DA"],
                    [0.5, "#F8C2A7"],
                    [1, "#F08C6C"],
                ],
                zmin=0,
                zmax=maximum,
                xgap=4,
                ygap=4,
                showscale=False,
                hovertemplate=(
                    "%{customdata}<br>"
                    "%{z} closure event(s)"
                    "<extra></extra>"
                ),
            )
        )

        fig.update_layout(
            height=60 * len(weeks) + 68,
            margin=dict(
                l=0,
                r=0,
                t=24,
                b=0,
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            dragmode=False,
        )

        fig.update_xaxes(
            side="top",
            showgrid=False,
            ticks="",
            tickfont=dict(
                size=11,
                color="#405348",
            ),
            fixedrange=True,
        )

        fig.update_yaxes(
            visible=False,
            autorange="reversed",
            fixedrange=True,
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "displayModeBar": False
            },
        )

        st.caption(
            "No shaded dates do not guarantee "
            "that a centre is open."
        )


# ============================================================
# ALL CLOSURE PERIODS FOR SELECTED HAWKER CENTRES
# ============================================================

# IMPORTANT:
# These records are NOT restricted to the calendar month
# or selected date range.
#
# The area, selected centres, and closure-type filters
# still apply.


all_dated_periods = dated[
    dated["Area"].eq(area)
    & dated["Hawker Centre"].isin(selected_centres)
    & dated["Closure Type"].isin(selected_types)
].copy()


all_review_periods = needs_review[
    needs_review["Area"].eq(area)
    & needs_review["Hawker Centre"].isin(selected_centres)
    & needs_review["Closure Type"].isin(selected_types)
].copy()


def show_dated_event(event):
    start_text = event["Start Date"].strftime(
        "%d %b %Y"
    )

    end_text = event["End Date"].strftime(
        "%d %b %Y"
    )

    period = f"{start_text} – {end_text}"

    remarks = str(
        event.get("Remarks", "")
    ).strip()

    if remarks.lower() in (
        "nan", "none", "<na>"
    ):
        remarks = ""

    st.markdown(
        '<div class="hg-period">'
        f'<div class="hg-period-date">{escape(period)}</div>'
        f'<div class="hg-period-type">'
        f'{escape(str(event["Closure Type"]))}'
        '</div>'
        + (
            f'<div class="hg-period-type">'
            f'{escape(remarks)}'
            '</div>'
            if remarks
            else ""
        )
        + '</div>',
        unsafe_allow_html=True,
    )


def show_uncertain_event(event):
    period = str(
        event.get(
            "Period",
            "Date not confirmed",
        )
    ).strip()

    if period.lower() in (
        "", "nan", "none", "<na>"
    ):
        period = "Date not confirmed"

    st.markdown(
        '<div class="hg-period">'
        '<div class="hg-period-date">'
        'Date needs confirmation'
        '</div>'
        f'<div class="hg-period-type">'
        f'{escape(period)}'
        '</div>'
        f'<div class="hg-period-type">'
        f'{escape(str(event["Closure Type"]))}'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )


with right:
    with st.container(border=True):

        st.markdown(
            '<div class="hg-panel-title">'
            'Closure periods'
            '</div>',
            unsafe_allow_html=True,
        )

        period_count = (
            len(all_dated_periods)
            + len(all_review_periods)
        )

        st.markdown(
            '<p class="hg-help">'
            f'{period_count} recorded period(s) '
            'for the selected hawker centre(s). '
            'Showing all available dates, '
            'not just the selected month.'
            '</p>',
            unsafe_allow_html=True,
        )

        if not selected_centres:
            st.info(
                "Select at least one hawker centre "
                "to see its closure periods."
            )

        elif period_count == 0:
            st.info(
                "No recorded closure periods "
                "for these centres and closure types."
            )

        else:
            for centre_name in sorted(selected_centres):

                centre_dated = all_dated_periods[
                    all_dated_periods[
                        "Hawker Centre"
                    ].eq(centre_name)
                ].sort_values(
                    ["Start Date", "End Date"],
                    ascending=[False, False],
                )

                centre_review = all_review_periods[
                    all_review_periods[
                        "Hawker Centre"
                    ].eq(centre_name)
                ]

                centre_count = (
                    len(centre_dated)
                    + len(centre_review)
                )

                if centre_count == 0:
                    continue

                st.markdown(
                    '<div class="hg-centre-group">'
                    f'{escape(str(centre_name))} '
                    f'<span>({centre_count})</span>'
                    '</div>',
                    unsafe_allow_html=True,
                )

                for _, event in centre_dated.iterrows():
                    show_dated_event(event)

                for _, event in centre_review.iterrows():
                    show_uncertain_event(event)


# ============================================================
# DATA DISCLAIMER
# ============================================================

st.markdown(
    '<div class="hg-data-note">'
    '<strong>About the data.</strong> '
    'These are hawker-centre closure records, '
    'not live stall-level operating status. '
    'Area classification is approximate. '
    'Verify official dates before visiting.'
    '</div>',
    unsafe_allow_html=True,
)
