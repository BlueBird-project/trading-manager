from typing import List, Optional

from effi_onto_tools.db.postgresql.connection_wrapper import ConnectionWrapper

from tm.core.db.api.job_api import JobAPI
from tm.core.db.postgresql.api_impl import QueryObject
from tm.models.job_dao import JobDAO


# class JobDAO

class JobAPIQueries(QueryObject):
    __PROJECTION__ = """ "job_id", "market_id", "command_uri" ,"job_name" ,"job_description" ,"update_ts" ,"ext" """
    __TABLE_NAME__ = "service_jobs"
    LIST = """SELECT ${projection}  FROM "${table_prefix}${table_name}" """
    SELECT_BY_ID = """SELECT ${projection}  FROM "${table_prefix}${table_name}"
     WHERE job_id = :job_id """
    SELECT_BY_COMMAND = """SELECT ${projection}  FROM "${table_prefix}${table_name}"
     WHERE command_uri = :command_uri """
    SELECT_BY_MARKET = """SELECT ${projection}  FROM "${table_prefix}${table_name}"
     WHERE market_id = :market_id """

    INSERT = """INSERT INTO "${table_prefix}${table_name}"
     ( "command_uri", "market_id","job_name","job_description","ext" ,"update_ts"  )
     VALUES (:command_uri, :market_id, :job_name, :job_description, :ext,extract(epoch from now()) * 1000) """

    UPDATE = """UPDATE  "${table_prefix}${table_name}" SET 
     "command_uri"=:command_uri, "market_id"= :market_id,"job_name"=:job_name,
     "job_description"=:job_description,"ext"=:ext ,"update_ts"= extract(epoch from now()) * 1000
     WHERE job_id = :job_id """


class JobAPIImpl(JobAPI):
    queries: JobAPIQueries

    def __init__(self, table_prefix: str):
        super().__init__()
        self.queries: JobAPIQueries = JobAPIQueries.build(table_prefix=table_prefix)

    def save(self, job: JobDAO) -> JobDAO:
        with ConnectionWrapper() as conn:
            inserted_id = conn.insert(q=self.queries.INSERT, args=vars(job),
                                      return_id_col="job_id")
            if inserted_id is None:
                raise ValueError(f"Job not saved: {job.__dict__}")
            job.job_id = inserted_id
            return job

    def update(self, job: JobDAO) -> JobDAO:
        with ConnectionWrapper() as conn:
            updated = conn.update(q=self.queries.UPDATE, args=vars(job))
            if updated != 1:
                raise ValueError(f"Job not updated: {job.__dict__}")
            return self.get(job_id=job.job_id)

    def list(self, ) -> List[JobDAO]:
        with ConnectionWrapper() as conn:
            return conn.select(q=self.queries.LIST, args={}, obj_type=JobDAO)

    def get(self, job_id: int) -> Optional[JobDAO]:
        with ConnectionWrapper() as conn:
            return conn.get(q=self.queries.SELECT_BY_ID, args={"job_id": job_id}, obj_type=JobDAO)

    def get_by_command(self, command_uri: str) -> Optional[JobDAO]:
        with ConnectionWrapper() as conn:
            return conn.get(q=self.queries.SELECT_BY_COMMAND, args={"command_uri": command_uri}, obj_type=JobDAO)

    def get_by_market(self, market_id: int) -> Optional[JobDAO]:
        with ConnectionWrapper() as conn:
            return conn.get(q=self.queries.SELECT_BY_MARKET, args={"market_id": market_id}, obj_type=JobDAO)
