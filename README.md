# Ferry Capacity Utilization & Operational Efficiency Analytics System

## 📌 Project Overview

The Ferry Capacity Utilization & Operational Efficiency Analytics System is a data analytics dashboard developed to analyze Toronto ferry ticket sales and redemption activity.

The system transforms timestamped ticket activity into meaningful operational indicators such as Operational Load Index, congestion-prone periods, idle periods, activity spikes, seasonal patterns, weekday/weekend patterns, and time-based demand trends.

## 🎯 Objectives

- Analyze historical ferry ticket activity
- Measure ticket sales and redemptions
- Calculate an activity-based Operational Load Index (OLI)
- Identify congestion-prone periods
- Identify low-activity and sustained-idle periods
- Detect unusual activity spikes
- Compare weekday and weekend activity
- Analyze seasonal and time-of-day patterns
- Provide an interactive analytics dashboard

## 🛠️ Technologies Used

- Python
- Pandas
- NumPy
- Plotly
- Streamlit

## 📂 Project Structure

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
