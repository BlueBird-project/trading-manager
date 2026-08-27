import hashlib
from datetime import timedelta
from typing import List

from isodate import duration_isoformat
from ke_client import KIHolder
from ke_client.ki_model import KIPostResponse, ExchangeInfoStatus, KIAskResponse
from ke_client.utils import time_utils

from examples.ki import dt_model
from examples.ki.dt_model import *
from tm.modules.ke_interaction.interactions.dt_model import DigitalTwinInfo, DTTSUri, \
    DTTSInfoRequest

dt_ki = KIHolder()
_tm_info: dt_model.TMInfo = None


# region dt info
def _init_command_uri(market_uri: str):
    md5_hash = hashlib.md5(market_uri.encode())
    hash_str = md5_hash.hexdigest()

    return URIRef(dt_ki.get_kb_id() + "/command/" + hash_str)


@dt_ki.post("dt-info")
def _post_dt_info(market_uri: URIRef) -> List[DigitalTwinInfo]:
    dt_info = DigitalTwinInfo(dt_uri=URIRef(dt_ki.get_kb_id()),
                              command_uri=_init_command_uri(market_uri=str(market_uri)),
                              market_uri=market_uri)
    return [dt_info]


@dt_ki.post("self-dt-info")
def _post_self_dt_info(market_uri: URIRef) -> List[SelfDigitalTwinInfo]:
    dt_info = SelfDigitalTwinInfo(
        command_uri=_init_command_uri(market_uri=str(market_uri)),
        market_uri=market_uri)
    return [dt_info]


@dt_ki.answer("self-dt-info")
def on_self_dt_info_request(ki_id, bindings):
    global _tm_info
    print("on_self_dt_info_request")
    dt_info = SelfDigitalTwinInfo(
        command_uri=_init_command_uri(market_uri=str(_tm_info.market_uri)),
        market_uri=_tm_info.market_uri)
    print(dt_info)

    return [dt_info]


@dt_ki.answer("dt-info")
def on_dt_info_request(ki_id, bindings):
    global _tm_info
    print("on_dt_info_request")
    dt_info = DigitalTwinInfo(dt_uri=URIRef(dt_ki.get_kb_id()),
                              command_uri=_init_command_uri(market_uri=str(_tm_info.market_uri)),
                              market_uri=_tm_info.market_uri)
    print(dt_info)

    return [dt_info]


# endregion


# region forecast

@dt_ki.post("dt-ts-info")
def _post_ts_info(offer_uri: URIRef, sequence: Optional[str]) -> List[DTTSInfo]:
    global _tm_info
    # set timeseries time range
    ts_start = time_utils.current_timestamp()
    ts_end = ts_start + 3600 * 1000 * 24
    from examples.ki.dt_offer_helper import offer_manager, _get_forecast_uri
    tm_offer = offer_manager.get_offer_info(offer_uri=offer_uri, get_info_handler=get_offer_uri)
    forecast_uri = _get_forecast_uri(command_uri=_init_command_uri(market_uri=str(_tm_info.market_uri)),
                                     sequence=tm_offer.sequence, offer_end_ts=tm_offer.end_ts)
    ts_interval_uri = URIRef(forecast_uri.uri + "/interval")
    dt_info = DTTSInfo(command_uri=_init_command_uri(market_uri=str(_tm_info.market_uri)),
                       market_uri=_tm_info.market_uri,
                       ts_uri=forecast_uri.uri_ref, forecast_of=offer_uri, sequence=sequence,
                       update_rate=Literal(duration_isoformat(timedelta(minutes=15))),
                       time_create=Literal(time_utils.xsd_from_ts(time_utils.current_timestamp())),
                       ts_interval_uri=ts_interval_uri,
                       ts_date_from=Literal(time_utils.xsd_from_ts(ts_start)),
                       ts_date_to=Literal(time_utils.xsd_from_ts(ts_end)))

    return [dt_info]


def _get_forecast_info(offer_uri: URIRef) -> DTTSInfo:
    from examples.ki.dt_offer_helper import offer_manager
    from examples.ki.dt_offer_helper import _get_forecast_uri
    tm_offer = offer_manager.get_offer_info(offer_uri=offer_uri, get_info_handler=get_offer_uri)
    forecast_uri = _get_forecast_uri(command_uri=_init_command_uri(market_uri=str(_tm_info.market_uri)),
                                     sequence=tm_offer.sequence, offer_end_ts=tm_offer.end_ts)
    tm_offer.forecast_uri = forecast_uri.uri_ref
    ts_start = time_utils.current_timestamp()
    ts_end = ts_start + 3600 * 1000 * 24
    ts_interval_uri = URIRef(forecast_uri.uri + "/interval")
    dt_info = DTTSInfo(command_uri=_init_command_uri(market_uri=str(_tm_info.market_uri)),
                       market_uri=_tm_info.market_uri,
                       ts_uri=forecast_uri.uri_ref, forecast_of=tm_offer.offer_uri, sequence=tm_offer.sequence,
                       update_rate=Literal(duration_isoformat(timedelta(minutes=15))),
                       time_create=Literal(time_utils.xsd_from_ts(time_utils.current_timestamp())),
                       ts_interval_uri=ts_interval_uri,
                       ts_date_from=Literal(time_utils.xsd_from_ts(ts_start)),
                       ts_date_to=Literal(time_utils.xsd_from_ts(ts_end)))
    return dt_info


#
@dt_ki.answer("dt-ts-info")
def on_ts_info(ki_id, bindings: List[DTTSInfoRequest]) -> List[DTTSInfo]:
    global _tm_info
    res = []
    for b in bindings:
        res.append(_get_forecast_info(b.forecast_of))

    print(res)

    return res


@dt_ki.answer("dt-ts")
def on_ts_info(ki_id, bindings: List[DTPntRequest]) -> List[DTPnt]:
    global _tm_info
    from examples.ki.dt_offer_helper import offer_manager, generate_sample_forecast
    res = []
    for b in bindings:
        tm_offer = offer_manager.get_forecast_of(forecast_uri=b.ts_uri)
        forecast_ts = offer_manager.get_forecast(ts_uri=b.ts_uri)
        if len(forecast_ts) < 1:
            def _get_offer():
                return get_offer(offer_uris=[tm_offer.offer_uri])

            offer = offer_manager.get_offer(tm_offer.offer_uri, get_info_handler=get_offer_uri,
                                            get_offer_handler=_get_offer)
            print(f"forecast size for {tm_offer.offer_uri} : {len(offer)} ")
            forecast_ts = generate_sample_forecast(ts_uri=DTTSUri.parse(b.ts_uri,prefix=_init_command_uri(market_uri=str(_tm_info.market_uri))),
                                                   offer=offer, kb_id=dt_ki.get_kb_id())

        print(f"forecast: {forecast_ts}")
        res += forecast_ts

    return res


@dt_ki.post("dt-ts")
def _post_ts(ts_uri: DTTSUri, offer: List[TMMarketOfferBindings]) -> List[DTPnt]:
    from examples.ki.dt_offer_helper import generate_sample_forecast
    forecast_ts = generate_sample_forecast(ts_uri=ts_uri, offer=offer, kb_id=dt_ki.get_kb_id())

    return forecast_ts


# endregion


# @dt_ki.answer("dt-ts")
# def on_dt_ts_request(ki_id, bindings: List[DTPntRequest]) -> List[DTPnt]:
#     print("on_dt_ts_request:dt-ts")
#     if len(bindings) > 0:
#         ts_uri = DTTSUri.parse(uri=bindings[0].ts_uri, prefix=dt_ki.get_kb_id())
#         sample_ts = _generate_sample_ts(ts_uri=ts_uri)
#
#     else:
#         global _current_forecast_uri
#         if _current_forecast_uri is None:
#             current_forecast_uri = _get_forecast_uri()
#         else:
#             current_forecast_uri = _current_forecast_uri
#         sample_ts = _generate_sample_ts(ts_uri=current_forecast_uri)
#
#     print(f"forecast size: {len(sample_ts)}")
#     return sample_ts

# region trading manager
@dt_ki.ask("tm-info")
def _ask_tm_info():
    return [dt_model.TMInfoRequest()]


@dt_ki.ask("tm-market-offer-info")
def _ask_offer_info(tm_uri: URIRef, command_uri: URIRef):
    return [dt_model.TMMarketOfferInfoRequest(tm_uri=tm_uri, command_uri=command_uri)]


@dt_ki.ask("tm-market-offer")
def _ask_offer(offer_uris: List[URIRef], tm_uri: URIRef):
    return [dt_model.TMMarketOfferRequest(offer_uri=u, tm_uri=tm_uri) for u in offer_uris]


# def set_market_uri(market_uri: URIRef):
#     global _market_uri
#     if _market_uri is None:
#         _market_uri = market_uri
#     else:
#         raise Exception(f"Market has been already set: {_market_uri}")


def set_tm(tm: dt_model.TMInfo):
    global _tm_info
    if _tm_info is None:
        _tm_info = tm
    else:
        raise Exception(f"Market has been already set: {_tm_info}")


def post_dt_info():
    global _tm_info
    resp_bindings: KIPostResponse = _post_dt_info(market_uri=_tm_info.market_uri)
    info_ack = [{"status": b.status == ExchangeInfoStatus.SUCCEEDED, "kb_id": b.knowledgeBaseId}
                for b in resp_bindings.exchangeInfo]
    return info_ack


def post_self_dt_info():
    global _tm_info
    resp_bindings: KIPostResponse = _post_self_dt_info(market_uri=_tm_info.market_uri)
    info_ack = [{"status": b.status == ExchangeInfoStatus.SUCCEEDED, "kb_id": b.knowledgeBaseId}
                for b in resp_bindings.exchangeInfo]
    return info_ack


def post_forecast(offer_uri: URIRef, offer: List[TMMarketOfferBindings]):
    # global _current_forecast_uri
    from examples.ki.dt_offer_helper import offer_manager
    from examples.ki.dt_offer_helper import _get_forecast_uri
    offer_info = offer_manager.get_offer_info(offer_uri=offer_uri, get_info_handler=get_offer_uri)
    if offer_info is None:
        print(f"no offer: {offer_uri}")
        return
    ts_uri = _get_forecast_uri(command_uri=_init_command_uri(market_uri=str(_tm_info.market_uri)),
                               sequence=offer_info.sequence, offer_end_ts=offer_info.end_ts)

    # _current_forecast_uri = ts_uri
    ################################################
    # post metadata
    ################################################

    resp_bindings: KIPostResponse = _post_ts_info(offer_uri=offer_uri, sequence=offer_info.sequence)
    info_ack = resp_bindings.get_ack()
    print("info ack")
    print(info_ack)
    ################################################
    # post timeseries
    ################################################
    print("info ts")
    cur_ts = time_utils.current_timestamp()
    resp_bindings: KIPostResponse = _post_ts(ts_uri, offer=offer)
    duration_sec = (time_utils.current_timestamp() - cur_ts) / 1000
    print(f"POST ts forecast duration {duration_sec}s")
    ts_ack = resp_bindings.get_ack()
    return ts_ack


def find_tm() -> List[dt_model.TMInfo]:
    resp: KIAskResponse = _ask_tm_info()
    print(resp)
    evaluated_resp: List[dt_model.TMInfo] = [dt_model.TMInfo(**b) for b in resp.binding_set]
    return evaluated_resp


def get_offer_uri() -> List[dt_model.TMMarketOfferInfoBindings]:
    global _tm_info
    resp: KIAskResponse = _ask_offer_info(tm_uri=_tm_info.tm_uri, command_uri=_tm_info.command_uri)
    print(resp)
    evaluated_resp: List[dt_model.TMMarketOfferInfoBindings] = [dt_model.TMMarketOfferInfoBindings(**b) for b in
                                                                resp.binding_set]

    from examples.ki.dt_offer_helper import offer_manager
    for oi in evaluated_resp:
        offer_manager.set_offer_info(offer_uri=oi.offer_uri, end_ts=oi.end_ts, sequence=oi.sequence)
    return evaluated_resp


def get_offer(offer_uris: List[URIRef]) -> List[dt_model.TMMarketOfferBindings]:
    global _tm_info
    resp: KIAskResponse = _ask_offer(offer_uris=offer_uris, tm_uri=_tm_info.tm_uri)
    evaluated_resp: List[dt_model.TMMarketOfferBindings] = [dt_model.TMMarketOfferBindings(**b) for b in
                                                            resp.binding_set]
    return evaluated_resp
