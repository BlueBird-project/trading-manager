import hashlib
import random
from datetime import timedelta
from typing import List, Optional

from isodate import duration_isoformat, parse_duration
from ke_client.utils import time_utils
from ke_client import KIHolder, BindingsBase, OptionalLiteral, ki_object
from ke_client.ki_model import KIPostResponse, ExchangeInfoStatus
from rdflib import URIRef, Literal
from tm.modules.ke_interaction.interactions.dt_model import DigitalTwinInfo, DTTSUri, \
    DTDPUri, DTDPRUri,  DTTSInfoRequest


@ki_object("dt-ts-info")
class DTTSInfo(BindingsBase):
    command_uri: URIRef
    ts_uri: URIRef
    time_create: Literal
    ts_interval_uri: URIRef
    ts_date_from: Literal
    sequence: OptionalLiteral = None
    ts_date_to: Literal

    def __init__(self, **kwargs):
        super().__init__(bindings=kwargs)

    @property
    def update_rate_min(self) -> int:
        return int(parse_duration(self.update_rate, as_timedelta_if_possible=True).total_seconds() / 60)

    @property
    def create_ts(self):
        return time_utils.xsd_to_ts(self.time_create)

    @property
    def from_ts(self) -> int:
        return time_utils.xsd_to_ts(self.ts_date_from)

    @property
    def to_ts(self) -> int:
        return time_utils.xsd_to_ts(self.ts_date_to)

    @property
    def interval_ts(self) -> int:
        return self.to_ts - self.from_ts


@ki_object("dt-ts")
class DTPnt(BindingsBase):
    ts_uri: URIRef
    dp: URIRef
    ts: Literal
    dpr: URIRef
    value: Optional[Literal]

    def __init__(self, **kwargs):
        super().__init__(bindings=kwargs)

    @property
    def ts_ms(self) -> int:
        return time_utils.xsd_to_ts(self.ts)

    def get_value(self) -> Optional[float]:
        return self.convert_value(self.value, float)


@ki_object("dt-ts", allow_partial=True)
class DTPntRequest(BindingsBase):
    ts_uri: URIRef

    # def __init__(self, **kwargs):
    #     super().__init__(bindings=kwargs)

    def get_ts_uri(self) -> 'DTTSUri':
        return DTTSUri.parse(uri=self.ts_uri)


dt_ki = KIHolder()
_market_uri: URIRef = None
_current_forecast_uri: DTTSUri = None
TM_KB_ID = ["http://demo.tm.bluebird.com", "http://tm.bluebird.com"]


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


#
@dt_ki.post("dt-ts-info")
def _post_ts_info(market_uri: URIRef, ts_uri: DTTSUri) -> List[DTTSInfo]:
    ts_start = time_utils.current_timestamp()
    ts_end = ts_start + 3600 * 1000 * 24
    ts_interval_uri = URIRef(ts_uri.uri + "/interval")
    dt_info = DTTSInfo(command_uri=_init_command_uri(market_uri=str(market_uri)),
                       ts_uri=ts_uri.uri_ref,
                       update_rate=Literal(duration_isoformat(timedelta(minutes=15))),
                       time_create=Literal(time_utils.xsd_from_ts(time_utils.current_timestamp())),
                       ts_interval_uri=ts_interval_uri,
                       ts_date_from=Literal(time_utils.xsd_from_ts(ts_start)),
                       ts_date_to=Literal(time_utils.xsd_from_ts(ts_end)))

    return [dt_info]


#
@dt_ki.answer("dt-ts-info")
def on_ts_info(ki_id, bindings: List[DTTSInfoRequest]) -> List[DTTSInfo]:
    global _market_uri
    global _current_forecast_uri
    if _current_forecast_uri is None:
        current_forecast_uri = _get_forecast_uri()
    else:
        current_forecast_uri = _current_forecast_uri
    print("dt-ts-info")
    ts_start = time_utils.current_timestamp()
    ts_end = ts_start + 3600 * 1000 * 24
    ts_interval_uri = URIRef(current_forecast_uri.uri + "/interval")
    ds_info = DTTSInfo(command_uri=_init_command_uri(market_uri=str(_market_uri)),
                       ts_uri=current_forecast_uri.uri_ref,
                       update_rate=Literal(duration_isoformat(timedelta(minutes=15))),
                       time_create=Literal(time_utils.xsd_from_ts(time_utils.current_timestamp())),
                       ts_interval_uri=ts_interval_uri,
                       ts_date_from=Literal(time_utils.xsd_from_ts(ts_start)),
                       ts_date_to=Literal(time_utils.xsd_from_ts(ts_end)))

    print(ds_info)
    return [ds_info]


#
#
def _generate_sample_ts(ts_uri: DTTSUri, size=96) -> List[DTPnt]:
    cur_ts = ts_uri.ts_start
    isp = 0
    res = []
    while cur_ts <= ts_uri.ts_end and isp < (size):
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
    sample_ts = _generate_sample_ts(ts_uri=ts_uri, size=96)

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
            current_forecast_uri = _get_forecast_uri()
        else:
            current_forecast_uri = _current_forecast_uri
        sample_ts = _generate_sample_ts(ts_uri=current_forecast_uri)

    print(f"forecast size: {len(sample_ts)}")
    return sample_ts


def set_market_uri(market_uri: URIRef):
    global _market_uri
    if _market_uri is None:
        _market_uri = market_uri
    else:
        raise Exception(f"Market has been already set: {_market_uri}")


def post_dt_info():
    global _market_uri
    resp_bindings: KIPostResponse = _post_dt_info(market_uri=_market_uri)
    info_ack = [{"status": b.status == ExchangeInfoStatus.SUCCEEDED, "kb_id": b.knowledgeBaseId}
                for b in resp_bindings.exchangeInfo]
    return info_ack


def _get_forecast_uri() -> DTTSUri:
    ts_start = time_utils.current_timestamp()
    ts_end = ts_start + 3600 * 1000 * 24
    ts_uri = DTTSUri(prefix=dt_ki.get_kb_id(), ts_start=ts_start, ts_end=ts_end)
    return ts_uri


def post_forecast(market_uri: URIRef):
    global _current_forecast_uri
    ts_uri = _get_forecast_uri()
    _current_forecast_uri = ts_uri
    ################################################
    # post metadata
    ################################################
    resp_bindings: KIPostResponse = _post_ts_info(market_uri, ts_uri)
    info_ack = resp_bindings.get_ack()
    print("info ack")
    print(info_ack)
    ################################################
    # post timeseries
    ################################################
    print("info ts")
    cur_ts = time_utils.current_timestamp()
    resp_bindings: KIPostResponse = _post_ts(ts_uri)
    duration_sec = (time_utils.current_timestamp() - cur_ts) / 1000
    print(f"POST ts forecast duration {duration_sec}s")
    ts_ack = resp_bindings.get_ack()
    return ts_ack
