from typing import Optional, Tuple

from ke_client import ki_object, BindingsBase, OptionalLiteral, is_nil, rdf_nil
from ke_client.utils import time_utils
from rdflib import URIRef, Literal

from tm.modules.ke_interaction.interactions.dam_model import TimeIntervalUri
from tm.utils import TimeSpan


class TOUPriceInfoQuery(BindingsBase):
    tm_uri: URIRef
    max_value: OptionalLiteral = None
    min_value: OptionalLiteral = None
    power_range: Optional[URIRef] = None

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

    # def __init__(self, ti: Optional[TimeSpan] = None, **kwargs):
    #     if ti is None:
    #         super().__init__(ts_interval_uri=rdf_nil, ts_date_from=rdf_nil, ts_date_to=rdf_nil, **kwargs)
    #     else:
    #         ts_interval_uri_ref = TimeIntervalUri(ts_from=ti.ts_from, ts_to=ti.ts_to).uri_ref
    #         super().__init__(ts_interval_uri=ts_interval_uri_ref,
    #                          ts_date_from=Literal(time_utils.xsd_from_ts(ti.ts_from)),
    #                          ts_date_to=Literal(time_utils.xsd_from_ts(ti.ts_to)), **kwargs)
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
    tm_uri: URIRef
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
    tm_uri: URIRef
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
    tm_uri: URIRef
    tou_uri: URIRef

    def __init__(self, **kwargs):
        super().__init__(bindings=kwargs)


@ki_object("tm-agent")
class TMAgent(BindingsBase):
    tm_uri: URIRef
