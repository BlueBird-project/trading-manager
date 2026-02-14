import json
from typing import List

from tm.modules.ke_interaction.interactions.dt_model import DigitalTwinInfo, DigitalTwinInfoACK
from tm.models.digital_twin import DigitalTwinDAO
from tm.models.job_dao import JobDAO


def process(dt_info_list: List[DigitalTwinInfo]) -> List[DigitalTwinInfoACK]:
    response: List[DigitalTwinInfoACK] = []
    for dt_info in dt_info_list:
        from tm.core.db.postgresql import dao_manager
        market = dao_manager.market_dao.get_market(market_uri=dt_info.market_uri)
        job = dao_manager.job_api.save(JobDAO(command_uri=dt_info.command_uri, job_name=dt_info.dt_uri,
                                              ext=json.dumps({"market_uri": dt_info.market_uri})))
        dt = dao_manager.dt_api.save(
            DigitalTwinDAO(dt_uri=dt_info.dt_uri, market_id=market.market_id, job_id=job.job_id))
        response.append(DigitalTwinInfoACK(dt_uri=dt.dt_uri,command_uri=job.command_uri))
    return response
