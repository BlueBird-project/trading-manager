from typing import List, Optional, Dict

from fastapi import APIRouter

from tm.models.digital_twin import DigitalTwinDAO, DTForecastInfoDAO, DTForecastOfferDAO, DTForecastOfferDTO
from tm.models.job_dao import JobDAO
from tm.utils import TimeSpan

dt_router = APIRouter(prefix="", tags=["Digital Twin"])


@dt_router.get("")
async def list_dt() -> List[DigitalTwinDAO]:
    from tm.modules.tm_api import dt_service
    return dt_service.list_dt()


@dt_router.get("/jobs")
async def list_jobs() -> List[JobDAO]:
    from tm.modules.tm_api import dt_service
    return dt_service.list_jobs()


@dt_router.get("/jobs/{job_id}")
async def get_job(job_id: int) -> Optional[JobDAO]:
    from tm.modules.tm_api import dt_service
    return dt_service.get_job(job_id=job_id)


@dt_router.get("/market/{market_id}/job")
async def list_offer_forecast_info(market_id: int) -> Optional[JobDAO]:
    from tm.modules.tm_api import dt_service
    return dt_service.get_market_job(market_id=market_id)


@dt_router.post("/market/{market_id}/forecast/info")
async def list_offer_forecast_info(market_id: int, ts: Optional[TimeSpan] = None) -> List[DTForecastInfoDAO]:
    from tm.modules.tm_api import dt_service
    return dt_service.list_offer_forecast_info(market_id=market_id, ts=TimeSpan.non_empty(ts=ts))


@dt_router.get("/forecast_id/{forecast_id}")
async def get_offer_forecast(forecast_id: int) -> List[DTForecastOfferDAO]:
    from tm.modules.tm_api import dt_service
    return dt_service.get_offer_forecast(forecast_id=forecast_id)


@dt_router.post("/market/{market_id}/forecast/offer")
async def list_offer_forecast(market_id: int, ts: Optional[TimeSpan] = None) -> Dict[str, DTForecastOfferDTO]:
    from tm.modules.tm_api import dt_service
    return dt_service.list_offer_forecast(market_id=market_id, ts=TimeSpan.non_empty(ts=ts))


@dt_router.delete("/forecast/{forecast_id}")
async def get_forecast(forecast_id: int):
    from tm.modules.tm_api import dt_service
    dt_service.delete_forecast(forecast_id=forecast_id)
