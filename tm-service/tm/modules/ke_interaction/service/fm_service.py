from typing import List, Any

from ke_client.utils import time_utils 
from ke_client import rdf_nil
from rdflib import URIRef

from tm.core.db.postgresql import dao_manager
from tm.modules.ke_interaction.interactions.fm_model import FMTSSplitURI, FMEvaluateQuery, DPSplitURI, \
    FMEvaluateResponse
from tm.modules.ke_interaction.interactions import tou_model


# def evaluate(q: List[FMEvaluateQuery]):
def evaluate(query: List[FMEvaluateQuery]) -> List[FMEvaluateResponse]:
    response = []
    for q in query:
        ts_uri: FMTSSplitURI = FMTSSplitURI.parse(q.ts_uri)
        dp_uri = DPSplitURI.parse(q.dp)
        ts = time_utils.xsd_to_ts(q.ts)
        value = q.value
        # //TODO: evaluate power cost

        range_id = dao_manager.offer_dao.get_range(None, None).range_id
        # tou_uri = tou_model.TOUSplitURI(range_id=range_id, period_minutes=ts_uri.period_minutes, ts=ts)
        tou_price = FMEvaluateResponse(cost_dp=dp_uri.uri_ref, cost_dpr=URIRef(dp_uri.uri + "/dpr"), cost=rdf_nil)

        response.append(tou_price)

    return response
