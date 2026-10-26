from abc import abstractmethod
from typing import List, Optional

from tm.models.capacity_market import CapacityNotification
from tm.models.digital_twin import DigitalTwinDAO


class NotificationAPI:
    @abstractmethod
    def save(self, notification: CapacityNotification) -> CapacityNotification:
        pass

    @abstractmethod
    def list(self, ) -> List[CapacityNotification]:
        pass

    @abstractmethod
    def get_by_uri(self, asset_manager_uri: str) -> Optional[CapacityNotification]:
        pass

    @abstractmethod
    def get_recent(self, ) -> List[CapacityNotification]:
        pass
