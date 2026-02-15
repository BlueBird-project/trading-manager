from typing import List

from ke_client import KIHolder
from ke_client.ki_model import KIAskResponse

from tm.modules.ke_interaction.interactions.dam_model import EnergyMarketRequest, EnergyMarketBindings

sample_ki = KIHolder()


@sample_ki.ask("market")
def _request_market(query: List[EnergyMarketRequest]):
    return query


def request_market()->List[EnergyMarketBindings]:
    resp: KIAskResponse = _request_market(query=[])
    return [EnergyMarketBindings(**b) for b in resp.bindingSet]