class TimeFrame():
    def __init__(self, days=[], hours=[], weeks=[]):
        self.days = days
        self.hours = hours

        self.weeks = weeks

        # if len(self.weeks) == 0:
        #     self.weeks = list(range(4))
        # if len(self.days) == 0:
        #     self.days = list(range(7))
        # if len(self.hours) == 0:
        #     self.days = []
        #     self.hours = []
        #     self.weeks = []

    def toJSON(self):
        obj = {
                "days": self.days,
                "hours": self.hours,
                "weeks": self.weeks
        }
        return obj
        