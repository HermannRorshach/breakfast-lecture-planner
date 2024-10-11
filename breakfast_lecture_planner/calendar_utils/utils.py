from datetime import date, timedelta


def get_weeks_in_year(year):
    """Определяет количество недель в году. Если 1 января — пятница,
    суббота или воскресенье, то оно относится к предыдущему году,
    и первая неделя начинается с ближайшего понедельника."""
    first_day_of_year = date(year, 1, 1)
    first_weekday = first_day_of_year.weekday()

    if first_weekday <= 3:  # Если 1 января — понедельник-четверг
        start_of_first_week = first_day_of_year - timedelta(days=first_weekday)
    else:  # Если 1 января — пятница-воскресенье
        start_of_first_week = first_day_of_year + timedelta(
            days=7 - first_weekday)

    last_day_of_year = date(year, 12, 31)
    last_weekday = last_day_of_year.weekday()

    if last_weekday >= 3:
        # Если 31 декабря — среда и далее, год заканчивается в этом году
        end_of_last_week = last_day_of_year + timedelta(days=6 - last_weekday)
    else:
        # Если 31 декабря — понедельник-вторник,
        # последняя неделя относится к следующему году
        end_of_last_week = last_day_of_year - timedelta(days=last_weekday + 1)

    # Разница в днях между последней и первой неделями,
    # делённая на 7 даёт количество недель
    return (end_of_last_week - start_of_first_week).days // 7 + 1


def get_start_and_end_dates(week_number, year):
    """Вычисляет даты начала (понедельник) и конца (воскресенье) недели
    по номеру недели и году"""
    first_day_of_year = date(year, 1, 1)
    first_weekday = first_day_of_year.weekday()

    # Вычисляем смещение до начала первой недели
    if first_weekday <= 3:
        start_of_first_week = first_day_of_year - timedelta(days=first_weekday)
    else:
        start_of_first_week = first_day_of_year + timedelta(
            days=7 - first_weekday)

    # Вычисляем дату начала выбранной недели
    start_of_week = start_of_first_week + timedelta(weeks=week_number - 1)
    end_of_week = start_of_week + timedelta(days=6)

    return start_of_week, end_of_week


def get_next_week_number(year):
    from planner.models import WeekEvents
    last_week_event = WeekEvents.objects.order_by('week_number').last()
    if last_week_event:
        next_week_number = last_week_event.week_number + 1
        # Проверка на количество недель в году
        if next_week_number > get_weeks_in_year(year):
            return 1
        return next_week_number
    return (date.today() - date(date.today().year, 1, 1)).days // 7 + 1
