from abc import ABC, abstractmethod
import datetime


class AbstractDateMapper(ABC):
    @abstractmethod
    def get_date(self) -> datetime.datetime:
        pass

    @staticmethod
    def now_date() -> datetime.datetime:
        return datetime.datetime.now()


class ClosestWeekDayDateMapper(AbstractDateMapper):
    day: int

    def __init__(self, day: int = 0):
        assert day in [0, 1, 2, 3, 4, 5, 6]
        self.day = day

    def get_date(self) -> datetime.datetime:
        now_date = self.now_date()
        for day_num in range(1, 8):
            date = datetime.datetime.fromtimestamp(
                now_date.timestamp() + 86400 * day_num
            )
            if date.weekday() == self.day:
                return datetime.datetime(date.year, date.month, date.day)
        raise Exception("Unreachable!")


class TomorrowDateMapper(AbstractDateMapper):
    def get_date(self) -> datetime.datetime:
        now = TomorrowDateMapper.now_date()
        tm = datetime.datetime.fromtimestamp(now.timestamp() + 86400)
        return datetime.datetime(tm.year, tm.month, tm.day)


class TodayDateMapper(AbstractDateMapper):
    def get_date(self) -> datetime.datetime:
        now = self.now_date()
        return datetime.datetime(now.year, now.month, now.day)
