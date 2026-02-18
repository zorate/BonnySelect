# timezone_config.py
"""
Timezone configuration for Bonny Selects
Sets all timestamps to Nigeria Standard Time (WAT - UTC+1)
"""

from datetime import datetime, timezone, timedelta
import pytz

# Define Nigeria timezone
NIGERIA_TZ = pytz.timezone('Africa/Lagos')  # West Africa Time (WAT) - UTC+1

def get_nigeria_time():
    """
    Get current time in Nigeria timezone
    Returns timezone-aware datetime object
    """
    return datetime.now(NIGERIA_TZ)

def get_naive_nigeria_time():
    """
    Get current time in Nigeria timezone as naive datetime (without timezone info)
    Useful for MongoDB storage
    """
    return datetime.now(NIGERIA_TZ).replace(tzinfo=None)

def localize_to_nigeria(naive_datetime):
    """
    Convert a naive datetime to Nigeria timezone
    """
    if naive_datetime.tzinfo is None:
        return NIGERIA_TZ.localize(naive_datetime)
    return naive_datetime.astimezone(NIGERIA_TZ)

def format_nigeria_time(dt, format_str="%d/%m/%y %H:%M"):
    """
    Format datetime in Nigeria timezone
    """
    if dt is None:
        return "N/A"
    
    if dt.tzinfo is None:
        dt = NIGERIA_TZ.localize(dt)
    else:
        dt = dt.astimezone(NIGERIA_TZ)
    
    return dt.strftime(format_str)