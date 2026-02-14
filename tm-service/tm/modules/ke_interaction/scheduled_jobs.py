import logging

from apscheduler.schedulers.base import BaseScheduler


def add_jobs(service_job_scheduler: BaseScheduler):
    logging.info("Add TM jobs")

    @service_job_scheduler.scheduled_job(trigger='cron', id="tge_check_offer_job", day_of_week='*', hour='13,18',
                                         minute='0',
                                         month='*', year='*', day='*', max_instances=1, coalesce=True)
    def post_offer():
        # TODO:
        print("post some offers")
        # ke_client.stop()
