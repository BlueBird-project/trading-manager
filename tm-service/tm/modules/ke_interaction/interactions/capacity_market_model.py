from ke_client import BindingsBase, ki_object
from rdflib import URIRef, Literal


@ki_object("flex-demand")
class TMNotification(BindingsBase):
    flex_request: URIRef
    flex_offer: URIRef
    flex_profile: URIRef
    flex_participant: URIRef
    power_limit: URIRef
    ts: Literal
    max_consumption: URIRef
    max_consumption_value: Literal
