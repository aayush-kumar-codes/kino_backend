from datetime import datetime, timedelta, date, time
from django.db.models import Q
import calendar


def GraphData(params):
    key = {}
    if params.get("weekly"):
        start_date = datetime.today() - timedelta(days=7)

        for i in range(7):
            day = start_date + timedelta(days=i)
            key[day.strftime("%a")] = Q(created_at__date=day)

        lists = list(key.keys())
        return lists, key
    if params.get("day"):
        dates = date.today()
        for i in range(0, 24, 4):
            start_time = datetime.combine(dates, time(i, 0, 0))
            end_time = datetime.combine(dates, time(i, 59, 59))
            key[i] = Q(created_at__range=[start_time, end_time])

        lists = list(key.keys())
        return lists, key

    current_year = datetime.today().year
    for i in range(1, 13):
        month_name = calendar.month_name[i][:3]
        start_date = datetime(current_year, i, 1)
        end_date = datetime(
            current_year, i, calendar.monthrange(current_year, i)[1]
        )
        key[month_name] = Q(
            created_at__range=[start_date, end_date]
        )
    lists = list(key.keys())
    return lists, key
