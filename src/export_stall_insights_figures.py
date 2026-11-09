
"""Export Stall Insights charts to outputs/figures."""

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

            data_file = (
                folder
                / "data"
                / "processed"
                / "hawker_centres_final.csv"
            )

            if data_file.is_file():
                return folder

    raise FileNotFoundError(
        "Cannot find hawker_centres_final.csv. "
        "Make sure this script is inside your HawkerGO project."
    )


# ============================================================
# MAIN EXPORT FUNCTION
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

    print("\nSUCCESS: All 3 figures exported to:")
    print(output)


if __name__ == "__main__":
    main()
