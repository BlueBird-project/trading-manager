from collections import defaultdict
from typing import List, Dict, Callable

from ke_client import rdf_nil, BindingsBase
from ke_client.utils import time_utils
from rdflib import URIRef, Literal

from tm.core.db.postgresql import dao_manager
from tm.models.market_offer import EnergyMarketOfferInfo, EnergyMarketOffer
from tm.modules.ke_interaction.interactions.fm_model import FMTSSplitURI, DPSplitURI, \
    FMEvaluateResponseAsk, FMEvaluateQueryAsk, FMEvaluateQuery, FMEvaluateResponse
from tm.utils import TimeSpan


def _evaluate(input_bindings: List[FMEvaluateQuery], kb_id: str,
              out_initializer: Callable[[FMEvaluateQuery, str, float], BindingsBase]):
    from tm.modules.ke_interaction.interactions.tm_uris import OfferDPSplitURIFiltered
    response = []
    min_ts = min([m.ts_ms for m in input_bindings]) - 30 * 60 * 1000  # 30minutes
    max_ts = max([m.ts_ms for m in input_bindings]) + 30 * 60 * 1000  # 30minutes
    # TODO: set global isp unit to 15 minutes
    # TODO: select best market and sequence
    offers = dao_manager.offer_dao.list_offer_info(ts=TimeSpan(ts_from=min_ts, ts_to=max_ts), isp_unit=15)
    offer_map: Dict[str, List[EnergyMarketOfferInfo]] = defaultdict(list)
    if len(offers) == 0:
        return []
    for offer_info in offers:
        offer_map[f"{offer_info.market_id}_{offer_info.sequence}"].append(offer_info)
    # TODO: select best market and sequence
    offers_key: str = next(iter(offer_map))
    # for market_offers in offer_map.values():
    market_offers = offer_map[offers_key]

    offer_ts: List[EnergyMarketOffer] = []
    for offer_info in market_offers:
        offer_ts += dao_manager.offer_dao.get_market_offer(offer_id=offer_info.offer_id)
    # TODO: sort query by timestamp (and reduce loop iterations)
    for f_pnt in input_bindings:
        for i in range(len(offer_ts) - 1):
            prev_pnt = offer_ts[i]
            next_pnt = offer_ts[i + 1]
            if prev_pnt.ts <= f_pnt.ts_ms < next_pnt.ts:
                dp_uri = OfferDPSplitURIFiltered(prefix=kb_id, period_minutes=prev_pnt.isp_len,
                                                 offer_id=prev_pnt.offer_id,
                                                 isp_start=prev_pnt.isp_start).uri

                tou_price = out_initializer(f_pnt, dp_uri, prev_pnt.cost_mwh * f_pnt.convert_value(f_pnt.value, float))
                # FMEvaluateResponse(cost_dp=URIRef(dp_uri), cost_dpr=URIRef(dp_uri + "/dpr"),
                #                    cost=Literal(
                #                        prev_pnt.cost_mwh * f_pnt.convert_value(f_pnt.value, float)))
                response.append(tou_price)
                continue

    return response


# def evaluate(q: List[FMEvaluateQuery]):

def evaluate(query: List[FMEvaluateQuery], kb_id: str) -> List[FMEvaluateResponse]:
    def out_initializer(f_pnt: FMEvaluateQuery, dp_uri: str, cost: float):
        return FMEvaluateResponse(cost_dp=URIRef(dp_uri), cost_dpr=URIRef(dp_uri + "/dpr"),
                                  cost=Literal(cost))

    return _evaluate(input_bindings=query, kb_id=kb_id, out_initializer=out_initializer)


def evaluate_ask(query: List[FMEvaluateQueryAsk], kb_id: str) -> List[FMEvaluateResponseAsk]:
    def out_initializer(f_pnt: FMEvaluateQuery, dp_uri: str, cost: float):
        return FMEvaluateResponseAsk(ts_uri=f_pnt.ts_uri, dp=f_pnt.dp, ts=f_pnt.ts, dpr=f_pnt.dpr, value=f_pnt.value,
                                     cost_dp=URIRef(dp_uri), cost_dpr=URIRef(dp_uri + "/dpr"), cost=Literal(cost))

    return _evaluate(input_bindings=query, kb_id=kb_id, out_initializer=out_initializer)
