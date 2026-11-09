# Group Contributions

**Project:** HawkerGo — DS608 Data Analytics for Economics (MDSE, 2026)

HawkerGo was developed collaboratively as a three-member group project. The primary dashboard page responsibilities are listed below. These are assigned responsibilities; they should not be interpreted as a verified record of every Git commit or secondary task.

| Member | Primary responsibility | Main dashboard component |
| --- | --- | --- |
| **Madhurima Subramaniam Rudra** | Page 1 — Explore Hawkers | Centre exploration, closure status, map, and nearby alternative finder |
| **Nicolyne Tiana Lie** | Page 2 — Maintenance Calendar | Area and date filters, closure overview, monthly calendar, closure details, and closure-pattern views |
| **Toh En Hui** | Page 3 — Stall Insights | Top-ten stall-count comparison and market-versus-food-stall distribution |

## Individual contributions

### Madhurima Subramaniam Rudra — Explore Hawkers

Responsible for the first dashboard page, which lets users examine hawker centres, their scheduled closure status, location information, stall counts, and nearby alternatives. The page uses a processed hawker centre dataset and a precomputed walking-distance matrix. _Confirm whether Madhu also prepared the walking-distance matrix, geographic joins, and raw-data processing before attributing those tasks._

### Nicolyne Tiana Lie — Maintenance Calendar

Responsible for the second dashboard page, which presents planned cleaning and other maintenance records in an interactive calendar. Work includes filtering by area and hawker centre, summarising scheduled events and affected centres, showing closure details, and handling records with incomplete dates. The associated closure-data reshaping logic is in `src/wrangle.py`. Nicolyne also contributed to dashboard styling and configuration troubleshooting, and preparation of project documentation and presentation materials.

### Toh En Hui — Stall Insights

Responsible for the third dashboard page, which compares hawker centres by food and market stall counts. This includes a stacked bar chart of the ten largest centres, a scatter plot of market versus food stalls, and descriptive stall-type labels. Additional contributions include assisting with the project presentation materials and performing final validation checks across the dashboard charts prior to submission.

## Shared work and collaboration

The team integrated the three pages into a Streamlit multipage dashboard and used a shared GitHub repository. Shared work may include project planning, reviewing each other's pages, verifying results, maintaining documentation, preparing slides, and testing the combined app. **Each member should confirm their actual shared contributions** before the final submission.

Recommended evidence for the final version:

- Relevant Git commits, branches, pull requests, and reviews.
- Specific data preparation or integration tasks performed by each member.
- Who prepared the presentation, tested the final app, and reviewed the README.
- Any changes in responsibilities during development.

## Academic integrity and accountability

This project is group work for **DS608 Data Analytics for Economics**. Each member is responsible for understanding and being able to explain their contribution. Generative AI assistance is disclosed separately in [AI_USAGE.md](AI_USAGE.md).

_Review this file with Madhu and Enhui before submission to ensure that all contributions are accurate and complete._
