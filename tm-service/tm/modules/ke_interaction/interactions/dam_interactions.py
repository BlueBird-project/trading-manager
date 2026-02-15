import logging
from typing import List, Optional

from effi_onto_tools.db import TimeSpan
from ke_client import KIHolder, TargetedBindings
from ke_client.ki_model import KIAskResponse
from rdflib import URIRef, Literal

from tm.modules.ke_interaction.interactions.dam_model import EnergyMarketBindings, MarketOfferInfoBindings, \
    MarketOfferBindings, EnergyMarketRequest, \
    MarketOfferRequest, MarketOfferInfoFilteredRequest, MarketOfferInfoFilteredBindings
from tm.modules.ke_interaction.service import dam_service

ki = KIHolder()


# region market ki
@ki.ask("market")
def _get_all_markets():
    from tm.core import app_settings
    return TargetedBindings(
        bindings=[EnergyMarketRequest(country_name=Literal(c)) for c in app_settings.country_list],
        # knowledge_bases=['https://demo.entsoe.bluebird.com/ke'])
        knowledge_bases=[])


@ki.answer("market")
def on_market_request(ki_id: str, bindings: List[EnergyMarketRequest]):
    if len(bindings) > 0:
        return dam_service.list_markets(market_query=bindings[0])
    return dam_service.list_markets(market_query=None)


@ki.react("market")
def on_market_information(ki_id: str, bindings: List[EnergyMarketBindings]):
    from tm.core import app_settings
    subscribed_countries = [b for b in bindings if b.country_name.upper() in app_settings.country_list_upper]
    dam_service.save_markets(market_bindings=subscribed_countries)
    return []


def get_all_markets() -> List[EnergyMarketBindings]:
    bindings: KIAskResponse = _get_all_markets()
    market_bindings = [EnergyMarketBindings(**b) for b in bindings.bindingSet]
    dam_service.save_markets(market_bindings=market_bindings)
    return market_bindings


# endregion

# region offer details (timeseries metadata)
@ki.react("market-offer-info")
def on_market_offer_info(ki_id: str, bindings: List[MarketOfferInfoBindings]):
    dam_service.save_offer_info(offer_bindings=bindings)
    return []


@ki.ask("market-offer-info-filtered")
def _get_market_offer_info_filtered(market_uri: URIRef, ti: Optional[TimeSpan]):
    return [MarketOfferInfoFilteredRequest(ti=ti, market_uri=market_uri)]


def get_market_offer_info_filtered(market_uri: str, ti: Optional[TimeSpan]) -> List[MarketOfferInfoBindings]:
    bindings: KIAskResponse = _get_market_offer_info_filtered(market_uri=URIRef(market_uri), ti=ti)
    if ti is not None:
        market_offer_bindings = [MarketOfferInfoFilteredBindings(**b) for b in bindings.bindingSet]
    else:
        market_offer_bindings = [MarketOfferInfoBindings(**b) for b in bindings.bindingSet]
    logging.info(f"Received {len(market_offer_bindings)} offers.")
    dam_service.save_offer_info(offer_bindings=market_offer_bindings)
    return market_offer_bindings


def get_current_market_offer_info(market_uri: str) -> List[MarketOfferInfoBindings]:
    return get_market_offer_info_filtered(market_uri=URIRef(market_uri), ti=None)


# endregion

# region market offer
@ki.ask("market-offer")
def _get_market_offer(offer_uris: List[URIRef]) -> List[MarketOfferRequest]:
    return [MarketOfferRequest(offer_uri=offer_uri) for offer_uri in offer_uris]


@ki.react("market-offer")
def on_market_offer(ki_id, bindings: List[MarketOfferBindings]):
    dam_service.save_offer(offer_bindings=bindings, clear=True)


def get_market_offer(offer_uris: List[str], clear_prev: bool = True):
    if len(offer_uris) == 0:
        return {}
    bindings: KIAskResponse = _get_market_offer(offer_uris=[URIRef(offer_uri) for offer_uri in offer_uris])

    offer_bindings = [MarketOfferBindings(**b) for b in bindings.bindingSet]
    return dam_service.save_offer(offer_bindings=offer_bindings, clear=clear_prev)
# endregion
