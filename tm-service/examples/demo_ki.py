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
    from examples.fm_test.sample_client import set_bg_ke_client
    from examples.fm_test.sample_ki import sample_ki

    client=set_bg_ke_client([sample_ki])

    while True:
        print("start")
        try:
            print(f"tick: {client.state()}")
            from examples.fm_test.sample_ki import   request_market
            print(request_market())
            sleep(5)
        except Exception as ex:
            print("Some issue occurred: ")
            print(ex)
            sleep(5)
