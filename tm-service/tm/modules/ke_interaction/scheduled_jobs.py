import logging
from datetime import datetime, timedelta

from apscheduler.schedulers.base import BaseScheduler
from effi_onto_tools.db import TimeSpan
from effi_onto_tools.utils import time_utils


def _dt_jobs(scheduler: BaseScheduler):
    @scheduler.scheduled_job(trigger='cron', id="dt_check", day_of_week='*', hour='12',
                             minute='15',
                             month='*', year='*', day='*', max_instances=1, coalesce=True)
    def scan_dt():
        from tm.modules.ke_interaction.interactions.dt_interactions import request_dt_info
        logging.info("Scan for Digital Twins")
        dt_ack = request_dt_info()
        logging.info(f"Scanned dts: {",".join([dt.dt_uri for dt in dt_ack])}")

    @scheduler.scheduled_job(trigger='cron', id="forecast_scan", day_of_week='*', hour='8',
                             minute='15',
                             month='*', year='*', day='*', max_instances=1, coalesce=True)
    def scan_forecast():
        from tm.modules.ke_interaction.interactions.dt_interactions import request_dt_ts_info, request_dt_data_by_id
        logging.info("Scan for Forecast")
        # todo: set 'req' argument
        ts_info = request_dt_ts_info(req=[])
        logging.info(f"Scanned dts: {",".join([ts.ts_uri for ts in ts_info])}")
        for uri in ts_info:
            ts = request_dt_data_by_id(ts_uri_ref=uri.ts_uri)
            logging.info(f"received timeseries , length: {len(ts)}")
            #         TODO store timeseries
            print(ts)

    job = scheduler.get_job("dt_check")
    from tm import core
    job.modify(next_run_time=(datetime.now(tz=core.__TIME_ZONE__) + timedelta(seconds=120)))
    job = scheduler.get_job("forecast_scan")

    job.modify(next_run_time=(datetime.now(tz=core.__TIME_ZONE__) + timedelta(seconds=180)))


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

    job.modify(next_run_time=(datetime.now(tz=core.__TIME_ZONE__) + timedelta(seconds=5)))


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
    _fm_jobs(scheduler=service_job_scheduler)
