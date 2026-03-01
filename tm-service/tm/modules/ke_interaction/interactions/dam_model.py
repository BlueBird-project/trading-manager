import math
from typing import Optional, Union, Type

from effi_onto_tools.db import TimeSpan
from ke_client.utils import time_utils 
from isodate import parse_duration
from ke_client import ki_object, is_nil, ki_split_uri, SplitURIBase, OptionalLiteral, rdf_nil
from ke_client import BindingsBase
from ke_client.utils.enum_utils import   BaseEnum, EnumItem
from pydantic import BaseModel, ConfigDict
from rdflib import URIRef, Literal
from rdflib.util import from_n3

# DAM_market_type: Literal = Literal("ubmarket:DayAheadMarket")
UBEFLEX_MARKET_BASE = "https://ubeflex.bluebird.eu/market/"
DAYAHEAD_MARKET_TYPE = URIRef(value="DayAheadMarket", base=UBEFLEX_MARKET_BASE)
INTRADAY_MARKET_TYPE = URIRef(value="IntradayMarket", base=UBEFLEX_MARKET_BASE)


class MarketTypeValue(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    name: str
    uri_ref: URIRef


class MarketType(BaseEnum["MarketTypeValue"]):
    DAY_AHEAD = EnumItem(MarketTypeValue(name="DayAheadMarket", uri_ref=DAYAHEAD_MARKET_TYPE), alias="DayAheadMarket")
    INTRADAY = EnumItem(MarketTypeValue(name="IntradayMarket", uri_ref=INTRADAY_MARKET_TYPE), alias="IntradayMarket")


@ki_object("market")
class EnergyMarketBindings(BindingsBase):
    market_uri: URIRef
    country_name: Literal
    country_uri: URIRef
    market_type: URIRef

    # market_type: Literal = Literal("ubmarket:DayAheadMarket")

    # market_type: Literal = DAM_market_type

    def __init__(self, **kwargs):
        super().__init__(bindings=kwargs)


@ki_object("market", allow_partial=True)
class EnergyMarketRequest(BindingsBase):
    country_name: OptionalLiteral = None
    market_type: Optional[URIRef] = None


# @ki_object("market", allow_partial=True)
# class EnergyMarketRequest(BindingsBase):
#     country_name: OptionalLiteral = None
# @ki_object("market-offer-info-query", allow_partial=True)
# class MarketOfferInfoQuery(BindingsBase):
#     ts_interval_uri: URIRef
#     market_uri: URIRef
#     ts_date_from: Literal
#     ts_date_to: Literal
#
#     def __init__(self, **kwargs):
#         super().__init__(bindings=kwargs)
#
#     @property
#     def ts_from(self) -> int:
#         return time_utils.xsd_to_ts(self.ts_date_from)
#
#     @property
#     def ts_to(self) -> int:
#         return time_utils.xsd_to_ts(self.ts_date_to)


# @ki_object("market-offer-info-query", result=True)
# class MarketOfferInfoResponse(BindingsBase):
#     market_uri: URIRef
#     offer_uri: URIRef
#     time_create: Literal
#
#     @property
#     def create_ts(self):
#         return time_utils.xsd_to_ts(self.time_create)


@ki_object("market-offer-info")
class MarketOfferInfoBindings(BindingsBase):
    market_uri: URIRef
    market_type: URIRef
    offer_uri: URIRef
    time_create: Literal
    sequence: OptionalLiteral = None
    update_rate: Literal
    duration: Literal

    def __init__(self, skip_nil=True, **kwargs):
        super().__init__(bindings=kwargs)
        if skip_nil:
            if is_nil(self.sequence):
                self.sequence = None

    @property
    def create_ts(self):
        return time_utils.xsd_to_ts(self.time_create)

    @property
    def duration_ms(self) -> int:
        return int(parse_duration(self.duration, as_timedelta_if_possible=True).total_seconds() * 1000)

    @property
    def update_rate_min(self) -> int:
        return int(parse_duration(self.update_rate, as_timedelta_if_possible=True).total_seconds() / 60)

    @property
    def isp_len(self) -> int:
        isp_unit = self.update_rate_min
        total_min = int(parse_duration(self.duration, as_timedelta_if_possible=True).total_seconds() / 60)
        r = total_min % isp_unit
        return int(total_min / isp_unit) + (1 if r != 0 else 0)
    # @property
    # def isp_unit(self) -> int:
    #     from tm.modules.ke_interaction import KIVars
    #     res = from_n3(KIVars.ISP_UNIT)
    #     return int(parse_duration(res, as_timedelta_if_possible=True).total_seconds() / 60)

    # @property
    # def isp_len(self) -> int:
    #     from tm.modules.ke_interaction import KIVars
    #     res = from_n3(KIVars.DAY_DURATION)
    #     day_duration = int(parse_duration(res, as_timedelta_if_possible=True).total_seconds() / 60)
    #     isp_unit = self.isp_unit
    #     if day_duration % isp_unit == 0:
    #         return int(day_duration / isp_unit)
    #         # TODO: raise exception ? the last isp is going to have different length
    #     return int(day_duration / isp_unit) + 1


@ki_object("market-offer-info-filtered")
class MarketOfferInfoFilteredBindings(MarketOfferInfoBindings):
    ts_interval_uri: URIRef
    ts_date_from: Literal
    ts_date_to: Literal


@ki_object("market-offer-info", allow_partial=True)
class MarketOfferInfoRequest(BindingsBase):
    market_uri: URIRef
    # market_type: Optional[URIRef]
    # sequence: Optional[Literal]


@ki_object("market-offer-info-filtered", allow_partial=True)
class MarketOfferInfoFilteredRequest(MarketOfferInfoRequest):
    ts_interval_uri: Optional[URIRef]
    ts_date_from: OptionalLiteral
    ts_date_to: OptionalLiteral

    def __init__(self, ti: Optional[TimeSpan] = None, **kwargs):
        if ti is None:
            super().__init__(ts_interval_uri=rdf_nil, ts_date_from=rdf_nil, ts_date_to=rdf_nil, **kwargs)
        else:
            ts_interval_uri_ref = TimeIntervalUri(ts_from=ti.ts_from, ts_to=ti.ts_to).uri_ref
            super().__init__(ts_interval_uri=ts_interval_uri_ref,
                             ts_date_from=Literal(time_utils.xsd_from_ts(ti.ts_from)),
                             ts_date_to=Literal(time_utils.xsd_from_ts(ti.ts_to)), **kwargs)


@ki_object("market-offer")
class MarketOfferBindings(BindingsBase):
    offer_uri: URIRef
    dp: URIRef
    ts: Literal
    dpr: URIRef
    is_measured_in: Literal
    duration: Literal
    value: Union[URIRef, Literal, None]

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


@ki_object("market-offer", allow_partial=True)
class MarketOfferRequest(BindingsBase):
    offer_uri: URIRef


@ki_split_uri(uri_template="http://bluebird.com/interval/${ts_from}/${ts_to}")
class TimeIntervalUri(SplitURIBase):
    ts_from: int
    ts_to: int


@ki_split_uri(uri_template="https://ubeflex.bluebird.eu/country/${country}")
class CountryUri(SplitURIBase):
    country: str
