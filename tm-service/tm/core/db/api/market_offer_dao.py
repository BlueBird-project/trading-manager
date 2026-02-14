from abc import abstractmethod
from typing import List, Optional, Dict

from effi_onto_tools.db import TimeSpan
from effi_onto_tools.db.dao import DAO
from tm.models.market_offer import EnergyMarketOfferInfo, RangeInfo, EnergyMarketOffer


class MarketOfferAPI(DAO):
    def __init__(self, table_prefix: str):
        super(MarketOfferAPI, self).__init__(table_prefix=table_prefix)

    @abstractmethod
    def register_offer(self, market_offer: EnergyMarketOfferInfo) -> EnergyMarketOfferInfo:
        pass

    @abstractmethod
    def list_offer_info(self, ts: TimeSpan, market_id: Optional[int] = None, isp_unit: Optional[int] = None) -> List[
        EnergyMarketOfferInfo]:
        pass

    @abstractmethod
    def get_offer_info(self, offer_uri: str) -> EnergyMarketOfferInfo:
        pass

    @abstractmethod
    def add_range(self, range_info: RangeInfo) -> RangeInfo:
        pass

    @abstractmethod
    def get_range(self, min_value: Optional[float] = None, max_value: Optional[float] = None) -> Optional[RangeInfo]:
        pass

    @abstractmethod
    def list_range(self, min_value: Optional[float] = None, max_value: Optional[float] = None) -> List[RangeInfo]:
        pass

    @abstractmethod
    def add_offer(self, market_offer_items: List[EnergyMarketOffer]) -> List[Dict]:
        pass

    @abstractmethod
    def clear_market_offer(self, offer_id) -> int:
        pass

    # TODO anothermethod: list subscribed offers
    @abstractmethod
    def list_market_offer(self, ts: TimeSpan, market_id: Optional[int] = None,
                          isp_unit: Optional[int] = None) -> List[EnergyMarketOffer]:
        pass

    @abstractmethod
    def get_market_offer(self, offer_id: int) -> List[EnergyMarketOffer]:
        pass
