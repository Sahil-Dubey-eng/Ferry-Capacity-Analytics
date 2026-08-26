def format_number(value):
    """
    Format a number with comma separators.
    Example: 1234567 -> 1,234,567
    """

    if value is None:
        return "0"

    try:
        return f"{value:,.0f}"
    except (ValueError, TypeError):
        return str(value)


def format_decimal(value, decimals=2):
    """
    Format a number with a fixed number of decimal places.
    """

    if value is None:
        return "0"

    try:
        return f"{value:,.{decimals}f}"
    except (ValueError, TypeError):
        return str(value)


def safe_percentage(value, decimals=2):
    """
    Convert a numeric value into percentage display format.
    """

    if value is None:
        return "0%"

    try:
        return f"{value:.{decimals}f}%"
    except (ValueError, TypeError):
        return str(value)


def get_status_icon(status):
    """
    Return an icon based on efficiency status.
    """

    icons = {
        "High Pressure": "🔴",
        "Normal": "🟢",
        "Low Utilization": "🟡",
        "Idle": "🔵"
    }

    return icons.get(
        status,
        "⚪"
    )


def get_status_message(status):
    """
    Return a short operational message.
    """

    messages = {
        "High Pressure":
            "Congestion-prone period",

        "Normal":
            "Normal operational condition",

        "Low Utilization":
            "Low utilization period",

        "Idle":
            "Idle capacity detected"
    }

    return messages.get(
        status,
        "No status available"
    )