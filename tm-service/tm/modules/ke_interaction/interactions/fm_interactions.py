from typing import List

from effi_onto_tools.db import TimeSpan
from ke_client import KIHolder
from ke_client.ki_model import KIPostResponse, KIAskResponse

from tm.modules.ke_interaction.interactions.fm_model import *
from tm.modules.ke_interaction.service import fm_service

ki = KIHolder()


@ki.post("fm-ts-info-request")
def _request_market_info(request: FMTSRequest):
    return [request]


@ki.ask("fm-ts")
def _request_data(ts_uris: List[FMPntQuery]):
    return ts_uris


# noinspection PyUnusedLocal
@ki.react("fm-ts-evaluate")
def _on_evaluate_request(ki_id, bindings: List[FMEvaluateQuery]):
    resp = fm_service.evaluate(bindings)
    return resp


def request_ts_info(ts: TimeSpan) -> List[FMTSResponse]:
    resp_bindings: KIPostResponse = _request_market_info(FMTSRequest(
        ts_interval_uri=KETimeIntervalUri(ts_from=ts.ts_from, ts_to=ts.ts_to).n3(),
        ts_date_from=Literal(time_utils.xsd_from_ts(ts.ts_from)),
        ts_date_to=Literal(time_utils.xsd_from_ts(ts.ts_to)),
    ))
    return [FMTSResponse(**b) for b in resp_bindings.result_binding_set]


def request_data(ts_uris: List[str]) -> List[FMPnt]:
    ts_uri_refs = [FMPntQuery(ts_uri=URIRef(ts_uri)) for ts_uri in ts_uris]
    bindings: KIAskResponse = _request_data(ts_uris=ts_uri_refs)
    return [FMPnt(**b) for b in bindings.binding_set]
