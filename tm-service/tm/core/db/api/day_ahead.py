from abc import abstractmethod
from datetime import tzinfo, timezone
from typing import List, Union, Optional, Dict, Any, Tuple

from effi_onto_tools.db import TimeSpan
from effi_onto_tools.db.dao import DAO


class DayAheadAPI(DAO):
    def __init__(self, table_prefix: str):
        super(DayAheadAPI, self).__init__(table_prefix=table_prefix)

    @abstractmethod
    def log_day_offer(self, offer: List[Dict[str, Union[float, str, None]]]) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def offers_last_date(self, ) -> Optional[str]:
        pass

    @abstractmethod
    def get_offer_last_ts(self, ) -> Optional[int]:
        pass

    @abstractmethod
    def get_day_offer(self, date_str: str, isp_unit: Optional[int] = None) -> List[dict]:
        pass

    @abstractmethod
    def get_day_offer_by_ts(self, ts: int, isp_unit: Optional[int] = None) -> List[dict]:
        pass

    @abstractmethod
    def list_day_offer(self, ts: TimeSpan, isp_unit: Optional[int] = None) -> List[dict]:
        pass

    @abstractmethod
    def count_day_offer(self, ts: TimeSpan, isp_unit: int) -> Tuple[int, int, int]:
        pass

    @abstractmethod
    def list_day_offer_dates(self, ts: TimeSpan, isp_unit: int, tz: tzinfo = timezone.utc) -> List[str]:
        pass
