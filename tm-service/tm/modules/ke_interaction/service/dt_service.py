import logging
from typing import List

from ke_client.utils import to_json

from tm.models.digital_twin import DigitalTwinDAO, DTForecastInfoDAO
from tm.models.job_dao import JobDAO
from tm.modules.ke_interaction.interactions.dt_model import DigitalTwinInfo, DTTSInfo


def process(dt_info_list: List[DigitalTwinInfo]):
    # response: List[] = []
    # TODO: update all dt metadata ?
    for dt_info in dt_info_list:
        from tm.core.db.postgresql import dao_manager
        market = dao_manager.market_api.get_market(market_uri=dt_info.market_uri)
        if market is None:
            logging.error(f"Unknown market: {dt_info.market_uri}")
        else:
            db_job = dao_manager.job_api.get(command_uri=dt_info.command_uri)
            if db_job is None:
                job = dao_manager.job_api.save(JobDAO(command_uri=dt_info.command_uri, market_id=market.market_id,
                                                      job_name=dt_info.dt_uri,
                                                      ext=to_json({"market_uri": dt_info.market_uri})))
            else:
                job = db_job
            db_dt = dao_manager.dt_api.get(dt_uri=dt_info.dt_uri)
            if db_dt is None:
                dt = dao_manager.dt_api.save(
                    DigitalTwinDAO(dt_uri=dt_info.dt_uri, job_id=job.job_id))
            else:
                # TODO: dt_api.update(....)
                dt = db_dt
            # response.append(DigitalTwinInfoACK(dt_uri=URIRef(dt.dt_uri), command_uri=URIRef(job.command_uri)))
    # return response


def process_forecast(bindings: List[DTTSInfo]):
    from tm.core.db.postgresql import dao_manager
    added_ts = []
    for b in bindings:
        job = dao_manager.job_api.get(command_uri=b.command_uri)
        if job is None:
            logging.error(f"Job(Command) not found: {b.command_uri}")
        else:
            db_ts = dao_manager.forecast_api.get_by_uri(forecast_uri=b.ts_uri)
            if db_ts is not None:
                logging.info(f"Forecast {b.ts_uri} have already been added")
                #     TODO: update current instance in Db?
                # added_ts.append(new_ts)
            else:
                new_ts = DTForecastInfoDAO(forecast_uri=b.ts_uri, job_id=job.job_id, ts=b.create_ts,
                                           isp_unit=b.update_rate_min, sequence=b.sequence,
                                           isp_len=b.isp_len)
                logging.info(f"Forecast {b.ts_uri}:{new_ts.forecast_id} have been added")
                added_ts.append(new_ts)
    return added_ts
