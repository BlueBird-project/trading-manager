from dataclasses import dataclass
from typing import Optional

from pydantic import BaseModel


class DigitalTwinDAO(BaseModel):
    dt_id: Optional[int] = None
    job_id: Optional[int] = None
    # market_id: Optional[int] = None
    dt_uri: str
    update_ts: Optional[int] = None
    ext: Optional[str] = None


@dataclass
class DTModelDAO(BaseModel):
    isp_len: int
    isp_unit: int
    model_id: Optional[int] = None
    model_uri: Optional[int] = None
    model_name: Optional[int] = None
    model_description: Optional[int] = None
    update_ts: Optional[int] = None
    ext: Optional[str] = None


@dataclass
class DTForecastInfoDAO:
    ts: int
    job_id: int
    isp_len: int
    isp_unit: int
    range_id:int
    update_ts: Optional[int] = None
    forecast_id: Optional[int] = None
    forecast_uri: Optional[str] = None
    sequence: Optional[str] = None
    offer_id: Optional[int] = None
    model_id: Optional[int] = None


@dataclass
class DTForecastOfferDAO:
    forecast_id: int
    isp_start: int
    cost_mwh: Optional[float]
    ts: int
    isp_len: int = 1
