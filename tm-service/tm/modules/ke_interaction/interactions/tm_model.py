from typing import Optional, Tuple, Union

from ke_client import BindingsBase, rdf_nil, OptionalLiteral, is_nil
from ke_client import ki_object
from ke_client.utils import time_utils
from rdflib import URIRef, Literal

from tm.modules.ke_interaction.interactions.dam_model import TimeIntervalUri
from tm.utils import TimeSpan


# region tm info

@ki_object("tm-agent")
class TMAgent(BindingsBase):
    tm_uri: URIRef


@ki_object("tm-info", allow_partial=True)
class TMInfoRequest(BindingsBase):
    market_uri: Optional[URIRef] = None


@ki_object("tm-info")
class TMInfo(BindingsBase):
    market_uri: URIRef
    command_uri: URIRef


# endregion

# region raw offers
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


@ki_object("tm-market-offer", allow_partial=True)
class TMMarketOfferRequest(BindingsBase):
    offer_uri: URIRef


@ki_object("tm-market-offer")
class TMMarketOfferBindings(BindingsBase):
    offer_uri: URIRef
    market_uri: URIRef
    command_uri: URIRef
    dp: URIRef
    ts: Literal
    dpr: URIRef
    duration: Literal
    duration_uri: URIRef
    value: Union[URIRef, Literal, None]


# endregion


# @ki_object("tou-price-info", allow_partial=True)
class TOUPriceInfoQuery(BindingsBase):
    max_value: OptionalLiteral = None
    min_value: OptionalLiteral = None
    power_range: Optional[URIRef] = None
    ts_type:Optional[URIRef] = None

    def __init__(self, **kwargs):
        if "power_range" not in kwargs:
            kwargs["power_range"] = rdf_nil
        super().__init__(bindings=kwargs)

    def get_power_limit(self) -> Tuple[float, float]:
        min_value = self.convert_value(self.min_value, float)
        max_value = self.convert_value(self.max_value, float)
        return min_value, max_value


@ki_object("tou-price-info-filtered", allow_partial=True)
class TOUPriceInfoQueryFiltered(TOUPriceInfoQuery):
    ts_interval_uri: Optional[URIRef]
    ts_date_from: OptionalLiteral
    ts_date_to: OptionalLiteral

    @staticmethod
    def init(ti: Optional[TimeSpan] = None, **kwargs):
        if ti is None:
            kwargs["ts_date_to"] = rdf_nil
            kwargs["ts_date_from"] = rdf_nil
            kwargs["ts_interval_uri"] = rdf_nil
        else:
            kwargs["ts_date_to"] = Literal(time_utils.xsd_from_ts(ti.ts_to))
            kwargs["ts_date_from"] = Literal(time_utils.xsd_from_ts(ti.ts_from))
            kwargs["ts_interval_uri"] = TimeIntervalUri(ts_from=ti.ts_from, ts_to=ti.ts_to).uri_ref
        return TOUPriceInfoQueryFiltered(**kwargs)

    @property
    def ts(self) -> TimeSpan:
        return TimeSpan(ts_from=self.ts_from, ts_to=self.ts_to)

    @property
    def ts_from(self) -> Optional[int]:
        if self.ts_date_from is None or is_nil(self.ts_date_from):
            return None
        return time_utils.xsd_to_ts(self.ts_date_from)

    @property
    def ts_to(self) -> Optional[int]:
        if self.ts_date_to is None or is_nil(self.ts_date_to):
            return None
        return time_utils.xsd_to_ts(self.ts_date_to)


# @ki_object("tou-price-info")
class TOUPriceInfo(BindingsBase):
    tou_uri: URIRef
    ts_type:URIRef
    time_create: Literal
    tou_period: Literal
    tou_period_uri: URIRef
    power_range: Optional[URIRef] = rdf_nil
    power_range_max: Optional[URIRef] = rdf_nil
    max_value: OptionalLiteral = rdf_nil
    power_range_min: Optional[URIRef] = rdf_nil
    min_value: OptionalLiteral = rdf_nil

    def __init__(self, **kwargs):
        super().__init__(bindings=kwargs)

    def get_power_limit(self) -> Tuple[float, float]:
        min_value = self.convert_value(self.min_value, float)
        max_value = self.convert_value(self.max_value, float)
        return min_value, max_value


@ki_object("tou-price-info-filtered")
class TOUPriceInfoFiltered(TOUPriceInfo):
    ts_interval_uri: Optional[URIRef]
    ts_date_from: OptionalLiteral
    ts_date_to: OptionalLiteral

    @property
    def ts_from(self) -> int:
        return time_utils.xsd_to_ts(self.ts_date_from)

    @property
    def ts_to(self) -> int:
        return time_utils.xsd_to_ts(self.ts_date_to)


@ki_object("tou-price")
class TOUPrice(BindingsBase):
    tou_uri: URIRef
    ts_type: URIRef
    dp: URIRef
    ts: Literal
    dpr: URIRef
    value: OptionalLiteral

    def __init__(self, **kwargs):
        if "value" not in kwargs:
            kwargs["value"] = rdf_nil
        super().__init__(bindings=kwargs)

    @property
    def ts_ms(self) -> int:
        return time_utils.xsd_to_ts(self.ts)

    def get_value(self) -> Optional[float]:
        return self.convert_value(self.value, float)


@ki_object("tou-price", allow_partial=True)
class TOUPriceQuery(BindingsBase):
    tou_uri: URIRef
    ts_type: URIRef

    def __init__(self, **kwargs):
        super().__init__(bindings=kwargs)

# @ki_object("tou-price-filtered", allow_partial=True)
# class TOUPriceQueryFiltered(BindingsBase):
#     tou_uri: URIRef
#
#     def __init__(self, **kwargs):
#         super().__init__(bindings=kwargs)


# endregion
