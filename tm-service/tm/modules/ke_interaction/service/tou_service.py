from typing import List

from isodate import parse_duration
from rdflib.util import from_n3
from ubflex.rdf import UBMARKET_FORECAST
from ubflex.rdf.saref.saref4ener import SAREF4ENER_TIMESERIES

from tm.models.digital_twin import DTForecastOfferDAO
from tm.models.job_dao import JobDAO
from tm.models.market_offer import RangeInfo, EnergyMarketOfferDAO
from tm.modules.ke_interaction import KIVars
from tm.modules.ke_interaction.interactions.ki_models import DurationURI
from tm.modules.ke_interaction.interactions.tm_model import *
from tm.modules.ke_interaction.interactions.tm_uris import *
from tm.utils import TimeSpan


# def get_all_tou(binding_query: List[TOUPriceInfoSimpleQuery]) -> List[TOUPriceInfoSimpleResponse]:
#     from tm.core.db.postgresql import dao_manager
#     for q in binding_query:
#         ts_from = time_utils.xsd_to_ts(q.time_create.value)
#         # time_span_ms =  from_n3(KIVars.DAY_DURATION)
#         time_span_ms = int(parse_duration(q.tou_period, as_timedelta_if_possible=True).total_seconds() * 1000)
#         range_id = dao_manager.offer_dao.get_range(None, None).range_id
#         # tou_uriref = tou_uri_parser.n3(TOUSplitURI(range_id=range_id,
#         period_minutes=time_span_ms / 60000, ts=ts_from))
#         tou_uriref = TOUSplitURI(range_id=range_id, period_minutes=time_span_ms / 60000, ts=ts_from).uri_ref
#         kwargs = {**q.__dict__, **{"tou_uri": tou_uriref}}
#         return [TOUPriceInfoSimpleResponse(**kwargs).n3()]


# def get_range_tou(binding_query: List[TOUPriceInfoQuery], kb_id: str) -> List[TOUPriceInfo]:
#     from tm.core.db.postgresql import dao_manager
#     for q in binding_query:
#         ts_from = time_utils.xsd_to_ts(q.time_create.value)
#         # time_span_ms =  from_n3(KIVars.DAY_DURATION)
#         time_span_ms = int(parse_duration(q.tou_period, as_timedelta_if_possible=True).total_seconds() * 1000)
#         if is_nil(q.power_range):
#             p_range = dao_manager.offer_dao.get_range(None, None)
#             if p_range is None:
#                 range_id = dao_manager.offer_dao.add_range(RangeInfo(min_value=None, max_value=None)).range_id
#             else:
#                 range_id = p_range.range_id
#             tou_uriref = TOUSplitURIFiltered(prefix=kb_id, range_id=range_id, period_minutes=time_span_ms / 60000,
#                                      ts=ts_from,sequence=sequence,market_id=market_id).uri_ref
#             return [TOUPriceInfo(**{**q.input_bindings, **{"tou_uri": tou_uriref}})]
#
#         min_val, max_val = q.get_power_limit()
#         ranges = dao_manager.offer_dao.list_range(min_val, max_val)
#
#         def process_range(ri: RangeInfo):
#             # power_range = tou_range_uri_parser.n3(TOURangeSplitURI(range_id=ri.range_id))
#             # range_max = tou_range_max.n3(TOURangeSplitURI(range_id=ri.range_id))
#             # range_min = tou_range_min.n3(TOURangeSplitURI(range_id=ri.range_id))
#             power_range = TOURangeURI(prefix=kb_id, range_id=ri.range_id).n3()
#             range_max = TOURangeMaxURI(prefix=kb_id, range_id=ri.range_id).n3()
#             range_min = TOURangeMinURI(prefix=kb_id, range_id=ri.range_id).n3()
#             tou_uri = TOUSplitURI(range_id=ri.range_id, period_minutes=time_span_ms / 60000, ts=ts_from,
#                                   prefix=kb_id).n3()
#             ri_max_val = ri.max_value if ri.max_value is not None else URIRef("rdf:nil")
#             ri_min_val = ri.min_value if ri.min_value is not None else URIRef("rdf:nil")
#
#             return {"tou_uri": tou_uri, "power_range": power_range, "max_value": ri_max_val, "min_value": ri_min_val,
#                     "power_range_min": range_min, "power_range_max": range_max}
#
#         price_info = [
#             TOUPriceInfo(**{**process_range(ri), **q.input_bindings}) for ri in ranges
#         ]
#
#         return price_info

def _get_market_forecasts(kb_id: str, range_id: int, market_id: int, ts: TimeSpan, q: TOUPriceInfoQueryFiltered) -> \
        List[TOUPriceInfoFiltered]:
    from tm.core.db.postgresql import dao_manager
    job: JobDAO = dao_manager.job_api.get_by_market(market_id=market_id)
    if job is None:
        return []
    ts = TimeSpan(ts_from=ts.ts_from,
                  ts_to=ts.ts_to + 72 * 3600 * 1000)
    f_info_list = dao_manager.forecast_api.list_recent_forecasts(job_id=job.job_id, ts=ts)

    # offers = dao_manager.forecast_api.get_offers(forecast_ids=[f_info.forecast_id for f_info in f_info_list])

    def _get_uri(forecast_id: int, ts_from: int, period_minutes: int):
        # return TOUForecastSplitURIFiltered(prefix=kb_id, range_id=range_id,
        #                                    period_minutes=period_minutes,
        #                                    ts=ts_from, job_id=job.job_id, sequence=sequence).uri_ref
        return TOUForecastSplitURIFiltered(prefix=kb_id, forecast_id=forecast_id, period_minutes=period_minutes,
                                           ts=ts_from).uri_ref

    return [TOUPriceInfoFiltered(time_create=Literal(time_utils.xsd_from_ts(ts.ts_from)),
                                 ts_type=UBMARKET_FORECAST,
                                 tou_period=Literal(lexical_or_value=f"PT{ts.time_span_min}M",
                                                    datatype="xsd:duration"),
                                 tou_period_uri=DurationURI(minutes=ts.time_span_min).uri_ref,
                                 tou_uri=_get_uri(forecast_id=mo.forecast_id, ts_from=mo.ts,
                                                  period_minutes=mo.isp_len * mo.isp_unit),
                                 **q.input_bindings) for mo in f_info_list]


def get_range_tou_filtered(binding_query: List[TOUPriceInfoQueryFiltered], kb_id: str) -> List[TOUPriceInfoFiltered]:
    from tm.core.db.postgresql import dao_manager

    subscribed_markets = dao_manager.market_api.list_subscribed_market()
    all_info = []
    for q in binding_query:
        ts = q.ts
        range_id = None
        if is_nil(q.power_range):
            p_range = dao_manager.offer_dao.get_range(None, None)
            if p_range is None:
                range_id = dao_manager.offer_dao.add_range(RangeInfo(min_value=None, max_value=None)).range_id
            else:
                range_id = p_range.range_id
        else:
            min_val, max_val = q.get_power_limit()
            p_range = dao_manager.offer_dao.get_range(min_val, max_val)
            if p_range is not None:
                range_id = p_range.range_id

        if range_id is not None:
            # TODO: interpolate prices when ISP unit is different then isp unit stored in the db
            isp_unit = int(parse_duration(from_n3(KIVars.ISP_UNIT), as_timedelta_if_possible=True).total_seconds() / 60)

            def _get_uri(offer_id: int):
                return TOUSplitURIFiltered(prefix=kb_id,
                                           offer_id=offer_id,
                                           period_minutes=ts.time_span_min,
                                           ts=ts.ts_from).uri_ref

            for market in subscribed_markets:
                # TODO: get offer by range_id (currently range_id is not used) !!!!

                market_offers = dao_manager.offer_dao.list_offer_info(ts=ts, market_id=market.market_id,
                                                                      isp_unit=isp_unit)
                all_info += [
                    TOUPriceInfoFiltered(time_create=Literal(time_utils.xsd_from_ts(ts.ts_from)),
                                         ts_type=SAREF4ENER_TIMESERIES,
                                         tou_period=Literal(lexical_or_value=f"PT{ts.time_span_min}M",
                                                            datatype="xsd:duration"),
                                         tou_period_uri=DurationURI(minutes=ts.time_span_min).uri_ref,
                                         tou_uri=_get_uri(offer_id=mo.offer_id),
                                         # ts_interval_uri=TimeIntervalUri(ts_from=ts.ts_from, ts_to=ts.ts_to).uri_ref,
                                         # ts_date_from=Literal(time_utils.xsd_from_ts(mo.ts)),
                                         # ts_date_to=Literal(
                                         #     time_utils.xsd_from_ts(mo.ts + mo.isp_len * mo.isp_unit * 60000)),
                                         **q.input_bindings)
                    for mo in market_offers
                ]
                # TODO: for each sequence,  get forecasts after maximum date
                all_info += _get_market_forecasts(kb_id=kb_id, range_id=range_id, market_id=market.market_id, ts=ts,
                                                  q=q)
    return all_info


# def get_price(binding_query: List[TOUPriceQuery], kb_id: str) -> List[TOUPrice]:
#     from tm.core.db.postgresql import dao_manager
#
#     all_offers = []
#     for q in binding_query:
#         split_uri = TOUSplitURIFiltered.parse(uri=q.tou_uri, prefix=kb_id)
#         ts = TimeSpan(ts_from=split_uri.ts, ts_to=split_uri.ts + isp_unit_to_ms(isp_unit=split_uri.period_minutes))
#         isp_unit = int(parse_duration(from_n3(KIVars.ISP_UNIT), as_timedelta_if_possible=True).total_seconds() / 60)
#         # time_span_ms =  from_n3(KIVars.DAY_DURATION)
#         subscribed_markets = dao_manager.market_api.list_subscribed_market()
#         if len(subscribed_markets) == 0:
#             logging.warning("No subscribed markets")
#             return []
#             # powyzej
#         for market in subscribed_markets:
#             market_offers = dao_manager.offer_dao.list_market_offer(ts=ts, market_id=market.market_id,
#                                                                     isp_unit=isp_unit)
#             all_offers += market_offers
#             # todo: list recent offers  popatrz entsoe -service
#
#         # TODO: interpolate prices when ISP unit is different then isp unit stored in the db
#
#     def converter(o: EnergyMarketOffer):
#         tou_uri = q.tou_uri
#         # tou_uri_parser.n3(TOUSplitURI(range_id=o.range_id, period_minutes=o.isp_len, ts=o.ts))
#         dp_uri = OfferDPSplitURI(prefix=kb_id, range_id=o.range_id, period_minutes=o.isp_len,
#                                  offer_id=o.offer_id,
#                                  isp_start=o.isp_start).uri
#         return TOUPrice(tou_uri=tou_uri, dp=URIRef(dp_uri), ts=Literal(time_utils.xsd_from_ts(o.ts)),
#                         dpr=URIRef(dp_uri + "/dpr"),
#                         value=o.cost_mwh)
#
#     offer_bindings = [converter(o) for o in all_offers]
#
#     return offer_bindings


def get_forecasted_prices(q: TOUPriceQuery, kb_id: str, isp_unit: int, split_uri: TOUForecastSplitURIFiltered,
                          all_offers: List[TOUPrice]):
    from tm.core.db.postgresql import dao_manager

    def converter(o: DTForecastOfferDAO):
        tou_uri = q.tou_uri
        # tou_uri_parser.n3(TOUSplitURI(range_id=o.range_id, period_minutes=o.isp_len, ts=o.ts))
        # TODO: warning
        dp_uri = ForecastDPSplitURIFiltered(prefix=kb_id, period_minutes=o.isp_len,
                                            forecast_id=o.forecast_id,
                                            isp_start=o.isp_start).uri
        return TOUPrice(tou_uri=tou_uri, dp=URIRef(dp_uri), ts=Literal(time_utils.xsd_from_ts(o.ts)),
                        ts_type=UBMARKET_FORECAST,
                        dpr=URIRef(dp_uri + "/dpr"),
                        value=o.cost_mwh)

    f_offer = dao_manager.forecast_api.get_offer(forecast_id=split_uri.forecast_id)
    all_offers += [converter(o) for o in f_offer]

    return all_offers


def get_prices(q: TOUPriceQuery, kb_id: str, isp_unit: int, split_uri: TOUSplitURIFiltered, all_offers: List[TOUPrice]):
    from tm.core.db.postgresql import dao_manager

    def converter(o: EnergyMarketOfferDAO):
        tou_uri = q.tou_uri
        # tou_uri_parser.n3(TOUSplitURI(range_id=o.range_id, period_minutes=o.isp_len, ts=o.ts))
        dp_uri = OfferDPSplitURIFiltered(prefix=kb_id, period_minutes=o.isp_len,
                                         offer_id=o.offer_id,
                                         isp_start=o.isp_start).uri
        return TOUPrice(tou_uri=tou_uri, dp=URIRef(dp_uri), ts=Literal(time_utils.xsd_from_ts(o.ts)),
                        ts_type=SAREF4ENER_TIMESERIES,
                        dpr=URIRef(dp_uri + "/dpr"),
                        value=o.cost_mwh)

    # offer_info = dao_manager.offer_dao.list_offer_info(ts=split_uri.time_span, market_id=split_uri.market_id,
    #                                                    isp_unit=isp_unit,
    #                                                    sequence=split_uri.sequence)
    market_offers = dao_manager.offer_dao.get_market_offer(offer_id=split_uri.offer_id)
    all_offers += [converter(o) for o in market_offers]
    return all_offers


# todo
def get_price_filtered(binding_query: List[TOUPriceQuery], kb_id: str) -> List[TOUPrice]:
    all_offers = []
    for q in binding_query:
        isp_unit = int(parse_duration(from_n3(KIVars.ISP_UNIT), as_timedelta_if_possible=True).total_seconds() / 60)
        if q.ts_type == SAREF4ENER_TIMESERIES:
            split_uri = TOUSplitURIFiltered.parse(uri=q.tou_uri, prefix=kb_id)
            get_prices(q=q, kb_id=kb_id, isp_unit=isp_unit, split_uri=split_uri, all_offers=all_offers)
        elif q.ts_type == UBMARKET_FORECAST:
            split_uri = TOUForecastSplitURIFiltered.parse(uri=q.tou_uri, prefix=kb_id)
            all_offers = get_forecasted_prices(q=q, kb_id=kb_id, isp_unit=isp_unit, split_uri=split_uri,
                                               all_offers=all_offers)
        else:
            # todo:
            raise Exception

    return all_offers
