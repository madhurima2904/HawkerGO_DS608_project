"""Export Stall Insights and Closure charts to outputs/figures."""

from pathlib import Path
import sys
import textwrap


# ============================================================
# FIND PROJECT DIRECTORY
# ============================================================

def find_project_root():

    places = [
        Path(__file__).resolve().parent,
        Path.cwd().resolve(),
    ]

    for place in places:
        for folder in (place, *place.parents):

            if (folder / "data" / "processed" / "hawker_centres_final.csv").is_file():
                return folder

            if (folder / "data" / "raw" / "DatesofHawkerCentresClosure.csv").is_file():
                return folder

    raise FileNotFoundError(
        "Cannot find the HawkerGO data files. "
        "Make sure this script is inside your HawkerGO project."
    )


# ============================================================
# STALL INSIGHTS CHARTS
# ============================================================

def main():

    try:
        import matplotlib
        matplotlib.use("Agg")

        import matplotlib.pyplot as plt
        import numpy as np
        import pandas as pd

    except ImportError as exc:
        raise SystemExit(
            f"Missing Python package: {exc}\n"
            "Run: python3 -m pip install pandas matplotlib numpy"
        ) from exc

    root = find_project_root()

    csv_file = (
        root
        / "data"
        / "processed"
        / "hawker_centres_final.csv"
    )

    output = root / "outputs" / "figures"

    output.mkdir(
        parents=True,
        exist_ok=True,
    )

    print(f"Python: {sys.executable}")
    print(f"Reading: {csv_file}")

    df = pd.read_csv(csv_file)

    required = {
        "name",
        "no_of_food_stalls",
        "no_of_market_stalls",
    }

    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            f"Missing CSV columns: {sorted(missing)}"
        )

    df = df.dropna(subset=["name"]).copy()

    for col in [
        "no_of_food_stalls",
        "no_of_market_stalls",
    ]:
        df[col] = (
            pd.to_numeric(
                df[col],
                errors="coerce",
            )
            .fillna(0)
            .clip(lower=0)
        )

    df["total_stalls"] = (
        df["no_of_food_stalls"]
        + df["no_of_market_stalls"]
    )

    if df.empty or df["total_stalls"].sum() == 0:
        raise ValueError(
            "No valid stall-capacity data to plot."
        )

    CREAM = "#FFFEFA"
    FOREST = "#103D2D"
    GREEN = "#246C53"
    ORANGE = "#EDA36D"

    # ========================================================
    # SAVE HELPER
    # ========================================================

    def save(fig, filename):

        location = output / filename

        fig.savefig(
            location,
            dpi=200,
            bbox_inches="tight",
            facecolor=CREAM,
        )

        plt.close(fig)

        print(f"Saved: {location}")

    def style(ax):

        ax.set_facecolor(CREAM)

        ax.tick_params(
            length=0,
            colors=FOREST,
            labelsize=10,
        )

        for spine in ax.spines.values():
            spine.set_visible(False)

        ax.set_axisbelow(True)

    # ========================================================
    # FIGURE 1 — LARGEST HAWKER CENTRES
    # ========================================================

    top = (
        df.nlargest(10, "total_stalls")
        .sort_values("total_stalls")
    )

    fig, ax = plt.subplots(
        figsize=(12, 7.8),
        facecolor=CREAM,
    )

    style(ax)

    positions = np.arange(len(top))

    food = top["no_of_food_stalls"].to_numpy()
    market = top["no_of_market_stalls"].to_numpy()
    totals = top["total_stalls"].to_numpy()

    ax.barh(
        positions,
        food,
        color=GREEN,
        height=0.65,
        label="Food stalls",
    )

    ax.barh(
        positions,
        market,
        left=food,
        color=ORANGE,
        height=0.65,
        label="Market stalls",
    )

    labels = [
        "\n".join(
            textwrap.wrap(
                str(name),
                28,
                break_long_words=False,
            )
        )
        for name in top["name"]
    ]

    ax.set_yticks(positions, labels)

    maximum = max(float(max(totals)), 1)

    ax.set_xlim(0, maximum * 1.18)

    for i, count in enumerate(totals):
        ax.text(
            count + maximum * 0.012,
            i,
            f"{count:,.0f}",
            va="center",
            color=FOREST,
            fontsize=10,
        )

    ax.xaxis.grid(
        True,
        color="#E9E8DF",
    )

    ax.set_xlabel(
        "Number of stalls",
        color=FOREST,
    )

    ax.set_title(
        "Largest hawker centres",
        color=FOREST,
        fontsize=19,
        fontweight="bold",
        loc="left",
        pad=16,
    )

    ax.legend(
        frameon=False,
        ncol=2,
        loc="lower right",
        bbox_to_anchor=(1, -0.16),
    )

    fig.subplots_adjust(
        left=0.38,
        right=0.96,
        top=0.91,
        bottom=0.13,
    )

    save(
        fig,
        "stall_insights_largest_centres.png",
    )

    # ========================================================
    # FIGURE 2 — STALL MIX
    # ========================================================

    food_total = int(
        df["no_of_food_stalls"].sum()
    )

    market_total = int(
        df["no_of_market_stalls"].sum()
    )

    total = food_total + market_total

    fig, ax = plt.subplots(
        figsize=(8.5, 6.5),
        facecolor=CREAM,
    )

    ax.set_facecolor(CREAM)

    ax.pie(
        [food_total, market_total],
        startangle=90,
        colors=[GREEN, ORANGE],
        wedgeprops={
            "width": 0.31,
            "edgecolor": CREAM,
            "linewidth": 2,
        },
    )

    ax.text(
        0,
        0.08,
        f"{total:,}",
        ha="center",
        va="center",
        color=FOREST,
        fontsize=24,
        fontweight="bold",
    )

    ax.text(
        0,
        -0.19,
        "total stalls",
        ha="center",
        fontsize=11,
        color=FOREST,
    )

    ax.legend(
        [
            f"Food stalls: {food_total:,} ({food_total/total:.0%})",
            f"Market stalls: {market_total:,} ({market_total/total:.0%})",
        ],
        loc="lower center",
        bbox_to_anchor=(0.5, -0.15),
        ncol=1,
        frameon=False,
    )

    ax.set_title(
        "Stall mix across Singapore",
        color=FOREST,
        fontsize=19,
        fontweight="bold",
        pad=22,
    )

    save(
        fig,
        "stall_insights_stall_mix.png",
    )

    # ========================================================
    # FIGURE 3 — FOOD VS MARKET STALLS
    # ========================================================

    fig, ax = plt.subplots(
        figsize=(10, 7),
        facecolor=CREAM,
    )

    style(ax)

    food = df["no_of_food_stalls"]
    market = df["no_of_market_stalls"]

    profiles = [
        (
            "Wet-market heavy",
            market > food,
            GREEN,
        ),
        (
            "Food-court style",
            food > market,
            ORANGE,
        ),
        (
            "Balanced",
            food == market,
            "#9CAFA1",
        ),
    ]

    for label, mask, colour in profiles:

        if mask.any():

            ax.scatter(
                food[mask],
                market[mask],
                s=45,
                color=colour,
                alpha=0.8,
                label=label,
                edgecolors=CREAM,
                linewidth=0.5,
            )

    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)

    ax.set_xlabel(
        "Food stalls",
        color=FOREST,
    )

    ax.set_ylabel(
        "Market stalls",
        color=FOREST,
    )

    ax.grid(
        True,
        color="#E9E8DF",
        linewidth=0.8,
    )

    ax.set_title(
        "Food stalls vs. market stalls",
        color=FOREST,
        fontsize=19,
        fontweight="bold",
        loc="left",
        pad=20,
    )

    ax.legend(
        frameon=False,
        fontsize=9,
    )

    save(
        fig,
        "stall_insights_food_vs_market.png",
    )

    print("\nSUCCESS: All 3 stall figures exported to:")
    print(output)

    # Closure charts run after the stall charts
    export_closure_charts(root)


# ============================================================
# CLOSURE CHARTS
# ============================================================

def export_closure_charts(root):

    import calendar
    import matplotlib.pyplot as plt
    import pandas as pd

    csv_file = root / "data" / "raw" / "DatesofHawkerCentresClosure.csv"
    output = root / "outputs" / "figures"
    output.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(csv_file)

    CREAM = "#FFFEFA"
    FOREST = "#103D2D"
    GREEN = "#246C53"
    ORANGE = "#EDA36D"
    LIGHT = "#9CAFA1"

    # ========================================================
    # PARSE DATES ("nil" and blanks become NaT)
    # ========================================================

    def parse(series):
        return pd.to_datetime(
            series,
            format="%d/%m/%Y",
            errors="coerce",
        )

    # Long table: one row per scheduled quarterly closure
    records = []

    for q in ["q1", "q2", "q3", "q4"]:

        start = parse(df[f"{q}_cleaningstartdate"])
        end = parse(df[f"{q}_cleaningenddate"])

        for s, e in zip(start, end):

            if pd.notna(s) and pd.notna(e):
                records.append({
                    "quarter": q.upper(),
                    "start": s,
                    "days": (e - s).days + 1,
                })

    closures = pd.DataFrame(records)

    # Other works (repairs, redecoration, etc.)
    other = pd.DataFrame({
        "start": parse(df["other_works_startdate"]),
        "end": parse(df["other_works_enddate"]),
    }).dropna(subset=["start"])

    other["days"] = (other["end"] - other["start"]).dt.days + 1

    # ========================================================
    # SAVE AND STYLE HELPERS
    # ========================================================

    def save(fig, filename):

        location = output / filename

        fig.savefig(
            location,
            dpi=200,
            bbox_inches="tight",
            facecolor=CREAM,
        )

        plt.close(fig)

        print(f"Saved: {location}")

    def style(ax):

        ax.set_facecolor(CREAM)

        ax.tick_params(
            length=0,
            colors=FOREST,
            labelsize=10,
        )

        for spine in ax.spines.values():
            spine.set_visible(False)

        ax.set_axisbelow(True)

    month_labels = [calendar.month_abbr[m] for m in range(1, 13)]

    # ========================================================
    # FIGURE 1 — CLOSURES CLUSTER AT QUARTER END
    # ========================================================

    monthly = (
        closures["start"]
        .dt.month
        .value_counts()
        .reindex(range(1, 13), fill_value=0)
    )

    # Quarter-end months: March, June, September, December
    colours = [
        GREEN if m in (3, 6, 9, 12) else LIGHT
        for m in range(1, 13)
    ]

    fig, ax = plt.subplots(
        figsize=(11, 6.5),
        facecolor=CREAM,
    )

    style(ax)

    bars = ax.bar(
        month_labels,
        monthly.values,
        color=colours,
        width=0.7,
    )

    for bar, value in zip(bars, monthly.values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            value + 1,
            f"{value}",
            ha="center",
            va="bottom",
            color=FOREST,
            fontsize=10,
        )

    ax.yaxis.grid(True, color="#E9E8DF")

    ax.set_ylabel(
        "Scheduled quarterly closures",
        color=FOREST,
    )

    ax.set_title(
        "Closures cluster at the end of each quarter",
        color=FOREST,
        fontsize=19,
        fontweight="bold",
        loc="left",
        pad=16,
    )

    save(
        fig,
        "closure_monthly_clustering.png",
    )

    # ========================================================
    # FIGURE 2 — CLOSURE LENGTH (MEDIAN AND MEAN)
    # ========================================================

    length = (
        closures
        .groupby("quarter")["days"]
        .agg(["median", "mean"])
        .reindex(["Q1", "Q2", "Q3", "Q4"])
    )

    fig, ax = plt.subplots(
        figsize=(9, 6.5),
        facecolor=CREAM,
    )

    style(ax)

    x = range(len(length))

    ax.bar(
        x,
        length["median"],
        color=GREEN,
        width=0.6,
        label="Median",
    )

    ax.scatter(
        x,
        length["mean"],
        color=ORANGE,
        s=90,
        zorder=3,
        label="Mean",
    )

    for i, (med, avg) in enumerate(
        zip(length["median"], length["mean"])
    ):
        ax.text(
            i,
            max(med, avg) + 0.12,
            f"median {med:.0f}\nmean {avg:.1f}",
            ha="center",
            va="bottom",
            color=FOREST,
            fontsize=9,
        )

    ax.set_xticks(list(x), length.index)

    ax.set_ylim(0, length.values.max() + 1.2)

    ax.yaxis.grid(True, color="#E9E8DF")

    ax.set_ylabel(
        "Closure length (days)",
        color=FOREST,
    )

    ax.set_title(
        "Closures are short, and slightly longer in Q4",
        color=FOREST,
        fontsize=19,
        fontweight="bold",
        loc="left",
        pad=16,
    )

    ax.legend(frameon=False)

    save(
        fig,
        "closure_length_by_quarter.png",
    )

    # ========================================================
    # FIGURE 3 — OTHER WORKS BY START MONTH
    # ========================================================

    other_monthly = (
        other["start"]
        .dt.month
        .value_counts()
        .reindex(range(1, 13), fill_value=0)
    )

    fig, ax = plt.subplots(
        figsize=(11, 6.5),
        facecolor=CREAM,
    )

    style(ax)

    bars = ax.bar(
        month_labels,
        other_monthly.values,
        color=ORANGE,
        width=0.7,
    )

    for bar, value in zip(bars, other_monthly.values):
        if value:
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                value + 0.2,
                f"{value}",
                ha="center",
                va="bottom",
                color=FOREST,
                fontsize=10,
            )

    ax.yaxis.grid(True, color="#E9E8DF")

    ax.set_ylabel(
        "Centres with other works",
        color=FOREST,
    )

    ax.set_title(
        f"Other works: {len(other)} scheduled events, "
        f"median {other['days'].median():.0f} days",
        color=FOREST,
        fontsize=19,
        fontweight="bold",
        loc="left",
        pad=16,
    )

    save(
        fig,
        "other_works_by_month.png",
    )

    print("\nSUCCESS: All 3 closure figures exported to:")
    print(output)


if __name__ == "__main__":
    main()