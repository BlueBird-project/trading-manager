import json
import logging
from typing import List

from ke_client.utils import to_json
from rdflib import URIRef

from tm.modules.ke_interaction.interactions.dt_model import DigitalTwinInfo, DigitalTwinInfoACK
from tm.models.digital_twin import DigitalTwinDAO
from tm.models.job_dao import JobDAO


def process(dt_info_list: List[DigitalTwinInfo]) -> List[DigitalTwinInfoACK]:
    response: List[DigitalTwinInfoACK] = []
    # TODO: update all dt metadata ?
    for dt_info in dt_info_list:
        from tm.core.db.postgresql import dao_manager
        market = dao_manager.market_dao.get_market(market_uri=dt_info.market_uri)
        if market is None:
            logging.error(f"Unknown market: {dt_info.market_uri}")
        else:
            db_job = dao_manager.job_api.get(command_uri=dt_info.command_uri)
            if db_job is None:
                job = dao_manager.job_api.save(JobDAO(command_uri=dt_info.command_uri, job_name=dt_info.dt_uri,
                                                      ext=to_json({"market_uri": dt_info.market_uri})))
            else:
                job = db_job
            db_dt = dao_manager.dt_api.get(dt_uri=dt_info.dt_uri, market_id=market.market_id)
            if db_dt is None:
                dt = dao_manager.dt_api.save(
                    DigitalTwinDAO(dt_uri=dt_info.dt_uri, market_id=market.market_id, job_id=job.job_id))
            else:
                dt = db_dt
            response.append(DigitalTwinInfoACK(dt_uri=URIRef(dt.dt_uri), command_uri=URIRef(job.command_uri)))
    return response
