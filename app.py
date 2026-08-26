import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Ferry Capacity Analytics",
    page_icon="⛴️",
    layout="wide"
)


# ============================================================
# CONSTANTS
# ============================================================

DATA_PATH = Path(__file__).resolve().parent / "data" / "Toronto_Ferry_Terminal_Ticket_Sales.csv"

CONGESTION_DEFAULT = 80
IDLE_DEFAULT = 20


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():

    # Ensure the dataset exists at the expected path relative to app.py
    if not DATA_PATH.exists():
        # Raise a clear error that will be shown in Streamlit's error display
        raise FileNotFoundError(
            f"Dataset not found at {DATA_PATH}.\nPlease place 'Toronto_Ferry_Terminal_Ticket_Sales.csv' in the project's 'data/' folder relative to app.py, or update DATA_PATH to point to the CSV."
        )

    df = pd.read_csv(DATA_PATH)

    df.columns = df.columns.str.strip()

    required = [
        "_id",
        "Timestamp",
        "Redemption Count",
        "Sales Count"
    ]

    missing = [
        col for col in required
        if col not in df.columns
    ]

    if missing:
        raise ValueError(
            "Missing columns: " + ", ".join(missing)
        )

    # Preserve original values for quality checks
    df["Original Sales Count"] = pd.to_numeric(
        df["Sales Count"],
        errors="coerce"
    )

    df["Original Redemption Count"] = pd.to_numeric(
        df["Redemption Count"],
        errors="coerce"
    )

    df["Timestamp"] = pd.to_datetime(
        df["Timestamp"],
        errors="coerce"
    )

    # Quality flags BEFORE cleaning
    df["Invalid Timestamp"] = df["Timestamp"].isna()

    df["Negative Sales"] = (
        df["Original Sales Count"] < 0
    )

    df["Negative Redemption"] = (
        df["Original Redemption Count"] < 0
    )

    df["Zero Activity"] = (
        df["Original Sales Count"].fillna(0)
        +
        df["Original Redemption Count"].fillna(0)
        == 0
    )

    # Duplicate ID
    df["Duplicate ID"] = df.duplicated(
        subset=["_id"],
        keep=False
    )

    # Duplicate timestamp
    df["Duplicate Timestamp"] = df.duplicated(
        subset=["Timestamp"],
        keep=False
    )

    # Clean numeric columns
    df["Sales Count"] = (
        df["Original Sales Count"]
        .fillna(0)
        .clip(lower=0)
    )

    df["Redemption Count"] = (
        df["Original Redemption Count"]
        .fillna(0)
        .clip(lower=0)
    )

    # Remove invalid timestamps
    df = df.dropna(
        subset=["Timestamp"]
    )

    df = df.sort_values(
        "Timestamp"
    ).reset_index(drop=True)

    return df


# ============================================================
# LOAD
# ============================================================

try:

    df = load_data()

except Exception as e:

    st.error(f"Dataset loading error: {e}")
    st.stop()


# ============================================================
# BASIC FEATURES
# ============================================================

df["Total Activity"] = (
    df["Sales Count"] +
    df["Redemption Count"]
)

df["Redemption Pressure Ratio"] = (
    df["Redemption Count"] /
    (df["Total Activity"] + 1)
)

df["Year"] = df["Timestamp"].dt.year
df["Month"] = df["Timestamp"].dt.month
df["Month Name"] = df["Timestamp"].dt.month_name()
df["Date"] = df["Timestamp"].dt.date
df["Hour"] = df["Timestamp"].dt.hour
df["Day of Week"] = df["Timestamp"].dt.day_name()

df["Day Type"] = np.where(
    df["Timestamp"].dt.dayofweek >= 5,
    "Weekend",
    "Weekday"
)


# ============================================================
# SEASON
# ============================================================

def season(month):

    if month in [12, 1, 2]:
        return "Winter"

    if month in [3, 4, 5]:
        return "Spring"

    if month in [6, 7, 8]:
        return "Summer"

    return "Autumn"


df["Season"] = df["Month"].apply(season)


# ============================================================
# OPERATIONAL LOAD INDEX
# ============================================================

reference = df["Total Activity"].quantile(0.95)

if reference <= 0:
    reference = 1

df["Operational Load Index"] = (
    df["Total Activity"] / reference
) * 100

df["Operational Load Index"] = (
    df["Operational Load Index"]
    .clip(0, 100)
)


# ============================================================
# ROLLING SPIKE DETECTION
# ============================================================

rolling_window = 8

df["Rolling Activity Mean"] = (
    df["Total Activity"]
    .rolling(
        window=rolling_window,
        min_periods=3
    )
    .mean()
)

df["Rolling Activity Std"] = (
    df["Total Activity"]
    .rolling(
        window=rolling_window,
        min_periods=3
    )
    .std()
)

df["Spike Upper Limit"] = (
    df["Rolling Activity Mean"]
    +
    2 * df["Rolling Activity Std"]
)

df["Spike Detected"] = (
    df["Total Activity"]
    >
    df["Spike Upper Limit"]
)

df["Spike Detected"] = (
    df["Spike Detected"]
    .fillna(False)
)

# ============================================================
# PROJECT INFORMATION - ENGLISH + HINDI
# ============================================================

st.sidebar.divider()

show_about = st.sidebar.checkbox(
    "📘 About Project / प्रोजेक्ट के बारे में"
)

if show_about:

    st.title(
        "📘 Project Documentation / प्रोजेक्ट डॉक्यूमेंटेशन"
    )

    st.caption(
        "Ferry Capacity Utilization & Operational Efficiency Analytics System"
    )

    st.divider()

    # ========================================================
    # PROJECT OVERVIEW
    # ========================================================

    st.header("🚢 Project Overview / प्रोजेक्ट का परिचय")

    tab1, tab2 = st.tabs([
        "🇬🇧 English",
        "🇮🇳 हिंदी"
    ])

    # --------------------------------------------------------
    # ENGLISH OVERVIEW
    # --------------------------------------------------------

    with tab1:

        st.subheader(
            "Ferry Capacity Utilization & Operational Efficiency Analytics System"
        )

        st.write(
            """
            This project is a data-driven analytical system developed
            to analyse ferry ticket sales and redemption activity.

            The system processes historical timestamp-based ferry
            activity data and transforms raw records into meaningful
            operational indicators.

            The dashboard helps identify high-activity periods,
            congestion-prone intervals, low-activity periods,
            sustained idle periods, seasonal patterns,
            weekday/weekend differences and time-of-day trends.
            """
        )

        st.subheader("🎯 Main Objectives")

        objectives = [
            "Analyse historical ferry ticket activity.",
            "Measure total sales and redemption activity.",
            "Calculate an Operational Load Index.",
            "Identify congestion-prone periods.",
            "Identify low-activity and sustained idle periods.",
            "Detect unusual activity spikes.",
            "Compare weekday and weekend activity.",
            "Analyse seasonal demand patterns.",
            "Analyse morning, afternoon, evening and night activity.",
            "Provide an interactive analytical dashboard."
        ]

        for objective in objectives:
            st.markdown(f"✅ {objective}")

    # --------------------------------------------------------
    # HINDI OVERVIEW
    # --------------------------------------------------------

    with tab2:

        st.subheader(
            "फेरी क्षमता उपयोग एवं परिचालन दक्षता विश्लेषण प्रणाली"
        )

        st.write(
            """
            यह परियोजना फेरी टिकट बिक्री और रिडेम्पशन गतिविधि
            का डेटा-आधारित विश्लेषण करने के लिए विकसित की गई है।

            सिस्टम historical timestamp-based ferry activity data
            को process करके raw records को meaningful operational
            indicators में बदलता है।

            Dashboard के माध्यम से अधिक activity वाले समय,
            congestion-prone periods, low-activity periods,
            sustained idle periods, seasonal patterns,
            weekday/weekend differences और time-of-day trends
            को समझा जा सकता है।
            """
        )

        st.subheader("🎯 मुख्य उद्देश्य")

        objectives_hindi = [
            "Historical ferry ticket activity का विश्लेषण करना।",
            "Sales और redemption activity को measure करना।",
            "Operational Load Index calculate करना।",
            "Congestion-prone periods की पहचान करना।",
            "Low-activity और sustained idle periods की पहचान करना।",
            "Unusual activity spikes detect करना।",
            "Weekday और weekend activity की तुलना करना।",
            "Seasonal demand patterns का विश्लेषण करना।",
            "Morning, afternoon, evening और night activity का विश्लेषण करना।",
            "Interactive analytical dashboard उपलब्ध कराना।"
        ]

        for objective in objectives_hindi:
            st.markdown(f"✅ {objective}")

    st.divider()

    # ========================================================
    # TECHNOLOGY STACK
    # ========================================================

    st.header("💻 Technology Stack / प्रयुक्त Technologies")

    st.write(
        """
        The following technologies are used in the implementation
        of this analytical system.
        """
    )

    technology_data = pd.DataFrame({
        "Technology": [
            "Python",
            "Streamlit",
            "Pandas",
            "NumPy",
            "Plotly",
            "CSV",
            "VS Code"
        ],

        "Role in Project": [
            "Main programming language",
            "Interactive dashboard and web application",
            "Data loading, cleaning, transformation and analysis",
            "Numerical calculations and conditional processing",
            "Interactive charts and data visualization",
            "Dataset storage and input format",
            "Development and debugging environment"
        ],

        "Where It Is Used": [
            "Entire app.py application logic",
            "Dashboard UI, sidebar, filters, metrics and tables",
            "pd.read_csv(), data cleaning, groupby(), resample() and aggregations",
            "np.where(), numerical operations and calculations",
            "px.line(), px.bar(), px.imshow(), go.Figure() and charts",
            "Toronto_Ferry_Terminal_Ticket_Sales.csv",
            "Project development and testing"
        ]
    })

    st.dataframe(
        technology_data,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # ========================================================
    # TECHNOLOGY DETAILS
    # ========================================================

    st.header(
        "🔧 Technology Implementation / Technology का उपयोग"
    )

    with st.expander("🐍 Python — Main Programming Language"):

        st.write(
            """
            Python is the primary programming language of this project.

            It is responsible for the main application logic,
            data processing, calculations, feature engineering,
            analytical operations and dashboard execution.
            """
        )

        st.code(
            """
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
            """,
            language="python"
        )

    with st.expander("📊 Streamlit — Dashboard Development"):

        st.write(
            """
            Streamlit is used to convert the Python analytics into
            an interactive web-based dashboard.

            It is used for:

            • Sidebar filters
            • Date selection
            • Dropdowns
            • KPI cards
            • Tables
            • Charts
            • Download buttons
            • Project documentation
            """
        )

        st.code(
            """
st.set_page_config(...)
st.sidebar.checkbox(...)
st.sidebar.selectbox(...)
st.sidebar.slider(...)
st.metric(...)
st.dataframe(...)
st.plotly_chart(...)
st.download_button(...)
            """,
            language="python"
        )

    with st.expander("🐼 Pandas — Data Analysis"):

        st.write(
            """
            Pandas is one of the main analytical libraries used
            in this project.

            It is used for:

            • Reading the CSV dataset
            • Cleaning data
            • Converting timestamps
            • Filtering records
            • Grouping data
            • Resampling data
            • Calculating aggregates
            • Creating analytical features
            """
        )

        st.code(
            """
df = pd.read_csv(DATA_PATH)

df["Timestamp"] = pd.to_datetime(
    df["Timestamp"],
    errors="coerce"
)

filtered = df[
    (df["Timestamp"] >= start_date) &
    (df["Timestamp"] < end_date)
].copy()

filtered.groupby("Day Type")
            """,
            language="python"
        )

    with st.expander("🔢 NumPy — Numerical Processing"):

        st.write(
            """
            NumPy is used for numerical and conditional operations.

            For example, NumPy is used to classify records as
            weekday or weekend using np.where().
            """
        )

        st.code(
            """
df["Day Type"] = np.where(
    df["Timestamp"].dt.dayofweek >= 5,
    "Weekend",
    "Weekday"
)
            """,
            language="python"
        )

    with st.expander("📈 Plotly — Data Visualization"):

        st.write(
            """
            Plotly is used to create interactive visualizations.

            The project uses Plotly for:

            • Operational load timeline
            • Congestion Pressure Index
            • Sales vs Redemption activity
            • Weekday vs Weekend analysis
            • Seasonal analysis
            • Time-of-day analysis
            • Heatmap
            • Year-wise trend
            """
        )

        st.code(
            """
fig = px.bar(
    day_analysis,
    x="Day Type",
    y="Average_Load"
)

st.plotly_chart(
    fig,
    use_container_width=True
)
            """,
            language="python"
        )

    with st.expander("📄 CSV — Dataset Storage"):

        st.write(
            """
            The ferry activity dataset is stored in CSV format.

            The application loads the dataset using Pandas and
            processes the following important fields:

            • _id
            • Timestamp
            • Sales Count
            • Redemption Count
            """
        )

        st.code(
            """
DATA_PATH = "data/Toronto_Ferry_Terminal_Ticket_Sales.csv"

df = pd.read_csv(DATA_PATH)
            """,
            language="python"
        )

    with st.expander("💻 VS Code — Development Environment"):

        st.write(
            """
            Visual Studio Code can be used as the development
            environment for writing, testing and debugging the
            Python and Streamlit application.
            """
        )

    st.divider()

    # ========================================================
    # DATA FLOW
    # ========================================================

    st.header("🔄 Data Processing Flow / Data कैसे Process होता है")

    st.code(
        """
        Ferry Ticket Activity Data
                    ↓
                 CSV File
                    ↓
             Pandas Data Loading
                    ↓
              Data Validation
                    ↓
               Data Cleaning
                    ↓
            Timestamp Processing
                    ↓
             Feature Engineering
                    ↓
          Aggregation & Calculation
                    ↓
       Operational Load Calculation
                    ↓
       Congestion / Idle Detection
                    ↓
          Spike Detection Analysis
                    ↓
          Plotly Visualization
                    ↓
          Streamlit Dashboard
                    ↓
             Business Insights
        """,
        language="text"
    )

    st.divider()

    # ========================================================
    # DATASET
    # ========================================================

    st.header("📁 Dataset / Dataset की जानकारी")

    st.markdown(
        """
        **Dataset File:**

        `Toronto_Ferry_Terminal_Ticket_Sales.csv`

        **Location in Project:**

        `data/Toronto_Ferry_Terminal_Ticket_Sales.csv`
        """
    )

    dataset_columns = pd.DataFrame({
        "Column": [
            "_id",
            "Timestamp",
            "Sales Count",
            "Redemption Count"
        ],

        "Purpose": [
            "Unique record identifier",
            "Date and time of ferry activity",
            "Number of tickets sold",
            "Number of tickets redeemed"
        ]
    })

    st.dataframe(
        dataset_columns,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # ========================================================
    # DATA QUALITY
    # ========================================================

    st.header("🧹 Data Quality & Validation")

    st.write(
        """
        The application performs several data-quality checks before
        performing the main analysis.
        """
    )

    quality_checks = [
        "Invalid timestamp detection",
        "Negative sales detection",
        "Negative redemption detection",
        "Zero-activity detection",
        "Duplicate ID detection",
        "Duplicate timestamp detection",
        "Irregular 15-minute interval detection",
        "Missing-value handling",
        "Numeric value validation"
    ]

    for check in quality_checks:
        st.markdown(f"🔍 {check}")

    st.divider()

    # ========================================================
    # FEATURE ENGINEERING
    # ========================================================

    st.header("⚙️ Feature Engineering")

    st.write(
        """
        Additional analytical features are generated from the
        original dataset to support deeper analysis.
        """
    )

    features_data = pd.DataFrame({
        "Feature": [
            "Total Activity",
            "Redemption Pressure Ratio",
            "Year",
            "Month",
            "Month Name",
            "Date",
            "Hour",
            "Day of Week",
            "Day Type",
            "Season",
            "Operational Load Index",
            "Rolling Activity Mean",
            "Rolling Activity Std",
            "Spike Upper Limit",
            "Spike Detected"
        ],

        "Purpose": [
            "Combined sales and redemption activity",
            "Measures redemption pressure relative to activity",
            "Year-based analysis",
            "Month-based analysis",
            "Seasonal/month-name analysis",
            "Daily analysis",
            "Time-of-day analysis",
            "Day-based analysis",
            "Weekday vs weekend classification",
            "Season classification",
            "Normalized operational activity indicator",
            "Rolling activity baseline",
            "Rolling activity variability",
            "Upper boundary for spike detection",
            "Identifies unusual activity spikes"
        ]
    })

    st.dataframe(
        features_data,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # ========================================================
    # ANALYTICS IMPLEMENTED
    # ========================================================

    st.header("📊 Analytics Implemented / किए गए Analytics")

    analytics = [
        "Sales Count Analysis",
        "Redemption Count Analysis",
        "Operational Load Analysis",
        "Congestion Pressure Analysis",
        "Idle Period Analysis",
        "Sustained Idle Detection",
        "Rolling Spike Detection",
        "Weekday vs Weekend Analysis",
        "Seasonal Analysis",
        "Time-of-Day Analysis",
        "Day and Hour Heatmap Analysis",
        "Year-wise Trend Analysis",
        "Automated Operational Insights"
    ]

    for item in analytics:
        st.markdown(f"📌 **{item}**")

    st.divider()

    # ========================================================
    # KPI DEFINITIONS
    # ========================================================

    st.header("📈 KPI Definitions / KPI का मतलब")

    kpi_data = pd.DataFrame({

        "KPI": [
            "Total Records",
            "Total Sales",
            "Total Redemptions",
            "Operational Utilization",
            "Idle Capacity",
            "Congestion Pressure",
            "Peak Load",
            "Sustained Idle",
            "Peak Strain Duration",
            "Operational Variability Score"
        ],

        "Meaning": [
            "Number of records in the selected analysis period",
            "Total number of recorded sales",
            "Total number of recorded redemptions",
            "Average normalized operational activity",
            "Percentage of analysed intervals below idle threshold",
            "Percentage of analysed intervals classified as congestion",
            "Highest normalized operational load",
            "Number of intervals forming sustained idle periods",
            "Estimated duration of congestion intervals",
            "Relative variability of operational load"
        ]
    })

    st.dataframe(
        kpi_data,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # ========================================================
    # METHODOLOGY
    # ========================================================

    st.header("⚙️ Methodology / कार्यप्रणाली")

    methodology = [
        "Data ingestion",
        "Data validation",
        "Data cleaning",
        "Timestamp conversion",
        "Feature engineering",
        "15-minute / hourly / daily aggregation",
        "Operational Load Index calculation",
        "Congestion Pressure Index calculation",
        "Congestion detection",
        "Idle-period detection",
        "Sustained idle detection",
        "Rolling spike detection",
        "Seasonal analysis",
        "Weekday/weekend analysis",
        "Time-of-day analysis",
        "Visualization",
        "Automated insight generation"
    ]

    for i, step in enumerate(methodology, start=1):
        st.markdown(f"**{i}.** {step}")

    st.divider()

    # ========================================================
    # DASHBOARD FEATURES
    # ========================================================

    st.header("🎨 Dashboard Features")

    dashboard_features = [
        "Interactive date range filtering",
        "Season filtering",
        "Weekday / weekend filtering",
        "15-minute, hourly and daily granularity",
        "Adjustable congestion threshold",
        "Adjustable idle threshold",
        "KPI cards",
        "Data quality monitoring",
        "Irregular interval detection",
        "Rolling spike detection",
        "Operational utilization timeline",
        "Congestion Pressure Index chart",
        "Sales vs Redemption chart",
        "Congestion period table",
        "Sustained idle period table",
        "Weekday vs Weekend comparison",
        "Seasonal comparison",
        "Time-of-day analysis",
        "Day-hour heatmap",
        "Year-wise trend",
        "Automated operational insights",
        "Filtered dataset export"
    ]

    for feature in dashboard_features:
        st.markdown(f"🔹 {feature}")

    st.divider()

    # ========================================================
    # PROJECT CONTRIBUTION
    # ========================================================

    st.header("👨‍💻 Project Contribution / Project में मेरा योगदान")

    contribution = [
        "Project problem identification",
        "Dataset integration",
        "Data preprocessing",
        "Data-quality validation",
        "Feature engineering",
        "Analytical metric development",
        "Operational load calculation",
        "Congestion and idle detection",
        "Spike detection",
        "Interactive dashboard development",
        "Data visualization",
        "Automated insight generation",
        "Data export functionality",
        "Testing and debugging",
        "Project documentation"
    ]

    for item in contribution:
        st.markdown(f"✔️ {item}")

    st.divider()

    # ========================================================
    # IMPORTANT METHODOLOGICAL NOTE
    # ========================================================

    st.header("⚠️ Important Methodological Note")

    st.warning(
        """
        The Operational Load Index is an activity-based normalized
        operational pressure indicator.

        It does NOT represent actual passenger occupancy because
        vessel-level passenger capacity is not available in the
        supplied dataset.

        Similarly, direct operational cost efficiency cannot be
        calculated from the current dataset because operating-cost
        information is not available.
        """
    )

    st.divider()

    # ========================================================
    # BUSINESS VALUE
    # ========================================================

    st.header("💼 Business Value / व्यावसायिक उपयोग")

    benefits = [
        "Better understanding of ferry demand patterns",
        "Identification of congestion-prone periods",
        "Identification of low-activity periods",
        "Better operational planning",
        "Improved scheduling decisions",
        "Seasonal planning support",
        "Identification of unusual demand spikes",
        "Data-driven operational decision making"
    ]

    for benefit in benefits:
        st.markdown(f"💡 {benefit}")

    st.divider()

    # ========================================================
    # FUTURE SCOPE
    # ========================================================

    st.header("🔮 Future Scope / भविष्य में सुधार")

    future_scope = [
        "Actual vessel capacity integration",
        "Passenger count integration",
        "Route information",
        "Vessel assignment information",
        "Staffing information",
        "Operating cost information",
        "Weather conditions",
        "Special event information",
        "Real-time operational data",
        "Predictive demand forecasting",
        "Machine-learning based demand prediction"
    ]

    for item in future_scope:
        st.markdown(f"🚀 {item}")

    st.divider()

    # ========================================================
    # PROJECT SUMMARY
    # ========================================================

    st.header("📌 Project Summary / संक्षिप्त सारांश")

    st.success(
        """
        This project demonstrates how raw ferry ticket activity
        data can be transformed into meaningful operational insights.

        Python is used for application logic and analytics,
        Pandas for data processing, NumPy for numerical operations,
        Plotly for interactive visualization and Streamlit for
        building the final analytical dashboard.

        The system provides an interactive approach for analysing
        ferry activity, identifying operational pressure,
        detecting idle periods and understanding demand patterns.
        """
    )

    st.info(
        """
        हिंदी में:

        यह परियोजना दिखाती है कि raw ferry ticket activity data
        को data processing, analytics और visualization की सहायता
        से meaningful operational insights में बदला जा सकता है।

        Python, Pandas, NumPy, Plotly और Streamlit का उपयोग करके
        एक interactive analytical dashboard तैयार किया गया है।
        """
    )

    st.divider()

    st.caption(
        "⛴️ Ferry Capacity Utilization & Operational Efficiency Analytics System"
    )

    st.caption(
        "Technology Stack: Python • Streamlit • Pandas • NumPy • Plotly • CSV"
    )

    st.stop()
# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("⛴️ Ferry Analytics")

st.sidebar.header("Dashboard Filters")


min_date = df["Timestamp"].min().date()
max_date = df["Timestamp"].max().date()


date_range = st.sidebar.date_input(
    "📅 Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)


if isinstance(date_range, tuple) and len(date_range) == 2:

    start_date = pd.Timestamp(date_range[0])
    end_date = (
        pd.Timestamp(date_range[1])
        + pd.Timedelta(days=1)
    )

else:

    start_date = pd.Timestamp(min_date)
    end_date = (
        pd.Timestamp(max_date)
        + pd.Timedelta(days=1)
    )


selected_season = st.sidebar.selectbox(
    "🌦️ Season",
    [
        "All",
        "Winter",
        "Spring",
        "Summer",
        "Autumn"
    ]
)


selected_day = st.sidebar.selectbox(
    "📅 Day Type",
    [
        "All",
        "Weekday",
        "Weekend"
    ]
)


granularity = st.sidebar.radio(
    "⏱️ Granularity",
    [
        "15-Minute",
        "Hourly",
        "Daily"
    ]
)


st.sidebar.subheader(
    "⚙️ Thresholds"
)


congestion_threshold = st.sidebar.slider(
    "🔴 Congestion Threshold (%)",
    50,
    100,
    CONGESTION_DEFAULT,
    5
)


idle_threshold = st.sidebar.slider(
    "🔵 Idle Threshold (%)",
    0,
    50,
    IDLE_DEFAULT,
    5
)


# ============================================================
# FILTER DATA
# ============================================================

filtered = df[
    (df["Timestamp"] >= start_date) &
    (df["Timestamp"] < end_date)
].copy()


if selected_season != "All":

    filtered = filtered[
        filtered["Season"] == selected_season
    ]


if selected_day != "All":

    filtered = filtered[
        filtered["Day Type"] == selected_day
    ]


if filtered.empty:

    st.warning(
        "Selected filters के लिए कोई data नहीं मिला."
    )

    st.stop()


# ============================================================
# AGGREGATION
# ============================================================

if granularity == "15-Minute":

    analysis = (
        filtered
        .set_index("Timestamp")
        .resample("15min")
        .agg({
            "Sales Count": "sum",
            "Redemption Count": "sum",
            "Total Activity": "sum"
        })
        .reset_index()
    )

elif granularity == "Hourly":

    analysis = (
        filtered
        .set_index("Timestamp")
        .resample("1h")
        .agg({
            "Sales Count": "sum",
            "Redemption Count": "sum",
            "Total Activity": "sum"
        })
        .reset_index()
    )

else:

    analysis = (
        filtered
        .set_index("Timestamp")
        .resample("1D")
        .agg({
            "Sales Count": "sum",
            "Redemption Count": "sum",
            "Total Activity": "sum"
        })
        .reset_index()
    )


analysis = analysis[
    analysis["Total Activity"] > 0
].copy()


if analysis.empty:

    st.warning(
        "Selected period में usable activity नहीं मिली."
    )

    st.stop()


# ============================================================
# NORMALIZED LOAD
# ============================================================

analysis_reference = (
    analysis["Total Activity"]
    .quantile(0.95)
)

if analysis_reference <= 0:
    analysis_reference = 1


analysis["Operational Load Index"] = (
    analysis["Total Activity"]
    / analysis_reference
) * 100


analysis["Operational Load Index"] = (
    analysis["Operational Load Index"]
    .clip(0, 100)
)


# ============================================================
# CONGESTION PRESSURE INDEX
# ============================================================

analysis["Congestion Pressure Index"] = (
    analysis["Operational Load Index"]
    * (
        analysis["Redemption Count"]
        /
        (analysis["Total Activity"] + 1)
    )
)


# Normalize CPI
cpi_max = analysis[
    "Congestion Pressure Index"
].max()

if cpi_max > 0:

    analysis["Congestion Pressure Index"] = (
        analysis["Congestion Pressure Index"]
        / cpi_max
    ) * 100


# ============================================================
# CONGESTION / IDLE
# ============================================================

analysis["Congestion"] = (
    analysis["Operational Load Index"]
    >= congestion_threshold
)


analysis["Idle"] = (
    analysis["Operational Load Index"]
    <= idle_threshold
)


# ============================================================
# SUSTAINED IDLE INDICATOR
# ============================================================

analysis["Idle Streak"] = (
    analysis["Idle"]
    .astype(int)
    .groupby(
        (~analysis["Idle"]).cumsum()
    )
    .cumsum()
)


analysis["Sustained Idle"] = (
    analysis["Idle Streak"] >= 3
)


# ============================================================
# KPI
# ============================================================

total_records = len(filtered)

total_sales = filtered[
    "Sales Count"
].sum()

total_redemptions = filtered[
    "Redemption Count"
].sum()

average_utilization = analysis[
    "Operational Load Index"
].mean()

peak_utilization = analysis[
    "Operational Load Index"
].max()

congestion_count = int(
    analysis["Congestion"].sum()
)

idle_count = int(
    analysis["Idle"].sum()
)

sustained_idle_count = int(
    analysis["Sustained Idle"].sum()
)

total_intervals = len(analysis)


congestion_percentage = (
    congestion_count /
    total_intervals
) * 100


idle_percentage = (
    idle_count /
    total_intervals
) * 100


# ============================================================
# VARIABILITY
# ============================================================

mean_load = analysis[
    "Operational Load Index"
].mean()

std_load = analysis[
    "Operational Load Index"
].std()

if mean_load > 0:

    variability_score = (
        std_load / mean_load
    )

else:

    variability_score = 0


# ============================================================
# PEAK STRAIN
# ============================================================

if granularity == "15-Minute":

    minutes = 15

elif granularity == "Hourly":

    minutes = 60

else:

    minutes = 1440


peak_strain = (
    congestion_count * minutes
)


if peak_strain >= 60:

    peak_strain_text = (
        f"{peak_strain / 60:.1f} hrs"
    )

else:

    peak_strain_text = (
        f"{peak_strain:.0f} min"
    )


# ============================================================
# TITLE
# ============================================================

st.title(
    "⛴️ Ferry Capacity Utilization & Operational Efficiency Analytics System"
)

st.write(
    "Toronto Ferry Terminal Ticket Activity Analytics"
)

st.divider()


# ============================================================
# KPI CARDS
# ============================================================

st.subheader(
    "📊 Key Performance Indicators"
)


c1, c2, c3, c4, c5 = st.columns(5)


with c1:

    st.metric(
        "Total Records",
        f"{total_records:,}"
    )


with c2:

    st.metric(
        "Total Sales",
        f"{total_sales:,.0f}"
    )


with c3:

    st.metric(
        "Total Redemptions",
        f"{total_redemptions:,.0f}"
    )


with c4:

    st.metric(
        "Operational Utilization",
        f"{average_utilization:.2f}%"
    )


with c5:

    st.metric(
        "Idle Capacity",
        f"{idle_percentage:.2f}%"
    )


c6, c7, c8, c9 = st.columns(4)


with c6:

    st.metric(
        "Congestion Pressure",
        f"{congestion_percentage:.2f}%"
    )


with c7:

    st.metric(
        "Peak Load",
        f"{peak_utilization:.2f}%"
    )


with c8:

    st.metric(
        "Sustained Idle",
        f"{sustained_idle_count:,}"
    )


with c9:

    st.metric(
        "Peak Strain Duration",
        peak_strain_text
    )


st.info(
    f"Operational Variability Score: "
    f"{variability_score:.2f}"
)


st.info(
    "Methodological Note: Operational Load Index एक "
    "activity-based normalized indicator है. Supplied dataset "
    "में vessel-level passenger capacity उपलब्ध नहीं है, इसलिए "
    "यह actual passenger occupancy percentage नहीं है."
)


# ============================================================
# DATA QUALITY
# ============================================================

st.divider()

st.subheader(
    "🧹 Data Quality & Consistency Checks"
)


invalid_timestamp_count = int(
    df["Invalid Timestamp"].sum()
)

negative_sales_count = int(
    df["Negative Sales"].sum()
)

negative_redemption_count = int(
    df["Negative Redemption"].sum()
)

zero_activity_count = int(
    df["Zero Activity"].sum()
)

duplicate_id_count = int(
    df["Duplicate ID"].sum()
)

duplicate_timestamp_count = int(
    df["Duplicate Timestamp"].sum()
)


q1, q2, q3, q4, q5, q6 = st.columns(6)


with q1:
    st.metric(
        "Invalid Timestamp",
        invalid_timestamp_count
    )

with q2:
    st.metric(
        "Negative Sales",
        negative_sales_count
    )

with q3:
    st.metric(
        "Negative Redemption",
        negative_redemption_count
    )

with q4:
    st.metric(
        "Zero Activity",
        zero_activity_count
    )

with q5:
    st.metric(
        "Duplicate IDs",
        duplicate_id_count
    )

with q6:
    st.metric(
        "Duplicate Timestamps",
        duplicate_timestamp_count
    )


# ============================================================
# IRREGULAR INTERVAL CHECK
# ============================================================

st.subheader(
    "⏱️ Irregular 15-Minute Interval Check"
)


timestamp_diff = (
    df["Timestamp"]
    .sort_values()
    .diff()
)


expected_interval = pd.Timedelta(
    minutes=15
)


irregular_intervals = (
    timestamp_diff[
        timestamp_diff != expected_interval
    ]
    .dropna()
)


st.metric(
    "Detected Irregular Gaps",
    f"{len(irregular_intervals):,}"
)


if len(irregular_intervals) > 0:

    st.warning(
        "Dataset में कुछ intervals 15-minute pattern से अलग हैं."
    )

else:

    st.success(
        "15-minute interval pattern consistent है."
    )


# ============================================================
# SPIKE ANALYSIS
# ============================================================

st.divider()

st.subheader(
    "📈 Rolling Statistics & Extreme Spike Detection"
)


spike_count = int(
    filtered["Spike Detected"].sum()
)


st.metric(
    "Detected Activity Spikes",
    f"{spike_count:,}"
)


spike_df = filtered[
    filtered["Spike Detected"]
].copy()


if not spike_df.empty:

    st.dataframe(
        spike_df[
            [
                "Timestamp",
                "Sales Count",
                "Redemption Count",
                "Total Activity",
                "Rolling Activity Mean",
                "Spike Upper Limit"
            ]
        ]
        .sort_values(
            "Total Activity",
            ascending=False
        )
        .head(20),
        use_container_width=True
    )

else:

    st.success(
        "No extreme rolling-statistic spikes detected."
    )


# ============================================================
# UTILIZATION TIMELINE
# ============================================================

st.divider()

st.subheader(
    "📈 Capacity Utilization Timeline"
)


fig = go.Figure()


fig.add_trace(
    go.Scattergl(
        x=analysis["Timestamp"],
        y=analysis[
            "Operational Load Index"
        ],
        mode="lines",
        name="Operational Load"
    )
)


fig.add_hline(
    y=congestion_threshold,
    line_dash="dash",
    annotation_text="Congestion"
)


fig.add_hline(
    y=idle_threshold,
    line_dash="dash",
    annotation_text="Idle"
)


fig.update_layout(
    title="Operational Load Over Time",
    xaxis_title="Time",
    yaxis_title="Operational Load (%)",
    yaxis=dict(
        range=[0, 105]
    ),
    height=500,
    template="plotly_dark"
)


st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# CONGESTION PRESSURE
# ============================================================

st.subheader(
    "🔥 Congestion Pressure Index"
)


fig_cpi = px.line(
    analysis,
    x="Timestamp",
    y="Congestion Pressure Index",
    title="Congestion Pressure Index Over Time",
    labels={
        "Congestion Pressure Index":
        "Pressure Index (%)"
    },
    template="plotly_dark"
)


fig_cpi.add_hline(
    y=80,
    line_dash="dash",
    annotation_text="High Pressure"
)


st.plotly_chart(
    fig_cpi,
    use_container_width=True
)


# ============================================================
# SALES VS REDEMPTIONS
# ============================================================

st.subheader(
    "🎟️ Sales vs Redemption Activity"
)


fig_sales = go.Figure()


fig_sales.add_trace(
    go.Scattergl(
        x=analysis["Timestamp"],
        y=analysis["Sales Count"],
        mode="lines",
        name="Sales"
    )
)


fig_sales.add_trace(
    go.Scattergl(
        x=analysis["Timestamp"],
        y=analysis["Redemption Count"],
        mode="lines",
        name="Redemptions"
    )
)


fig_sales.update_layout(
    title="Sales and Redemption Activity",
    xaxis_title="Time",
    yaxis_title="Count",
    height=500,
    template="plotly_dark"
)


st.plotly_chart(
    fig_sales,
    use_container_width=True
)


# ============================================================
# CONGESTION / IDLE
# ============================================================

st.divider()

st.subheader(
    "🚨 Congestion & Idle Period Analysis"
)


left, right = st.columns(2)


with left:

    st.write("### 🔴 Congestion Periods")

    congestion_df = analysis[
        analysis["Congestion"]
    ]

    if not congestion_df.empty:

        st.dataframe(
            congestion_df[
                [
                    "Timestamp",
                    "Sales Count",
                    "Redemption Count",
                    "Total Activity",
                    "Operational Load Index",
                    "Congestion Pressure Index"
                ]
            ]
            .sort_values(
                "Operational Load Index",
                ascending=False
            )
            .head(20),
            use_container_width=True
        )

    else:

        st.success(
            "No congestion periods found."
        )


with right:

    st.write("### 🟢 Sustained Idle Periods")

    idle_df = analysis[
        analysis["Sustained Idle"]
    ]

    if not idle_df.empty:

        st.dataframe(
            idle_df[
                [
                    "Timestamp",
                    "Sales Count",
                    "Redemption Count",
                    "Total Activity",
                    "Operational Load Index"
                ]
            ]
            .sort_values(
                "Operational Load Index"
            )
            .head(20),
            use_container_width=True
        )

    else:

        st.success(
            "No sustained idle periods found."
        )


# ============================================================
# WEEKDAY / WEEKEND
# ============================================================

st.divider()

st.subheader(
    "📅 Weekday vs Weekend Efficiency"
)


day_analysis = (
    filtered
    .groupby("Day Type")
    .agg(
        Average_Activity=(
            "Total Activity",
            "mean"
        ),
        Total_Activity=(
            "Total Activity",
            "sum"
        ),
        Average_Load=(
            "Operational Load Index",
            "mean"
        )
    )
    .reset_index()
)


fig_day = px.bar(
    day_analysis,
    x="Day Type",
    y="Average_Load",
    title="Average Operational Load by Day Type",
    labels={
        "Average_Load":
        "Average Load (%)"
    },
    template="plotly_dark"
)


st.plotly_chart(
    fig_day,
    use_container_width=True
)


# ============================================================
# SEASONAL
# ============================================================

st.divider()

st.subheader(
    "🌦️ Seasonal Efficiency Comparison"
)


season_analysis = (
    filtered
    .groupby("Season")
    .agg(
        Average_Activity=(
            "Total Activity",
            "mean"
        ),
        Total_Activity=(
            "Total Activity",
            "sum"
        ),
        Average_Load=(
            "Operational Load Index",
            "mean"
        )
    )
    .reset_index()
)


season_order = [
    "Winter",
    "Spring",
    "Summer",
    "Autumn"
]


season_analysis["Season"] = pd.Categorical(
    season_analysis["Season"],
    categories=season_order,
    ordered=True
)


season_analysis = season_analysis.sort_values(
    "Season"
)


fig_season = px.bar(
    season_analysis,
    x="Season",
    y="Average_Load",
    title="Seasonal Operational Efficiency",
    labels={
        "Average_Load":
        "Average Load (%)"
    },
    template="plotly_dark"
)


st.plotly_chart(
    fig_season,
    use_container_width=True
)


# ============================================================
# TIME OF DAY
# ============================================================

st.divider()

st.subheader(
    "🕐 Morning / Afternoon / Evening Analysis"
)


filtered["Time Band"] = pd.cut(
    filtered["Hour"],
    bins=[
        -1,
        11,
        16,
        20,
        24
    ],
    labels=[
        "Morning",
        "Afternoon",
        "Evening",
        "Night"
    ]
)


time_analysis = (
    filtered
    .groupby(
        "Time Band",
        observed=True
    )
    .agg(
        Average_Activity=(
            "Total Activity",
            "mean"
        ),
        Average_Load=(
            "Operational Load Index",
            "mean"
        )
    )
    .reset_index()
)


fig_time = px.bar(
    time_analysis,
    x="Time Band",
    y="Average_Load",
    title="Operational Load by Time Band",
    labels={
        "Average_Load":
        "Average Load (%)"
    },
    template="plotly_dark"
)


st.plotly_chart(
    fig_time,
    use_container_width=True
)


# ============================================================
# HEATMAP
# ============================================================

st.divider()

st.subheader(
    "🔥 Congestion & Idle Heatmap"
)


heatmap = (
    filtered
    .groupby(
        [
            "Day of Week",
            "Hour"
        ],
        observed=True
    )[
        "Operational Load Index"
    ]
    .mean()
    .reset_index()
)


days = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday"
]


heatmap["Day of Week"] = pd.Categorical(
    heatmap["Day of Week"],
    categories=days,
    ordered=True
)


pivot = heatmap.pivot(
    index="Day of Week",
    columns="Hour",
    values="Operational Load Index"
)


pivot = pivot.reindex(days)


fig_heatmap = px.imshow(
    pivot,
    aspect="auto",
    title="Average Operational Load by Day and Hour",
    labels={
        "x": "Hour",
        "y": "Day",
        "color": "Load (%)"
    },
    template="plotly_dark"
)


st.plotly_chart(
    fig_heatmap,
    use_container_width=True
)


# ============================================================
# YEAR TREND
# ============================================================

st.divider()

st.subheader(
    "📆 Year-wise Operational Trend"
)


year_analysis = (
    filtered
    .groupby("Year")
    .agg(
        Average_Activity=(
            "Total Activity",
            "mean"
        ),
        Total_Activity=(
            "Total Activity",
            "sum"
        ),
        Average_Load=(
            "Operational Load Index",
            "mean"
        )
    )
    .reset_index()
)


fig_year = px.line(
    year_analysis,
    x="Year",
    y="Average_Load",
    markers=True,
    title="Year-wise Operational Load",
    labels={
        "Average_Load":
        "Average Load (%)"
    },
    template="plotly_dark"
)


st.plotly_chart(
    fig_year,
    use_container_width=True
)


# ============================================================
# AUTOMATED INSIGHTS
# ============================================================

st.divider()

st.subheader(
    "🤖 Automated Operational Insights"
)


highest_season = None
highest_season_value = None

if not season_analysis.empty:

    row = season_analysis.loc[
        season_analysis["Average_Load"].idxmax()
    ]

    highest_season = row["Season"]
    highest_season_value = row["Average_Load"]


highest_day = None
highest_day_value = None

if not day_analysis.empty:

    row = day_analysis.loc[
        day_analysis["Average_Load"].idxmax()
    ]

    highest_day = row["Day Type"]
    highest_day_value = row["Average_Load"]


highest_time = None
highest_time_value = None

if not time_analysis.empty:

    row = time_analysis.loc[
        time_analysis["Average_Load"].idxmax()
    ]

    highest_time = row["Time Band"]
    highest_time_value = row["Average_Load"]


if highest_season is not None:

    st.write(
        f"🌦️ **Highest-load season:** "
        f"{highest_season} "
        f"({highest_season_value:.2f}%)"
    )


if highest_day is not None:

    st.write(
        f"📅 **Higher-load day type:** "
        f"{highest_day} "
        f"({highest_day_value:.2f}%)"
    )


if highest_time is not None:

    st.write(
        f"🕐 **Highest-load time band:** "
        f"{highest_time} "
        f"({highest_time_value:.2f}%)"
    )


st.write(
    f"🔴 **Congestion share:** "
    f"{congestion_percentage:.2f}% of analysed intervals."
)


st.write(
    f"🟢 **Idle share:** "
    f"{idle_percentage:.2f}% of analysed intervals."
)


st.write(
    f"📈 **Detected extreme activity spikes:** "
    f"{spike_count:,}"
)


# ============================================================
# TOP CONGESTION
# ============================================================

st.divider()

st.subheader(
    "🚨 Top Congestion Windows"
)


top_congestion = (
    analysis[
        analysis["Congestion"]
    ]
    .sort_values(
        "Congestion Pressure Index",
        ascending=False
    )
    .head(20)
)


if not top_congestion.empty:

    st.dataframe(
        top_congestion[
            [
                "Timestamp",
                "Sales Count",
                "Redemption Count",
                "Total Activity",
                "Operational Load Index",
                "Congestion Pressure Index"
            ]
        ],
        use_container_width=True
    )

else:

    st.info(
        "No congestion windows detected."
    )


# ============================================================
# DATASET SUMMARY
# ============================================================

st.divider()

st.subheader(
    "📋 Dataset Summary"
)


s1, s2, s3, s4 = st.columns(4)


with s1:

    st.metric(
        "Dataset Rows",
        f"{len(df):,}"
    )


with s2:

    st.metric(
        "Dataset Columns",
        f"{len(df.columns):,}"
    )


with s3:

    st.metric(
        "Start Date",
        str(df["Timestamp"].min().date())
    )


with s4:

    st.metric(
        "End Date",
        str(df["Timestamp"].max().date())
    )


# ============================================================
# DATA PREVIEW
# ============================================================

with st.expander(
    "🔍 View Filtered Data"
):

    st.dataframe(
        filtered.head(100),
        use_container_width=True
    )


# ============================================================
# DOWNLOAD
# ============================================================

st.divider()

st.subheader(
    "📥 Export"
)


download_csv = filtered.to_csv(
    index=False
).encode("utf-8")


st.download_button(
    "📥 Download Filtered Dataset",
    data=download_csv,
    file_name="ferry_filtered_analysis.csv",
    mime="text/csv"
)


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Ferry Capacity Utilization & Operational Efficiency Analytics System | "
    "Streamlit"
)