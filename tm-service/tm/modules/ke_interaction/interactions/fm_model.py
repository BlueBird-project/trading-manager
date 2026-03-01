from typing import Optional, Union, Any

from ke_client import ki_split_uri, SplitURIBase, BindingsBase, ki_object, OptionalLiteral
from ke_client.utils import time_utils 
from rdflib import URIRef, Literal


@ki_object("fm-ts-info-request")
class FMTSRequest(BindingsBase):
    ts_interval_uri: URIRef
    ts_date_from: Literal
    ts_date_to: Literal

    def __init__(self, **kwargs):
        super().__init__(bindings=kwargs)


@ki_object("fm-ts-info-request", result=True)
class FMTSResponse(BindingsBase):
    ts_uri: URIRef
    ts_interval_uri: URIRef
    # ts_usage: Union[Literal, URIRef]
    ts_usage:  URIRef
    time_create: Literal

    def __init__(self, **kwargs):
        super().__init__(bindings=kwargs)


@ki_object("fm-ts", allow_partial=True)
class FMPntQuery(BindingsBase):
    ts_uri: URIRef

    def __init__(self, **kwargs):
        super().__init__(bindings=kwargs)


@ki_object("fm-ts-evaluate")
class FMEvaluateQuery(BindingsBase):
    ts_uri: URIRef
    dp: URIRef
    ts: Literal
    dpr: URIRef
    value: Literal

    def __init__(self, **kwargs):
        super().__init__(bindings=kwargs)


@ki_object("fm-ts-evaluate", result=True)
class FMEvaluateResponse(BindingsBase):
    cost_dp: URIRef
    cost_dpr: URIRef
    cost: OptionalLiteral

    def __init__(self, **kwargs):
        super().__init__(bindings=kwargs)


@ki_object("fm-ts")
class FMPnt(BindingsBase):
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
        return self.convert_value(self.value,float)


@ki_split_uri(uri_template=f"http://fm.bluebird.com/dp" + "/${ts_start}/${isp_start}/${ts_usage}")
class DPSplitURI(SplitURIBase):
    ts_start: int
    ts_usage: int
    isp_start: int


@ki_split_uri(uri_template="http://ke.bluebird.com/interval/${ts_from}/${ts_to}")
class KETimeIntervalUri(SplitURIBase):
    ts_from: int
    ts_to: int


@ki_split_uri(uri_template=f"http://fm.bluebird.com/ts" + "/${ts_from}/${ts_to}/${period_minutes}/${ts_usage}")
class FMTSSplitURI(SplitURIBase):
    ts_from: int
    ts_to: int
    period_minutes: int
    ts_usage: int

    def __init__(self, /, ts_usage: Union[URIRef, int], **data: Any):
        if type(ts_usage) is URIRef:
            ts_usage = FMTSSplitURI.convert_ts_usage(ts_usage)
        super().__init__(ts_usage=ts_usage, **data)

    @staticmethod
    def convert_ts_usage(ts_usage_uri_ref: URIRef):
        uri_fragment: str = ts_usage_uri_ref.defrag().lower()
        #  s4ener:Consumption, s4ener:Downflex,   s4ener:Production,  s4ener:Upflex
        if "Consumption".lower() in uri_fragment:
            return 0
        if "Downflex".lower() in uri_fragment:
            # Downward flexibility (DOWN-flex): The ability to increase consumption or decrease generation
            # to absorb excess energy in the system.
            return 1
        if "Production".lower() in uri_fragment:
            return 2
        if "Upflex".lower() in uri_fragment:
            # Upward flexibility (UP-flex): The ability to decrease consumption or increase generation to
            # meet high demand or low supply conditions.
            return 3

    @staticmethod
    def parse_usage(usage_id: int):
        if 0 == usage_id:
            return URIRef("s4ener:Consumption")
        if 1 == usage_id:
            return URIRef("s4ener:Downflex")
        if 2 == usage_id:
            return URIRef("s4ener:Production")
        if 3 == usage_id:
            return URIRef("s4ener:Upflex")
