from typing import List

from ke_client import KIHolder
from ke_client.ki_model import KIPostResponse

from tm.modules.ke_interaction.interactions.capacity_market_model import KECapacityNotification

ki = KIHolder()


@ki.react("flex-demand")
def _on_notification(ki_id: str, bindings: List[KECapacityNotification]):
    print(f"On demand {bindings}")
    from tm.core.db.postgresql import dao_manager
    for b in bindings:
        from tm.models.capacity_market import CapacityNotification
        notification = CapacityNotification(asset_manager_uri=b.asset_manager, flex_instruction_uri=b.flex_instruction,
                                            flex_offer_uri=b.flex_offer, flex_profile_uri=b.flex_profile,
                                            power_limit_uri=b.power_limit, ts=b.ts_ms,
                                            max_consumption_uri=b.max_consumption,
                                            max_consumption=b.convert_value(b.max_consumption_value, float)
                                            )
        dao_manager.capacity_notification_api.save(notification=notification)
    return []
