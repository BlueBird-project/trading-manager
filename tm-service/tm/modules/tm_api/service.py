from typing import List, Optional

from effi_onto_tools.db import TimeSpan

from tm.models.market import EnergyMarket
from tm.models.market_offer import EnergyMarketOfferInfo, RangeInfo, EnergyMarketOffer


def list_markets() -> List[EnergyMarket]:
    from tm.core.db.postgresql import dao_manager
    return dao_manager.market_api.list_market()


def list_offer_info(market_id, ts: TimeSpan, granularity: Optional[int] = None) -> List[EnergyMarketOfferInfo]:
    from tm.core.db.postgresql import dao_manager
    return dao_manager.offer_dao.list_offer_info(market_id=market_id, ts=ts, isp_unit=granularity)


def list_offer(market_id: int, ts: TimeSpan, granularity: Optional[int] = None) -> List[EnergyMarketOffer]:
    from tm.core.db.postgresql import dao_manager
    return dao_manager.offer_dao.list_market_offer(ts=ts, market_id=market_id, isp_unit=granularity)


def get_offer(offer_id: int) -> List[EnergyMarketOffer]:
    from tm.core.db.postgresql import dao_manager
    return dao_manager.offer_dao.get_market_offer(offer_id=offer_id)


def get_range(min_value: Optional[float] = None, max_value: Optional[float] = None) -> Optional[RangeInfo]:
    from tm.core.db.postgresql import dao_manager
    return dao_manager.offer_dao.get_range(min_value=min_value, max_value=max_value)


def add_range(min_value: Optional[float] = None, max_value: Optional[float] = None) -> RangeInfo:
    from tm.core.db.postgresql import dao_manager
    return dao_manager.offer_dao.add_range(RangeInfo(min_value=min_value, max_value=max_value))
