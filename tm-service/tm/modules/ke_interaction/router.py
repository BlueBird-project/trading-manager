from typing import List, Optional, Dict, Any

from effi_onto_tools.db import TimeSpan
from fastapi import APIRouter
from ke_client.utils import time_utils

from tm.modules.ke_interaction.interactions.dt_model import DigitalTwinInfoACK
from tm.modules.ke_interaction.interactions.fm_model import FMTSResponse, FMPnt

ki_router = APIRouter(prefix="")


@ki_router.get("/dam/scan")
@ki_router.post("/dam/scan")
async def dam_scan() -> Dict[str, Any]:
    res = {}
    from tm.modules.ke_interaction.interactions.dam_interactions import get_all_markets
    from tm.modules.ke_interaction.interactions.dam_interactions import get_current_market_offer_info
    from tm.modules.ke_interaction.interactions.dam_interactions import get_market_offer
    res["markets"] = get_all_markets(False)
    offer_infos = get_current_market_offer_info()
    res["info_uris"] = offer_infos
    offer = get_market_offer(offer_uris=[offer_info.offer_uri for offer_info in offer_infos])
    res["market_offer"] = offer
    return res


@ki_router.get("/dt/scan")
@ki_router.post("/dt/scan")
async def dt_scan() -> List[DigitalTwinInfoACK]:
    from tm.modules.ke_interaction.interactions.dt_interactions import request_dt_info
    dt_ack = request_dt_info()
    return dt_ack


@ki_router.get("/dt/forecast")
@ki_router.post("/dt/forecast")
async def scan_forecast() -> Dict[str, Any]:
    res = {}
    from tm.modules.ke_interaction.interactions.dt_interactions import request_dt_ts_info, request_dt_data_by_id
    ts_info = request_dt_ts_info(req=[])
    res["ts_info"] = ts_info
    for uri in ts_info:
        ts = request_dt_data_by_id(ts_uri_ref=uri.ts_uri)
        res[uri] = ts

    return res


@ki_router.get("/fm/ask/flex_info")
@ki_router.post("/fm/ask/flex_info")
async def flex_info(ts: Optional[TimeSpan] = None) -> List[FMTSResponse]:
    from tm.modules.ke_interaction.interactions.fm_interactions import request_ts_info
    if ts is None:
        cur_ts = time_utils.current_timestamp()
        ts = TimeSpan(ts_from=cur_ts, ts_to=cur_ts + 3600 * 1000 * 24)
    return request_ts_info(ts=ts)


@ki_router.get("/fm/ask/flex_ts/{ts_uri}}")
@ki_router.post("/fm/ask/flex_ts")
async def flex_ts(ts_uri: str) -> List[FMPnt]:
    from tm.modules.ke_interaction.interactions.fm_interactions import request_data
    return request_data(ts_uris=[ts_uri])
