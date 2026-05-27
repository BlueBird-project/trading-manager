from abc import abstractmethod
from typing import List, Optional

from tm.models.digital_twin import DigitalTwinDAO


class DTAPI:
    # TODO currently DT can have only one command/job
    @abstractmethod
    def save(self, job: DigitalTwinDAO) -> DigitalTwinDAO:
        pass

    @abstractmethod
    def update(self, job: DigitalTwinDAO) -> DigitalTwinDAO:
        pass

    @abstractmethod
    def list(self, ) -> List[DigitalTwinDAO]:
        pass

    @abstractmethod
    def get(self, dt_id: int) -> Optional[DigitalTwinDAO]:
        pass

    @abstractmethod
    def get_by_uri(self, dt_uri: str) -> Optional[DigitalTwinDAO]:
        pass
