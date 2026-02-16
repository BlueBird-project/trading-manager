import random
from typing import List

from effi_onto_tools.utils import time_utils
from ke_client import KIHolder
from ke_client.ki_model import KIPostResponse
from rdflib import URIRef, Literal

dt_ki = KIHolder()
from tm.modules.ke_interaction.interactions.dt_model import DigitalTwinInfoACK, DigitalTwinInfo


#
@dt_ki.post("dt-info")
def _post_dt_info(market_uri: URIRef) -> List[DigitalTwinInfo]:
    from tm.modules.ke_interaction.interactions import ki_client
    dt_info = DigitalTwinInfo(dt_uri=URIRef(dt_ki.get_kb_id()), command_uri=URIRef(dt_ki.get_kb_id() + "/command_1"),
                              market_uri=market_uri)

    return [dt_info]

#
# @ki_client.answer("dt-info")
# def on_dt_info_request(ki_id, bindings):
#     dt_info = DigitalTwinInfo(dt_uri=URIRef(ki_client.kb_id), command_uri=URIRef(ki_client.kb_id + "/command_1"),
#                               market_uri=URIRef("https://tge.test.bluebird.com/market"))
#
#     return [dt_info.n3()]
#
#
# @ki_client.post("dt-ts-info")
# def _post_ts_info():
#     ts_start = time_utils.current_timestamp()
#     ts_end = ts_start + 3600 * 1000 * 24
#     ts_uri = DTTSUri(dt_uri=URIRef(ki_client.kb_id), ts_start=ts_start, ts_end=ts_end)
#     ts_interval_uri = URIRef(ts_uri.uri + "/interval")
#     dt_info = DTTSInfo(command_uri=URIRef(ki_client.kb_id + "/command_1"),
#                        ts_uri=ts_uri.uri_ref,
#                        time_create=Literal(time_utils.xsd_from_ts(time_utils.current_timestamp())),
#                        ts_interval_uri=ts_interval_uri,
#                        ts_date_from=Literal(time_utils.xsd_from_ts(ts_start)),
#                        ts_date_to=Literal(time_utils.xsd_from_ts(ts_end)))
#
#     return [dt_info.n3()]
#
#
# def _generate_sample_ts(ts_uri: DTTSUri) -> List[DTPnt]:
#     cur_ts = ts_uri.ts_start
#     isp = 0
#     res = []
#     while cur_ts <= ts_uri.ts_end:
#         isp += 1
#         pnt = DTPnt(ts_uri=ts_uri.uri_ref,
#                     dp=DTDPUri(**ts_uri.__dict__, isp=isp).uri_ref,
#                     ts=Literal(time_utils.xsd_from_ts(cur_ts)),
#                     dpr=DTDPRUri(**ts_uri.__dict__, isp=isp).uri_ref,
#                     value=random.random() * 200 + 50)
#         res.append(pnt)
#         cur_ts += 60000 * 15
#     return res
#
#
# @ki_client.post("dt-ts")
# def _post_dt_ts():
#     ts_start = time_utils.current_timestamp()
#     ts_end = ts_start + 3600 * 1000 * 24
#     ts_uri = DTTSUri(dt_uri=URIRef(ki_client.kb_id), ts_start=ts_start, ts_end=ts_end)
#     ts_interval_uri = URIRef(ts_uri.uri + "/interval")
#     sample_ts = _generate_sample_ts(ts_uri=ts_uri)
#
#     return [sample.n3() for sample in sample_ts]
#
#
# @ki_client.answer("dt-ts")
# def on_dt_ts_request(ki_id, bindings):
#     ts_uri = DTPntRequest(**bindings[0]).get_ts_uri()
#     sample_ts = _generate_sample_ts(ts_uri=ts_uri)
#     return [sample.n3() for sample in sample_ts]
#

def post_dt_info(market_uri: URIRef) -> List[DigitalTwinInfoACK]:
    # noinspection PyTypeChecker
    resp_bindings: KIPostResponse = _post_dt_info(market_uri)
    return [DigitalTwinInfoACK(**b) for b in resp_bindings.resultBindingSet]

#
# def post_ts_info() -> List[DTTSInfoACK]:
#     # noinspection PyTypeChecker
#     resp_bindings: KIPostResponse = _post_ts_info()
#     return [DTTSInfoACK(**b) for b in resp_bindings.resultBindingSet]
#
#
# def post_ts():
#     # noinspection PyTypeChecker
#     resp_bindings: KIPostResponse = _post_dt_ts()
#     return resp_bindings.resultBindingSet
