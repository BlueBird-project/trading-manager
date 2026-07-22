from typing import List, Union

from ke_client import KIHolder
from ke_client.ki_model import KIAskResponse
from rdflib import URIRef

from tm.utils import TimeSpan

tou_ki = KIHolder()
from examples.ki.fm_model import TOUPrice, TOUPriceQuery, \
    TOUPriceInfoFiltered, TOUPriceInfoQueryFiltered, TMAgent


@tou_ki.ask("tm-agent")
def _find_tm():
    return []


@tou_ki.ask("tou-price")
def _get_tou_price(tou_uris: List[URIRef], tm_uri: URIRef):
    ask_bindings = [TOUPriceQuery(tou_uri=tou_uri, tm_uri=tm_uri) for tou_uri in tou_uris]
    return ask_bindings


@tou_ki.ask("tou-price-info-filtered")
def _get_price_info(query: Union[TOUPriceInfoQueryFiltered]):
    print("tou-price-info: query: ")
    print(query)
    return [query]


def get_tou_info(ts: TimeSpan, tm_uri: URIRef) -> list[TOUPriceInfoFiltered]:
    """
    get timeseries metadata
    :param ts:
    :return:
    """
    minutes = int((ts.ts_to - ts.ts_from) / 60000)
    iso_duration = f"PT{minutes}M"
    # q = TOUPriceInfoQueryFiltered(time_create=Literal(time_utils.xsd_from_ts(ts.ts_from)),
    #                       tou_period=Literal(lexical_or_value=iso_duration, datatype="xsd:duration"),
    #                       tou_period_uri=DurationURI(minutes=minutes).uri_ref)
    q = TOUPriceInfoQueryFiltered.init(ti=ts, tm_uri=tm_uri)
    price_info_bindings: KIAskResponse = _get_price_info(query=q)
    return [TOUPriceInfoFiltered(**b) for b in price_info_bindings.binding_set]


def get_tou_price(tou_uris: List[str], tm_uri: URIRef) -> List[TOUPrice]:
    tou_uris_refs = [URIRef(tou_uri) for tou_uri in tou_uris]
    bindings: KIAskResponse = _get_tou_price(tou_uris=tou_uris_refs, tm_uri=tm_uri)
    return [TOUPrice(**b) for b in bindings.binding_set]


def find_tm() -> List[TMAgent]:
    bindings: KIAskResponse = _find_tm()
    return [TMAgent(**b) for b in bindings.binding_set]
