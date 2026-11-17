import random
from threading import Thread
from typing import List

from ke_client import KIHolder, TargetedBindings, rdf_nil
from ke_client.ki_model import KIPostResponse, KIAskResponse, ExchangeInfoStatus

from examples.ki.fm_model import KEFlexRequest, BaselineDateRequest, BaselineDateResponse, BaselineRequest, Baseline
from tm.modules.ke_interaction.interactions.capacity_market_model import KEFlexOffer
from tm.modules.ke_interaction.interactions.fm_model import *
from examples.ki import fm_model

fm_ki = KIHolder()


@fm_ki.ask("baseline-request")
def _get_required_days() -> List[BaselineDateRequest]:
    # http://fm.bluebird.com
    ts_usage = URIRef("s4ener:Consumption")
    ts_from = time_utils.current_timestamp() - 20 * 24 * 3600 * 1000
    ts_to = time_utils.current_timestamp()
    ts_uri = FMTSSplitURI(ts_from=ts_from, ts_to=ts_to, period_minutes=15,
                          ts_usage=ts_usage).uri_ref  # my timeseries uri
    req = BaselineDateRequest(
        asset_manager=URIRef(fm_ki.get_kb_id()), ts_uri=ts_uri,
        baseline_interval_uri=KETimeIntervalUri(ts_from=ts_from, ts_to=ts_to).uri_ref,

        ts_baseline_from=Literal(time_utils.xsd_from_ts(ts_from)),
        ts_baseline_to=Literal(time_utils.xsd_from_ts(ts_to)))
    return [req]


@fm_ki.post("baseline")
def _get_baseline(baseline_dates: List[BaselineDateResponse]) -> List[BaselineRequest]:
    hour_ms = 3600000
    current_ts = int(time_utils.current_timestamp() / hour_ms) * hour_ms
    # ts_end = current_ts + 24 * hour_ms
    ts_usage = URIRef("s4ener:Consumption")
    response: List[BaselineRequest] = []
    # return response
    for bdt in baseline_dates:
        ts_from = bdt.from_ts
        ts_to = bdt.to_ts
        ts_uri = FMTSSplitURI(ts_from=ts_from, ts_to=ts_to, period_minutes=60, ts_usage=ts_usage)
        i = 0
        ts = i * hour_ms + ts_from
        while ts < ts_to + hour_ms:
            xsd_ts = Literal(time_utils.xsd_from_ts(ts))
            response.append(BaselineRequest(
                ts_uri=ts_uri.uri_ref, asset_manager=URIRef(fm_ki.get_kb_id()),
                dp=ts_uri.append_ref(f"dp/{i}"), dpr=ts_uri.append_ref(f"dpr/{i}"),

                value=Literal(random.randrange(400, 1200)), ts=xsd_ts))
            i += 1
            ts = i * hour_ms + ts_from
    return response


@fm_ki.react("baseline-response")
def _on_baseline(ki_id, bindings: List[Baseline]):
    global flex_request
    print(f"_on_baseline ")
    # baseline: List[Baseline] = [Baseline(**b) for b in bindings]
    flex_value: float = sum([b.convert_value(b.value_baseline, float) for b in bindings]) / len(bindings) * 0.1

    def _t():
        _send_flexibility(flex_value=flex_value)

    t = Thread(target=_t)
    t.start()
    return []


@fm_ki.post("flex-offer")
def _send_flexibility(flex_value: float) -> List[KEFlexOffer]:
    global flex_request
    print(f"_send_flexibility {flex_value}")
    flex_profile = SplitURIBase.uri_append_ref( URIRef(fm_ki.get_kb_id()) , "profile")
    flex_offer = KEFlexOffer(
        market=flex_request.market, flex_request=flex_request.flex_request, asset_manager=URIRef(fm_ki.get_kb_id()),
        flex_profile=flex_profile,
        profile_price=rdf_nil, price=Literal(0.0),
        dp=SplitURIBase.uri_append_ref(str(flex_profile), "dp"),
        dpr=SplitURIBase.uri_append_ref(flex_profile, "dpr"),
        ts=Literal(time_utils.xsd_from_ts(ts=time_utils.current_timestamp())),
        value=Literal(flex_value))
    return [flex_offer]


@fm_ki.react("flex-request")
def on_flex_request(ki_id, bindings: List[KEFlexRequest]):
    # respond with timeseries metadata
    print("on flex request")

    def _handle_request():
        handle_request(bindings)

    t = Thread(target=_handle_request)
    t.start()
    return []


flex_request: KEFlexRequest


def handle_request(bindings: List[KEFlexRequest]):
    """
    slow interaction
    :return:
    """
    global flex_request
    if len(bindings) != 1:
        raise Exception("invalid flex request count")
    flex_request = bindings[0]
    print("get list of dates")
    resp: KIAskResponse = _get_required_days()

    baseline_dates: List[BaselineDateResponse] = [BaselineDateResponse(**b) for b in resp.binding_set]
    print(f"get baseline (ref profile) {baseline_dates}")
    resp: KIPostResponse = _get_baseline(baseline_dates=baseline_dates)
    print(f"baseline resp {[k.knowledgeBaseId for k in resp.exchangeInfo]}")
