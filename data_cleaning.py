import pandas as pd


def load_and_clean_data(file_path):
    """
    Load ferry ticket data and perform basic cleaning.
    """

    # Load CSV file
    df = pd.read_csv(file_path)

    # Remove extra spaces from column names
    df.columns = df.columns.str.strip()

    # Convert Timestamp column to datetime
    df["Timestamp"] = pd.to_datetime(
        df["Timestamp"],
        errors="coerce"
    )

    # Convert Sales Count to numeric
    df["Sales Count"] = pd.to_numeric(
        df["Sales Count"],
        errors="coerce"
    )

    # Convert Redemption Count to numeric
    df["Redemption Count"] = pd.to_numeric(
        df["Redemption Count"],
        errors="coerce"
    )

    # Remove rows with invalid timestamps
    df = df.dropna(
        subset=["Timestamp"]
    )

    # Replace missing Sales values with 0
    df["Sales Count"] = df[
        "Sales Count"
    ].fillna(0)

    # Replace missing Redemption values with 0
    df["Redemption Count"] = df[
        "Redemption Count"
    ].fillna(0)

    # Remove negative sales values
    df.loc[
        df["Sales Count"] < 0,
        "Sales Count"
    ] = 0

    # Remove negative redemption values
    df.loc[
        df["Redemption Count"] < 0,
        "Redemption Count"
    ] = 0

    # Remove duplicate rows
    df = df.drop_duplicates()

    # Sort data by timestamp
    df = df.sort_values(
        "Timestamp"
    ).reset_index(drop=True)

    return df


def get_data_quality_report(df):
    """
    Generate data quality statistics.
    """

    report = {
        "total_rows": len(df),

        "total_columns": len(
            df.columns
        ),

        "missing_values": int(
            df.isna().sum().sum()
        ),

        "duplicate_rows": int(
            df.duplicated().sum()
        ),

        "negative_sales": int(
            (df["Sales Count"] < 0).sum()
        ),

        "negative_redemptions": int(
            (df["Redemption Count"] < 0).sum()
        )
    }

    return report