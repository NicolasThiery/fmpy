from datetime import datetime


def is_valid_time_format(time_format):
    try:
        datetime.strptime(time_format, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return False
    else:
        return True


def format_period(period):
    if 'd' not in period:
        if 'm' in period:
            period = period.replace('m', 'min')
        elif 'h' in period:
            period = period.replace('h', 'hour')
    return period


def get_current_minute():
    return datetime.now().replace(second=0, microsecond=0)

