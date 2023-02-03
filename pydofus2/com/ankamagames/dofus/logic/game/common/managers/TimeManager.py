from datetime import datetime, timezone, timedelta
from pydofus2.com.ankamagames.jerakine.data.I18n import I18n
from pydofus2.com.ankamagames.jerakine.metaclasses.ThreadSharedSingleton import \
    ThreadSharedSingleton


class TimeManager(metaclass=ThreadSharedSingleton):
    def __init__(self) -> None:
        self.serverTimeLag: int = 0
        self.serverUtcTimeLag: int = 0
        self.timezoneOffset: int = 0
        self.dofusTimeYearLag: int = 0

    def getUtcTimestamp(self):
        dt = datetime.now(timezone.utc)
        utc_time = dt.replace(tzinfo=timezone.utc)
        utc_timestamp = utc_time.timestamp()
        return utc_timestamp
    
    def getDateFromTime(self, timeUTC: int, useTimezoneOffset: bool = False) -> list:
        date: datetime = None
        nday = nmonth = nyear = nhour = nminute = None
        if timeUTC == 0:
            date = datetime.now() + timedelta(seconds=self.serverTimeLag/1000)
        else:
            date = datetime.fromtimestamp(timeUTC/1000) + timedelta(seconds=self.serverTimeLag/1000)
        if useTimezoneOffset:
            nday = date.day
            nmonth = date.month
            nyear = date.year
            nhour = date.hour
            nminute = date.minute
        else:
            nday = date.utcnow().day
            nmonth = date.utcnow().month
            nyear = date.utcnow().year
            nhour = date.utcnow().hour
            nminute = date.utcnow().minute
        return [nminute, nhour, nday, nmonth, nyear]


    def initText(self):
        self._nameYears = I18n.getUiText("ui.time.years");
        self._nameMonths = I18n.getUiText("ui.time.months");
        self._nameDays = I18n.getUiText("ui.time.days");
        self._nameHours = I18n.getUiText("ui.time.hours");
        self._nameMinutes = I18n.getUiText("ui.time.minutes");
        self._nameSeconds = I18n.getUiText("ui.time.seconds");
        self._nameYearsShort = I18n.getUiText("ui.time.short.year");
        self._nameMonthsShort = I18n.getUiText("ui.time.short.month");
        self._nameDaysShort = I18n.getUiText("ui.time.short.day");
        self._nameHoursShort = I18n.getUiText("ui.time.short.hour");
        self._nameAnd = I18n.getUiText("ui.common.and").lower();
        self._bTextInit = True

    def getDateIG(self, time: int):
        date = self.getDateFromTime(time)
        nyear = date[4] + self.dofusTimeYearLag
        month = Month.getMonthById(date[3] - 1).name
        return [date[2], month, nyear]
