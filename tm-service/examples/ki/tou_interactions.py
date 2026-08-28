from typing import List, Union

from ke_client import KIHolder
from ke_client.ki_model import KIAskResponse
from rdflib import URIRef

from tm.utils import TimeSpan

tou_ki = KIHolder()
from examples.ki.fm_model import TOUPrice, TOUPriceQuery, \
    TOUPriceInfoFiltered, TOUPriceInfoQueryFiltered


#
# @tou_ki.ask("tm-agent")
# def _find_tm():
#     return []


@tou_ki.ask("tou-price")
def _get_tou_price(tou_list: List[TOUPriceInfoFiltered], tm_uri: URIRef):
    ask_bindings = [TOUPriceQuery(tou_uri=tou.tou_uri, tm_uri=tm_uri, ts_type=tou.ts_type) for tou in tou_list]
    # return graph pattern bindings to the knowledge engine interaction wrapper
    return ask_bindings


@tou_ki.ask("tou-price-info-filtered")
def _get_price_info(query: TOUPriceInfoQueryFiltered):
    print(f"tou-price-info: query: {query}")
    # return graph pattern bindings to the knowledge engine interaction wrapper
    return [query]


def get_tou_info(ts: TimeSpan, tm_uri: URIRef) -> list[TOUPriceInfoFiltered]:
    """
    get timeseries' metadata
    :param ts:
    :param tm_uri: trading manager uri
    :return:
    """
    q = TOUPriceInfoQueryFiltered.init(ti=ts, tm_uri=tm_uri)
    price_info_bindings: KIAskResponse = _get_price_info(query=q)
    return [TOUPriceInfoFiltered(**b) for b in price_info_bindings.binding_set]


def get_tou_price(tou_uris: List[TOUPriceInfoFiltered], tm_uri: URIRef) -> List[TOUPrice]:
    bindings: KIAskResponse = _get_tou_price(tou_list=tou_uris, tm_uri=tm_uri)
    return [TOUPrice(**b) for b in bindings.binding_set]
