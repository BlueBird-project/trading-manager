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

        # setup_ke()

        from tm.modules.ke_interaction import interactions as ki

        if app_settings.use_scheduler or app_settings.use_rest_api:
            from tm.modules.ke_interaction import set_bg_ke_client

            logging.info("Running BG KE client")
            set_bg_ke_client()
        else:
            from tm.modules.ke_interaction import set_sync_ke_client

            set_sync_ke_client()

if __name__ == "__main__":
    if app_settings.use_scheduler:
        from tm.core import task_manager

        task_manager.setup_scheduler()

    from tm.modules.ke_interaction.interactions.dam_interactions import get_all_markets
    from tm.modules.ke_interaction.interactions.fm_interactions import request_ts_info

    cur_ts = time_utils.current_timestamp()
    while True:
        print("ticktick1")
        ts_info = request_ts_info(ts=TimeSpan(ts_from=cur_ts, ts_to=cur_ts + 3600 * 1000 * 24))
        print("ticktick")
        sleep(50)
    # markets=get_all_markets()
    # print("#########################")
    # print("markets:")
    # print("#########################")
    # print(markets)
    # print("#########################")
    if app_settings.use_rest_api:
        import uvicorn
        from tm.modules.tm_api.router import router as tm_router
        from tm.core.healthcheck.router import router as healthcheck_router
        # from main.modules.tge_api.admin_router import router as admin_router
        from fastapi import FastAPI

        app = FastAPI(docs_url="/api",
                      openapi_url="/openapi.json", redoc_url="/redoc")
        app.include_router(router=tm_router, prefix="/api")

        healthcheck_app = FastAPI(docs_url="/docs",
                                  openapi_url="/openapi.json", redoc_url="/redoc")

        healthcheck_app.include_router(router=healthcheck_router, prefix="")
        app.mount("/healthcheck", healthcheck_app)
        # admin_app = FastAPI(docs_url="/docs",
        #                     openapi_url="/openapi.json", redoc_url="/redoc")
        # admin_app.include_router(router=admin_router, prefix="")
        # app.mount("/admin", admin_app)
        uvicorn.run(app, port=service_settings.port, host=service_settings.host, root_path=service_settings.root_path)
