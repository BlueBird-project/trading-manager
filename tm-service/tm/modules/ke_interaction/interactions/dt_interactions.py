from typing import List

from effi_onto_tools.db import TimeSpan
from ke_client import KIHolder
from ke_client.ki_model import KIPostResponse, KIAskResponse

from tm.modules.ke_interaction.interactions.dt_model import *
from tm.modules.ke_interaction.service import fm_service, dt_service

ki = KIHolder()


# region digital twin service details
@ki.react("dt-info")
def on_dt_info(ki_id, bindings: List[DigitalTwinInfo]) -> List[DigitalTwinInfoACK]:
    print("dt-info")
    ack = dt_service.process(bindings)
    return ack


@ki.ask("dt-info")
def _request_dt_info():
    return []


# endregion

@ki.ask("dt-ts-info")
def _request_dt_ts_info(req: List[DTTSInfoRequest]):
    return req


@ki.react("dt-ts-info")
def on_dt_ts_info(ki_id, bindings: List[DTTSInfo]):
    print("on new digital twin timeseries info")
    print(bindings)
    # TODO  save
    # ack = dt_service.process_timeseries_info(bindings)
    ack = [DTTSInfoACK(command_uri=d.command_uri, ts_uri=d.ts_uri) for d in bindings]
    return ack


@ki.react("dt-ts")
def on_dt_ts(ki_id, bindings: List[DTPnt]):
    print(f"on new digital twin timeseries data: {len(bindings)}")
    # TODO  save
    # ack = dt_service.process_timeseries(bindings)
    # print(dt_ts)
    if len(bindings) > 0:
        #     TODO: check if ack binding can have different length
        return [{"ts_uri": bindings[0].ts_uri.n3()}]
    return []


@ki.ask("dt-ts")
def _request_dt_ts(ts_uri_ref: URIRef):
    return [DTPntRequest(ts_uri=ts_uri_ref)]


def request_dt_info() -> List[DigitalTwinInfo]:
    # noinspection PyTypeChecker
    bindings: KIAskResponse = _request_dt_info()
    # TODO: store response
    return [DigitalTwinInfo(**b) for b in bindings.bindingSet]


def request_dt_ts_info() -> List[DTTSInfo]:
    # noinspection PyTypeChecker
    bindings: KIAskResponse = _request_dt_ts_info()
    # TODO: store response
    return [DTTSInfo(**b) for b in bindings.bindingSet]


def request_dt_data(dt_uri: str, ts_from: int, ts_to: int) -> List[DTPnt]:
    ts_uri_ref: URIRef = DTTSUri(dt_uri=dt_uri, ts_start=ts_from, ts_end=ts_to).uri_ref
    # noinspection PyTypeChecker
    bindings: KIAskResponse = _request_dt_ts(ts_uri_ref=ts_uri_ref)
    # TODO: store response
    return [DTPnt(**b) for b in bindings.bindingSet]


def request_dt_data_by_id(ts_uri_ref: URIRef) -> List[DTPnt]:
    # noinspection PyTypeChecker
    bindings: KIAskResponse = _request_dt_ts(ts_uri_ref=ts_uri_ref)
    # TODO: store response
    return [DTPnt(**b) for b in bindings.bindingSet]
