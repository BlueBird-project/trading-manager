from typing import Optional

from pydantic import BaseModel

DAY_MS = 24 * 3600 * 1000
WEEK_MS = 7 * DAY_MS


# TODO: replace other timespan references
class TimeSpan(BaseModel):
    ts_from: Optional[int] = None
    ts_to: Optional[int] = None

    def __init__(self, ts_from: Optional[int] = None, ts_to: Optional[int] = None):
        if ts_from is None and ts_to is None:
            from ke_client.utils import time_utils
            ts_to = time_utils.current_timestamp()
        ts_from = ts_from if ts_from is not None else ts_to - DAY_MS
        ts_to = ts_to if ts_to is not None else ts_from + DAY_MS
        if ts_to < ts_from:
            raise ValueError("Time from cannot be after time to")
        super().__init__(ts_from=ts_from, ts_to=ts_to)

    @staticmethod
    def last_week():
        from ke_client.utils import time_utils
        ts_to = time_utils.current_timestamp()
        ts_from = ts_to - WEEK_MS
        return TimeSpan(ts_from=ts_from, ts_to=ts_to)

    @staticmethod
    def last_day():
        from ke_client.utils import time_utils
        ts_to = time_utils.current_timestamp()
        ts_from = ts_to - DAY_MS
        return TimeSpan(ts_from=ts_from, ts_to=ts_to)
