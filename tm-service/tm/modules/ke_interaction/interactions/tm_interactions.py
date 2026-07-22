from typing import List

from ke_client import KIHolder
from rdflib import URIRef

from tm.modules.ke_interaction.interactions.tm_model import TMInfoRequest, TMMarketOfferInfoRequest, \
    TMMarketOfferRequest, TMAgent
from tm.modules.ke_interaction.interactions.tm_model import TOUPriceQuery, TOUPriceInfoQueryFiltered
from tm.modules.ke_interaction.service import tou_service, tm_service

tm_ki = KIHolder()


@tm_ki.answer("tou-price-info-filtered")
def on_price_info_request(ki_id: str, bindings: List[TOUPriceInfoQueryFiltered]):
    tou_bindings = bindings
    prince_info_resp = tou_service.get_range_tou_filtered(tou_bindings, kb_id=tm_ki.get_kb_id())
    return prince_info_resp


@tm_ki.answer("tou-price")
def on_price_request(ki_id: str, bindings: List[TOUPriceQuery]):
    print("tou-price")
    return tou_service.get_price_filtered(bindings, kb_id=tm_ki.get_kb_id())


# @tm_ki.answer("tou-price")
# def on_price_request(ki_id: str, bindings: List[TOUPriceQuery]):
#     print("tou-price")
#     return tou_service.get_price_filtered(bindings, kb_id=tm_ki.get_kb_id())


@tm_ki.answer("tm-info")
def on_tm_info_ask(ki_id: str, bindings: List[TMInfoRequest]):
    return tm_service.get_tm_info(bindings, kb_id=tm_ki.get_kb_id())


@tm_ki.answer("tm-agent")
def on_tm_info_ask(ki_id: str, bindings: List):
    # return [TMAgent(tm_uri=URIRef(tm_ki.get_kb_id() + "/service"))]
    return [{}]


@tm_ki.react("tm-info")
def on_tm_info_post(ki_id: str, bindings: List[TMInfoRequest]):
    return tm_service.get_tm_info(bindings, kb_id=tm_ki.get_kb_id())


@tm_ki.react("tm-agent")
def on_tm_info_ask(ki_id: str, bindings: List):
    return [TMAgent(tm_uri=URIRef(tm_ki.get_kb_id() + "/service"))]


@tm_ki.answer("tm-market-offer-info")
def on_price_info_request(ki_id: str, bindings: List[TMMarketOfferInfoRequest]):
    return tm_service.get_tm_offer_info(bindings=bindings, kb_id=tm_ki.get_kb_id())


@tm_ki.react("tm-market-offer-info")
def on_price_info_post(ki_id: str, bindings: List[TMMarketOfferInfoRequest]):
    return tm_service.get_tm_offer_info(bindings=bindings, kb_id=tm_ki.get_kb_id())


@tm_ki.answer("tm-market-offer")
def on_price_request(ki_id: str, bindings: List[TMMarketOfferRequest]):
    result = []
    for b in bindings:
        result += tm_service.get_tm_market_offer(offer_uri=b.offer_uri, kb_id=tm_ki.get_kb_id())
    return result
