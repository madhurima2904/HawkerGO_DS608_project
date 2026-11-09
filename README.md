# HawkerGo — Singapore Hawker Centre Explorer

**DS608 Data Analytics for Economics | MDSE Group Project (2026)**

**Group members:** Madhurima Subramaniam Rudra, Nicolyne Tiana Lie, and Toh En Hui.

**Project repository:** https://github.com/madhurima2904/HawkerGO_DS608_project

## Motivation and Background

Hawker centres are an essential part of daily life in Singapore. However, scheduled cleaning and closures inconvenience visitors. Our project turns publicly available closure data into an interactive dashboard that helps users plan trips and locate nearby alternatives

## Research Question

How can public hawker centre closure data be transformed into an interactive dashboard to help residents plan visits and identify nearby dining alternatives?

## Project Objectives

- Help users discover hawker centres and explore nearby alternatives.
- Provide information about scheduled hawker centre closures.
- Filter closure schedules by area, hawker centre, closure type, and date.
- Visualise the distribution of food and market stalls across hawker centres.
- Identify peak maintenance periods and high-concentration windows.
- Analyse patterns in closure frequencies, durations, and timings.


## Dashboard Features

### Explore Hawkers 

Explore hawker centres and identify nearby dining alternatives using location-based information.
- Interactive map
- Alternate stall finder
- Filter by date, MRT station, status, or Hawker centre.

### Maintenance Calendar 

- Area and hawker centre selection
- Closure type and date filters
- Summary statistics for scheduled closures
- Monthly closure calendar and detailed closure information
- Visualisation of closure patterns

### Stall Insights 

- Top 10 largest hawker centres by total stalls
- Comparison of food stalls and market stalls
- Scatter plot of stall types
- Interactive charts and summary tables

## Data Sources

The project uses publicly available Singapore datasets, including:

- Primary Dataset: NEA Hawker Centre Closing Data - https://data.gov.sg/datasets/d_bda4baa634dd1cc7a6c7cad5f19e2d68/view
- Supplementary Dataset 1: Hawker Centres (GEOJSON) - https://data.gov.sg/datasets/d_4a086da0a5553be1d89383cd90d07ecd/view
- Supplementary Dataset 2: LTA MRT Station Exit (GEOJSON) - https://data.gov.sg/datasets/d_b39d3a0871985372d7e1637193335da5/view
- Geofabrik Map of Singapore: https://download.geofabrik.de/asia/malaysia-singapore-brunei.html (not added to git as file size exceeds limit)
  
_Source: data.gov.sg_

## Repository Structure

```
HawkerGO_DS608_project/
├── app.py                      # Entry point: page config, theme, navigation
├── pages/
│   ├── 1_Explore_Hawkers.py
│   ├── 2_Maintenance_Calendar.py
│   └── 3_Stall_Insights.py
├── src/
│   └── theme.py                # Custom styling
├── data/
│   ├── raw/                    # Original data.gov.sg files
│   └── processed/              # Cleaned data (e.g. hc_final.csv)
├── outputs/
├── requirements.txt
└── README.md
```

## Setup and Execution Instructions

1. Download the Singapore map from https://download.geofabrik.de/asia/malaysia-singapore-brunei.html as "malaysia-singapore-brunei-261018.osm.pbf"

2. Clone the repository:

```bash
git clone https://github.com/madhurima2904/HawkerGO_DS608_project.git
cd HawkerGO_DS608_project
```

3. Install dependencies and launch the dashboard:

```bash
python3 -m pip install -r requirements.txt
python3 -m streamlit run app.py
```

Open the local URL displayed by Streamlit (usually `http://localhost:8501`). Required processed datasets must be available under `data/processed/`.

## Summary of Analytical Approach

1. **Data collection:** Obtain public hawker centre, closure, and geographical datasets.
2. **Data cleaning:** Check missing values, inconsistent formats, and data quality.
3. **Merge Datasets** Merge the hawker centre data to the MRT data to find the nearest MRT station and Exit.
4. **Data transformation:** Convert closure schedules into structured records.
5. **Feature engineering:** Calculate closure durations and total stall counts.
6. **Exploratory analysis:** Examine closure patterns and differences between centres.
7. **Data visualisation:** Create interactive charts, maps, filters, and calendars.
8. **Dashboard development:** Integrate analyses into a multipage Streamlit app.

## Technologies Used

Python, Pandas, Streamlit, Plotly, Git, and GitHub.


## Key Limitations

- Closure schedules may change after publication.
- Some records have missing or unconfirmed dates.
- Scheduled closures may affect only part of a hawker centre.
- Nearby alternatives depend on geographical data quality.
- The dashboard does not confirm real-time operating status.

## Project Team

| Group Member | Main Responsibility |
|---|---|
| Madhu | Explore Hawkers |
| Nicolyne Tiana Lie | Maintenance Calendar |
| Enhui | Stall Insights |

This is collaborative group work for DS608 Data Analytics for Economics in the Master of Science in Data Science for Economics programme. See [CONTRIBUTIONS.md](CONTRIBUTIONS.md) for individual contributions.

## AI Usage

Generative AI assistance is documented in [AI_USAGE.md](AI_USAGE.md). Group members are responsible for reviewing and verifying their final work.

## Dashboard and Presentation

- **GitHub repository:** https://github.com/madhurima2904/HawkerGO_DS608_project
- **Live Streamlit dashboard:** To be added after deployment.
- **Final presentation:** To be added under `outputs/presentation/`.

## Reproducibility

The repository includes the Streamlit application, data-processing code, and documentation. Before final submission, the group should document the original data sources, preprocessing steps, required files, and any limits to regenerating processed datasets.

## Acknowledgement

This is a collaborative academic group project for DS608 Data Analytics for Economics. Individual contributions are documented in `CONTRIBUTIONS.md`.
