from typing import Optional, Union

from ke_client import ki_object, BindingsBase, OptionalLiteral, is_nil
from rdflib import URIRef, Literal


@ki_object("tm-info", allow_partial=True)
class TMInfoRequest(BindingsBase):
    market_uri: Optional[URIRef] = None


@ki_object("tm-info")
class TMInfo(BindingsBase):
    tm_uri: URIRef
    market_uri: URIRef
    command_uri: URIRef


@ki_object("tm-market-offer-info", allow_partial=True)
class TMMarketOfferInfoRequest(BindingsBase):
    command_uri: URIRef = None
    time_create: OptionalLiteral = None
    sequence: OptionalLiteral = None

    def __init__(self, skip_nil=True, **kwargs):
        super().__init__(bindings=kwargs)
        if skip_nil:
            if is_nil(self.sequence):
                self.sequence = None


@ki_object("tm-market-offer-info")
class TMMarketOfferInfoBindings(BindingsBase):
    tm_uri: URIRef
    market_uri: URIRef
    market_type: URIRef
    command_uri: URIRef
    offer_uri: URIRef
    time_create: Literal
    sequence: OptionalLiteral = None
    update_rate: Literal
    duration: Literal
    duration_uri: URIRef

    def __init__(self, skip_nil=True, **kwargs):
        super().__init__(bindings=kwargs)
        if skip_nil:
            if is_nil(self.sequence):
                self.sequence = None

    # @property
    # def duration_ms(self) -> int:
    #     return int(parse_duration(self.duration, as_timedelta_if_possible=True).total_seconds() * 1000)
    #
    # @property
    # def update_rate_min(self) -> int:
    #     return int(parse_duration(self.update_rate, as_timedelta_if_possible=True).total_seconds() / 60)

    # @property
    # def isp_len(self) -> int:
    #     isp_unit = self.update_rate_min
    #     total_min = int(parse_duration(self.duration, as_timedelta_if_possible=True).total_seconds() / 60)
    #     r = total_min % isp_unit
    #     return int(total_min / isp_unit) + (1 if r != 0 else 0)


@ki_object("tm-market-offer", allow_partial=True)
class TMMarketOfferRequest(BindingsBase):
    tm_uri: URIRef
    offer_uri: URIRef


@ki_object("tm-market-offer")
class TMMarketOfferBindings(BindingsBase):
    offer_uri: URIRef
    market_uri: URIRef
    tm_uri: URIRef
    command_uri: URIRef
    dp: URIRef
    ts: Literal
    dpr: URIRef
    duration: Literal
    duration_uri: URIRef
    value: Union[URIRef, Literal, None]

    # def __init__(self, **kwargs):
    #     super().__init__(bindings=kwargs)
    #
    # @property
    # def ts_ms(self) -> int:
    #     return time_utils.xsd_to_ts(self.ts)
    #
    # def get_value(self) -> Optional[float]:
    #     return self.convert_value(self.value, float)
    #
    # def isp_len(self, isp_unit: int):
    #     period_minutes = int(parse_duration(self.duration, as_timedelta_if_possible=True).total_seconds() / 60)
    #     return math.ceil(period_minutes / isp_unit)
