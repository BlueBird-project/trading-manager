import logging
import threading
from datetime import datetime, timedelta
from time import sleep
from typing import List

from apscheduler.schedulers.base import BaseScheduler
from ke_client.utils import time_utils

from tm.utils import TimeSpan

_BASE_TIME_OFFSET_ = 60


def _dt_jobs(scheduler: BaseScheduler):
    @scheduler.scheduled_job(trigger='cron', id="dt_check", day_of_week='*', hour='12',
                             minute='15',
                             month='*', year='*', day='*', max_instances=1, coalesce=True)
    def scan_dt():
        from tm.modules.ke_interaction.interactions.dt_interactions import request_dt_info
        logging.info("Scan for Digital Twins")
        from tm.models.digital_twin import DigitalTwinDAO
        dt_ack: List[DigitalTwinDAO] = request_dt_info()
        logging.info(f"Scanned dts: {",".join([f"{dt.dt_uri}({dt.kb_id})" for dt in dt_ack])}")

    @scheduler.scheduled_job(trigger='cron', id="forecast_scan", day_of_week='*', hour='8',
                             minute='15',
                             month='*', year='*', day='*', max_instances=1, coalesce=True)
    def scan_forecast():
        from tm.modules.ke_interaction.interactions.dt_api import scan_forecast_info, scan_forecast

        logging.info("Scan for Forecast")
        # todo: set 'req' argument
        ts_info = scan_forecast_info()
        logging.info(f"Scanned dts: {",".join([ts.forecast_uri for ts_list in ts_info.values() for ts in ts_list])}")

        ts = scan_forecast(forecast_info=ts_info)
        logging.info(f"received timeseries , length: {len(ts)}")


    job = scheduler.get_job("dt_check")
    from tm import core
    job.modify(next_run_time=(datetime.now(tz=core.__TIME_ZONE__) + timedelta(seconds=_BASE_TIME_OFFSET_ + 120)))
    job = scheduler.get_job("forecast_scan")

    job.modify(next_run_time=(datetime.now(tz=core.__TIME_ZONE__) + timedelta(seconds=_BASE_TIME_OFFSET_ + 180)))


def _fm_jobs(scheduler: BaseScheduler):
    @scheduler.scheduled_job(trigger='cron', id="flexibility_scan", day_of_week='*', hour='8',
                             minute='15',
                             month='*', year='*', day='*', max_instances=1, coalesce=True)
    def scan_flexibility():
        from tm.modules.ke_interaction.interactions.fm_interactions import request_ts_info, request_data
        logging.info("Scan for flexibility")
        # todo: set 'req' argument
        cur_ts = time_utils.current_timestamp()
        ts_info = request_ts_info(ts=TimeSpan(ts_from=cur_ts, ts_to=cur_ts + 3600 * 1000 * 24))
        logging.info(f"Scanned fms: {",".join([ts.ts_uri for ts in ts_info])}")
        # TODO: request_data
        for uri in ts_info:
            ts = request_data(ts_uris=[uri.ts_uri])
            logging.info(f"received flexibility timeseries , length: {len(ts)} , for {uri.ts_uri}")
            #         TODO store timeseries
            print(ts)

    from tm import core
    job = scheduler.get_job("flexibility_scan")

    job.modify(next_run_time=(datetime.now(tz=core.__TIME_ZONE__) + timedelta(seconds=_BASE_TIME_OFFSET_ + 240)))


def _dam_jobs(scheduler: BaseScheduler):
    @scheduler.scheduled_job(trigger='cron', id="market_scan", day_of_week='*', hour='8',
                             minute='15',
                             month='*', year='*', day='*', max_instances=1, coalesce=True)
    def market_scan():
        logging.info("Scan for dam markets")
        # todo: set 'req' argument
        from tm.modules.ke_interaction.interactions.dam_interactions import get_all_markets
        get_all_markets(False)

    @scheduler.scheduled_job(trigger='cron', id="offer_scan", day_of_week='*', hour='8,19',
                             minute='25',
                             month='*', year='*', day='*', max_instances=1, coalesce=True)
    def scan_offer():
        logging.info("Scan for dam offer")
        # todo: set 'req' argument
        from tm.modules.ke_interaction.interactions.dam_interactions import get_current_market_offer_info, \
            get_market_offer
        offer_infos = get_current_market_offer_info()
        get_market_offer(offer_uris=[offer_info.offer_uri for offer_info in offer_infos])

    from tm import core
    job = scheduler.get_job("market_scan")
    job.modify(next_run_time=(datetime.now(tz=core.__TIME_ZONE__) + timedelta(seconds=_BASE_TIME_OFFSET_ + 30)))

    job = scheduler.get_job("offer_scan")
    job.modify(next_run_time=(datetime.now(tz=core.__TIME_ZONE__) + timedelta(seconds=_BASE_TIME_OFFSET_ + 90)))

    def _get_markets():
        from tm.modules.ke_interaction.interactions.dam_interactions import get_all_markets
        from tm.modules.ke_interaction.interactions.client import ki_client
        i = 0
        while i < 10 and (not ki_client.state()):
            # wait for client to register
            sleep(20)
            i += 1
        if not ki_client.state():
            logging.warning("Ki client hasn't  started on timee, dam offers are not scanned on start")
        else:
            logging.info(f"KI state: {ki_client.state()}")
            get_all_markets(True)
            scan_offer()

    t = threading.Thread(target=_get_markets)
    t.start()


def add_jobs(service_job_scheduler: BaseScheduler):
    logging.info("Add TM jobs")

    @service_job_scheduler.scheduled_job(trigger='cron', id="tge_check_offer_job", day_of_week='*', hour='13,18',
                                         minute='0',
                                         month='*', year='*', day='*', max_instances=1, coalesce=True)
    def post_offer():
        # TODO:
        print("post some offers")
        # ke_client.stop()

    _dt_jobs(scheduler=service_job_scheduler)
    _dam_jobs(scheduler=service_job_scheduler)
    _fm_jobs(scheduler=service_job_scheduler)
