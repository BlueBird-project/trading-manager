from abc import abstractmethod
from typing import List, Optional

from tm.models.job_dao import JobDAO


class JobAPI:

    @abstractmethod
    def save(self, job: JobDAO) -> JobDAO:
        pass

    @abstractmethod
    def list(self, ) -> List[JobDAO]:
        pass
    @abstractmethod
    def get(self, command_uri: str) -> Optional[JobDAO]:
        pass
