from typing import Optional, List

from pydantic import BaseModel


class PowerPnt(BaseModel):
    ts: int
    isp_len: int = 1
    power: float
    min_pow: Optional[float] = None
    max_pow: Optional[float] = None
    cost: Optional[float] = None


class PowerSchedule(BaseModel):
    ts: int
    init_ts: Optional[int] = None
    granularity: int
    data: List[PowerPnt]
    cost: Optional[float] = None
