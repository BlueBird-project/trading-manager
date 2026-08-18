################################################
# load env files :
# ./resources/.env
# ./resources/env/.env.fm
################################################
import logging
from time import sleep
from typing import Optional

import tm

################################################
# setup configurations
################################################
app_args = tm.init_args()
from tm.core import   app_settings
# from tm.core.service import settings as service_settings
tm.set_logging()
logging.info(f"START DT Smart Clieant")


# region helpers
def get_tm():
    from examples.ki.dt_interactions import find_tm
    from examples.ki.dt_interactions import set_tm
    _tm: Optional[TMInfo] = None
    tm_info_list = find_tm()
    if len(tm_info_list) < 1:
        print("Error: no tm")
        sleep(10)
    else:
        _tm = tm_info_list[0]
        set_tm(tm=_tm)
    return _tm


# endregion

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
    from examples.ki.smart_client import set_bg_ke_client
    from examples.ki.dt_interactions import dt_ki

    ################################################
    # register knowledge interaction modules
    ################################################
    client = set_bg_ke_client([  dt_ki])
    from examples.ki.dt_model import TMInfo

    success = False
    #####################################
    # Find trading manager
    #####################################
    tm_info: Optional[TMInfo] = None

    while tm_info is None:
        try:
            tm_info = get_tm()
            print(f"tick: {client.state()}")
        except Exception as ex:
            print(f"can't get TM :{ex} ")
            sleep(5)

    print(f"Observed tm : {tm_info}")
    ################################################
    ################################################
    # #publish information about digital twin
    ################################################
    ################################################
    success = False
    while not success:
        try:
            from examples.ki.dt_interactions import post_dt_info

            print(f"tick: {client.state()}")
            # inform TM that there is DT in the network
            print(f"Post Digital Twin metadata ")
            dt_info_ack = post_dt_info()
            print(len(dt_info_ack))
            print(dt_info_ack)
            if len(dt_info_ack) > 0:
                success = True
            else:
                sleep(30)
        except Exception as ex:
            print(f"can't publish DT info :{ex} ")
            sleep(5)

    ################################################
    ################################################
    # #publish dummy forecast
    ################################################
    ################################################
    while True:
        try:

            from examples.ki.dt_interactions import post_dt_info, post_forecast, get_offer_uri, get_offer
            # get current offer
            offer_uris = get_offer_uri()
            if len(offer_uris) < 1:
                print("Error: no offer")
                continue
            else:
                print(f"offer info: {len(offer_uris)}")
                success = True
            current_offer = get_offer(offer_uris=[o.offer_uri for o in offer_uris])
            print(current_offer)
            print(f"len offer: {len(current_offer)}")
            current_offer_dict = {c.offer_uri: c for c in current_offer}

            print(f"tick: {client.state()}")
            print(f"Post ts")
            for k in current_offer_dict.keys():
                # publish dummy forecast for each offer
                ts_ack = post_forecast(offer_uri=k, offer=[o for o in current_offer if o.offer_uri == k])
                print("ack: " + str(len(ts_ack)))
                if len(ts_ack) > 0:
                    print("ack: " + str(len(ts_ack)) + " " + str(ts_ack[0]))
                else:
                    print("ack: " + str(len(ts_ack)))

            print(f"tock")
            sleep(240)
        except Exception as ex:
            print("Some issue occurred: ")
            print(ex)
            sleep(35)
