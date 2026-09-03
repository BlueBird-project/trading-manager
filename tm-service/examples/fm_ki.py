################################################
# load env files :
# ./resources/.env
# ./resources/env/.env.fm
# then run: ./examples/fm_ki.py -c ./examples/config.yaml
################################################
from typing import Optional

import tm
import logging
from time import sleep

from tm.utils import TimeSpan

################################################
# setup configurations
################################################
app_args = tm.init_args()
from tm.core import app_settings

# optional logger initializer
tm.set_logging()
logging.info(f"START FM")


# region helpers
def get_tm():
    """
    Find trading manager in the KE
    :return:
    """
    from examples.ki.fm_interactions import find_tm
    from examples.ki.fm_interactions import set_tm
    from examples.ki.fm_model import TMInfo
    _tm: Optional[TMInfo] = None
    tm_info_list = find_tm()
    if len(tm_info_list) < 1:
        print("Error: no tm")
        sleep(10)
    else:
        _tm = tm_info_list[0]
        set_tm(tm=_tm)
        print(f"TM : {_tm}")
    return _tm


# endregion

if __name__ == "__main__" and app_settings:
    # region set client and load knowledge interaction
    logging.info("INIT KI")
    ################################################
    # setup ke
    ################################################
    import ke_client

    ke_client.VERIFY_SERVER_CERT = False
    ke_client.ENV_FILE = tm.app_args.env_path
    from tm.modules.ke_interaction.interactions import setup_ke

    setup_ke()
    from examples.ki.smart_client import start_bg_ke_client
    from examples.ki.fm_interactions import fm_ki
    from examples.ki.tou_interactions import tou_ki

    ################################################
    # register knowledge interaction modules
    ################################################
    client = start_bg_ke_client([fm_ki, tou_ki])
    # endregion

    from examples.ki.fm_model import TMInfo

    #####################################
    #     Find trading manager
    #####################################
    tm_agent: Optional[TMInfo] = None

    while tm_agent is None:
        try:
            tm_agent = get_tm()
        except Exception as ex:
            print(f"can't get TM :{ex} ({client.state()} ")
            sleep(5)
    print(f"Observed TM : {tm_agent}")
    while True:
        try:
            from examples.ki.fm_interactions import evaluate_flexibility_ask, evaluate_flexibility
            from examples.ki.tou_interactions import get_tou_info, get_tou_price

            ################################################
            # get prices
            ################################################
            # get timeseries' details/metadata
            time_span=TimeSpan.next_day() #TimeSpan.last_day()
            res = get_tou_info(ts=time_span, tm_uri=tm_agent.tm_uri)

            for ts_info in res:
                ################################################
                # get data points for each timeseries uri
                ################################################
                print("get prices for: " + str(ts_info.tou_uri))
                prices = get_tou_price(tou_uris=[ts_info], tm_uri=tm_agent.tm_uri)
                if len(prices) > 0:
                    print(f"price response = {len(prices)}: {prices[0]}")
                else:
                    print(f"empty price response")
            sleep(15)
            ###########################
            print(f"Evaluate power plan")
            # get prices for power demand
            response = evaluate_flexibility_ask()
            # print(len(response))
            if len(response) > 0:
                print(f"{len(response)}: {response[0]}")
            else:
                print(f"empty response")
            # print(response)
            sleep(120)
        except Exception as ex:
            print(f"Some issue occurred: {ex} ({client.state()})")
            sleep(15)
