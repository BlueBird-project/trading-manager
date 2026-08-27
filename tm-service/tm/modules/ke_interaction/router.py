from datetime import timedelta
from typing import List, Optional, Dict, Any

from fastapi import APIRouter
from isodate import duration_isoformat
from rdflib import URIRef, Literal

from tm.models.digital_twin import DigitalTwinDAO
from tm.modules.ke_interaction.interactions.dam_model import MarketType
from tm.utils import TimeSpan

ki_router = APIRouter(prefix="", tags=["KI"])


@ki_router.post("/dam/scan", description="Scan for available markets in the network,"
                                         " current offers metadata and current offers time series")
# @ki_router.get("/dam/scan")
async def dam_scan(isp_unit: int = 15, ts_from: Optional[int] = None, ts_to: Optional[int] = None) -> Dict[str, Any]:
    res = {}
    from tm.modules.ke_interaction.interactions.dam_interactions import get_all_markets
    from tm.modules.ke_interaction.interactions.dam_interactions import get_current_market_offer_info
    from tm.modules.ke_interaction.interactions.dam_interactions import get_market_offer
    res["markets"] = [m.n3() for m in get_all_markets(False)]
    # TODO: iterate overdays when ti is very long
    offer_infos = get_current_market_offer_info(isp_unit=isp_unit, ti=TimeSpan(ts_from=ts_from, ts_to=ts_to))
    res["offer_info_uri"] = [o.n3() for o in offer_infos]
    offer = get_market_offer(offer_uris=[offer_info.offer_uri for offer_info in offer_infos])
    res["market_offer_ts"] = offer
    return res


# @ki_router.get("/dt/scan", description="returns List[DigitalTwinInfoACK]")
@ki_router.post("/dt/scan", response_description="returns List[DigitalTwinInfoACK]",
                description="Scan for available digital twin services in KE network")
# async def dt_scan() -> List[DigitalTwinInfoACK]:
async def dt_scan() -> List[DigitalTwinDAO]:
    from tm.modules.ke_interaction.interactions.dt_interactions import request_dt_info
    dt_dao = request_dt_info()
    return dt_dao


# @ki_router.get("/dt/forecast")
@ki_router.post("/dt/forecast", description="Request for forecast from DT ")
async def scan_forecast() -> List[Dict[str, Any]]:
    from tm.modules.ke_interaction.interactions.dt_interactions import request_forecast_info, request_forecast
    from tm.modules.ke_interaction.interactions.dt_model import DTTSInfoRequest
    # e
    from tm.core.db.postgresql import dao_manager
    res = []
    for dt_info in dao_manager.dt_api.list():
        dt_forecast = {}
        job = dao_manager.job_api.get(dt_info.job_id)
        market = dao_manager.market_api.get_market_by_id(market_id=job.market_id)
        offers = dao_manager.offer_dao.list_offer_info(ts=None, market_id=market.market_id)
        # mt: MarketTypeValue = MarketType.parse(market.market_type).value

        if dt_info.kb_id is not None:
            ts_info = request_forecast_info(req=[DTTSInfoRequest(
                forecast_of=URIRef(oi.offer_uri)) for oi in offers], kb_id=dt_info.kb_id)
            dt_forecast["ts_info"] = ts_info
            for uri in ts_info:
                ts = request_forecast(ts_uri=URIRef(uri.forecast_uri), kb_id=dt_info.kb_id)
                # ask_test(ts_uri_ref=URIRef( uri.forecast_uri))
                dt_forecast.update(**ts)
                # res[uri.ts_uri] = [ts[uri.ts_uri]]
            res.append(dt_forecast)

    return res


# @ki_router.get("/fm/ask/flex_info", description="returns List[FMTSResponse]")
@ki_router.post("/fm/ask/flex_info", response_description="returns List[FMTSResponse]",
                description="request for flexibility from FM")
async def flex_info(ts: Optional[TimeSpan] = None) -> List[Dict[str, Any]]:
    # async def flex_info(ts: Optional[TimeSpan] = None) -> List[FMTSResponse]:
    from tm.modules.ke_interaction.interactions.fm_interactions import request_ts_info
    return [t.n3() for t in request_ts_info(ts=TimeSpan.non_empty(ts=ts))]


@ki_router.post("/fm/ask/flex_ts", response_description="returns List[FMPnt]",
                description="Request flexibility timeseries")
async def flex_ts(ts_uri: str) -> List[Dict[str, Any]]:
    # async def flex_ts(ts_uri: str) -> List[FMPnt]:
    from tm.modules.ke_interaction.interactions.fm_interactions import request_data
    return [r.n3() for r in request_data(ts_uris=[ts_uri])]


@ki_router.get("/tou", response_description="returns List[FMPnt]",
               description="tou test")
async def flex_ts() -> List[Dict[str, Any]]:
    # sprawdzic
    from tm.modules.ke_interaction.interactions.tm_model import TOUPriceInfoQueryFiltered, TOUPriceQuery
    from tm.modules.ke_interaction.service.tou_service import get_price_filtered, get_range_tou_filtered
    from tm.modules.ke_interaction.interactions.tm_interactions import tm_ki
    from tm.core.db.postgresql import dao_manager
    ts = TimeSpan()

    range_id = dao_manager.offer_dao.get_range().range_id
    info_q = TOUPriceInfoQueryFiltered.init()

    from tm.modules.ke_interaction.interactions.client import ki_client

    info_resp = get_range_tou_filtered(binding_query=[info_q], kb_id=ki_client.kb_id)
    price_q = [TOUPriceQuery(tou_uri=info.tou_uri) for info in info_resp]
    # async def flex_ts(ts_uri: str) -> List[FMPnt]:
    # q = TOUPriceQuery(tou_uri=uri)
    prices = get_price_filtered(binding_query=price_q, kb_id=tm_ki.get_kb_id())
    return [p.__dict__ for p in prices]


@ki_router.get("/tou/offer_info", response_description="returns List[FMPnt]",
               description="tou test")
async def tou_offer_info() -> list[Dict]:
    # sprawdzic
    from tm.modules.ke_interaction.interactions.tm_model import TOUPriceInfoQueryFiltered
    from tm.modules.ke_interaction.service.tou_service import get_range_tou_filtered
    from tm.core.db.postgresql import dao_manager
    ts = TimeSpan.last_day()

    range_id = dao_manager.offer_dao.get_range().range_id
    info_q = TOUPriceInfoQueryFiltered.init()

    from tm.modules.ke_interaction.interactions.client import ki_client

    info_resp = get_range_tou_filtered(binding_query=[info_q], kb_id=ki_client.kb_id)
    # todo zwracac informacje o sequence
    return [{**vars(i)} for i in info_resp]
