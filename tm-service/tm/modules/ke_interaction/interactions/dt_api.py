from typing import List, Dict, Any

from rdflib import URIRef

from tm.models.digital_twin import DTForecastInfoDAO
from tm.modules.ke_interaction.interactions.dt_model import DTPnt


def scan_forecast_info() -> Dict[str, List[DTForecastInfoDAO]]:
    """

    :return: dictionay of kb_id with list of forecasts details
    """
    from tm.modules.ke_interaction.interactions.dt_interactions import request_forecast_info
    from tm.modules.ke_interaction.interactions.dt_model import DTTSInfoRequest
    # e
    from tm.core.db.postgresql import dao_manager
    res = {}
    for dt_info in dao_manager.dt_api.list():
        dt_forecast = {}
        job = dao_manager.job_api.get(dt_info.job_id)
        market = dao_manager.market_api.get_market_by_id(market_id=job.market_id)
        offers = dao_manager.offer_dao.list_offer_info(ts=None, market_id=market.market_id)
        if dt_info.kb_id is not None:
            ts_infos: List[DTForecastInfoDAO] = request_forecast_info(req=[DTTSInfoRequest(
                forecast_of=URIRef(oi.offer_uri)) for oi in offers], kb_id=dt_info.kb_id)
            res[dt_info.kb_id] = ts_infos
    return res


def scan_forecast(forecast_info: Dict[str, List[DTForecastInfoDAO]]) -> Dict[Any, List[DTPnt]]:
    from tm.modules.ke_interaction.interactions.dt_interactions import request_forecast
    dt_forecast = {}
    for kb_id, fi_list in forecast_info.items():
        for fi in fi_list:
            ts = request_forecast(ts_uri=URIRef(fi.forecast_uri), kb_id=kb_id)
            dt_forecast.update(**ts)
    return dt_forecast
