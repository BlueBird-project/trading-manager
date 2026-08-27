from typing import List, Dict, Tuple, Any

from ke_client import KIHolder, TargetedBindings
from ke_client.ki_model import KIAskResponse, KIPostResponse

from tm.models.digital_twin import DTForecastInfoDAO, DigitalTwinDAO
from tm.modules.ke_interaction.interactions.dt_model import *
from tm.modules.ke_interaction.service import dt_service

ki = KIHolder()


# region digital twin service details
# noinspection PyUnusedLocal
@ki.react("dt-info")
def on_dt_info(ki_id, bindings: List[DigitalTwinInfo], kb_id):
    print("on dt-info")
    dt_service.process(bindings, kb_id)
    return []


@ki.ask("dt-info")
def _request_dt_info():
    return []


# endregion
# @ki.react("dt-offer-relation")
# def _request_dt_ts_info(ki_id, bindings: List[ForecastOfferRelation]):
#     dt_service.join_forecast_offer(relations=bindings)
#     return []


# noinspection PyUnusedLocal
@ki.ask("dt-ts-info")
def _request_dt_ts_info(req: List[DTTSInfoRequest], kb_id: str):
    return TargetedBindings(
        bindings=req,
        knowledge_bases=[kb_id])


# @ki.post("dt-ts-info")
# def _request_dt_ts_by_market(req: List[DTTSInfoMarketRequest]):
#     return req


# noinspection PyUnusedLocal
@ki.react("dt-ts-info")
def on_dt_ts_info(ki_id, bindings: List[DTTSInfo]):
    print("on new digital twin timeseries info")
    ack = dt_service.process_forecast_info(bindings)
    print(bindings)
    # TODO  save dt ts metadata
    # ack = dt_service.process_timeseries_info(bindings)
    return []


@ki.react("dt-ts")
def on_forecast(ki_id, bindings: List[DTPnt]):
    print(f"on new digital twin timeseries data: {len(bindings)}")
    dt_service.process_forecast(forecast=bindings)
    # ack = dt_service.process_timeseries(bindings)
    # print(dt_ts)
    return []


@ki.ask("dt-ts")
def _request_forecast(req: List[DTPntRequest], kb_id):
    return TargetedBindings(
        bindings=req,
        knowledge_bases=[kb_id])


# @ki.react("forecast-test")
# def on_dt_ts(ki_id, bindings):
#     print(f"forecast-test data: {len(bindings)}")
#     print(bindings)
#     return []
# @ki.ask("forecast-test")
# def _ask_test(ts_uri_ref: URIRef):
#     return [DTPntRequest(ts_uri=ts_uri_ref)]


# @ki.react("dt-ts2")
# def on_dt_ts(ki_id, bindings: List[DTPnt2]):
#     print(f"test new digital twin timeseries data: {len(bindings)}")
#     # dt_service.process_forecast(forecast=bindings)
#     # ack = dt_service.process_timeseries(bindings)
#     # print(dt_ts)
#     return []


# @ki.ask("dt-ts")
# def _request_dt_ts(ts_uri_ref: URIRef):
#     return [DTPntRequest(ts_uri=ts_uri_ref)]


def request_dt_info() -> List[DigitalTwinDAO]:
    bindings: KIAskResponse = _request_dt_info()

    res = []
    for i, b in enumerate(bindings.binding_set):
        kb_id = bindings.exchangeInfo[i].knowledgeBaseId
        res += dt_service.process([DigitalTwinInfo(**b)], kb_id=kb_id)
        # res.append(DigitalTwinInfo(**b))
    return res


def request_forecast_info(req: List[DTTSInfoRequest], kb_id: str) -> List[DTForecastInfoDAO]:
    bindings: KIAskResponse = _request_dt_ts_info(req, kb_id)
    forecast_info = [DTTSInfo(**b) for b in bindings.binding_set]
    ack = dt_service.process_forecast_info(bindings=forecast_info)
    return ack


# def request_dt_data(dt_uri: str, ts_from: int, ts_to: int) -> Dict[str, List]:
#     ts_uri_ref: URIRef = DTTSUri(prefix=dt_uri, ts_start=ts_from, ts_end=ts_to).uri_ref
#     # noinspection PyTypeChecker
#
#     bindings: KIAskResponse = _request_dt_ts(ts_uri_ref=ts_uri_ref)
#     stored_forecasts = dt_service.process_forecast(forecast=[DTPnt(**b) for b in bindings.binding_set])
#     return stored_forecasts


# def ask_test(ts_uri_ref: URIRef)  :
#     # noinspection PyTypeChecker
#     print("ASK test")
#     bindings: KIAskResponse = _ask_test(ts_uri_ref=ts_uri_ref)
#
#     print(bindings)


# def request_dt_data_by_id(ts_uri_ref: URIRef) -> Dict[str, List]:
#     # noinspection PyTypeChecker
#     bindings: KIAskResponse = _request_dt_ts(ts_uri_ref=ts_uri_ref)
#     stored_forecasts = dt_service.process_forecast(forecast=[DTPnt(**b) for b in bindings.binding_set])
#     return stored_forecasts

def request_forecast(ts_uri: URIRef, kb_id) -> Dict[Any, List[DTPnt]]:
    # noinspection PyTypeChecker
    resp: KIAskResponse = _request_forecast([DTPntRequest(ts_uri=ts_uri)], kb_id)
    forecast = [DTPnt(**b) for b in resp.binding_set]
    ack = dt_service.process_forecast(forecast=forecast)
    return ack
