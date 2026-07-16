from datetime import date, datetime, time, timedelta


def func(now, today, date=None):
    if not date:
        current_weekday = today.weekday()  # 0 - понедельник, 6 - воскресенье

        # Вычисляем ближайшую пятницу 15:00
        days_until_friday = (4 - current_weekday) % 7  # 4 - пятница
        this_friday_17 = datetime.combine(
            today + timedelta(days=days_until_friday), datetime.min.time()
        ) + timedelta(hours=17)

        if now < this_friday_17 and current_weekday != 5:  # Не в субботу
            # Записываем на ближайшую субботу
            days_until_saturday = (5 - current_weekday) % 7
        else:
            # Записываем на субботу следующей недели
            days_until_saturday = (5 - current_weekday) % 7 + 7

        date = today + timedelta(days=days_until_saturday)
        return date


# print('14 декабря')
# print(func(datetime.strptime("13.12.24 16:30", "%d.%m.%y %H:%M"), datetime.strptime("13.12.24", "%d.%m.%y"), date=None))

# print('\n\n21 декабря\n\n')
# print(func(datetime.strptime("13.12.24 17:00", "%d.%m.%y %H:%M"), datetime.strptime("13.12.24", "%d.%m.%y"), date=None))
# print(func(datetime.strptime("13.12.24 17:01", "%d.%m.%y %H:%M"), datetime.strptime("13.12.24", "%d.%m.%y"), date=None))
# print(func(datetime.strptime("14.12.24 00:00", "%d.%m.%y %H:%M"), datetime.strptime("14.12.24", "%d.%m.%y"), date=None))
# print(func(datetime.strptime("14.12.24 12:30", "%d.%m.%y %H:%M"), datetime.strptime("14.12.24", "%d.%m.%y"), date=None))
# print(func(datetime.strptime("14.12.24 11:30", "%d.%m.%y %H:%M"), datetime.strptime("14.12.24", "%d.%m.%y"), date=None))
# print(func(datetime.strptime("15.12.24 16:30", "%d.%m.%y %H:%M"), datetime.strptime("15.12.24", "%d.%m.%y"), date=None))
# print(func(datetime.strptime("16.12.24 17:00", "%d.%m.%y %H:%M"), datetime.strptime("16.12.24", "%d.%m.%y"), date=None))
# print(func(datetime.strptime("17.12.24 17:01", "%d.%m.%y %H:%M"), datetime.strptime("17.12.24", "%d.%m.%y"), date=None))
# print(func(datetime.strptime("18.12.24 00:00", "%d.%m.%y %H:%M"), datetime.strptime("18.12.24", "%d.%m.%y"), date=None))
# print(func(datetime.strptime("19.12.24 12:30", "%d.%m.%y %H:%M"), datetime.strptime("19.12.24", "%d.%m.%y"), date=None))
# print(func(datetime.strptime("20.12.24 11:30", "%d.%m.%y %H:%M"), datetime.strptime("20.12.24", "%d.%m.%y"), date=None))
# print('\n\n28 декабря\n')
# print(func(datetime.strptime("20.12.24 17:01", "%d.%m.%y %H:%M"), datetime.strptime("20.12.24", "%d.%m.%y"), date=None))
# print(func(datetime.strptime("26.12.24 17:01", "%d.%m.%y %H:%M"), datetime.strptime("26.12.24", "%d.%m.%y"), date=None))
# print(func(datetime.strptime("27.12.24 10:00", "%d.%m.%y %H:%M"), datetime.strptime("27.12.24", "%d.%m.%y"), date=None))
# print('\n\n4 января 2025\n\n')
# print(func(datetime.strptime("27.12.24 17:00", "%d.%m.%y %H:%M"), datetime.strptime("27.12.24", "%d.%m.%y"), date=None))
# print(func(datetime.strptime("28.12.24 11:30", "%d.%m.%y %H:%M"), datetime.strptime("28.12.24", "%d.%m.%y"), date=None))

# print(datetime.now())

# current_weekday = date.today().weekday()


# if current_weekday == 4 and datetime.now().time() > time(17, 0):
#     raise ValueError("Registracija į artimiausius pietus baigėsi.")
# elif current_weekday == 5:
#     raise ValueError("Registracija į pietus dar neprasidėjo. Ji prasidės sekmadienį.")


import time

created_at = int(time.time())
print(created_at)
