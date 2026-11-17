from collections import defaultdict
from typing import List, Dict

from ke_client import SplitURIBase
from rdflib import URIRef, Literal

from tm.modules.ke_interaction.interactions.capacity_market_model import KEFlexOffer, KEFlexPriceOffer


def process_flex_offers(offers: List[KEFlexOffer]):
    from tm.core.db.postgresql import dao_manager
    grouped_offers: Dict[str, List[KEFlexOffer]] = defaultdict(list)
    prices_offers: List[KEFlexPriceOffer] = []
    for offer in offers:
        grouped_offers[offer.asset_manager].append(offer)
    for asset_uri, offers in grouped_offers.items():
        for offer in offers:
            flex_profile = URIRef(offer.flex_profile)
            price = get_price()
            price_offer = KEFlexPriceOffer(
                **vars(offer), flex_dp=offer.dp, flex_dpr=offer.dpr, flex_value=offer.value,
                price_dp=SplitURIBase.uri_append_ref(offer.flex_profile, "price_dp"),
                price_dpr=SplitURIBase.uri_append_ref(offer.flex_profile, "price_dpr"),
                price_value=Literal(price)
            )
            prices_offers.append(price_offer)
    post_prices_offers()
