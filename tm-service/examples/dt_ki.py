################################################
# load env files :
# ./resources/.env
# ./resources/env/.env.fm
################################################
from rdflib import URIRef

import tm
import logging
from time import sleep

################################################
# setup configurations
################################################
app_args = tm.init_args()
from tm.core import service_settings, app_settings

tm.set_logging()
logging.info(f"START {service_settings.name}")

if __name__ == "__main__" and app_settings:
    logging.info("INIT KI")
    ################################################
    # setup ke
    ################################################
    import ke_client

    ke_client.VERIFY_SERVER_CERT = False
    ke_client.ENV_FILE = tm.app_args.env_path
    from tm.modules.ke_interaction.interactions import setup_ke

    setup_ke()
    from examples.ki.sample_client import set_bg_ke_client
    from examples.ki.sample_ki import sample_ki
    from examples.ki.dt_interactions import dt_ki

    ################################################
    # register knowledge interaction modules
    ################################################
    client = set_bg_ke_client([sample_ki, dt_ki])
    from examples.ki.sample_ki import get_markets
    from tm.modules.ke_interaction.interactions.dam_model import EnergyMarketBindings

    success = False
    #####################################
    # Set market
    ##################################33
    market: EnergyMarketBindings = None

    while not success:
        try:
            from examples.ki.dt_interactions import set_market_uri

            print(f"tick: {client.state()}")
            # set market which will be forecasted
            markets = get_markets()
            market = markets[0]
            set_market_uri(market_uri=market.market_uri)
            success = True
        except Exception as ex:
            print("Some issue occurred: ")
            print(ex)
            sleep(5)

    print(f"Observed market : {market}")
    ################################################
    #############################
    # #publish information about digital twin
    ##############################
    success = False
    while not success:
        try:
            from examples.ki.dt_interactions import post_dt_info

            print(f"tick: {client.state()}")
            print(f"Post dt")
            dt_info_ack = post_dt_info()
            print(len(dt_info_ack))
            print(dt_info_ack)
            if len(dt_info_ack) > 0:
                success = True
            else:
                sleep(10)
        except Exception as ex:
            print("Some issue occurred: ")
            print(ex)
            sleep(5)

    while True:
        try:
            from examples.ki.dt_interactions import post_dt_info, post_forecast

            print(f"tick: {client.state()}")
            print(f"Post ts")
            ts_ack = post_forecast(market_uri=market.market_uri)
            # ts_ack = post_forecast(market_uri=URIRef("http://market.uri.com.pl"))
            print(len(ts_ack))
            if len(ts_ack) > 0:
                print(ts_ack[0])
            print(f"END Post ts")
            sleep(5)
        except Exception as ex:
            print("Some issue occurred: ")
            print(ex)
            sleep(35)
