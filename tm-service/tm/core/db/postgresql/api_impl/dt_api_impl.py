from typing import List, Optional

from effi_onto_tools.db.postgresql.connection_wrapper import ConnectionWrapper

from tm.core.db.api.dt_api import DTAPI
from tm.core.db.postgresql.api_impl import QueryObject
from tm.models.digital_twin import DigitalTwinDAO


# class JobDAO

class DTAPIQueries(QueryObject):
    __PROJECTION__ = """ "dt_id", "market_id" ,"dt_uri" ,"job_id" ,"update_ts" ,"ext" """
    __TABLE_NAME__ = "dt_info"
    LIST = """SELECT ${projection}  FROM "${table_prefix}${table_name}" """
    GET_BY_URI = """SELECT ${projection}  FROM "${table_prefix}${table_name}" WHERE 
    dt_uri = :dt_uri and (( market_id is NULL and :market_id is NULL) or market_id=:market_id )"""

    INSERT = """INSERT INTO "${table_prefix}${table_name}"
     ( "dt_uri","market_id","job_id","ext" ,"update_ts"  )
     VALUES (:dt_uri, :market_id,:job_id, :ext,extract(epoch from now()) * 1000) """


class DTAPIImpl(DTAPI):
    queries: DTAPIQueries

    def __init__(self, table_prefix: str):
        super().__init__()
        self.queries: DTAPIQueries = DTAPIQueries.build(table_prefix=table_prefix)

    def save(self, job: DigitalTwinDAO) -> DigitalTwinDAO:
        with ConnectionWrapper() as conn:
            inserted_id = conn.insert(q=self.queries.INSERT, args=vars(job),
                                      return_id_col="dt_id")
            if inserted_id is None:
                raise ValueError(f"DigitalTwin not saved: {job.__dict__}")
            job.market_id = inserted_id
            return job

    def list(self, ) -> List[DigitalTwinDAO]:
        with ConnectionWrapper() as conn:
            return conn.select(q=self.queries.LIST, args={}, obj_type=DigitalTwinDAO)

    def get(self, dt_uri: str, market_id: Optional[int]) -> Optional[DigitalTwinDAO]:
        with ConnectionWrapper() as conn:
            return conn.get(q=self.queries.GET_BY_URI, args={"market_id": market_id, "dt_uri": dt_uri},
                            obj_type=DigitalTwinDAO)
