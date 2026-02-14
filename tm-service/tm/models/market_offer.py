from typing import Optional

from pydantic import BaseModel


class EnergyMarketOfferInfo(BaseModel):
    offer_id: Optional[int] = None
    market_id: int
    ts: int
    date_str: str
    offer_uri: Optional[str]
    sequence: Optional[str]
    isp_unit: int
    isp_len: int
    update_ts: Optional[int] = None
    ext: Optional[str] = None




# TODO: add offer range to graphs and ontology
class EnergyMarketOffer(BaseModel):
    offer_id: int
    isp_start: int
    range_id: int
    cost_mwh: Optional[float]
    ts: int
    isp_len: int = 1


class RangeInfo(BaseModel):
    range_id: Optional[int] = None
    min_value: Optional[float]
    max_value: Optional[float]
