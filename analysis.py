import pandas as pd


# =========================================================
# DATA AGGREGATION
# =========================================================

def aggregate_data(df, granularity):
    """
    Aggregate ferry data according to selected
    time granularity.
    """

    data = df.copy()

    # -----------------------------------------------------
    # 15-MINUTE
    # -----------------------------------------------------

    if granularity == "15-Minute":

        return data

    # -----------------------------------------------------
    # HOURLY
    # -----------------------------------------------------

    elif granularity == "Hourly":

        result = (
            data
            .set_index("Timestamp")
            .resample("1h")
            .agg({
                "Sales Count": "sum",
                "Redemption Count": "sum",
                "Total Activity Load": "sum",
                "Operational Load Index": "mean",
                "Redemption Pressure Ratio": "mean"
            })
            .reset_index()
        )

        return result

    # -----------------------------------------------------
    # DAILY
    # -----------------------------------------------------

    elif granularity == "Daily":

        result = (
            data
            .set_index("Timestamp")
            .resample("1D")
            .agg({
                "Sales Count": "sum",
                "Redemption Count": "sum",
                "Total Activity Load": "sum",
                "Operational Load Index": "mean",
                "Redemption Pressure Ratio": "mean"
            })
            .reset_index()
        )

        return result

    return data


# =========================================================
# SEASONAL ANALYSIS
# =========================================================

def seasonal_analysis(df):
    """
    Compare ferry operational efficiency
    across seasons.
    """

    result = (
        df
        .groupby("Season")
        .agg(
            Average_OLI=(
                "Operational Load Index",
                "mean"
            ),

            Total_Activity=(
                "Total Activity Load",
                "sum"
            ),

            Total_Sales=(
                "Sales Count",
                "sum"
            ),

            Total_Redemptions=(
                "Redemption Count",
                "sum"
            ),

            Records=(
                "Timestamp",
                "count"
            )
        )
        .reset_index()
    )

    return result


# =========================================================
# YEARLY ANALYSIS
# =========================================================

def yearly_analysis(df):
    """
    Analyze operational trends across years.
    """

    result = (
        df
        .groupby("Year")
        .agg(
            Average_OLI=(
                "Operational Load Index",
                "mean"
            ),

            Total_Activity=(
                "Total Activity Load",
                "sum"
            ),

            Total_Sales=(
                "Sales Count",
                "sum"
            ),

            Total_Redemptions=(
                "Redemption Count",
                "sum"
            )
        )
        .reset_index()
    )

    return result


# =========================================================
# WEEKDAY VS WEEKEND
# =========================================================

def weekday_analysis(df):
    """
    Compare weekday and weekend efficiency.
    """

    result = (
        df
        .groupby("Week Type")
        .agg(
            Average_OLI=(
                "Operational Load Index",
                "mean"
            ),

            Average_Activity=(
                "Total Activity Load",
                "mean"
            ),

            Total_Activity=(
                "Total Activity Load",
                "sum"
            ),

            Records=(
                "Timestamp",
                "count"
            )
        )
        .reset_index()
    )

    return result


# =========================================================
# TIME-OF-DAY ANALYSIS
# =========================================================

def time_period_analysis(df):
    """
    Analyze ferry activity during morning,
    afternoon, evening and night.
    """

    result = (
        df
        .groupby("Time Period")
        .agg(
            Average_OLI=(
                "Operational Load Index",
                "mean"
            ),

            Average_Activity=(
                "Total Activity Load",
                "mean"
            ),

            Total_Activity=(
                "Total Activity Load",
                "sum"
            ),

            Records=(
                "Timestamp",
                "count"
            )
        )
        .reset_index()
    )

    # Desired display order
    order = [
        "Morning",
        "Afternoon",
        "Evening",
        "Night"
    ]

    result["Time Period"] = pd.Categorical(
        result["Time Period"],
        categories=order,
        ordered=True
    )

    result = result.sort_values(
        "Time Period"
    )

    return result


# =========================================================
# HOURLY HEATMAP DATA
# =========================================================

def hourly_heatmap_data(df):
    """
    Prepare hourly data for day/hour heatmap.
    """

    result = (
        df
        .groupby(
            ["Day Name", "Hour"]
        )
        .agg(
            Operational_Load=(
                "Operational Load Index",
                "mean"
            ),

            Activity=(
                "Total Activity Load",
                "mean"
            )
        )
        .reset_index()
    )

    return result


# =========================================================
# CONGESTION ANALYSIS
# =========================================================

def congestion_analysis(
    df,
    threshold=80
):
    """
    Identify intervals where operational
    load crosses the congestion threshold.
    """

    result = df[
        df["Operational Load Index"]
        >= threshold
    ].copy()

    result = result.sort_values(
        "Operational Load Index",
        ascending=False
    )

    return result


# =========================================================
# IDLE CAPACITY ANALYSIS
# =========================================================

def idle_capacity_analysis(
    df,
    threshold=20
):
    """
    Identify intervals with very low
    operational activity.
    """

    result = df[
        df["Operational Load Index"]
        <= threshold
    ].copy()

    result = result.sort_values(
        "Operational Load Index",
        ascending=True
    )

    return result


# =========================================================
# TOP PEAK INTERVALS
# =========================================================

def top_peak_intervals(
    df,
    number_of_intervals=10
):
    """
    Return the highest activity intervals.
    """

    return (
        df
        .sort_values(
            "Operational Load Index",
            ascending=False
        )
        .head(number_of_intervals)
        .copy()
    )


# =========================================================
# LOW ACTIVITY INTERVALS
# =========================================================

def top_idle_intervals(
    df,
    number_of_intervals=10
):
    """
    Return the lowest activity intervals.
    """

    return (
        df
        .sort_values(
            "Operational Load Index",
            ascending=True
        )
        .head(number_of_intervals)
        .copy()
    )


# =========================================================
# MONTHLY ANALYSIS
# =========================================================

def monthly_analysis(df):
    """
    Analyze monthly operational patterns.
    """

    result = (
        df
        .groupby(
            [
                "Year",
                "Month",
                "Month Name"
            ]
        )
        .agg(
            Average_OLI=(
                "Operational Load Index",
                "mean"
            ),

            Total_Activity=(
                "Total Activity Load",
                "sum"
            ),

            Total_Sales=(
                "Sales Count",
                "sum"
            ),

            Total_Redemptions=(
                "Redemption Count",
                "sum"
            )
        )
        .reset_index()
    )

    return result


# =========================================================
# OPERATIONAL VARIABILITY
# =========================================================

def operational_variability(df):
    """
    Calculate standard deviation of the
    Operational Load Index.
    """

    if len(df) == 0:

        return 0

    value = (
        df["Operational Load Index"]
        .std()
    )

    if pd.isna(value):

        return 0

    return value