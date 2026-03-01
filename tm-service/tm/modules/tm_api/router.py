from typing import List, Optional

from effi_onto_tools.db import TimeSpan
from fastapi import APIRouter

from tm.models.market import EnergyMarket
from tm.models.market_offer import EnergyMarketOfferInfo, RangeInfo, EnergyMarketOffer

router = APIRouter(prefix="")


@router.get("/market")
async def list_markets() -> List[EnergyMarket]:
    from tm.modules.tm_api import service
    return service.list_markets()


@router.get("/market/{market_id}/offerinfo")
async def get_market_offer_info(market_id: int, ts_from: Optional[int] = None, ts_to: Optional[int] = None,
                                granularity: Optional[int] = None) -> List[EnergyMarketOfferInfo]:
    from tm.modules.tm_api import service
    ts = TimeSpan(ts_from=ts_from, ts_to=ts_to)
    return service.list_offer_info(market_id=market_id, ts=ts, granularity=granularity)


@router.get("/market/{market_id}/offer")
async def get_market_offer(market_id: int, ts_from: Optional[int] = None, ts_to: Optional[int] = None,
                           granularity: Optional[int] = None) -> List[EnergyMarketOffer]:
    from tm.modules.tm_api import service
    ts = TimeSpan(ts_from=ts_from, ts_to=ts_to)
    return service.list_offer(market_id=market_id, ts=ts, granularity=granularity)


@router.get("/offer/", deprecated=True)
async def list_offer(ts_from: Optional[int] = None, ts_to: Optional[int] = None,
                     granularity: Optional[int] = None) -> List[EnergyMarketOfferInfo]:
    from tm.modules.tm_api import service
    ts = TimeSpan(ts_from=ts_from, ts_to=ts_to)
    return service.list_offer_info(market_id=None, ts=ts, granularity=granularity)


@router.get("/offer/{offer_id}")
async def get_offer(offer_id: int) -> List[EnergyMarketOffer]:
    from tm.modules.tm_api import service
    return service.get_offer(offer_id=offer_id)


@router.get("/range")
async def get_range(min_value: Optional[float] = None, max_value: Optional[float] = None) -> Optional[RangeInfo]:
    from tm.modules.tm_api import service
    return service.get_range(min_value=min_value, max_value=max_value)


@router.post("/range")
async def add_range(min_value: Optional[float] = None, max_value: Optional[float] = None) -> RangeInfo:
    from tm.modules.tm_api import service
    return service.add_range(min_value=min_value, max_value=max_value)
