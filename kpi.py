def calculate_kpis(
    df,
    congestion_threshold=80,
    idle_threshold=20
):
    """
    Calculate key performance indicators
    for ferry operational efficiency.
    """

    # =====================================================
    # BASIC COUNTS
    # =====================================================

    total_records = len(df)

    total_sales = (
        df["Sales Count"].sum()
    )

    total_redemptions = (
        df["Redemption Count"].sum()
    )

    # =====================================================
    # ACTIVITY METRICS
    # =====================================================

    average_activity = (
        df["Total Activity Load"].mean()
    )

    maximum_activity = (
        df["Total Activity Load"].max()
    )

    minimum_activity = (
        df["Total Activity Load"].min()
    )

    # =====================================================
    # OPERATIONAL LOAD INDEX
    # =====================================================

    average_oli = (
        df["Operational Load Index"].mean()
    )

    peak_oli = (
        df["Operational Load Index"].max()
    )

    minimum_oli = (
        df["Operational Load Index"].min()
    )

    # =====================================================
    # CONGESTION ANALYSIS
    # =====================================================

    congestion_count = (
        df["Operational Load Index"]
        >= congestion_threshold
    ).sum()

    # =====================================================
    # IDLE ANALYSIS
    # =====================================================

    idle_count = (
        df["Operational Load Index"]
        <= idle_threshold
    ).sum()

    # =====================================================
    # PERCENTAGES
    # =====================================================

    if total_records > 0:

        congestion_percentage = (
            congestion_count
            / total_records
        ) * 100

        idle_percentage = (
            idle_count
            / total_records
        ) * 100

    else:

        congestion_percentage = 0

        idle_percentage = 0

    # =====================================================
    # OPERATIONAL VARIABILITY
    # =====================================================

    operational_variability = (
        df["Operational Load Index"]
        .std()
    )

    if operational_variability is None:

        operational_variability = 0

    # =====================================================
    # PEAK STRAIN DURATION
    # =====================================================

    peak_strain_duration = (
        calculate_peak_strain_duration(
            df,
            congestion_threshold
        )
    )

    # =====================================================
    # CAPACITY UTILIZATION
    # =====================================================

    capacity_utilization = (
        average_oli
    )

    # =====================================================
    # RETURN ALL KPIs
    # =====================================================

    return {

        "total_records":
            total_records,

        "total_sales":
            total_sales,

        "total_redemptions":
            total_redemptions,

        "average_activity":
            average_activity,

        "maximum_activity":
            maximum_activity,

        "minimum_activity":
            minimum_activity,

        "average_oli":
            average_oli,

        "peak_oli":
            peak_oli,

        "minimum_oli":
            minimum_oli,

        "capacity_utilization":
            capacity_utilization,

        "congestion_count":
            congestion_count,

        "congestion_percentage":
            congestion_percentage,

        "idle_count":
            idle_count,

        "idle_percentage":
            idle_percentage,

        "operational_variability":
            operational_variability,

        "peak_strain_duration":
            peak_strain_duration
    }


# =========================================================
# PEAK STRAIN DURATION
# =========================================================

def calculate_peak_strain_duration(
    df,
    congestion_threshold=80
):
    """
    Calculate the longest continuous period
    where Operational Load Index remains above
    the congestion threshold.

    Data is recorded at 15-minute intervals.
    """

    if len(df) == 0:

        return 0

    data = df.sort_values(
        "Timestamp"
    ).copy()

    data["Is Congested"] = (
        data["Operational Load Index"]
        >= congestion_threshold
    )

    longest_streak = 0
    current_streak = 0

    for value in data["Is Congested"]:

        if value:

            current_streak += 1

            if current_streak > longest_streak:

                longest_streak = (
                    current_streak
                )

        else:

            current_streak = 0

    # Each interval = 15 minutes
    peak_strain_minutes = (
        longest_streak * 15
    )

    return peak_strain_minutes