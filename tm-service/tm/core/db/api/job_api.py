from abc import abstractmethod
from typing import List, Optional

from tm.models.job_dao import JobDAO


class JobAPI:
    # command/job is connected with market
    @abstractmethod
    def save(self, job: JobDAO) -> JobDAO:
        pass

    @abstractmethod
    def update(self, job: JobDAO) -> JobDAO:
        pass

    @abstractmethod
    def list(self, ) -> List[JobDAO]:
        pass

    @abstractmethod
    def get(self, job_id: int) -> Optional[JobDAO]:
        pass

    @abstractmethod
    def get_by_command(self, command_uri: str) -> Optional[JobDAO]:
        pass

    @abstractmethod
    def get_by_market(self, market_id: int) -> Optional[JobDAO]:
        pass
