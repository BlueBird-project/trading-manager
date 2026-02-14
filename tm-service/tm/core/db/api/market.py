from abc import abstractmethod
from datetime import tzinfo, timezone
from typing import List, Union, Optional, Dict, Any, Tuple

from effi_onto_tools.db import TimeSpan
from effi_onto_tools.db.dao import DAO

from tm.models.market import EnergyMarket


class MarketAPI(DAO):
    def __init__(self, table_prefix: str):
        super(MarketAPI, self).__init__(table_prefix=table_prefix)

    @abstractmethod
    def save_market(self, market: EnergyMarket) -> EnergyMarket:
        pass

    @abstractmethod
    def list_market(self, ) -> List[EnergyMarket]:
        pass

    @abstractmethod
    def list_subscribed_market(self, ) -> List[EnergyMarket]:
        pass

    @abstractmethod
    def get_market(self, market_uri: str) -> EnergyMarket:
        pass
