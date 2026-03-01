import logging
from time import sleep

from effi_onto_tools.db import TimeSpan

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
    from tm.modules.ke_interaction.interactions import setup_ke

    setup_ke()
    from examples.ki.sample_client import set_bg_ke_client
    from examples.ki.sample_ki import sample_ki
    from examples.ki.fm_interactions import fm_ki
    from examples.ki.tou_interactions import tou_ki

    client = set_bg_ke_client([sample_ki, fm_ki, tou_ki])

    while True:
        try:
            from examples.ki.fm_interactions import evaluate_flexibility
            from examples.ki.tou_interactions import get_tou, get_tou_price

            print(f"tick: {client.state()}")
            ###########################
            res = get_tou(ts=TimeSpan.last_day())
            print(res)
            for ts_info in res:
                print("get prices")
                prices = get_tou_price(tou_uris=[ts_info.tou_uri])
                print(prices)
            sleep(15)
            ###########################
            print(f"Evaluate power plan")
            response = evaluate_flexibility()
            print(f"End Evaluate power plan")
            print(len(response))
            print(response)
            sleep(45)
        except Exception as ex:
            print("Some issue occurred: ")
            print(ex)
            sleep(15)
