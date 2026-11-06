from datetime import datetime


def money(value):
    """Format a number as Indian rupees."""
    return f"₹{value:,.2f}"


def valid_date(value):
    """Check whether a date is in YYYY-MM-DD format and is valid."""
    try:
        datetime.strptime(value, "%Y-%m-%d")
        return True
    except ValueError:
        return False
