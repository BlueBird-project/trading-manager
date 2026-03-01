import logging
from typing import Dict, Any

from ke_client.utils import time_utils 

__DAY_MS__ = 24 * 3600 * 1000


def check_ke(report: Dict) -> Dict:

    from tm.core import app_settings
    report["knowledge_engine_api_available"] = app_settings.use_ke_api
    if app_settings.use_ke_api:
        from tm.modules.ke_interaction.interactions import ki_client
        report["knowledge_engine_api_state"] = ki_client.state()
        report["knowledge_engine_api_registered"] = ki_client.is_registered
    return report


def ke_state() -> bool:
    from tm.core import app_settings
    if app_settings.use_ke_api:
        from tm.modules.ke_interaction.interactions import ki_client
        return  ki_client.state()
    else:
        return True


def check_scheduler(report: Dict) -> Dict:
    from tm.core import app_settings
    report["bg_scheduler_available"] = app_settings.use_scheduler
    if app_settings.use_ke_api:
        from tm.core.task_manager import service_job_scheduler
        from apscheduler.schedulers.base import STATE_RUNNING
        report["bg_scheduler_state"] = service_job_scheduler.state == STATE_RUNNING
        report["bg_scheduler_state_value"] = service_job_scheduler.state
    return report


def scheduler_state() -> bool:
    from tm.core import app_settings
    if app_settings.use_ke_api:
        from tm.core.task_manager import service_job_scheduler
        from apscheduler.schedulers.base import STATE_RUNNING
        return service_job_scheduler.state == STATE_RUNNING
    else:
        return True


def check_db(report: Dict) -> Dict:
    from tm.core.db.postgresql import dao_manager
    try:
        prev, current = dao_manager.app_settings_dao.set("app_healthcheck", time_utils.current_timestamp())
    except Exception as ex:
        prev = None
        current = None
        logging.error(f"db health check failed {ex}")

    report["db_state"] = current is not None
    report["db_healthcheck"] = current
    return report


def db_state() -> Dict:
    from tm.core.db.postgresql import dao_manager
    try:
        prev, current = dao_manager.app_settings_dao.set("app_healthcheck", time_utils.current_timestamp())

    except Exception as ex:
        prev = None
        current = None
        logging.error(f"db health check failed {ex}")
    return current is not None


def check_market(report: Dict) -> Dict:
    from tm.core.db.postgresql import dao_manager
    try:
        last_ts = dao_manager.day_ahead_dao.get_offer_last_ts()
    except Exception as ex:
        last_ts = None
        logging.error(f"Market check failed {ex}")

    report["db_market_last_ts"] = last_ts
    if last_ts is None:
        report["db_market_state"] = False
    else:
        report["db_market_state"] = (time_utils.current_timestamp() - last_ts) < (2 * __DAY_MS__)
    return report


def market_state() -> bool:
    from tm.core.db.postgresql import dao_manager
    try:
        last_ts = dao_manager.day_ahead_dao.get_offer_last_ts()
    except Exception as ex:
        last_ts = None
        logging.error(f"Market check failed {ex}")

    if last_ts is None:
        return False
    else:
        return (time_utils.current_timestamp() - last_ts) < (2 * __DAY_MS__)


def get_service_report() -> Dict[str, Any]:
    report = {"check_start": time_utils.current_timestamp()}

    report = check_ke(report=report)
    report = check_db(report=report)
    report = check_market(report=report)
    report = check_scheduler(report=report)
    report["check_end"] = time_utils.current_timestamp()
    return report


def get_service_state() -> bool:
    return ke_state() and db_state() and market_state() and scheduler_state()
