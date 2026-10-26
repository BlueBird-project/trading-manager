from dataclasses import dataclass
from typing import Optional, List

from pydantic import BaseModel
from rdflib import URIRef


@dataclass
class CapacityNotification:
    asset_manager_uri: str
    flex_instruction_uri: str
    flex_offer_uri: str
    flex_profile_uri: str
    power_limit_uri: str
    ts: int
    max_consumption_uri: str
    max_consumption: float
    update_ts: Optional[int] = None
