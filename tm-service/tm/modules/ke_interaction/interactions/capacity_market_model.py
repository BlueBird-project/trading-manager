from ke_client import BindingsBase, ki_object
from rdflib import URIRef, Literal


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
