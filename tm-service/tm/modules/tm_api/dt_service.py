from collections import defaultdict
from typing import List, Dict, Optional

from tm.models.digital_twin import DigitalTwinDAO, DTForecastInfoDAO, DTForecastOfferDAO, DTForecastOfferDTO
from tm.models.job_dao import JobDAO
from tm.utils import TimeSpan


def list_dt() -> List[DigitalTwinDAO]:
    from tm.core.db.postgresql import dao_manager
    return dao_manager.dt_api.list()


def list_jobs() -> List[JobDAO]:
    from tm.core.db.postgresql import dao_manager
    return dao_manager.job_api.list()


def get_job(job_id: int) -> Optional[JobDAO]:
    from tm.core.db.postgresql import dao_manager
    return dao_manager.job_api.get(job_id=job_id)


def get_market_job(market_id: int) -> Optional[JobDAO]:
    from tm.core.db.postgresql import dao_manager
    return dao_manager.job_api.get_by_market(market_id=market_id)


# def get_market_job(market_id:int) -> JobDAO:
#     from tm.core.db.postgresql import dao_manager
#     return dao_manager.job_api.get_by_market(market_id=market_id)


def list_offer_forecast_info(market_id: int, ts: TimeSpan) -> List[DTForecastInfoDAO]:
    from tm.core.db.postgresql import dao_manager
    job_dao: JobDAO = dao_manager.job_api.get_by_market(market_id=market_id)

    if job_dao is None:
        raise KeyError(f"JOB or market not found for market_id: {market_id}")
    return dao_manager.forecast_api.list_forecasts(job_id=job_dao.job_id, ts=ts)


def list_offer_forecast(market_id: int, ts: TimeSpan) -> Dict[str, DTForecastOfferDTO]:
    from tm.core.db.postgresql import dao_manager
    f_info_list = list_offer_forecast_info(market_id=market_id, ts=ts)
    offers = dao_manager.forecast_api.get_offers(forecast_ids=[f_info.forecast_id for f_info in f_info_list])
    res = {f_dto.id: f_dto
           for f_dto in
           [DTForecastOfferDTO(offers=[], forecast_id=f_info.forecast_id, forecast_uri=f_info.forecast_uri)
            for f_info in f_info_list]
           }
    id_map = {f.forecast_id: f.id for f in res.values()}
    for offer in offers:
        res[id_map[offer.forecast_id]].offers.append(offer)
    return res


def get_offer_forecast(forecast_id) -> List[DTForecastOfferDAO]:
    from tm.core.db.postgresql import dao_manager
    return dao_manager.forecast_api.get_offer(forecast_id=forecast_id)


def delete_forecast(forecast_id):
    from tm.core.db.postgresql import dao_manager
    dao_manager.forecast_api.clear_forecast_offer(forecast_id=forecast_id)
    dao_manager.forecast_api.delete_forecast(forecast_id=forecast_id)
