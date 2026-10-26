from datetime import date, timedelta


def get_running_stats_window():
    today = date.today()
    current_monday = today - timedelta(days=today.weekday())

    start_date = current_monday - timedelta(weeks=11)
    end_date = today + timedelta(days=1)

    return start_date, end_date