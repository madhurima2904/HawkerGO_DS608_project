
from pathlib import Path

import pandas as pd


# ============================================================
# LOAD HAWKER CENTRE CLOSURE DATA
# ============================================================

def load_closure_data():
    """
    Load hawker-centre closure records.

    Convert quarterly cleaning schedules and
    other maintenance works into individual
    closure events.
    """

    project_root = Path(__file__).resolve().parent.parent

    processed_path = (
        project_root
        / "data"
        / "processed"
        / "DatesofHawkerCentresClosure.csv"
    )

    raw_path = (
        project_root
        / "data"
        / "raw"
        / "DatesofHawkerCentresClosure.csv"
    )

    # Find the dataset
    if processed_path.exists():
        csv_path = processed_path

    elif raw_path.exists():
        csv_path = raw_path

    else:
        raise FileNotFoundError(
            "Cannot find DatesofHawkerCentresClosure.csv "
            "in data/processed or data/raw."
        )

    df = pd.read_csv(csv_path)

    # ========================================================
    # VALIDATE COLUMNS
    # ========================================================

    required_columns = [
        "name",
        "q1_cleaningstartdate",
        "q1_cleaningenddate",
        "q2_cleaningstartdate",
        "q2_cleaningenddate",
        "q3_cleaningstartdate",
        "q3_cleaningenddate",
        "q4_cleaningstartdate",
        "q4_cleaningenddate",
        "other_works_startdate",
        "other_works_enddate",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing CSV columns: "
            + ", ".join(missing_columns)
        )

    df["name"] = (
        df["name"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    # ========================================================
    # DEFINE CLOSURE PERIODS
    # ========================================================

    periods = [
        (
            "Q1",
            "q1_cleaningstartdate",
            "q1_cleaningenddate",
            "remarks_q1",
            "Cleaning",
        ),
        (
            "Q2",
            "q2_cleaningstartdate",
            "q2_cleaningenddate",
            "remarks_q2",
            "Cleaning",
        ),
        (
            "Q3",
            "q3_cleaningstartdate",
            "q3_cleaningenddate",
            "remarks_q3",
            "Cleaning",
        ),
        (
            "Q4",
            "q4_cleaningstartdate",
            "q4_cleaningenddate",
            "remarks_q4",
            "Cleaning",
        ),
        (
            "Other works",
            "other_works_startdate",
            "other_works_enddate",
            "remarks_other_works",
            "Other works",
        ),
    ]

    events = []

    # ========================================================
    # PROCESS EACH HAWKER CENTRE
    # ========================================================

    for _, row in df.iterrows():

        centre = row["name"]

        if not centre:
            continue

        for (
            period,
            start_column,
            end_column,
            remarks_column,
            closure_type,
        ) in periods:

            start_raw = row[start_column]
            end_raw = row[end_column]

            remarks = str(
                row.get(remarks_column, "")
            ).strip()

            if remarks.lower() in [
                "nil",
                "nan",
                "none",
                "n/a",
                "-",
            ]:
                remarks = ""

            # Skip periods with no information
            if (
                pd.isna(start_raw)
                and pd.isna(end_raw)
                and not remarks
            ):
                continue

            # =================================================
            # CONVERT DATES
            # =================================================

            start_date = pd.to_datetime(
                start_raw,
                format="%d/%m/%Y",
                errors="coerce",
            )

            end_date = pd.to_datetime(
                end_raw,
                format="%d/%m/%Y",
                errors="coerce",
            )

            valid_dates = (
                pd.notna(start_date)
                and pd.notna(end_date)
                and end_date >= start_date
            )

            if valid_dates:

                duration = (
                    end_date - start_date
                ).days + 1

                schedule_status = "Dated"

            else:

                duration = None
                schedule_status = "Needs review"

            # =================================================
            # STORE CLOSURE EVENT
            # =================================================

            events.append(
                {
                    "Hawker Centre": centre,
                    "Period": period,
                    "Closure Type": closure_type,
                    "Start Date": start_date,
                    "End Date": end_date,
                    "Duration": duration,
                    "Remarks": remarks,
                    "Schedule Status": schedule_status,
                    "Address": row.get(
                        "address_myenv", ""
                    ),
                    "Latitude": row.get(
                        "latitude_hc", None
                    ),
                    "Longitude": row.get(
                        "longitude_hc", None
                    ),
                }
            )

    # ========================================================
    # CREATE EVENT DATAFRAME
    # ========================================================

    events_df = pd.DataFrame(events)

    if events_df.empty:
        return events_df

    events_df["Start Date"] = pd.to_datetime(
        events_df["Start Date"]
    )

    events_df["End Date"] = pd.to_datetime(
        events_df["End Date"]
    )

    events_df["Duration"] = pd.to_numeric(
        events_df["Duration"],
        errors="coerce",
    )

    return events_df


# ============================================================
# TEST DATA LOADING
# ============================================================

if __name__ == "__main__":

    events = load_closure_data()

    print("Total event records:", len(events))

    if not events.empty:

        dated_count = (
            events["Schedule Status"] == "Dated"
        ).sum()

        review_count = (
            events["Schedule Status"] == "Needs review"
        ).sum()

        print("Dated events:", dated_count)

        print(
            "Events needing review:",
            review_count,
        )

        print(events.head())
