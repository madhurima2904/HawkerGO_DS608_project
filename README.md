# HawkerGo — Singapore Hawker Centre Explorer

**DS608 Data Analytics for Economics | MDSE Group Project (2026)**

**Group members:** Madhurima Subramaniam Rudra, Nicolyne Tiana Lie, and Toh En Hui .

**Project repository:** https://github.com/madhurima2904/HawkerGO_DS608_project

## Research Question

How can public hawker centre closure data be transformed into an interactive dashboard to help residents plan visits and identify nearby dining alternatives?

## Project Overview

HawkerGO is an interactive Streamlit dashboard designed to help residents explore hawker centres in Singapore, check scheduled closures, and understand the distribution of food and market stalls.

By combining publicly available hawker centre information with closure schedules and geographical data, the dashboard helps users plan visits and explore alternative dining locations.

## Project Objectives

- Help users discover hawker centres and explore nearby alternatives.
- Provide information about scheduled hawker centre closures.
- Filter closure schedules by area, hawker centre, closure type, and date.
- Visualise the distribution of food and market stalls across hawker centres.
- Present public data through clear, interactive visualisations.

## Dashboard Features

### Explore Hawkers 

Explore hawker centres and identify nearby dining alternatives using location-based information.

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

- Hawker centre information and geographical locations
- Scheduled hawker centre closure dates
- MRT station exit geographical information

**To complete before submission:** Verify and add the original dataset URLs, publication dates, and licensing terms.

## Data Preparation and Methodology

1. **Data collection:** Obtain public hawker centre, closure, and geographical datasets.
2. **Data cleaning:** Check missing values, inconsistent formats, and data quality.
3. **Data transformation:** Convert closure schedules into structured records.
4. **Feature engineering:** Calculate closure durations and total stall counts.
5. **Exploratory analysis:** Examine closure patterns and differences between centres.
6. **Data visualisation:** Create interactive charts, maps, filters, and calendars.
7. **Dashboard development:** Integrate analyses into a multipage Streamlit app.

## Technologies Used

Python, Pandas, Streamlit, Plotly, Git, and GitHub.

## Running the Dashboard Locally

Clone the repository:

```bash
git clone https://github.com/madhurima2904/HawkerGO_DS608_project.git
cd HawkerGO_DS608_project
```

Install dependencies and launch the dashboard:

```bash
python3 -m pip install -r requirements.txt
python3 -m streamlit run app.py
```

Open the local URL displayed by Streamlit (usually `http://localhost:8501`). Required processed datasets must be available under `data/processed/`.

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
