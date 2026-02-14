from abc import abstractmethod
from typing import List

from tm.models.digital_twin import DigitalTwinDAO


class DTAPI:

    @abstractmethod
    def save(self, job: DigitalTwinDAO) -> DigitalTwinDAO:
        pass

    @abstractmethod
    def list(self, ) -> List[DigitalTwinDAO]:
        pass
