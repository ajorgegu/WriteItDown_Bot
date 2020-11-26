import pytz, datetime

def calculateSettedHour(date, timezone):
    userTimezone = pytz.timezone(timezone)
    esp = pytz.timezone('Europe/Madrid')
    userTimezone = userTimezone.localize(date)
    hourSpain = userTimezone.astimezone(esp)
    return hourSpain

def calculateGettedHour(date, timezone):
    userTimezone = pytz.timezone(timezone)
    esp = pytz.timezone('Europe/Madrid')
    date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    esp = esp.localize(date)
    userHour = esp.astimezone(userTimezone)
    return userHour