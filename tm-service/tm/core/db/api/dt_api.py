from abc import abstractmethod
from typing import List, Optional

from tm.models.digital_twin import DigitalTwinDAO


class DTAPI:

    @abstractmethod
    def save(self, job: DigitalTwinDAO) -> DigitalTwinDAO:
        pass

    @abstractmethod
    def list(self, ) -> List[DigitalTwinDAO]:
        pass

    @abstractmethod
    def get(self, dt_uri: str, market_id: Optional[int]) -> Optional[DigitalTwinDAO]:
        pass
