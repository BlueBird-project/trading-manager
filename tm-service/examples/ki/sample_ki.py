from typing import List

from ke_client import KIHolder, TargetedBindings
from ke_client.ki_model import KIAskResponse

from tm.modules.ke_interaction.interactions.dam_model import EnergyMarketRequest, EnergyMarketBindings

sample_ki = KIHolder()

TM_KB_ID = ["http://demo.tm.bluebird.com", "http://tm.bluebird.com"]


@sample_ki.ask("market")
def _request_market(query: List[EnergyMarketRequest]):
    return TargetedBindings(
        bindings=query,
        knowledge_bases=TM_KB_ID)


def request_market() -> List[EnergyMarketBindings]:
    resp: KIAskResponse = _request_market(query=[])
    return [EnergyMarketBindings(**b) for b in resp.binding_set]
