from typing import List, Optional, Union

from effi_onto_tools.db import TimeSpan
from ke_client.utils import time_utils 
from ke_client import KIHolder
from ke_client.ki_model import KIAskResponse
from rdflib import URIRef, Literal

tou_ki = KIHolder()
from tm.modules.ke_interaction.interactions.tou_model import TOUPrice, TOUPriceInfoQuery, \
    TOUPriceInfo, TOUPriceQuery


# todo przetestować

@tou_ki.ask("tou-price")
def _get_tou_price(tou_uris: List[URIRef]):
    ask_bindings = [TOUPriceQuery(tou_uri=tou_uri) for tou_uri in tou_uris]
    return ask_bindings


@tou_ki.ask("tou-price-info")
def _get_price_info(query: Union[TOUPriceInfoQuery]):
    print("query: ")
    print(query)
    return [query]


def get_tou(ts: TimeSpan) -> list[TOUPriceInfo]:
    iso_duration = f"PT{int((ts.ts_to - ts.ts_from) / 60000)}M"
    q = TOUPriceInfoQuery(time_create=Literal(time_utils.xsd_from_ts(ts.ts_from)),
                          tou_period=Literal(lexical_or_value=iso_duration, datatype="xsd:duration"))
    price_info_bindings: KIAskResponse = _get_price_info(query=q)
    return [TOUPriceInfo(**b) for b in price_info_bindings.binding_set]


# def get_tiered_tou(ts: TimeSpan, min_value: Optional[float], max_value: Optional[float] = None) -> list[TOUPriceInfo]:
#     iso_duration = f"PT{int((ts.ts_to - ts.ts_from) / 60000)}M"
#     q = TOUPriceInfoQuery(time_create=Literal(time_utils.xsd_from_ts(ts.ts_from)),
#                           tou_period=Literal(lexical_or_value=iso_duration, datatype="xsd:duration"),
#                           min_value=Literal(min_value) if min_value is not None else None,
#                           max_value=Literal(max_value) if max_value is not None else None)
#     price_info_bindings = _get_price_info(query=q)
#     return [TOUPriceInfo(**b) for b in price_info_bindings]


def get_tou_price(tou_uris: List[str]) -> List[TOUPrice]:
    tou_uris_refs = [URIRef(tou_uri) for tou_uri in tou_uris]
    bindings:KIAskResponse = _get_tou_price(tou_uris=tou_uris_refs)
    return [TOUPrice(**b) for b in bindings.binding_set]
