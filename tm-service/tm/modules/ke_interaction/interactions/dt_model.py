from typing import Optional

from ke_client import ki_split_uri, SplitURIBase, BindingsBase, ki_object
from ke_client.utils import time_utils
from rdflib import URIRef, Literal


@ki_object("dt-info")
class DigitalTwinInfo(BindingsBase):
    dt_uri: URIRef
    command_uri: URIRef
    market_uri: URIRef

    def __init__(self, **kwargs):
        super().__init__(bindings=kwargs)


@ki_object("dt-info", result=True)
class DigitalTwinInfoACK(BindingsBase):
    dt_uri: URIRef
    command_uri: URIRef

    def __init__(self, **kwargs):
        super().__init__(bindings=kwargs)


@ki_object("dt-ts-info")
class DTTSInfo(BindingsBase):
    command_uri: URIRef
    ts_uri: URIRef
    time_create: Literal
    ts_interval_uri: URIRef
    ts_date_from: Literal
    ts_date_to: Literal

    def __init__(self, **kwargs):
        super().__init__(bindings=kwargs)

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


@ki_object("dt-ts-info", allow_partial=True)
class DTTSInfoRequest(BindingsBase):
    command_uri: URIRef


@ki_object("dt-ts-info", result=True)
class DTTSInfoACK(BindingsBase):
    command_uri: URIRef
    ts_uri: URIRef

@ki_object("dt-ts", result=True)
class DTTSACK(BindingsBase):
    ts_uri: URIRef


# @ki_object("dt-ts-info", allow_partial=True)
# class DTTSInfoRequest(BindingsBase):
#     command_uri: URIRef
#     ts_date_from: Literal
#     ts_date_to: Literal
#
#     def __init__(self, **kwargs):
#         super().__init__(bindings=kwargs)
#
#     @property
#     def from_ts(self) -> int:
#         return time_utils.xsd_to_ts(self.ts_date_from)
#
#     @property
#     def to_ts(self) -> int:
#         return time_utils.xsd_to_ts(self.ts_date_to)
#
#     @property
#     def interval_ts(self) -> int:
#         return self.to_ts - self.from_ts


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


@ki_split_uri(uri_template="ts/${ts_start}/${ts_end}")
class DTTSUri(SplitURIBase):
    ts_start: int
    ts_end: int

    # def __init__(self, dt_uri: str, **kwargs):
    #     dt_uri = self.normalize_kb_id(kb_id=dt_uri)
    #     super().__init__(dt_uri=dt_uri, **kwargs)


@ki_split_uri(uri_template="${ts_start}/${ts_end}/dp/${isp}")
class DTDPUri(SplitURIBase):
    # dt_uri: str
    ts_start: int
    ts_end: int
    isp: int

    # def __init__(self, dt_uri: str, **kwargs):
    #     dt_uri = self.normalize_kb_id(kb_id=dt_uri)
    #     super().__init__(dt_uri=dt_uri, **kwargs)


@ki_split_uri(uri_template="${ts_start}/${ts_end}/dpr/${isp}")
class DTDPRUri(SplitURIBase):
    # dt_uri: str
    ts_start: int
    ts_end: int
    isp: int

    # def __init__(self, dt_uri: str, **kwargs):
    #     dt_uri = self.normalize_kb_id(kb_id=dt_uri)
    #     super().__init__(dt_uri=dt_uri, **kwargs)
