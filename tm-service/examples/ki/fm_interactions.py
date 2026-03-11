import random
from typing import List

from ke_client import KIHolder, TargetedBindings
from ke_client.ki_model import KIPostResponse, KIAskResponse

from tm.modules.ke_interaction.interactions.dt_model import DTPnt
from tm.modules.ke_interaction.interactions.fm_model import *

fm_ki = KIHolder()
TM_KB_ID = ["http://demo.tm.bluebird.com", "http://tm.bluebird.com"]


# TM_KB_ID = "http://demo.tm.bluebird.com"


# BindingsBase
#
# @fm_ki.react("fm-ts-info-request")
# def on_request_ts_info(ki_id, bindings: List[FMTSRequest]):
#     # respond with timeseries metadata
#     print("on_request_ts_info")
#     for request in bindings:
#         #      support only one request
#         ts_from: int = time_utils.xsd_to_ts(request.ts_date_from.value)
#         ts_to = time_utils.xsd_to_ts(request.ts_date_to.value)
#         #######
#         # Saref data point usage
#         ###########
#         ts_usage = URIRef("s4ener:Consumption")
#         ts_usage2 = URIRef("s4ener:Production")
#         ts_uri2 = FMTSSplitURI(ts_from=ts_from, ts_to=ts_to, period_minutes=15, ts_usage=ts_usage2).n3()
#         ts_uri = FMTSSplitURI(ts_from=ts_from, ts_to=ts_to, period_minutes=15, ts_usage=ts_usage).n3()
#         time_create = Literal(time_utils.xsd_now())
#         return [
#             FMTSResponse(ts_uri=ts_uri, ts_interval_uri=request.ts_interval_uri, ts_usage=ts_usage,
#                          time_create=time_create).n3(),
#             FMTSResponse(ts_uri=ts_uri2, ts_interval_uri=request.ts_interval_uri, ts_usage=ts_usage2,
#                          time_create=time_create).n3()
#         ]  #


@fm_ki.answer("fm-ts-info-request")
def on_request_ts_info(ki_id, bindings: List[FMTSRequest]):
    # respond with timeseries metadata
    print("on_request_ts_info")
    for request in bindings:
        #      support only one request
        ts_from: int = time_utils.xsd_to_ts(request.ts_date_from.value)
        ts_to = time_utils.xsd_to_ts(request.ts_date_to.value)
        #######
        # Saref data point usage
        ###########
        ts_usage = URIRef("s4ener:Consumption")
        ts_usage2 = URIRef("s4ener:Production")
        ts_uri2 = FMTSSplitURI(ts_from=ts_from, ts_to=ts_to, period_minutes=15, ts_usage=ts_usage2).n3()
        ts_uri = FMTSSplitURI(ts_from=ts_from, ts_to=ts_to, period_minutes=15, ts_usage=ts_usage).n3()
        time_create = Literal(time_utils.xsd_now())
        return [
            # FMTSResponse2(ts_uri=ts_uri, ts_interval_uri=request.ts_interval_uri, ts_usage=ts_usage,
            #               time_create=time_create, ts_date_from=request.ts_date_from,
            #               ts_date_to=request.ts_date_to).n3(),
            # FMTSResponse2(ts_uri=ts_uri2, ts_interval_uri=request.ts_interval_uri, ts_usage=ts_usage2,
            #               time_create=time_create, ts_date_from=request.ts_date_from,
            #               ts_date_to=request.ts_date_to).n3()
            FMTSResponse(ts_uri=ts_uri, ts_interval_uri=request.ts_interval_uri, ts_date_from=request.ts_date_from,
                         ts_date_to=request.ts_date_to, time_create=time_create, ts_usage=ts_usage, ).n3(),
            FMTSResponse(ts_uri=ts_uri, ts_interval_uri=request.ts_interval_uri, ts_date_from=request.ts_date_from,
                         ts_date_to=request.ts_date_to, time_create=time_create, ts_usage=ts_usage2).n3()

        ]  #


@fm_ki.answer("fm-ts")
def on_fm_request(ki_id: str, bindings: List[FMPntQuery]):
    # response with timeseries
    print("received request for flexibility")
    for ts_binding in bindings:
        ts_uri = ts_binding.ts_uri
        parsed_uri = FMTSSplitURI.parse(ts_uri)
        ts_resp = [FMPnt(ts_uri=ts_uri,
                         dp=
                         DPSplitURI(ts_start=parsed_uri.ts_to, ts_usage=parsed_uri.ts_usage, isp_start=i).n3(),
                         ts=Literal(time_utils.xsd_from_ts(parsed_uri.ts_from + i * 15 * 60 * 1000)),
                         dpr=URIRef(
                             DPSplitURI(ts_start=parsed_uri.ts_to, ts_usage=parsed_uri.ts_usage,
                                        isp_start=i).uri + "/dpr"),
                         value=random.random() * 200 + 50) for i in range(1, 24 * 4)]
        # process just once timeseries
        print(ts_resp)
        return ts_resp


@fm_ki.post("fm-ts-evaluate")
def _evaluate_request():
    # ask TM to evaluate
    hour_ms = 3600000
    current_ts = int(time_utils.current_timestamp() / hour_ms) * hour_ms
    ts_end = current_ts + 24 * hour_ms
    ts_usage = URIRef("s4ener:Consumption")
    # ts_usage2 = URIRef("s4ener:Production")
    ts_uri = FMTSSplitURI(ts_from=current_ts, ts_to=ts_end, period_minutes=15, ts_usage=ts_usage)
    response: List[FMEvaluateQuery] = []
    # return response
    for i in range(0, 24 * 4):
        ts = i * hour_ms + current_ts
        xsd_ts = time_utils.xsd_from_ts(ts)
        dp_uri = DPSplitURI(ts_start=ts, ts_usage=FMTSSplitURI.convert_ts_usage(ts_usage), isp_start=i)
        dpr_uri_ref = URIRef(dp_uri.uri + "/dpr")
        value = Literal(random.randrange(400, 1200))
        response.append(FMEvaluateQuery(ts_uri=ts_uri.uri_ref, dp=dp_uri.uri_ref, ts=Literal(xsd_ts), dpr=dpr_uri_ref,
                                        value=value))
    return TargetedBindings(bindings=response, knowledge_bases=TM_KB_ID)


@fm_ki.ask("fm-ts-evaluate-ask")
def _evaluate_request_ask():
    # ask TM to evaluate
    hour_ms = 3600000
    current_ts = int(time_utils.current_timestamp() / hour_ms) * hour_ms
    ts_end = current_ts + 24 * hour_ms
    ts_usage = URIRef("s4ener:Consumption")
    # ts_usage2 = URIRef("s4ener:Production")
    ts_uri = FMTSSplitURI(ts_from=current_ts, ts_to=ts_end, period_minutes=15, ts_usage=ts_usage)
    response: List[FMEvaluateQueryAsk] = []
    # return response
    for i in range(0, 24 * 4):
        ts = i * hour_ms + current_ts
        xsd_ts = time_utils.xsd_from_ts(ts)
        dp_uri = DPSplitURI(ts_start=ts, ts_usage=FMTSSplitURI.convert_ts_usage(ts_usage), isp_start=i)
        dpr_uri_ref = URIRef(dp_uri.uri + "/dpr")
        value = Literal(random.randrange(400, 1200))
        response.append(
            FMEvaluateQueryAsk(ts_uri=ts_uri.uri_ref, dp=dp_uri.uri_ref, ts=Literal(xsd_ts), dpr=dpr_uri_ref,
                               value=value))
    return TargetedBindings(bindings=response, knowledge_bases=TM_KB_ID)


def evaluate_flexibility() -> List[FMEvaluateResponse]:
    """
    slow interaction
    :return:
    """
    resp: KIPostResponse = _evaluate_request()
    # print(resp)
    evaluated_resp: List[FMEvaluateResponse] = [FMEvaluateResponse(**b) for b in resp.result_binding_set]
    # resp: KIAskResponse = _ask_evaluate_request()
    # evaluated_resp: List[FMEvaluateQuery] = [FMEvaluateQuery(**b) for b in resp.binding_set]
    return evaluated_resp


# @fm_ki.react("dt-ts")
# def on_dt_ts(ki_id, bindings: List[DTPnt]):
#     print(f"on new digital twin timeseries data: {len(bindings)}")
#     # TODO  save
#     # ack = dt_service.process_timeseries(bindings)
#     # print(dt_ts)
#     if len(bindings) > 0:
#         #     TODO: check if ack binding can have different length
#         # return [DTTSACK(ts_uri=b.ts_uri) for b in bindings]
#         return []
#     return []
#

def evaluate_flexibility_ask() -> List[FMEvaluateResponseAsk]:
    resp: KIAskResponse = _evaluate_request_ask()
    print(resp)
    evaluated_resp: List[FMEvaluateResponseAsk] = [FMEvaluateResponseAsk(**b) for b in resp.binding_set]
    # resp: KIAskResponse = _ask_evaluate_request()
    # evaluated_resp: List[FMEvaluateQuery] = [FMEvaluateQuery(**b) for b in resp.binding_set]
    return evaluated_resp
