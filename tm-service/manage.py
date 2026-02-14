import logging
import time
from time import sleep
from typing import List, Optional

import psycopg2
from effi_onto_tools.db import TimeSpan
from effi_onto_tools.utils import time_utils
from rdflib import URIRef

import tm

if __name__ == "__main__":
    ###
    # setup configurations
    ###
    tm.init_args()
    from effi_onto_tools import utils
    from tm.core import service_settings, app_settings

    utils.ENV_FILE = tm.app_args.env_path
    tm.set_logging()
    logging.info(f"START {service_settings.name}")
    ###
    # setup DB
    ###
    from tm.core.db import setup_db

    setup_db()

if __name__ == "__main__" and app_settings:
    if app_settings.use_ke_api:
        logging.info("INIT KI")
        # setup ke
        import ke_client

        ke_client.VERIFY_SERVER_CERT = False
        ke_client.ENV_FILE = tm.app_args.env_path
        from tm.modules.ke_interaction import setup_ke

        setup_ke()

        from tm.modules.ke_interaction import interactions as ki

        if app_settings.use_scheduler or app_settings.use_rest_api:
            from tm.modules.ke_interaction import set_bg_ke_client

            logging.info("Running BG KE client")
            set_bg_ke_client()
        else:
            from tm.modules.ke_interaction import set_sync_ke_client

            set_sync_ke_client()

        from tm.modules.ke_interaction.interactions import ki_client, dam_interactions, fm_interactions, dt_interactions

        # TEST:
        while not ki_client.is_registered:
            print("wait for registration")
            time.sleep(5)
        from tm.core.db.postgresql import dao_manager

        while True:
            try:
                print("LOOP")
                print(f"received markets: {len(dam_interactions.get_all_markets())}")
                markets = dao_manager.market_dao.list_market()
                market = [m for m in markets if m.market_location.upper() == "POLAND"][0]
                # market = [m for m in markets if m.market_location.upper() == "SPAIN"][0]
                current_offers = dam_interactions.get_market_offer_info_filtered(market_uri=market.market_uri, ti=None)
                # res = dam_interactions.get_market_offer_info(market_uri=market.market_uri)
                print(f"received current_offers info: {len(current_offers)}")

                filtered_offers = dam_interactions.get_market_offer_info_filtered(market_uri=market.market_uri,
                                                                                  ti=TimeSpan(ts_from=1769216275000,
                                                                                              ts_to=1769648275000))
                print(f"received offers info: {len(filtered_offers)}")
                filtered = dam_interactions.get_market_offer(offer_uris=[str(o.offer_uri) for o in filtered_offers])
                print(f"received offers: {filtered.keys()}")
                current = dam_interactions.get_market_offer(offer_uris=[str(o.offer_uri) for o in current_offers])
                print(f"received current offers: {current.keys()}")
                sleep(300)
            except Exception as ex:
                print(ex)
                sleep(10)
                pass


    # 1766219559000, 1767951179000
    # dt_info = None
    # while dt_info is None:
    #     try:
    #         time.sleep(4)
    #         print("request dt info")
    #         r: List[dt_interactions.DigitalTwinInfo] = dt_interactions.request_dt_info()
    #         print(r)
    #         dt_info = r[0]
    #     except Exception as ex:
    #         print(ex)
    # dt_uri = str(dt_info.dt_uri)
    # ts_data = None
    # while ts_data is None:
    #     try:
    #         time.sleep(4)
    #         print(f"request dt data {dt_uri}")
    #         ts_data = (
    #             dt_interactions.request_dt_data(dt_uri=dt_uri,
    #                                             ts_from=time_utils.current_timestamp(),
    #                                             ts_to=time_utils.current_timestamp() + 3600 * 48)
    #         )
    #         print(ts_data)
    #
    #     except Exception as ex:
    #         print(ex)
    # ts_data = None
    print("end")

# def request_dt_data(dt_uri: str, ts_from: int, ts_to: int) -> List[DTPnt]
#
# def request_dt_data_by_id(ts_uri_ref: URIRef)


# TODO: flexibility manager publish subscribe
# endtest
# from main.modules.tge.service import check_data
# check_data()

# if __name__ == "__main__" and app_settings:
#  TODO: scheduler
#     if app_settings.use_scheduler:
#         from main.core import task_manager
#
#         task_manager.setup_scheduler()

if __name__ == "__main__":
    if app_settings.use_rest_api:
        import uvicorn
        from tm.modules.tm_api.router import router as tm_router
        # from main.core.healthcheck.router import router as healthcheck_router
        # from main.modules.tge_api.admin_router import router as admin_router
        from fastapi import FastAPI

        app = FastAPI(docs_url="/api",
                      openapi_url="/openapi.json", redoc_url="/redoc")
        app.include_router(router=tm_router, prefix="/api")

        healthcheck_app = FastAPI(docs_url="/docs",
                                  openapi_url="/openapi.json", redoc_url="/redoc")

        # healthcheck_app.include_router(router=healthcheck_router, prefix="")
        # app.mount("/healthcheck", healthcheck_app)
        # admin_app = FastAPI(docs_url="/docs",
        #                     openapi_url="/openapi.json", redoc_url="/redoc")
        # admin_app.include_router(router=admin_router, prefix="")
        # app.mount("/admin", admin_app)
        uvicorn.run(app, port=service_settings.port, host=service_settings.host, root_path=service_settings.root_path)
