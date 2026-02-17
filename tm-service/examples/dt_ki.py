import logging
from time import sleep

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

import tm

###
# setup configurations
###
# utils.ENV_FILE = "/env/.env.entsoe.demo"
app_args = tm.init_args()
from effi_onto_tools import utils
from tm.core import service_settings, app_settings

utils.ENV_FILE = tm.app_args.env_path
tm.set_logging()
logging.info(f"START {service_settings.name}")

if __name__ == "__main__" and app_settings:
    logging.info("INIT KI")
    # setup ke
    import ke_client

    ke_client.VERIFY_SERVER_CERT = False
    ke_client.ENV_FILE = tm.app_args.env_path
    from examples.ki.sample_client import set_bg_ke_client
    from examples.ki.sample_ki import sample_ki
    from examples.ki.dt_interactions import dt_ki

    client = set_bg_ke_client([sample_ki, dt_ki])

    from examples.ki.sample_ki import request_market
    from tm.modules.ke_interaction.interactions.dam_model import EnergyMarketBindings

    success = False
    market: EnergyMarketBindings = None
    while not success:
        try:
            from examples.ki.dt_interactions import set_market_uri

            print(f"tick: {client.state()}")
            markets = request_market()
            market = markets[0]
            set_market_uri(market_uri=market.market_uri)
            success = True
        except Exception as ex:
            print("Some issue occurred: ")
            print(ex)
            sleep(5)

    print(f"Observed market : {market}")
    ################################################

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
            print(len(ts_ack))
            if len(ts_ack) > 0:
                print(ts_ack[0])
            sleep(30)
        except Exception as ex:
            print("Some issue occurred: ")
            print(ex)
            sleep(35)
