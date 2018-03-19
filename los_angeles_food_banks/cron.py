class Cron(object):
    def __init__(self, minutes, hours, dayOfMonth, month, dayOfWeek):
        self.minutes = minutes
        self.hours = hours
        self.dayOfMonth = dayOfMonth
        self.month = month
        self.dayOfWeek = dayOfWeek

    def __str__(self):
        return str(f"{self.minutes} {self.hours} {self.dayOfMonth} {self.month} {self.dayOfWeek}")

    def __repr__(self):
        return str(f"{self.minutes} {self.hours} {self.dayOfMonth} {self.month} {self.dayOfWeek}")