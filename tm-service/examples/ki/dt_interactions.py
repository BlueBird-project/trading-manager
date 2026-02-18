import hashlib
import random
from typing import List

from effi_onto_tools.utils import time_utils
from ke_client import KIHolder
from ke_client.ki_model import KIPostResponse
from rdflib import URIRef, Literal
from tm.modules.ke_interaction.interactions.dt_model import DigitalTwinInfoACK, DigitalTwinInfo, DTTSUri, DTTSInfo, \
    DTPnt, DTDPUri, DTDPRUri, DTPntRequest, DTTSInfoACK, DTTSACK, DTTSInfoRequest

dt_ki = KIHolder()
_market_uri: URIRef = None
_current_forecast_uri: DTTSUri = None


def _init_command_uri(market_uri: str):
    md5_hash = hashlib.md5(_market_uri.encode())
    hash_str = md5_hash.hexdigest()

    return URIRef(dt_ki.get_kb_id() + "/command/" + hash_str)


#
@dt_ki.post("dt-info")
def _post_dt_info(market_uri: URIRef) -> List[DigitalTwinInfo]:
    dt_info = DigitalTwinInfo(dt_uri=URIRef(dt_ki.get_kb_id()),
                              command_uri=_init_command_uri(market_uri=str(_market_uri)),
                              market_uri=market_uri)

    return [dt_info]


@dt_ki.answer("dt-info")
def on_dt_info_request(ki_id, bindings):
    global _market_uri
    print("on_dt_info_request")
    dt_info = DigitalTwinInfo(dt_uri=URIRef(dt_ki.get_kb_id()),
                              command_uri=_init_command_uri(market_uri=str(_market_uri)),
                              market_uri=_market_uri)
    print(dt_info)

    return [dt_info]


@dt_ki.post("dt-ts-info")
def _post_ts_info(market_uri: URIRef, ts_uri: DTTSUri) -> List[DTTSInfo]:
    ts_start = time_utils.current_timestamp()
    ts_end = ts_start + 3600 * 1000 * 24
    ts_interval_uri = URIRef(ts_uri.uri + "/interval")
    dt_info = DTTSInfo(command_uri=_init_command_uri(market_uri=str(market_uri)),
                       ts_uri=ts_uri.uri_ref,
                       time_create=Literal(time_utils.xsd_from_ts(time_utils.current_timestamp())),
                       ts_interval_uri=ts_interval_uri,
                       ts_date_from=Literal(time_utils.xsd_from_ts(ts_start)),
                       ts_date_to=Literal(time_utils.xsd_from_ts(ts_end)))

    return [dt_info]


@dt_ki.answer("dt-ts-info")
def on_ts_info(ki_id, bindings: List[DTTSInfoRequest]) -> List[DTTSInfo]:
    global _market_uri
    global _current_forecast_uri
    if _current_forecast_uri is None:
        return []
    print("dt-ts-info")
    ts_start = time_utils.current_timestamp()
    ts_end = ts_start + 3600 * 1000 * 24
    ts_interval_uri = URIRef(_current_forecast_uri.uri + "/interval")
    ds_info = DTTSInfo(command_uri=_init_command_uri(market_uri=str(_market_uri)),
                       ts_uri=_current_forecast_uri.uri_ref,
                       time_create=Literal(time_utils.xsd_from_ts(time_utils.current_timestamp())),
                       ts_interval_uri=ts_interval_uri,
                       ts_date_from=Literal(time_utils.xsd_from_ts(ts_start)),
                       ts_date_to=Literal(time_utils.xsd_from_ts(ts_end)))

    print(ds_info)
    return [ds_info]


#
#
def _generate_sample_ts(ts_uri: DTTSUri) -> List[DTPnt]:
    cur_ts = ts_uri.ts_start
    isp = 0
    res = []
    while cur_ts <= ts_uri.ts_end:
        isp += 1
        pnt = DTPnt(ts_uri=ts_uri.uri_ref,
                    dp=DTDPUri(prefix=dt_ki.get_kb_id(), **ts_uri.__dict__, isp=isp).uri_ref,
                    ts=Literal(time_utils.xsd_from_ts(cur_ts)),
                    dpr=DTDPRUri(prefix=dt_ki.get_kb_id(), **ts_uri.__dict__, isp=isp).uri_ref,
                    value=random.random() * 200 + 50)
        res.append(pnt)
        cur_ts += 60000 * 15
    return res


@dt_ki.post("dt-ts")
def _post_ts(ts_uri: DTTSUri) -> List[DTPnt]:
    # ts_interval_uri = URIRef(ts_uri.uri + "/interval")
    sample_ts = _generate_sample_ts(ts_uri=ts_uri)

    return sample_ts


@dt_ki.answer("dt-ts")
def on_dt_ts_request(ki_id, bindings: List[DTPntRequest]) -> List[DTPnt]:
    print("on-ts")
    if len(bindings) > 0:
        ts_uri = DTTSUri.parse(uri=bindings[0].ts_uri, prefix=dt_ki.get_kb_id())
        sample_ts = _generate_sample_ts(ts_uri=ts_uri)

    else:
        global _current_forecast_uri
        if _current_forecast_uri is None:
            return []
        sample_ts = _generate_sample_ts(ts_uri=_current_forecast_uri)

    print(f"forecast size: {len(sample_ts)}")
    return sample_ts


def set_market_uri(market_uri: URIRef):
    global _market_uri
    if _market_uri is None:
        _market_uri = market_uri
    else:
        raise Exception(f"Market has been already set: {_market_uri}")


def post_dt_info() -> List[DigitalTwinInfoACK]:
    global _market_uri
    resp_bindings: KIPostResponse = _post_dt_info(market_uri=_market_uri)
    return [DigitalTwinInfoACK(**b) for b in resp_bindings.result_binding_set]


def post_forecast(market_uri: URIRef) -> List[DTTSACK]:
    global _current_forecast_uri
    ts_start = time_utils.current_timestamp()
    ts_end = ts_start + 3600 * 1000 * 24
    ts_uri = DTTSUri(prefix=dt_ki.get_kb_id(), ts_start=ts_start, ts_end=ts_end)
    _current_forecast_uri = ts_uri
    resp_bindings: KIPostResponse = _post_ts_info(market_uri, ts_uri)
    info_ack = [DTTSInfoACK(**b) for b in resp_bindings.result_binding_set]
    print("info ack")
    print(info_ack)
    resp_bindings: KIPostResponse = _post_ts(ts_uri)
    return [DTTSACK(**b) for b in resp_bindings.result_binding_set]
