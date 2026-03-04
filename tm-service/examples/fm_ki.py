################################################
# load env files :
# ./resources/.env
# ./resources/env/.env.fm
################################################
from effi_onto_tools.utils import time_utils
from effi_onto_tools.utils.time_utils import tick, tock

import tm
import logging
from time import sleep
from tm.utils import TimeSpan

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
    from examples.ki.fm_interactions import fm_ki
    from examples.ki.tou_interactions import tou_ki

    ################################################
    # register knowledge interaction modules
    ################################################
    client = set_bg_ke_client([sample_ki, fm_ki, tou_ki])

    while True:
        try:
            from examples.ki.fm_interactions import evaluate_flexibility_ask
            from examples.ki.tou_interactions import get_tou_info, get_tou_price

            print(f"tick: {client.state()}")
            ################################################
            # get prices
            ################################################
            res = get_tou_info(ts=TimeSpan.last_day())
            print(res)
            for ts_info in res:
                ################################################
                # get timeseries for each uri
                ################################################
                prices = get_tou_price(tou_uris=[ts_info.tou_uri])
                print(prices)
            sleep(15)
            ###########################
            # send power plan and receive prices
            # print(f"Evaluate power plan")
            # tick()
            # this is low
            # response = evaluate_flexibility()
            # tock()
            # print(f"Evaluate power plan2")
            # print(len(response))
            tick()
            print(f"Evaluate power plan")
            response = evaluate_flexibility_ask()
            tock()
            print(len(response))
            # print(response)
            sleep(45)
        except Exception as ex:
            print("Some issue occurred: ")
            print(ex)
            sleep(15)
