import logging
import random
import threading
from datetime import timedelta, datetime

import pytz
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.schedulers.base import BaseScheduler
from pytz import utc

executors = {
    'default': ThreadPoolExecutor(5)
    # 'processpool': ProcessPoolExecutor(5)
}
job_defaults = {
    'coalesce': True,
    'max_instances': 1
}
service_job_scheduler: BaseScheduler


def init(bg=True):
    global service_job_scheduler
    if bg:
        from apscheduler.schedulers.background import BackgroundScheduler
        service_job_scheduler = BackgroundScheduler(executors=executors, job_defaults=job_defaults, timezone=utc)
    else:
        from apscheduler.schedulers.background import BlockingScheduler
        service_job_scheduler = BlockingScheduler(executors=executors, job_defaults=job_defaults, timezone=utc)
    return service_job_scheduler


def _restart_jobs(scheduler: BaseScheduler, on_start=False):
    import logging
    # hotfix for knowledge engine graph pattern inference (after service or KE server restart,
    # inferred graph patterns are removed
    def start_retry_job():
        logging.info(f"Restart KE client and job scheduler ({threading.current_thread().ident}) ")

        from tm.modules.ke_interaction.interactions.client import ki_client as ke_ki_client
        ke_ki_client.reconnect(timeout_s=1, try_extend_gp=True)
        reset_scheduler()
        # next_run = datetime.now(pytz.utc) + timedelta(seconds=15)

    if on_start:
        logging.info(f"SET reset_job ({threading.current_thread().ident}) ")
        next_run = datetime.now(pytz.utc) + timedelta(seconds=random.Random().randint(30, 240))
        scheduler.add_job(start_retry_job, trigger="date", next_run_time=next_run, id=f"init_service_reconnect_1",
                          replace_existing=True, coalesce=True)
        next_run = datetime.now(pytz.utc) + timedelta(seconds=random.Random().randint(1800, 7200))
        scheduler.add_job(start_retry_job, trigger="date", next_run_time=next_run, id=f"init_service_reconnect_2",
                          replace_existing=True, coalesce=True)

    @service_job_scheduler.scheduled_job(trigger='cron', id="ke_client_reconnect", day_of_week='*', hour='0',
                                         minute='20',
                                         month='*', year='*', day='*', max_instances=1, coalesce=True,
                                         jitter=9000)  # jitter=int(60 * 60 * 2.5)
    def start_retry_job():
        logging.info(f"Restart KE client ({threading.current_thread().ident}) ")
        from tm.modules.ke_interaction.interactions.client import ki_client as ke_ki_client
        ke_ki_client.reconnect(timeout_s=1, try_extend_gp=True)


def setup_scheduler_jobs(scheduler: BaseScheduler, on_start: bool):
    from tm.modules.ke_interaction import scheduled_jobs as ke_jobs

    ke_jobs.add_jobs(scheduler)
    _restart_jobs(scheduler=scheduler, on_start=on_start)
    if not scheduler.running:
        scheduler.start()

    jobs = scheduler.get_jobs()
    logging.info(f"Scheduled job: {",".join([f"{j.name}({j.id})" for j in jobs])}")


def setup_scheduler(on_start=False):
    from tm.core import app_settings
    global service_job_scheduler
    import logging
    logging.info(f"INIT task scheduler ({threading.current_thread().ident})")

    if app_settings.use_rest_api:
        service_job_scheduler = init(bg=True)
    else:
        print("Start sync scheduler")
        service_job_scheduler = init(bg=False)
    setup_scheduler_jobs(scheduler=service_job_scheduler, on_start=on_start)


def reset_scheduler():
    global service_job_scheduler
    import logging
    logging.info(f"Restart scheduler ({threading.current_thread().ident})")
    # from tm.core.db.postgresql import dao_manager
    # dao_manager.
    service_job_scheduler.remove_all_jobs()
    setup_scheduler_jobs(scheduler=service_job_scheduler, on_start=False)
