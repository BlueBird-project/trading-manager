import random
from typing import List

from ke_client import KIHolder, TargetedBindings
from ke_client.ki_model import KIPostResponse, KIAskResponse, ExchangeInfoStatus

from tm.modules.ke_interaction.interactions.fm_model import *
from examples.ki import fm_model

fm_ki = KIHolder()
_tm_info: fm_model.TMInfo = None


@fm_ki.ask("tm-info")
def _ask_tm_info(kb_id: Optional[str] = None):
    if kb_id is None:
        return [fm_model.TMInfoRequest()]
    return TargetedBindings(bindings=[fm_model.TMInfoRequest()], knowledge_bases=[kb_id])


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
    return TargetedBindings(bindings=response, knowledge_bases=[_tm_info.kb_id])


@fm_ki.ask("fm-ts-evaluate-ask")
def _evaluate_request_ask():
    # ask Trading manager for prices for current power demand
    hour_ms = 3600000
    minute_15_ms = 900000
    current_ts = int(time_utils.current_timestamp() / hour_ms) * hour_ms
    ts_end = current_ts + 24 * hour_ms
    ts_usage = URIRef("s4ener:Consumption")
    # ts_usage2 = URIRef("s4ener:Production")
    ts_uri = FMTSSplitURI(ts_from=current_ts, ts_to=ts_end, period_minutes=15, ts_usage=ts_usage)
    response: List[FMEvaluateQueryAsk] = []
    # return response
    for i in range(0, 24 * 4):
        ts = i * minute_15_ms + current_ts
        xsd_ts = time_utils.xsd_from_ts(ts)
        dp_uri = DPSplitURI(ts_start=ts, ts_usage=FMTSSplitURI.convert_ts_usage(ts_usage), isp_start=i)
        dpr_uri_ref = URIRef(dp_uri.uri + "/dpr")
        value = Literal(random.randrange(400, 1200))
        response.append(
            FMEvaluateQueryAsk(ts_uri=ts_uri.uri_ref, dp=dp_uri.uri_ref, ts=Literal(xsd_ts), dpr=dpr_uri_ref,
                               value=value))
    return TargetedBindings(bindings=response, knowledge_bases=[_tm_info.kb_id])


def find_tm() -> List[fm_model.TMInfo]:
    resp: KIAskResponse = _ask_tm_info()

    if len(resp.exchangeInfo) > 1:
        print(
            f"Found {len(resp.exchangeInfo)} TMs: {[str(f"{ei.knowledgeBaseId}:{ei.status}") for ei in resp.exchangeInfo]}")
        for tm_src in resp.exchangeInfo:
            if tm_src.status == ExchangeInfoStatus.SUCCEEDED:
                resp = _ask_tm_info(kb_id=tm_src.knowledgeBaseId)

    if len(resp.exchangeInfo) == 0:
        return []
    kb_id = resp.exchangeInfo[0].knowledgeBaseId

    tm_resp: List[fm_model.TMInfo] = [fm_model.TMInfo(**b, kb_id=URIRef(kb_id)) for b in resp.binding_set]
    return tm_resp


def evaluate_flexibility() -> List[FMEvaluateResponse]:
    """
    slow interaction
    :return:
    """
    resp: KIPostResponse = _evaluate_request()
    evaluated_resp: List[FMEvaluateResponse] = [FMEvaluateResponse(**b) for b in resp.result_binding_set]
    return evaluated_resp


def evaluate_flexibility_ask() -> List[FMEvaluateResponseAsk]:
    resp: KIAskResponse = _evaluate_request_ask()
    # print(resp)
    evaluated_resp: List[FMEvaluateResponseAsk] = [FMEvaluateResponseAsk(**b) for b in resp.binding_set]
    # resp: KIAskResponse = _ask_evaluate_request()
    # evaluated_resp: List[FMEvaluateQuery] = [FMEvaluateQuery(**b) for b in resp.binding_set]
    return evaluated_resp


def set_tm(tm: fm_model.TMInfo):
    global _tm_info
    if _tm_info is None:
        _tm_info = tm
    else:
        raise Exception(f"Market has been already set: {_tm_info}")
