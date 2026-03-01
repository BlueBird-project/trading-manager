from typing import Optional

from pydantic import BaseModel


class DigitalTwinDAO(BaseModel):
    dt_id: Optional[int] = None
    market_id: Optional[int] = None
    job_id: Optional[int] = None
    dt_uri: str
    update_ts: Optional[int] = None
    ext: Optional[str] = None
