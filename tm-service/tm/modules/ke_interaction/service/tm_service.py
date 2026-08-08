from datetime import timedelta
from typing import List

from isodate import duration_isoformat

from tm.models.market_offer import EnergyMarketOfferDAO
from tm.modules.ke_interaction.interactions.dam_model import MarketType, MarketTypeValue
from tm.modules.ke_interaction.interactions.ki_models import DurationURI
from tm.modules.ke_interaction.interactions.tm_model import *
from tm.modules.ke_interaction.interactions.tm_uris import *


def _init_tm_info(kb_id: str) -> List[TMInfo]:
    from tm.core.db.postgresql import dao_manager
    markets = dao_manager.market_api.list_subscribed_market()
    return [TMInfo(market_uri=URIRef(m.market_uri),
                   command_uri=TMCommandURI(market_id=m.market_id, prefix=kb_id).uri_ref)
            for m
            in markets]


def get_tm_info(q: List[TMInfoRequest], kb_id: str):
    if len(q) == 0:
        return _init_tm_info(kb_id=kb_id)
    for market_uri in [m.market_uri for m in q]:
        if market_uri is not None:
            from tm.core.db.postgresql import dao_manager
            if dao_manager.market_api.get_market(market_uri=market_uri) is not None:
                return _init_tm_info(kb_id=kb_id)
    return []


def get_tm_offer_info(bindings: List[TMMarketOfferInfoRequest], kb_id: str) -> List[TMMarketOfferInfoBindings]:
    from tm.core.db.postgresql import dao_manager
    result: List[TMMarketOfferInfoBindings] = []
    for b in bindings:
        command_uri = TMCommandURI.parse(b.command_uri, prefix=kb_id)
        market = dao_manager.market_api.get_market_by_id(market_id=command_uri.market_id)
        if market is not None:
            offers = dao_manager.offer_dao.list_offer_info(ts=None, market_id=market.market_id)
            mt: MarketTypeValue = MarketType.parse(market.market_type).value
            result += [
                TMMarketOfferInfoBindings(market_uri=URIRef(market.market_uri), market_type=mt.uri_ref,
                                          command_uri=command_uri.uri_ref,
                                          offer_uri=URIRef(oi.offer_uri),
                                          time_create=Literal(time_utils.xsd_from_ts(ts=oi.ts)),
                                          sequence=Literal(oi.sequence),
                                          update_rate=Literal(duration_isoformat(timedelta(minutes=oi.isp_unit))),
                                          duration_uri=DurationURI(minutes=(oi.isp_len - oi.isp_unit)).uri_ref,
                                          duration=Literal(
                                              duration_isoformat(timedelta(minutes=(oi.isp_len - oi.isp_unit))))
                                          )
                for oi in offers]
    return result


def get_tm_market_offer(offer_uri: URIRef, kb_id: str):
    from tm.core.db.postgresql import dao_manager

    offer_details = dao_manager.offer_dao.get_offer_info(offer_uri=offer_uri)

    if offer_details is None:
        # todo log error /warning ?
        return []
    offer_uri = offer_details.offer_uri
    command_uri = TMCommandURI(market_id=offer_details.market_id, prefix=kb_id)
    market = dao_manager.market_api.get_market_by_id(market_id=offer_details.market_id)
    market_offer: List[EnergyMarketOfferDAO] = dao_manager.offer_dao.get_market_offer(offer_id=offer_details.offer_id)
    offer_bindings = [
        TMMarketOfferBindings(offer_uri=URIRef(offer_uri), command_uri=command_uri.uri_ref,
                              market_uri=URIRef(market.market_uri),
                              dp=SplitURIBase.uri_append_ref(offer_uri, "/dp"),
                              ts=Literal(time_utils.xsd_from_ts(mo.ts)),
                              dpr=SplitURIBase.uri_append_ref(offer_uri, "/dpr"),
                              duration_uri=DurationURI(minutes=mo.isp_len * offer_details.isp_unit).uri_ref,
                              duration=Literal(
                                  duration_isoformat(timedelta(minutes=mo.isp_len * offer_details.isp_unit))),
                              value=Literal(mo.cost_mwh))
        for mo in market_offer]
    return offer_bindings
