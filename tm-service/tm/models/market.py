from typing import Optional

from pydantic import BaseModel


class EnergyMarket(BaseModel):
    market_id: Optional[int] = None
    market_uri: str
    market_name: Optional[str] = None
    market_type: Optional[str] = None
    market_description: Optional[str] = None
    market_location: Optional[str] = None
    isp_unit: Optional[int] = None
    isp_len: Optional[int] = None
    update_ts: Optional[int] = None
    subscribe: Optional[bool] = None
    ext: Optional[str] = None
