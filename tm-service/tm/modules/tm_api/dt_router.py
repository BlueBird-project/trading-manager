from typing import List, Optional

from fastapi import APIRouter

from tm.models.market import EnergyMarket
from tm.models.market_offer import EnergyMarketOfferInfo, RangeInfo, EnergyMarketOfferDAO, EnergyMarketOffer
from tm.utils import TimeSpan

router = APIRouter(prefix="dt", tags=["Digital Twin"])


# TODO:


@router.get("/")
async def list_dt() -> List[EnergyMarket]:
    from tm.modules.tm_api import service
    return service.list_dt()


@router.delete("/forecast/{forecast_id}")
async def list_dt(forecast_id: int, clear_timeseries: bool):
    from tm.modules.tm_api import service
    if clear_timeseries:
        service.clear_forecast(forecast_id=forecast_id)
    service.delete_forecast_by_id(forecast_id=forecast_id, clear_timeseries=clear_timeseries)


@router.delete("/forecast_uri/{forecast_uri}")
async def list_dt(forecast_uri: str, clear_timeseries: bool):
    from tm.modules.tm_api import service
    service.delete_forecast_by_uri(forecast_uri=forecast_uri, clear_timeseries=clear_timeseries)
