from datetime import datetime, timezone
from pydofus2.com.ankamagames.jerakine.metaclasses.ThreadSharedSingleton import ThreadSharedSingleton


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
