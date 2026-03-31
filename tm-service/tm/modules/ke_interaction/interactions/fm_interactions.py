from typing import List

from ke_client import KIHolder
from ke_client.ki_model import KIAskResponse

from tm.modules.ke_interaction.interactions.fm_model import *
from tm.modules.ke_interaction.service import fm_service
from tm.utils import TimeSpan

ki = KIHolder()


# @ki.post("fm-ts-info-request")
# def _request_flexibility_info(request: FMTSRequest):
#     print("Request flex info")
#     return [request]


@ki.ask("fm-ts-info-request")
def _ask_request_flexibility_info(request: FMTSRequest):
    print("Request flex info")
    return [request]


@ki.ask("fm-ts")
def _request_data(ts_uris: List[FMPntQuery]):
    return ts_uris


@ki.react("fm-ts-evaluate")
def _on_evaluate_request(ki_id, bindings: List[FMEvaluateQuery]):
    print("fm react")
    print(len(bindings))
    resp = fm_service.evaluate(bindings)
    print("fm react2")
    print(len(resp))
    # return resp
    return resp


@ki.answer("fm-ts-evaluate-ask")
def _on_evaluate_request(ki_id, bindings: List[FMEvaluateQueryAsk]):
    print("fm answer")
    print(len(bindings))
    resp = fm_service.evaluate_ask(bindings)
    print("fm answer 2 ")
    print(len(resp))
    # return resp
    return resp


# def request_ts_info(ts: TimeSpan) -> List[FMTSResponse]:
#     resp_bindings: KIPostResponse = _request_flexibility_info(FMTSRequest(
#         ts_interval_uri=KETimeIntervalUri(ts_from=ts.ts_from, ts_to=ts.ts_to).n3(),
#         ts_date_from=Literal(time_utils.xsd_from_ts(ts.ts_from)),
#         ts_date_to=Literal(time_utils.xsd_from_ts(ts.ts_to)),
#     ))
#     return [FMTSResponse(**b) for b in resp_bindings.result_binding_set]

def request_ts_info(ts: TimeSpan) -> List[FMTSResponse]:
    resp_bindings: KIAskResponse = _ask_request_flexibility_info(FMTSRequest(
        ts_interval_uri=KETimeIntervalUri(ts_from=ts.ts_from, ts_to=ts.ts_to).n3(),
        ts_date_from=Literal(time_utils.xsd_from_ts(ts.ts_from)),
        ts_date_to=Literal(time_utils.xsd_from_ts(ts.ts_to)),
    ))
    return [FMTSResponse(**b) for b in resp_bindings.binding_set]


def request_data(ts_uris: List[str]) -> List[FMPnt]:
    ts_uri_refs = [FMPntQuery(ts_uri=URIRef(ts_uri)) for ts_uri in ts_uris]
    bindings: KIAskResponse = _request_data(ts_uris=ts_uri_refs)
    return [FMPnt(**b) for b in bindings.binding_set]
