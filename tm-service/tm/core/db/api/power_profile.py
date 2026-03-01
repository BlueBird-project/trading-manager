from abc import abstractmethod
from typing import List, Dict, Any

from effi_onto_tools.db import TimeSpan
from effi_onto_tools.db.dao import DAO

from tm.models.power_profile import PowerSchedule


class DayAheadAPI(DAO):
    def __init__(self, table_prefix: str):
        super(DayAheadAPI, self).__init__(table_prefix=table_prefix)

    @abstractmethod
    def log_schedule(self,agent_id:str, schedule: PowerSchedule,forecast:bool=False) -> List[Dict[str, Any]]:
        pass
    @abstractmethod
    def get_schedule(self,agent_id:str, ts: TimeSpan, isp_unit: int) -> PowerSchedule:
        pass

