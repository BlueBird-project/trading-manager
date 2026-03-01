import logging
from collections import defaultdict
from typing import List, Dict, Optional
from ke_client.utils import time_utils 
from rdflib import URIRef, Literal

from tm.models.market import EnergyMarket
from tm.models.market_offer import EnergyMarketOfferInfo, EnergyMarketOffer

from tm.modules.ke_interaction.interactions.dam_model import EnergyMarketBindings, MarketOfferInfoBindings, \
    MarketOfferBindings, UBEFLEX_MARKET_BASE, CountryUri, MarketType, EnergyMarketRequest

# TODO: make isp unit configurable (minutes, seconds etc)
__ISP_LEN_MS__ = 60 * 1000  # MINUTES as MILISECONDS


def save_markets(market_bindings: List[EnergyMarketBindings], subscribe: bool = False):
    from tm.core.db.postgresql import dao_manager
    for binding in market_bindings:
        market = EnergyMarket(market_location=binding.country_name, **vars(binding))

        db_market = dao_manager.market_api.get_market(binding.market_uri)
        if db_market is None:
            market.market_type = market.market_type.replace(UBEFLEX_MARKET_BASE, "")
            market.market_name = market.market_type + ":" + market.market_location
            market.subscribe = subscribe
            dao_manager.market_api.save_market(market)
        else:
            #         TODO:  update on duplicate ?
            logging.info(f"Market is registered: {binding.market_uri}")
            dao_manager.market_api.set_subscribe(db_market.market_id, subscribe)


def save_offer_info(offer_bindings: List[MarketOfferInfoBindings]):
    from tm.core.db.postgresql import dao_manager
    for binding in offer_bindings:
        import tm.core as core
        date_str = time_utils.datetime_to_str(time_utils.from_timestamp(binding.create_ts), tz=core.__TIME_ZONE__)
        market = dao_manager.market_api.get_market(binding.market_uri)
        if market is None:
            logging.warning(f"Market not registered: {binding.market_uri}")
        else:
            offer_info = EnergyMarketOfferInfo(**vars(binding), market_id=market.market_id, ts=binding.create_ts,
                                               isp_unit=binding.update_rate_min, date_str=date_str,
                                               isp_len=binding.isp_len)
            db_offer = dao_manager.offer_dao.get_offer_info(offer_uri=str(binding.offer_uri))
            if db_offer is not None:
                # logging.warning(f"Offer has been already added to the DB {db_offer.offer_uri}")
                # TODO: delete and insert ?
                # dao_manager.offer_dao.delete()
                # dao_manager.offer_dao.register_offer(market_offer=offer_info)
                pass
            else:
                dao_manager.offer_dao.register_offer(market_offer=offer_info)


def save_offer(offer_bindings: List[MarketOfferBindings], clear: bool = False):
    from tm.core.db.postgresql import dao_manager
    grouped_bindings: Dict[str, List[MarketOfferBindings]] = defaultdict(list)
    saved_bindings = defaultdict(list)
    for ob in offer_bindings:
        grouped_bindings[str(ob.offer_uri)].append(ob)

    unlimited_range = dao_manager.offer_dao.get_range(None, None)
    range_id = unlimited_range.range_id

    for offer_uri, market_offer in grouped_bindings.items():
        offer_info = dao_manager.offer_dao.get_offer_info(offer_uri=offer_uri)
        if offer_info is None:
            #     TODO:
            # raise Exception(f"Init offer info {offer_uri}")
            # TODO: add bg task to ask KE for offer details
            logging.error(f"Offer not registered {offer_uri}")
            # del grouped_bindings[offer_uri]
        else:
            if clear:
                # print(f"Updating with new offer {offer_uri}")
                logging.info(f"Removing old offer for {offer_uri}")
                dao_manager.offer_dao.clear_market_offer(offer_id=offer_info.offer_id)
            isp_len_ms = offer_info.isp_unit * __ISP_LEN_MS__
            ts_start = offer_info.ts
            market_offer_items: list = [None] * len(grouped_bindings[offer_info.offer_uri])
            for i, binding in enumerate(market_offer):
                isp_start = (binding.ts_ms - ts_start) / isp_len_ms
                mo = EnergyMarketOffer(offer_id=offer_info.offer_id, ts=offer_info.ts,
                                       isp_start=isp_start, range_id=range_id, cost_mwh=binding.get_value(),
                                       isp_len=binding.isp_len(offer_info.isp_unit))

                market_offer_items[i] = mo
            saved_bindings[offer_info.offer_uri]=dao_manager.offer_dao.add_offer(market_offer_items=market_offer_items)
    return saved_bindings


def get_all_markets() -> List[EnergyMarket]:
    from tm.core.db.postgresql import dao_manager
    return dao_manager.market_api.list_subscribed_market()


def unsubscribe_markets() -> List[EnergyMarket]:
    from tm.core.db.postgresql import dao_manager
    for m in dao_manager.market_api.list_market():
        dao_manager.market_api.set_subscribe(market_id=m.market_id, subscribe=False)


def list_markets(market_query: Optional[EnergyMarketRequest]):
    from tm.core.db.postgresql import dao_manager
    if market_query is not None:
        # todo: filter
        market_query.market_type
        market_query.country_name
    markets = [EnergyMarketBindings(market_uri=URIRef(m.market_uri), country_name=Literal(m.market_location),
                                    country_uri=CountryUri(country=m.market_location).uri_ref,
                                    market_type=MarketType.value(m.market_type).uri_ref) for m in
               dao_manager.market_api.list_subscribed_market()]
    return markets
