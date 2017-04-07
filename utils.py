from datetime import date, timedelta
import re

def is_holiday(day):
    return day.weekday() > 4


def time_spent_from_str(time_spent):
    res = 0
    minutes = re.search("([0-9]+)m", time_spent)
    hours = re.search("([0-9]+)h", time_spent)
    days = re.search("([0-9]+)d", time_spent)
    if days:
        res += int(days.groups()[0]) * 8.0
    if hours:
        res += int(hours.groups()[0])
    if minutes:
        res += int(minutes.groups()[0]) / 60.0
    return res


def calc_diff_days(from_date, to_date):
    from_date = from_date.split("-")
    to_date = to_date.split("-")
    from_date = date(int(from_date[0]), int(from_date[1]), int(from_date[2]))
    to_date = date(int(to_date[0]), int(to_date[1]), int(to_date[2]))
    day_generator = (from_date + timedelta(x + 1) for x in range((to_date - from_date).days))
    return sum(1 for day in day_generator if not is_holiday(day))


def last_work_day():
    day = date.today() - timedelta(1)
    while is_holiday(day):
        day -= timedelta(1)
    return day


def to_h(val):
    return val / 60.0 / 60.0