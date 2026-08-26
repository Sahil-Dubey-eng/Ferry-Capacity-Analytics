import numpy as np


def create_features(df):
    """
    Create analytical features for ferry capacity
    and operational efficiency analysis.
    """

    # =====================================================
    # 1. TOTAL ACTIVITY LOAD
    # =====================================================

    df["Total Activity Load"] = (
        df["Sales Count"]
        + df["Redemption Count"]
    )

    # =====================================================
    # 2. REDEMPTION PRESSURE RATIO
    # =====================================================

    df["Redemption Pressure Ratio"] = (
        df["Redemption Count"]
        / (df["Sales Count"] + 1)
    )

    # =====================================================
    # 3. OPERATIONAL LOAD INDEX (OLI)
    # =====================================================

    max_activity = df[
        "Total Activity Load"
    ].max()

    if max_activity > 0:

        df["Operational Load Index"] = (
            df["Total Activity Load"]
            / max_activity
        ) * 100

    else:

        df["Operational Load Index"] = 0

    # =====================================================
    # 4. DATE FEATURES
    # =====================================================

    df["Date"] = (
        df["Timestamp"].dt.date
    )

    df["Year"] = (
        df["Timestamp"].dt.year
    )

    df["Month"] = (
        df["Timestamp"].dt.month
    )

    df["Month Name"] = (
        df["Timestamp"].dt.month_name()
    )

    df["Day"] = (
        df["Timestamp"].dt.day
    )

    # =====================================================
    # 5. DAY FEATURES
    # =====================================================

    df["Day Name"] = (
        df["Timestamp"].dt.day_name()
    )

    df["Day Number"] = (
        df["Timestamp"].dt.dayofweek
    )

    # =====================================================
    # 6. HOUR / MINUTE
    # =====================================================

    df["Hour"] = (
        df["Timestamp"].dt.hour
    )

    df["Minute"] = (
        df["Timestamp"].dt.minute
    )

    # =====================================================
    # 7. WEEKDAY / WEEKEND
    # =====================================================

    df["Week Type"] = np.where(
        df["Timestamp"].dt.dayofweek >= 5,
        "Weekend",
        "Weekday"
    )

    # =====================================================
    # 8. SEASON
    # =====================================================

    df["Season"] = (
        df["Month"].apply(
            get_season
        )
    )

    # =====================================================
    # 9. TIME PERIOD
    # =====================================================

    df["Time Period"] = (
        df["Hour"].apply(
            get_time_period
        )
    )

    # =====================================================
    # 10. EFFICIENCY STATUS
    # =====================================================

    df["Efficiency Status"] = (
        df["Operational Load Index"]
        .apply(
            get_efficiency_status
        )
    )

    return df


# =========================================================
# SEASON FUNCTION
# =========================================================

def get_season(month):

    if month in [12, 1, 2]:

        return "Winter"

    elif month in [3, 4, 5]:

        return "Spring"

    elif month in [6, 7, 8]:

        return "Summer"

    else:

        return "Autumn"


# =========================================================
# TIME PERIOD FUNCTION
# =========================================================

def get_time_period(hour):

    if 5 <= hour < 12:

        return "Morning"

    elif 12 <= hour < 17:

        return "Afternoon"

    elif 17 <= hour < 22:

        return "Evening"

    else:

        return "Night"


# =========================================================
# EFFICIENCY STATUS
# =========================================================

def get_efficiency_status(oli):

    if oli >= 80:

        return "High Pressure"

    elif oli <= 20:

        return "Idle"

    elif oli >= 50:

        return "Normal"

    else:

        return "Low Utilization"