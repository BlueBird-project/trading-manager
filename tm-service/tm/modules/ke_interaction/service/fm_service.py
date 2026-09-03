from collections import defaultdict
from typing import List, Dict, Callable, Union

from ke_client import   BindingsBase
from rdflib import URIRef, Literal

from tm.core.db.postgresql import dao_manager
from tm.models.digital_twin import DTForecastInfoDAO, DTForecastOfferDAO
from tm.models.market_offer import EnergyMarketOfferInfo, EnergyMarketOffer, EnergyMarketOfferDAO
from tm.modules.ke_interaction.interactions.fm_model import FMTSSplitURI, DPSplitURI, \
    FMEvaluateResponseAsk, FMEvaluateQueryAsk, FMEvaluateQuery, FMEvaluateResponse
from tm.utils import TimeSpan


def _get_offer_dp(max_ts, min_ts) -> List[Union[EnergyMarketOffer, DTForecastOfferDAO]]:
    # TODO: set global isp unit to 15 minutes
    # TODO: select best market and sequence
    offers = dao_manager.offer_dao.list_offer_info(ts=TimeSpan(ts_from=min_ts, ts_to=max_ts), isp_unit=15)
    offer_ts: List[Union[EnergyMarketOfferDAO, DTForecastOfferDAO]] = []
    if len(offers) == 0:
        for market in dao_manager.market_api.list_subscribed_market():
            job = dao_manager.job_api.get_by_market(market_id=market.market_id)
            if job is not None:
                forecasted_offers: List[DTForecastInfoDAO] = \
                    dao_manager.forecast_api.find_forecasts(ts=TimeSpan(ts_from=min_ts, ts_to=max_ts),
                                                            job_id=job.job_id, model_id=None, sequence=None,
                                                            range_id=None)
                if len(forecasted_offers) > 0:
                    offer_ts += dao_manager.forecast_api.get_offer(forecast_id=forecasted_offers[0].forecast_id)
                    break

    else:
        offer_map: Dict[str, List[EnergyMarketOfferInfo]] = defaultdict(list)
        for offer_info in offers:
            offer_map[f"{offer_info.market_id}_{offer_info.sequence}"].append(offer_info)
        offers_key: str = next(iter(offer_map))
        market_offers = offer_map[offers_key]
        for offer_info in market_offers:
            offer_ts += dao_manager.offer_dao.get_market_offer(offer_id=offer_info.offer_id)
        last_offer = market_offers[len(market_offers) - 1]
        forecasted_offers: List[DTForecastInfoDAO] = dao_manager.forecast_api.get_offer_forecasts(
            offer_id=last_offer.offer_id, model_id=None)
        if len(forecasted_offers) > 0:
            offer_ts += dao_manager.forecast_api.get_offer(forecast_id=forecasted_offers[0].forecast_id)
    return offer_ts


def _evaluate(input_bindings: List[FMEvaluateQuery], kb_id: str,
              out_initializer: Callable[[FMEvaluateQuery, str, URIRef, float], BindingsBase]) -> List[BindingsBase]:
    from tm.modules.ke_interaction.interactions.tm_uris import OfferDPSplitURIFiltered
    response: List[BindingsBase] = []
    min_ts = min([m.ts_ms for m in input_bindings]) - 30 * 60 * 1000  # 30minutes
    max_ts = max([m.ts_ms for m in input_bindings]) + 30 * 60 * 1000  # 30minutes
    offer_ts: List[Union[EnergyMarketOffer, DTForecastOfferDAO]] = _get_offer_dp(max_ts, min_ts)
    # TODO: sort query by timestamp (and reduce loop iterations)
    for f_pnt in input_bindings:
        for i in range(len(offer_ts) - 1):
            prev_pnt = offer_ts[i]
            next_pnt = offer_ts[i + 1]
            if prev_pnt.ts <= f_pnt.ts_ms < next_pnt.ts:
                dp_uri = OfferDPSplitURIFiltered(prefix=kb_id, period_minutes=prev_pnt.isp_len,
                                                 offer_id=prev_pnt.offer_id,
                                                 isp_start=prev_pnt.isp_start).uri
                cost_value = prev_pnt.cost_mwh * f_pnt.convert_value(f_pnt.value, float)

                cost_dpr_type: URIRef = prev_pnt.get_value_type()
                tou_price = out_initializer(f_pnt, dp_uri, cost_dpr_type, cost_value)
                response.append(tou_price)
                break

    return response



def evaluate(query: List[FMEvaluateQuery], kb_id: str) -> List[BindingsBase]:
    """
    Get cost for a given power consumption timeseries
    :param query:
    :param kb_id:
    :return:
    """
    def out_initializer(f_pnt: FMEvaluateQuery, dp_uri: str, cost_dpr_type: URIRef, cost: float):
        return FMEvaluateResponse(dp=URIRef(f_pnt.dp), cost_dpr=URIRef(dp_uri + "/dpr"),
                                  cost=Literal(cost), cost_dpr_type=cost_dpr_type)

    return _evaluate(input_bindings=query, kb_id=kb_id, out_initializer=out_initializer)


def evaluate_ask(query: List[FMEvaluateQueryAsk], kb_id: str) -> List[BindingsBase]:
    """

    Get cost for a given power consumption timeseries
    :param query:
    :param kb_id:
    :return:
    """
    def out_initializer(f_pnt: FMEvaluateQuery, dp_uri: str, cost_dpr_type: URIRef, cost: float):
        return FMEvaluateResponseAsk(ts_uri=f_pnt.ts_uri, dp=f_pnt.dp, ts=f_pnt.ts, dpr=f_pnt.dpr,
                                     value=f_pnt.value,
                                     cost_dpr=URIRef(dp_uri + "/dpr"), cost_dpr_type=cost_dpr_type,
                                     cost=Literal(cost))

    return _evaluate(input_bindings=query, kb_id=kb_id, out_initializer=out_initializer)
