from typing import Optional

from ke_client import BindingsBase, ki_object, OptionalLiteral
from rdflib import URIRef, Literal

from ke_client.utils import time_utils


@ki_object("flex-offer")
class KEFlexOffer(BindingsBase):
    market: URIRef
    flex_request: URIRef
    asset_manager: URIRef
    flex_profile: URIRef
    profile_price: Optional[URIRef]=None
    price: OptionalLiteral=None
    dp: URIRef
    ts: Literal
    dpr: URIRef
    value: Literal

    @property
    def ts_ms(self) -> int:
        return time_utils.xsd_to_ts(self.ts)


    # def rdf_parse(self) -> FlexOffer:
    #     return FlexOffer(
    #         flex_request_uri=self.flex_request.n3(), asset_manager_uri=self.asset_manager.n3(),
    #         flex_profile_uri=self.flex_profile.n3(), profile_price_uri=self.profile_price.n3(),
    #         flex_price=self.convert_value(self.price, float),
    #         ts=time_utils.xsd_to_ts(self.ts), flex_value=self.convert_value(self.value, float))



@ki_object("price-offer")
class KEFlexPriceOffer(BindingsBase):
    market: URIRef
    flex_request: URIRef
    flex_profile: URIRef
    asset_manager: URIRef
    profile_price: URIRef
    price: Literal
    flex_dp: URIRef
    flex_dpr: URIRef
    ts: Literal
    price_dp: URIRef
    price_dpr: URIRef
    flex_value: Literal
    price_value: Literal

    @property
    def ts_ms(self) -> int:
        return time_utils.xsd_to_ts(self.ts)
    #
    # def rdf_parse(self) -> FlexPriceOffer:
    #     return FlexPriceOffer(
    #         flex_request_uri=self.flex_request.n3(), asset_manager_uri=self.asset_manager.n3(),
    #         flex_profile_uri=self.flex_profile.n3(), profile_price_uri=self.profile_price.n3(),
    #         flex_price=self.convert_value(self.price, float),
    #         ts=time_utils.xsd_to_ts(self.ts), flex_value=self.convert_value(self.value, float),
    #         price_value=self.convert_value(self.price_value, float), )