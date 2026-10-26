from datetime import date                 # date: gives today's date for the date picker's default
from pathlib import Path                  # Path: builds file paths relative to this script
import numpy as np                        # NumPy: used for labelling rows with np.select
import pandas as pd                       # Pandas: data handling
import streamlit as st                    # Streamlit: the web app framework
import plotly.express as px               # Plotly Express: quick interactive map
import plotly.graph_objects as go         # Plotly graph objects: lets us add the highlight ring and MRT marker

st.set_page_config(page_title="Hawker Downtime", layout="wide")  # tab title + full-width layout (must be the first Streamlit call)

ROOT = Path(__file__).resolve().parents[1]          # project root (pages/ -> project/)
PROCESSED = ROOT / "data" / "processed"
DATA_FILE = PROCESSED / "hawker_centres_final.csv"
WALK_FILE = PROCESSED / "hc_walk_distances.csv"                # EDIT if your file in data-processed has a different name
PAIRS = [                                                  # (start, end) date columns for every closure type
    ("q1_cleaningstartdate", "q1_cleaningenddate"),        # Q1 cleaning
    ("q2_cleaningstartdate", "q2_cleaningenddate"),        # Q2 cleaning
    ("q3_cleaningstartdate", "q3_cleaningenddate"),        # Q3 cleaning
    ("q4_cleaningstartdate", "q4_cleaningenddate"),        # Q4 cleaning
    ("other_works_startdate", "other_works_enddate"),      # R&R / other works
]
CLEAN_PAIRS = PAIRS[:4]                   # just the four quarterly cleanings (for "Next cleaning")
WORKS_START, WORKS_END = PAIRS[4]         # the R&R / other works columns
MRT_NAME_COL = "STATION_NA"              # EDIT: column with the nearest MRT station name
MRT_EXIT_COL = "EXIT_CODE"                # column with the MRT exit code
MRT_DIST_COL = "walk_dist_m"           # EDIT: column with distance to that MRT in metres
MIN_COL = "walk_min"                      # column with walking minutes (already computed in your dataset)
MRT_LAT_COL = "mrt_lat"                   # EDIT: column with the MRT exit's latitude (needed to draw it on the map)
MRT_LON_COL = "mrt_lon"                   # EDIT: column with the MRT exit's longitude
COLOURS = {                               # status label -> map colour (visible on light and dark backgrounds)
    "Open today": "#2e9e63",              # green
    "Closed today": "#e5533d",            # red
    "Closing within 7 days": "#e0a21a",   # yellow
}

try:                                      # tries to read the active Streamlit theme (needs Streamlit 1.46+)
    DARK = st.context.theme.type == "dark"  # True when the app is in dark mode
except Exception:                         # older Streamlit versions don't have this
    DARK = False                          # falls back to light mode
MAP_STYLE = "carto-darkmatter" if DARK else "carto-positron"  # dark map tiles in dark mode, light tiles otherwise
INK = "#f2f2f2" if DARK else "#1c2b27"    # text colour used on the map (light text on dark tiles)
MRT_COLOUR = "#4da3ff" if DARK else "#1f5fbf"  # MRT marker/line colour, readable on either map

@st.cache_data                            # caches the loaded data so it isn't re-read on every click
def load_data():                          # loads and tidies the dataset
    df = pd.read_csv(DATA_FILE)                # reads the CSV
    for s, e in PAIRS:                    # loops over every start/end column pair
        df[s] = pd.to_datetime(df[s], errors="coerce").astype("datetime64[ns]")  # text -> dates (bad values become blank)
        df[e] = pd.to_datetime(df[e], errors="coerce").astype("datetime64[ns]")  # same for the end date
    for c in (MRT_DIST_COL, MIN_COL, MRT_LAT_COL, MRT_LON_COL):  # numeric MRT columns
        if c in df.columns:               # only if the column exists
            df[c] = pd.to_numeric(df[c], errors="coerce")  # makes sure they are numbers (bad values become blank)
    df = df.dropna(subset=["latitude_hc", "longitude_hc"]).reset_index(drop=True)  # drops rows with no coordinates
    df[["no_of_food_stalls", "no_of_market_stalls"]] = df[["no_of_food_stalls", "no_of_market_stalls"]].fillna(0)  # blank stall counts -> 0
    return df                             # hands back the tidy DataFrame

@st.cache_data                            # caches the table so it loads once
def load_walk_matrix():                   # loads the precomputed walking distances between centres                            # loads the precomputed walking distances
    path = WALK_FILE
    if not path.exists():                           # if the file hasn't been generated yet
        return None                                 # signals "no data" instead of crashing
    return pd.read_csv(path, index_col=0)           # rows and columns keyed by centre

def closed_between(df, a, b):             # True for centres with any closure overlapping the dates a..b
    hit = pd.Series(False, index=df.index)            # starts with everyone "not closed"
    for s, e in PAIRS:                                # checks every closure type
        hit |= (df[s] <= b) & (df[e] >= a)            # overlap test: starts before b AND ends after a
    return hit                                        # returns the True/False column

def next_window(df, pairs, today):        # finds each centre's next upcoming (start, end) after today
    nxt_s = pd.Series(pd.NaT, index=df.index, dtype="datetime64[ns]")  # next start, blank to begin with
    nxt_e = pd.Series(pd.NaT, index=df.index, dtype="datetime64[ns]")  # matching end date
    for s, e in pairs:                                # loops over the given closure types
        better = (df[s] > today) & (nxt_s.isna() | (df[s] < nxt_s))    # upcoming AND earlier than what we have so far
        nxt_s = nxt_s.where(~better, df[s])           # where "better", replace with this start
        nxt_e = nxt_e.where(~better, df[e])           # and the matching end
    return nxt_s, nxt_e                               # returns both columns

def add_status(df, today):                # adds all the status columns for the chosen date
    df = df.copy()                                    # works on a copy so the cached data isn't changed
    df["closed_today"] = closed_between(df, today, today)                          # closed on the chosen date
    df["closed_week"] = closed_between(df, today, today + pd.Timedelta(days=6))    # any closure in the next 7 days (incl. today)
    df["closing_soon"] = df["closed_week"] & ~df["closed_today"]                   # yellow: open today but closing within 7 days
    df["status"] = np.select(                         # picks one label per row
        [df["closed_today"], df["closing_soon"]],     # conditions, checked in order
        ["Closed today", "Closing within 7 days"],    # labels for those conditions
        default="Open today",                         # everyone else is open
    )
    reopen = pd.Series(pd.NaT, index=df.index, dtype="datetime64[ns]")  # reopening date, blank to begin with
    for s, e in PAIRS:                                # loops over closure types
        inside = (df[s] <= today) & (today <= df[e])  # centres currently inside this closure window
        reopen = reopen.where(~inside, df[e] + pd.Timedelta(days=1))  # reopening = day after the window ends
    df["reopen"] = reopen                             # saves the reopening date
    df["next_clean_start"], df["next_clean_end"] = next_window(df, CLEAN_PAIRS, today)  # next cleaning dates
    return df                                         # returns the enriched DataFrame

def fmt(d):                               # formats a date for display
    return "-" if pd.isna(d) else d.strftime("%d %b %Y")  # blank dates show a dash

def kpi(col, label, value, colour=None):  # draws one KPI card in a given column
    style = f"color:{colour};" if colour else ""      # only sets a colour when given, so the theme's text colour is used otherwise
    with col.container(border=True):                  # bordered card
        st.caption(label)                             # small label
        st.markdown(f"<span style='font-size:2.2rem;font-weight:600;{style}'>{value:,}</span>",
                    unsafe_allow_html=True)           # big number with thousands separator

# ---------- load data and check which optional columns exist ----------
base = load_data()                                    # loads the cleaned dataset
HAS_MRT = {MRT_NAME_COL, MRT_EXIT_COL, MRT_DIST_COL, MIN_COL} <= set(base.columns)  # True only if all MRT info columns exist
HAS_MRT_XY = HAS_MRT and {MRT_LAT_COL, MRT_LON_COL} <= set(base.columns)  # True if MRT coordinates also exist (needed for the map)

# ---------- header ----------
st.markdown("<h1 style='color:#e5533d;margin-bottom:0'>Hawker Downtime</h1>", unsafe_allow_html=True)  # red title
date_line = st.empty()                                # empty slot for the date line, filled in once the date is chosen

# ---------- filter bar (horizontal, at the top) ----------
bar = st.container(border=True)                       # bordered box holding all filters
f1, f2, f3, f4 = bar.columns([1, 1.3, 1.5, 2])        # four side-by-side columns
today = pd.Timestamp(f1.date_input("Date", value=date.today()))  # date picker (the only non-dropdown)
df = add_status(base, today)                          # computes statuses for that date

mrt_options = ["All"] + (sorted(df[MRT_NAME_COL].dropna().unique()) if HAS_MRT else [])  # dropdown options: All + every station
mrt_pick = f2.selectbox("MRT station", mrt_options, disabled=not HAS_MRT)  # MRT dropdown (disabled if no MRT data)
status_filter = f3.multiselect("Status", list(COLOURS), default=list(COLOURS))  # status dropdown (pick one or more)

pool = df if mrt_pick == "All" else df[df[MRT_NAME_COL] == mrt_pick]  # centres matching the MRT choice
chosen = f4.selectbox("Selected hawker centre", sorted(pool["name"]))  # centre dropdown, limited to the chosen MRT's centres

view = pool[pool["status"].isin(status_filter)]       # centres shown on the map: MRT filter + status filter
row = df.loc[df["name"] == chosen].iloc[0]            # the selected centre's row

date_line.caption(f"{today.strftime('%A %d %B %Y')} · NEA-managed hawker centres")  # fills the date line under the title
st.subheader("1 · Live operational status")           # section heading

# ---------- KPI cards ----------
c1, c2, c3, c4 = st.columns(4)                        # four equal columns
kpi(c1, "Total hawker centres", len(pool))            # number of centres (respects the MRT filter)
kpi(c2, "Total food stalls", int(pool["no_of_food_stalls"].sum()))  # sum of food stalls
kpi(c3, "Closed today", int(pool["closed_today"].sum()), "#e5533d")  # closed on the chosen date (red)
kpi(c4, "Closed this week", int(pool["closed_week"].sum()), "#e0a21a")  # closure in the next 7 days (amber)

# ---------- map (left) and detail cards (right) ----------
left, right = st.columns([3, 2])                      # map gets 60% width, cards 40%

with left.container(border=True):                     # bordered map card
    st.markdown("**Status map**")                     # card title
    if view.empty:                                    # if the filters leave nothing to show
        st.info("No hawker centres match these filters.")  # friendly message instead of an error
    else:
        hover = {}                                    # which columns appear in the hover box
        if HAS_MRT:                                   # only if MRT info exists
            hover[MRT_NAME_COL] = True                # show MRT station
        hover.update({"no_of_food_stalls": True,      # show number of food stalls
                      "no_of_market_stalls": True,    # show number of market stalls
                      "latitude_hc": False,           # hide latitude
                      "longitude_hc": False})         # hide longitude
        fig = px.scatter_map(                         # one dot per centre
            view,                                     # filtered data
            lat="latitude_hc", lon="longitude_hc",    # coordinate columns
            color="status",                           # colour by status label
            color_discrete_map=COLOURS,               # fixed colours from the legend
            category_orders={"status": list(COLOURS)},  # keeps legend order consistent
            hover_name="name",                        # centre name as the hover title
            hover_data=hover,                         # extra hover fields chosen above
            labels={MRT_NAME_COL: "MRT station", "no_of_food_stalls": "Food stalls",
                    "no_of_market_stalls": "Market stalls", "status": "Status"},  # friendly hover labels
            center={"lat": 1.3521, "lon": 103.8198},  # centre the map on Singapore
            zoom=10.5,                                # city-wide zoom
            height=560,                               # map height in pixels
        )
        fig.add_trace(go.Scattermap(                  # translucent ring under the selected centre
            lat=[row["latitude_hc"]], lon=[row["longitude_hc"]],  # its coordinates
            mode="markers",                           # draw as a marker
            marker=dict(size=26, color="#e5533d", opacity=0.35),  # large, faint red circle
            name="Selected", hoverinfo="skip",        # legend name; no hover box
        ))
        if HAS_MRT_XY and pd.notna(row[MRT_LAT_COL]) and pd.notna(row[MRT_LON_COL]):  # if the centre's MRT has coordinates
            ex = row[MRT_EXIT_COL]                    # the exit code
            mrt_label = f"{row[MRT_NAME_COL]}" + (f" (Exit {ex})" if pd.notna(ex) else "")  # label: station + exit
            fig.add_trace(go.Scattermap(              # line from the centre to its MRT
                lat=[row["latitude_hc"], row[MRT_LAT_COL]],  # both latitudes
                lon=[row["longitude_hc"], row[MRT_LON_COL]],  # both longitudes
                mode="lines", line=dict(width=2, color=MRT_COLOUR),  # thin line in the MRT colour
                hoverinfo="skip", showlegend=False,   # no hover box, no legend entry
            ))
            fig.add_trace(go.Scattermap(              # the MRT marker itself
                lat=[row[MRT_LAT_COL]], lon=[row[MRT_LON_COL]],  # MRT coordinates
                mode="markers+text",                  # marker plus a text label
                marker=dict(size=14, color=MRT_COLOUR),  # solid blue dot
                text=[mrt_label], textposition="top right",  # label placed beside the dot
                textfont=dict(color=INK, size=12),    # label colour follows light/dark mode
                name="MRT station", hoverinfo="text", # legend name; hover shows the label
            ))
        fig.update_layout(map_style=MAP_STYLE,        # light or dark map tiles
                          margin=dict(l=0, r=0, t=0, b=0),  # trims margins
                          legend=dict(orientation="h", y=-0.03))  # legend below the map
        st.plotly_chart(fig)                          # shows the map (Streamlit adapts text colours to the theme)

with right:                                           # right-hand column
    with st.container(border=True):                   # selected centre card
        st.subheader(row["name"])                     # centre name
        st.caption(row["address_myenv"])              # address
        label = f"Closed today · reopens {fmt(row['reopen'])}" if row["closed_today"] else row["status"]  # pill text
        pill_text = "#1c2b27" if row["status"] == "Closing within 7 days" else "white"  # dark text on yellow, white on the others
        st.markdown(f"<span style='background:{COLOURS[row['status']]};color:{pill_text};padding:3px 12px;"
                    f"border-radius:12px;font-size:0.85rem'>{label}</span>", unsafe_allow_html=True)  # coloured status pill
        st.write(f"**Next cleaning:** {fmt(row['next_clean_start'])} to {fmt(row['next_clean_end'])}")  # next cleaning window
        has_works = pd.notna(row[WORKS_START]) or pd.notna(row[WORKS_END])  # any R&R dates recorded?
        st.write("**R&R works:** " + (f"{fmt(row[WORKS_START])} to {fmt(row[WORKS_END])}" if has_works else "None"))  # R&R dates or "None"
        if HAS_MRT:                                   # only if MRT columns exist
            ex = row[MRT_EXIT_COL]                    # the exit code
            ex_txt = f" ({ex})" if pd.notna(ex) else ""  # "(Exit A)" or nothing if blank
            st.write(f"**Nearest MRT:** {row[MRT_NAME_COL]}{ex_txt} · {row[MIN_COL]:.0f} min walk ({row[MRT_DIST_COL]:.0f} m)")  # uses walk_min straight from the dataset
        else:
            st.write("**Nearest MRT:** not in dataset yet")  # placeholder when no MRT data
        food, market = int(row["no_of_food_stalls"]), int(row["no_of_market_stalls"])  # stall counts
        st.write(f"**Stalls:** {food} food · {market} market · {food + market} total")  # stall breakdown

    with st.container(border=True):                   # alternative stall finder card
        st.subheader("Alternative stall finder")      # card title
        st.caption("Nearest open centres to your closed favourite")  # card subtitle
        walk = load_walk_matrix()                     # loads the walking-distance table (or None)
        if walk is None:                              # file not generated yet
            st.warning("Walking-distance file not found. Run precompute_walk.py first.")  # tells you what to do
        elif chosen not in walk.index:                # selected centre missing from the table
            st.warning("No walking distances for this centre. Re-run precompute_walk.py.")  # tells you what to do
        else:
            df["dist_m"] = df["name"].map(walk.loc[chosen])  # walking distance from the selected centre to every other centre
            alts = df[(~df["closed_today"]) & (df["name"] != chosen)].nsmallest(3, "dist_m")  # 3 closest open centres
            for _, a in alts.iterrows():              # loops over those 3
                n_col, d_col = st.columns([4, 1])     # name on the left, distance on the right
                n_col.markdown(f"**{a['name']}**")    # centre name
                trip_min = max(1, round(a["dist_m"] / 80))  # walking time at about 80 m per minute
                n_col.caption(f"{trip_min} min walk" + (f" · Nearest MRT: {a[MRT_NAME_COL]}" if HAS_MRT else ""))  # walk time + its MRT
                d_col.markdown(f"**{a['dist_m'] / 1000:.1f} km**")  # distance in km, 1 decimal place