from typing import List, Optional, Dict, Any

from fastapi import APIRouter
from ke_client.utils import time_utils
from tm.utils import TimeSpan

ki_router = APIRouter(prefix="", tags=["KI"])


@ki_router.get("/dam/scan")
@ki_router.post("/dam/scan")
async def dam_scan() -> Dict[str, Any]:
    res = {}
    from tm.modules.ke_interaction.interactions.dam_interactions import get_all_markets
    from tm.modules.ke_interaction.interactions.dam_interactions import get_current_market_offer_info
    from tm.modules.ke_interaction.interactions.dam_interactions import get_market_offer
    res["markets"] = [m.n3() for m in get_all_markets(False)]
    offer_infos = get_current_market_offer_info()
    res["info_uris"] = [o.n3() for o in offer_infos]
    offer = get_market_offer(offer_uris=[offer_info.offer_uri for offer_info in offer_infos])
    res["market_offer"] = offer
    return res


@ki_router.get("/dt/scan", description="returns List[DigitalTwinInfoACK]")
@ki_router.post("/dt/scan", description="returns List[DigitalTwinInfoACK]")
# async def dt_scan() -> List[DigitalTwinInfoACK]:
async def dt_scan() -> List[Dict[str, Any]]:
    from tm.modules.ke_interaction.interactions.dt_interactions import request_dt_info
    dt_ack = request_dt_info()
    return [b.n3() for b in dt_ack]


@ki_router.get("/dt/forecast")
@ki_router.post("/dt/forecast")
async def scan_forecast() -> Dict[str, Any]:
    res = {}
    from tm.modules.ke_interaction.interactions.dt_interactions import request_dt_ts_info, request_dt_data_by_id
    ts_info = request_dt_ts_info(req=[])
    res["ts_info"] = ts_info
    for uri in ts_info:
        ts = request_dt_data_by_id(ts_uri_ref=uri.ts_uri)
        res[uri.ts_uri] = [pnt.n3() for pnt in ts]

    return res


@ki_router.get("/fm/ask/flex_info", description="returns List[FMTSResponse]")
@ki_router.post("/fm/ask/flex_info", description="returns List[FMTSResponse]")
async def flex_info(ts: Optional[TimeSpan] = None) -> List[Dict[str, Any]]:
    # async def flex_info(ts: Optional[TimeSpan] = None) -> List[FMTSResponse]:
    from tm.modules.ke_interaction.interactions.fm_interactions import request_ts_info
    if ts is None:
        cur_ts = time_utils.current_timestamp()
        ts = TimeSpan(ts_from=cur_ts, ts_to=cur_ts + 3600 * 1000 * 24)
    return [t.n3() for t in request_ts_info(ts=ts)]


@ki_router.post("/fm/ask/flex_ts", description="returns List[FMPnt]")
async def flex_ts(ts_uri: str) -> List[Dict[str, Any]]:
    # async def flex_ts(ts_uri: str) -> List[FMPnt]:
    from tm.modules.ke_interaction.interactions.fm_interactions import request_data
    return [r.n3() for r in request_data(ts_uris=[ts_uri])]
