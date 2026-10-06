from typing import List

from ke_client import KIHolder
from ke_client.ki_model import KIPostResponse

from tm.modules.ke_interaction.interactions.capacity_market_model import TMNotification

ki = KIHolder()


@ki.react("flex-demand")
def _post_notification(notifications: List[TMNotification]):
    print(f"On demand {notifications}")
    return notifications
