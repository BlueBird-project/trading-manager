import logging
from typing import List

from effi_onto_tools.db import TimeSpan
from isodate import parse_duration
from ke_client import is_nil
from rdflib.util import from_n3

from tm.models.market_offer import EnergyMarketOffer, RangeInfo
from tm.modules.ke_interaction import KIVars

from tm.modules.ke_interaction.interactions.tou_model import *


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


def get_range_tou(binding_query: List[TOUPriceInfoQuery], kb_id: str) -> List[TOUPriceInfo]:
    from tm.core.db.postgresql import dao_manager
    # TODO: we support only one first binding query
    for q in binding_query:
        ts_from = time_utils.xsd_to_ts(q.time_create.value)
        # time_span_ms =  from_n3(KIVars.DAY_DURATION)
        time_span_ms = int(parse_duration(q.tou_period, as_timedelta_if_possible=True).total_seconds() * 1000)
        if is_nil(q.power_range):
            # TODO: check if range exist
            range_id = dao_manager.offer_dao.get_range(None, None).range_id
            tou_uriref = TOUSplitURI(prefix=kb_id, range_id=range_id, period_minutes=time_span_ms / 60000,
                                     ts=ts_from).uri_ref
            return [TOUPriceInfo(**{**q.input_bindings, **{"tou_uri": tou_uriref}})]

        min_val, max_val = q.get_power_limit()
        ranges = dao_manager.offer_dao.list_range(min_val, max_val)

        def process_range(ri: RangeInfo):
            # power_range = tou_range_uri_parser.n3(TOURangeSplitURI(range_id=ri.range_id))
            # range_max = tou_range_max.n3(TOURangeSplitURI(range_id=ri.range_id))
            # range_min = tou_range_min.n3(TOURangeSplitURI(range_id=ri.range_id))
            power_range = TOURangeURI(prefix=kb_id, range_id=ri.range_id).n3()
            range_max = TOURangeMaxURI(prefix=kb_id, range_id=ri.range_id).n3()
            range_min = TOURangeMinURI(prefix=kb_id, range_id=ri.range_id).n3()
            tou_uri = TOUSplitURI(range_id=ri.range_id, period_minutes=time_span_ms / 60000, ts=ts_from,
                                  prefix=kb_id).n3()
            ri_max_val = ri.max_value if ri.max_value is not None else URIRef("rdf:nil")
            ri_min_val = ri.min_value if ri.min_value is not None else URIRef("rdf:nil")

            return {"tou_uri": tou_uri, "power_range": power_range, "max_value": ri_max_val, "min_value": ri_min_val,
                    "power_range_min": range_min, "power_range_max": range_max}

        price_info = [
            TOUPriceInfo(**{**process_range(ri), **q.input_bindings}) for ri in ranges
        ]

        return price_info


def get_price(binding_query: List[TOUPriceQuery], kb_id: str) -> List[TOUPrice]:
    from tm.core.db.postgresql import dao_manager
    # TODO: we support only one first binding query
    for q in binding_query:
        split_uri = TOUSplitURI.parse(uri=q.tou_uri, prefix=kb_id)
        ts = TimeSpan(ts_from=split_uri.ts, ts_to=split_uri.ts + split_uri.period_minutes * 60 * 1000)
        # time_span_ms =  from_n3(KIVars.DAY_DURATION)
        # TODO  use all suybscribed markets
        if len(dao_manager.market_api.list_subscribed_market()) == 0:
            # TODO: check this on start service
            logging.warning("No subscribed markets")
            return []
        market_id = dao_manager.market_api.list_subscribed_market()[0].market_id
        isp_unit = int(parse_duration(from_n3(KIVars.ISP_UNIT), as_timedelta_if_possible=True).total_seconds() / 60)
        offers = dao_manager.offer_dao.list_market_offer(ts=ts, market_id=market_id, isp_unit=isp_unit)

        def converter(o: EnergyMarketOffer):
            tou_uri = q.tou_uri
            # tou_uri_parser.n3(TOUSplitURI(range_id=o.range_id, period_minutes=o.isp_len, ts=o.ts))
            dp_uri = OfferDPSplitURI(prefix=kb_id, range_id=o.range_id, period_minutes=o.isp_len,
                                     offer_id=o.offer_id,
                                     isp_start=o.isp_start).uri
            return TOUPrice(tou_uri=tou_uri, dp=URIRef(dp_uri), ts=Literal(time_utils.xsd_from_ts(o.ts)),
                            dpr=URIRef(dp_uri + "/dpr"),
                            value=o.cost_mwh)

        offer_bindings = [converter(o) for o in offers]

        return offer_bindings
