import math
from typing import Optional

from isodate import parse_duration
from ke_client import ki_split_uri, SplitURIBase, BindingsBase, ki_object, OptionalLiteral
from ke_client.utils import time_utils
from rdflib import URIRef, Literal


@ki_object("dt-info")
class DigitalTwinInfo(BindingsBase):
    dt_uri: URIRef
    command_uri: URIRef
    market_uri: URIRef

    def __init__(self, **kwargs):
        super().__init__(bindings=kwargs)


# @ki_object("self-dt-info")
# class SelfDigitalTwinInfo(BindingsBase):
#     command_uri: URIRef
#     market_uri: URIRef
#
#     def __init__(self, **kwargs):
#         super().__init__(bindings=kwargs)


@ki_object("dt-ts-info")
class DTTSInfo(BindingsBase):
    command_uri: URIRef
    market_uri: URIRef
    ts_uri: URIRef
    forecast_of: URIRef
    time_create: Literal
    ts_interval_uri: URIRef
    ts_date_from: Literal
    ts_date_to: Literal
    update_rate: Literal

    # range section

    # power_range: Optional[URIRef] = rdf_nil
    # power_range_max: Optional[URIRef] = rdf_nil
    # max_value: OptionalLiteral = rdf_nil
    # power_range_min: Optional[URIRef] = rdf_nil
    # min_value: OptionalLiteral = rdf_nil

    # range

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

    @property
    def isp_len(self) -> int:
        ms_diff = self.to_ts - self.from_ts
        min_diff = ms_diff / 60000
        return math.ceil(min_diff / self.update_rate_min)

    # def get_sequence(self) -> str:
    #     return self.convert_value(self.sequence)

    # def get_power_limit(self) -> Tuple[float, float]:
    #     min_value = self.convert_value(self.min_value, float)
    #     max_value = self.convert_value(self.max_value, float)
    #     return min_value, max_value


@ki_object("dt-ts-info", allow_partial=True)
class DTTSInfoRequest(BindingsBase):
    # command_uri: URIRef
    forecast_of: URIRef

    # def __init__(self, skip_nil=True, **kwargs):
    #     super().__init__(bindings=kwargs)
    #     if skip_nil:
    #         if is_nil(self.sequence):
    #             self.sequence = None


# @ki_object("dt-ts-info", allow_partial=True)
# class DTTSInfoMarketRequest(BindingsBase):
#     # find by market
#     market_uri: URIRef


# @ki_object("dt-ts-info", result=True)
# class DTTSInfoResponse(BindingsBase):
#     ts_uri: URIRef
#     command_uri: URIRef


@ki_object("dt-ts")
class DTPnt(BindingsBase):
    ts_uri: URIRef
    dp: URIRef
    ts: Literal
    dpr: URIRef
    duration: Literal
    duration_uri: URIRef
    value: OptionalLiteral

    def __init__(self, **kwargs):
        super().__init__(bindings=kwargs)

    @property
    def ts_ms(self) -> int:
        return time_utils.xsd_to_ts(self.ts)

    def get_value(self) -> Optional[float]:
        return self.convert_value(self.value, float)

    def isp_len(self, isp_unit: int):
        period_minutes = int(parse_duration(self.duration, as_timedelta_if_possible=True).total_seconds() / 60)
        return math.ceil(period_minutes / isp_unit)


@ki_object("dt-ts", allow_partial=True)
class DTPntRequest(BindingsBase):
    ts_uri: URIRef

    # def __init__(self, **kwargs):
    #     super().__init__(bindings=kwargs)

    def get_ts_uri(self) -> 'DTTSUri':
        return DTTSUri.parse(uri=self.ts_uri)


@ki_split_uri(uri_template="ts/${sequence}/${ts_start}/${ts_end}")
class DTTSUri(SplitURIBase):
    sequence: str
    ts_start: int
    ts_end: int
    __EMPTY__ = "_"

    def __init__(self, sequence: Optional[str], **kwargs):
        if sequence is None:
            sequence = DTTSUri.__EMPTY__
        super().__init__(sequence=sequence, **kwargs)

    @property
    def processed_sequence(self) -> Optional[str]:
        if self.sequence == DTTSUri.__EMPTY__:
            return None
        return self.sequence


@ki_split_uri(uri_template="${ts_start}/${ts_end}/dp/${isp}")
class DTDPUri(SplitURIBase):
    # dt_uri: str
    ts_start: int
    ts_end: int
    isp: int


@ki_split_uri(uri_template="${ts_start}/${ts_end}/dpr/${isp}")
class DTDPRUri(SplitURIBase):
    # dt_uri: str
    ts_start: int
    ts_end: int
    isp: int

    # def __init__(self, dt_uri: str, **kwargs):
    #     dt_uri = self.normalize_kb_id(kb_id=dt_uri)
    #     super().__init__(dt_uri=dt_uri, **kwargs)
