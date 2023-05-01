from datetime import datetime


def is_valid_time_format(time_format):
    try:
        datetime.strptime(time_format, "%Y-%M-%d")
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


def limit_data_list(data_list, date_target, end_target):
    reversed_data = data_list[::-1]
    start_index = 0
    end_index = -1
    for i, item in enumerate(reversed_data):
        if item['date'].split(' ')[0] == date_target:
            start_index = i+1
        elif end_target:
            if item['date'].split(' ')[0] == end_target:
                end_target = i
    return reversed_data[start_index:end_index]
