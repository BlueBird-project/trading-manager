from abc import abstractmethod
from typing import List

from tm.schemas.job_dao import JobDAO


class JobAPI:

    @abstractmethod
    def save(self, job: JobDAO) -> JobDAO:
        pass

    @abstractmethod
    def list(self, ) -> List[JobDAO]:
        pass
