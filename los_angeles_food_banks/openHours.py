import re

from timeFrame import TimeFrame


class OpenHours(object):
    def __init__(self, hoursText=None):
        self.text = hoursText

        self.rDay = "(?P<Day>Sunday|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday)"
        self.rDayContinuous = "(?P<DayContinuous>-|through)"
        self.rDayIndividual = "(?P<DayIndividual>,|and)"
        self.rDayConjunction = f"(?P<DayConjunction>{self.rDayIndividual}|{self.rDayContinuous})"
        self.rDayRange = f"(?P<DayRange>{re.sub('<Day>', '<Day1>', self.rDay)}.*?{self.rDayConjunction}.*?{re.sub('<Day>', '<Day2>', self.rDay)})"
        self.rDayAll = f"(?P<DayAll>{self.rDayRange}|{self.rDay})"

        self.rWeekNum = "(?P<Week>1st|2nd|3rd|4th)"
        self.rWeekWords = "(?P<WeekWords>first|second|third|fourth)"
        self.rWeekAll = f"(?P<WeekAll>{self.rWeekNum}|{self.rWeekWords})(?=\s*(?:Sunday|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday))"

        self.rTimeMinute = "(?P<TimeMinute>(?<=:)\d{2})"
        self.rTimeHour = "(?P<TimeHour>\d{1,2}(?=:))"
        self.rTimeAmPm = "(?P<TimeAmPm>am|pm|noon)"
        self.rTimeAll = f"(?P<TimeAll>{self.rTimeHour}:{self.rTimeMinute}.*?{self.rTimeAmPm}?)"
        self.rTimeOpenAll = re.sub("<Time", "<Open", self.rTimeAll)
        self.rTimeCloseAll = re.sub("<Time", "<Close", self.rTimeAll)
        self.rTimeOpenCloseAll = f"(?P<TimeOpenCloseAll>{self.rTimeOpenAll}.*?{self.rTimeCloseAll})"
        self.rTimeContinuous = "(?P<TimeContinuous>-|to)"

        self.dayResults = []
        self.hourResults = []
        self.weekResults = []

        self.openHours = None
        self.parseText()

    def toJSON(self):
        if self.openHours is not None:
            return self.openHours.toJSON()
        else:
            return ''

    def parseDays(self, results):
        r = re.compile(f"^.*?{self.rDayAll}", re.I)
        matchResults = r.match(self.text)
        if matchResults is not None:
            if matchResults['DayRange'] is not None:
                days = self.parseDayRange(matchResults)
                if days[0] in results:
                    days = days[1:]
                [results.append(day) for day in days]
                self.text = self.text[matchResults.start('Day2'):]
            elif matchResults['Day'] is not None:
                day = self.parseDay(matchResults['Day'])
                if day not in results:
                    results.append(day)
                self.text = self.text[matchResults.end('Day'):]
            self.parseDays(results)
        return results

    def parseDayRange(self, matchResults):
        days = []
        dayRange = []
        day1 = matchResults['Day1']
        day2 = matchResults['Day2']
        conjunction = matchResults['DayConjunction']

        if matchResults['DayIndividual']:
            dayRange = [self.parseDay(day1), self.parseDay(day2)]
        elif matchResults['DayContinuous']:
            dayRange = range(self.parseDay(day1), self.parseDay(day2))
        [days.append(day) for day in dayRange]
        return days

    def parseDay(self, day):
        mapper = {"sunday": 0,
                  "monday": 1,
                  "tuesday": 2,
                  "wednesday": 3,
                  "thursday": 4,
                  "friday": 5,
                  "saturday": 6}
        return mapper[day.lower()]

    def parseTime(self, results):
        r = re.compile(f"^.*?{self.rTimeOpenCloseAll}", re.I)
        matchResults = r.match(self.text)
        if matchResults is not None:
            hours = self.parseTimeMatch(matchResults)
            results.append(hours)
            self.text = self.text[matchResults.end('TimeOpenCloseAll'):]
            self.parseTime(results)
        return results

    def parseTimeMatch(self, matchResults):
        openHour = matchResults['OpenHour']
        openMinute = matchResults['OpenMinute']
        openAmPm = matchResults['OpenAmPm']
        closeHour = matchResults['CloseHour']
        closeMinute = matchResults['CloseMinute']
        closeAmPm = matchResults['CloseAmPm']

        print(f"closeAmPm {closeAmPm}")

        if closeAmPm is not None and closeAmPm.lower() == 'pm' and closeHour != '12':
            closeHour = str(int(closeHour) + 12)

        if openAmPm is not None and openAmPm.lower() == 'pm' and openHour != '12':
            openHour = str(int(openHour) + 12)

        if openAmPm is None:
            if (closeHour == '12' and closeMinute == '00') or (closeAmPm == 'pm' and openHour > closeHour):
                openAmPm = 'am'
        return ((openMinute, openHour), (closeMinute, closeHour))

    def parseWeeks(self, results):
        r = re.compile(f"^.*?{self.rWeekAll}", re.I)
        matchResults = r.match(self.text)
        if matchResults is not None:
            week = self.parseWeekMatch(matchResults)
            results.append(week)
            self.text = self.text[matchResults.end('WeekAll'):]
            self.parseWeeks(results)
        return results

    def parseWeekMatch(self, matchResults):
        numMapper = {"1st": 1,
                     "2nd": 2,
                     "3rd": 3,
                     "4th": 4}
        wordMapper = {"first": 1,
                      "second": 2,
                      "third": 3,
                      "fourth": 4}
        word = matchResults['WeekAll'].lower()
        if matchResults['WeekWords'] is not None:
            return wordMapper[word]
        elif matchResults["Week"] is not None:
            return numMapper[word]

    def parseText(self):
        r = re.compile(f"^.*?(?:{self.rDay}|{self.rTimeAll}|{self.rWeekAll})", re.I)
        matchResults = r.match(self.text)

        if matchResults is not None:
            if matchResults['Day'] is not None:
                results = self.parseDays([])
                print(f"Day: {results}")
                self.dayResults = self.dayResults + results
            elif matchResults['TimeAll'] is not None:
                results = self.parseTime([])
                print(f"TimeAll: {results}")
                self.hourResults = self.hourResults + results
            elif matchResults['WeekAll'] is not None:
                results = self.parseWeeks([])
                print(f"WeekAll: {results}")
                self.weekResults = self.weekResults + results

            self.parseText()
        else:
            if len(self.dayResults) > 0 and len(self.hourResults) > 0 and len(self.weekResults) == 0:
                self.weekResults = [1, 2, 3, 4]
            tf = TimeFrame(self.dayResults, self.hourResults, self.weekResults)
            print(f"Final TimeFrame: {self.hourResults}, *, *, {self.dayResults}{self.weekResults}")
            self.openHours = tf
            return
