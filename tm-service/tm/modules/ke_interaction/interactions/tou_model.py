from typing import Optional, Tuple, Union

from ke_client import BindingsBase, rdf_nil, OptionalLiteral

from tm.modules.ke_interaction.interactions import ki_client
from effi_onto_tools.utils import time_utils
from ke_client import ki_object, SplitURIBase, ki_split_uri
from rdflib import URIRef, Literal


# region exchange binding objects
# @ki_object("tou-price-info", allow_partial=True)
# class TOUPriceInfoSimpleQuery(BindingsBase):
#     time_create: Literal
#     tou_period: Literal
#     power_range: URIRef = rdf_nil
#
#     def __init__(self, **kwargs):
#         super().__init__(bindings=kwargs)


@ki_object("tou-price-info", allow_partial=True)
class TOUPriceInfoSimpleResponse(BindingsBase):
    tou_uri: URIRef

    def __init__(self, **kwargs):
        super().__init__(bindings=kwargs)


@ki_object("tou-price-info", allow_partial=True)
class TOUPriceInfoQuery(BindingsBase):
    time_create: Literal
    tou_period: Literal
    max_value: OptionalLiteral = None
    min_value: OptionalLiteral = None
    power_range: URIRef

    def __init__(self, **kwargs):
        if "power_range" not in kwargs:
            kwargs["power_range"] = rdf_nil
        super().__init__(bindings=kwargs)

    def get_power_limit(self) -> Tuple[float, float]:
        min_value = float(self.min_value) if self.min_value is not None else None
        max_value = float(self.max_value) if self.max_value is not None else None
        return min_value, max_value


@ki_object("tou-price-info")
class TOUPriceInfo(BindingsBase):
    tou_uri: URIRef
    time_create: Literal
    tou_period: Literal
    power_range: URIRef
    power_range_max: URIRef = rdf_nil
    max_value: Union[Literal, URIRef] = rdf_nil
    power_range_min: URIRef = rdf_nil
    min_value: Union[Literal, URIRef] = rdf_nil

    def __init__(self, **kwargs):
        super().__init__(bindings=kwargs)

    def get_power_limit(self) -> Tuple[float, float]:
        min_value = float(self.min_value) if self.min_value is not None else None
        max_value = float(self.max_value) if self.max_value is not None else None
        return min_value, max_value


@ki_object("tou-price")
class TOUPrice(BindingsBase):
    tou_uri: URIRef
    dp: URIRef
    ts: Literal
    dpr: URIRef
    value: Union[Literal, URIRef, None]

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

    def __init__(self, **kwargs):
        super().__init__(bindings=kwargs)


# endregion

# region uris

@ki_split_uri(uri_template=f"{ki_client.kb_id}/offer" + "/${offer_id}/${range_id}/${period_minutes}/${isp_start}")
class OfferDPSplitURI(SplitURIBase):
    range_id: int
    period_minutes: int
    offer_id: int
    isp_start: int


@ki_split_uri(uri_template=f"{ki_client.kb_id}/offer" + "/${range_id}/${period_minutes}/${isp_start}")
class TOUDPSplitURI(SplitURIBase):
    range_id: int
    period_minutes: int
    isp_start: int


@ki_split_uri(uri_template=f"{ki_client.kb_id}/tou" + "/${range_id}/${period_minutes}/${ts}")
class TOUSplitURI(SplitURIBase):
    range_id: int
    period_minutes: int
    ts: int


@ki_split_uri(uri_template=f"{ki_client.kb_id}/tou_range" + "/${range_id}")
class TOURangeURI(SplitURIBase):
    range_id: int


@ki_split_uri(uri_template=f"{ki_client.kb_id}/tou_range_max" + "/${range_id}")
class TOURangeMaxURI(SplitURIBase):
    range_id: int


@ki_split_uri(uri_template=f"{ki_client.kb_id}/tou_range_min" + "/${range_id}")
class TOURangeMinURI(SplitURIBase):
    range_id: int

# endregion
