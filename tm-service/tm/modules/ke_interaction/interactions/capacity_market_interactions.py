from typing import List

from ke_client import KIHolder
from ke_client.ki_model import KIPostResponse

from tm.modules.ke_interaction.interactions.capacity_market_model import  KECapacityNotification

ki = KIHolder()


@ki.react("flex-demand")
def _on_notification(ki_id:str,bindings: List[KECapacityNotification]):
    print(f"On demand {bindings}")
    return []
