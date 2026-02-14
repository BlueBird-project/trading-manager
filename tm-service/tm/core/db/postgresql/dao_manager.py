from effi_onto_tools.db.app_settings_dao import AppSettingsDAO
from effi_onto_tools.db.postgresql.init_db import DBMeta

from tm.core.db.api.day_ahead import DayAheadAPI
from tm.core.db.api.dt_api import DTAPI
from tm.core.db.api.job_api import JobAPI
from tm.core.db.api.market import MarketAPI
from tm.core.db.api.market_offer_dao import MarketOfferAPI
from tm.core.db.postgresql.api_impl import day_ahead_impl, market_dao_impl, market_offer_dao_impl, job_api_impl, \
    dt_api_impl

day_ahead_dao: DayAheadAPI
market_dao: MarketAPI
offer_dao: MarketOfferAPI
app_settings_dao: AppSettingsDAO
job_api: JobAPI
dt_api: DTAPI


def init_postgresql(db_meta: DBMeta):
    from effi_onto_tools.db.postgresql import dbconnection
    dbconnection.connection_manager.init(db_meta=db_meta)

    global day_ahead_dao, app_settings_dao, market_dao, offer_dao, job_api, dt_api
    day_ahead_dao = day_ahead_impl.DayAheadAPIImpl(db_meta.db_table_prefix)
    market_dao = market_dao_impl.MarketAPIImpl(db_meta.db_table_prefix)
    offer_dao = market_offer_dao_impl.MarketOfferAPIImpl(db_meta.db_table_prefix)
    job_api = job_api_impl.JobAPIImpl(db_meta.db_table_prefix)
    dt_api = dt_api_impl.DTAPIImpl(db_meta.db_table_prefix)
    from effi_onto_tools.db.postgresql.app_settings_dao_impl import AppSettingsImpl
    app_settings_dao = AppSettingsImpl(db_meta.db_table_prefix, init_db=False)


# TODO: make in configurable
def init() -> DBMeta:
    from tm.core.db.postgresql import api_impl
    db_meta = DBMeta(
        db_version=api_impl.__DB_VERSION__,
        db_version_hashmap=api_impl.__DB_HASH__,
        db_schema_name=api_impl.__SCHEMA_NAME__, )
    init_postgresql(db_meta=db_meta)
    return db_meta
