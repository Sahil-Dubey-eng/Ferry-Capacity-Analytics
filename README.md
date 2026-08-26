# Ferry Capacity Utilization & Operational Efficiency Analytics System

## Project Overview

The Ferry Capacity Utilization & Operational Efficiency Analytics System is an interactive data analytics dashboard developed to analyze Toronto ferry ticket sales and redemption activity.

The system converts timestamped ticket activity into operational indicators and helps identify high-activity periods, low-activity periods, unusual spikes, seasonal patterns, weekday/weekend differences, and time-based demand trends.

## Objectives

- Analyze historical ferry ticket activity
- Measure ticket sales and redemptions
- Calculate an activity-based Operational Load Index (OLI)
- Identify congestion-prone periods
- Identify low-activity and sustained-idle periods
- Detect unusual activity spikes
- Analyze weekday and weekend patterns
- Analyze seasonal and time-of-day trends
- Provide an interactive Streamlit dashboard

## Technologies Used

- Python
- Pandas
- NumPy
- Plotly
- Streamlit
- OpenPyXL

## Project Structure

```text
Ferry-Capacity-Analytics/
│
├── app.py
├── requirements.txt
├── README.md
│
├── analytics/
│   ├── analysis.py
│   ├── feature_engineering.py
│   └── kpi.py
│
├── utils/
│   ├── data_cleaning.py
│   └── helper.py
│
└── data/
    └── Toronto_Ferry_Terminal_Ticket_Sales.csv
