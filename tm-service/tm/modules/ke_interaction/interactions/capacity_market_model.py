from ke_client import BindingsBase, ki_object
from rdflib import URIRef, Literal

from ke_client.utils import time_utils

@ki_object("flex-demand")
class KECapacityNotification(BindingsBase):
    asset_manager: URIRef
    flex_instruction: URIRef
    flex_offer: URIRef
    flex_profile: URIRef
    power_limit: URIRef
    ts: Literal
    max_consumption: URIRef
    max_consumption_value: Literal

    @property
    def ts_ms(self):
        return time_utils.xsd_to_ts(self.ts)
