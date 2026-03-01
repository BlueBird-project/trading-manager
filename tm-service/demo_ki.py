import logging
import os
import time
from typing import List

from ke_client.utils import time_utils

import tm
from tm.models.market_offer import EnergyMarketOffer
from tm.utils import TimeSpan

# os.environ['APP_USE_REST_API'] = "True"
# os.environ['APP_USE_KE_API'] = "True"
# os.environ['KE_KNOWLEDGE_BASE_ID'] = "http://demo.tm.bluebird.com"
# os.environ['SERVICE_NAME'] = "TM-DEMO"
# os.environ['DB_INIT'] = "True"
# os.environ['DB_TABLE_PREFIX'] = "demo_tm_"
# os.environ['DB_PASS'] = "postgres"
# os.environ['DB_HOST'] = "tm-db"
# os.environ['DB_HOST'] = "localhost"
# os.environ['KE_REST_ENDPOINT'] = 'http://localhost:8280/rest/'
# os.environ.setdefault("SERVICE_LOG_DIR", "d:/tmp/logs/")

###
# setup configurations
###
# utils.ENV_FILE = "/env/.env.entsoe.demo"
demo_args = tm.init_demo_args()
from effi_onto_tools import utils
from tm.core import service_settings, app_settings

utils.ENV_FILE = tm.app_args.env_path
tm.set_logging()
logging.info(f"START {service_settings.name}")
from tm.core.db import setup_db

setup_db()
if __name__ == "__main__" and app_settings:
    logging.info("INIT KI")
    # setup ke
    import ke_client

    ke_client.VERIFY_SERVER_CERT = False
    ke_client.ENV_FILE = tm.app_args.env_path
    from examples import setup_ke

    setup_ke()

    if app_settings.use_scheduler or app_settings.use_rest_api:
        from tm.modules.ke_interaction import set_bg_ke_client

        logging.info("Running BG KE client")
        set_bg_ke_client()
    else:
        from tm.modules.ke_interaction import set_sync_ke_client

        set_sync_ke_client()

    from tm.modules.ke_interaction.interactions import   dam_interactions
    from tm.modules.ke_interaction.interactions.dam_model import EnergyMarketBindings
    from tm.modules.ke_interaction.interactions.client import ki_client

    # TEST:
    while not ki_client.is_registered:
        print("wait for registration")
        time.sleep(5)

    # while True:
    try:
        from ke_client import ki_conf

        print(f"KI for pattern: {ki_conf.graph_patterns["market"].pattern_value}")
        markets: List[EnergyMarketBindings] = dam_interactions.get_all_markets()
        print(f"Available markets: {[m.country_name.n3() + ":" + m.market_type.n3() for m in markets]}")
        try:
            country_markets = [m for m in markets if m.country_name.upper() == demo_args.country.upper()]
            if len(country_markets) > 1:
                try:
                    filter_by_type_markets = [m for m in country_markets if
                                              demo_args.type.lower() in m.market_type.n3().lower()]
                    market = filter_by_type_markets[0]
                except Exception as ex:
                    print(f"Issue with market filter {ex}")
                    market = country_markets[0]

            else:
                market = country_markets[0]
        except IndexError:
            raise Exception(f"Invalid country: `{demo_args.country}`")
        print(f"current market uri :{market.market_uri}: {market.market_type}")
        current_offers = dam_interactions.get_market_offer_info_filtered(market_uri=market.market_uri, ti=None)
        print(f"received current_offers info: {len(current_offers)}")
        for offer in current_offers:
            print(f"received current_offers info: {time_utils.from_timestamp(offer.create_ts)}")
        ts = time_utils.parse_date(demo_args.date)
        offers = dam_interactions.get_market_offer_info_filtered(market_uri=market.market_uri,
                                                                 ti=TimeSpan(ts_from=ts, ts_to=ts + 20 * 3600000))
        print(f"received offers for {demo_args.date} info: {len(offers)}")
        for offer in offers:
            print(f"offer for  {time_utils.from_timestamp(offer.create_ts)}:")
            offer_dict = dam_interactions.get_market_offer(offer_uris=[offer.offer_uri])
            mo: EnergyMarketOffer
            for market_offers in offer_dict[str(offer.offer_uri)]:
                market_offers = sorted(market_offers, key=lambda item: item["isp_start"])
                for mo in market_offers:
                    print(f"\t{mo["isp_start"]}-{mo["isp_start"] + mo["isp_len"]}= {mo["cost_mwh"]} EUR")
        # # res = dam_interactions.get_market_offer_info(market_uri=market.market_uri)
        # print(f"received current_offers info: {len(current_offers)}")
        #
        # filtered_offers = dam_interactions.get_market_offer_info_filtered(market_uri=market.market_uri,
        #                                                                   ti=TimeSpan(ts_from=1769216275000,
        #                                                                               ts_to=1769648275000))
        # print(f"received offers info: {len(filtered_offers)}")
        # filtered = dam_interactions.get_market_offer(offer_uris=[str(o.offer_uri) for o in filtered_offers])
        # print(f"received offers: {filtered.keys()}")
        # current = dam_interactions.get_market_offer(offer_uris=[str(o.offer_uri) for o in current_offers])
        # print(f"received current offers: {current.keys()}")
        # sleep(60)
        print("END")
        import sys

        os._exit(1)
        # sys.exit()
    except Exception as ex:
        print("Some issue occurred: ")
        print(ex)
        # sleep(10)
        pass
