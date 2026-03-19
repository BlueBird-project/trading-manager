from abc import abstractmethod
from typing import List, Optional

from effi_onto_tools.db.postgresql.connection_wrapper import ConnectionWrapper

from tm.core.db.api.dt_forecast import DTForecastAPI
from tm.core.db.postgresql.api_impl import QueryObject
from tm.models.digital_twin import DTForecastInfoDAO, DTForecastOfferDAO
from tm.utils import TimeSpan


class DTForecastInfoQueries(QueryObject):
    __PROJECTION__ = """ "forecast_id", "forecast_uri" ,"sequence" ,"offer_id" ,"model_id" ,"ts" , 
    "isp_len"  ,"isp_unit"  ,"update_ts" """
    __TABLE_NAME__ = "forecast_details"
    LIST = """SELECT ${projection}  FROM "${table_prefix}${table_name}" WHERE :ts """

    GET_BY_URI = """SELECT ${projection}  FROM "${table_prefix}${table_name}" WHERE   forecast_uri = :forecast_uri """
    GET_MAX_TS = """SELECT max("ts") as "ts" from "${table_prefix}${table_name}" WHERE  """
    GET = """SELECT ${projection}  FROM "${table_prefix}${table_name}" WHERE  forecast_id = :forecast_id """

    INSERT = """INSERT INTO "${table_prefix}${table_name}"
     ( "forecast_id", "forecast_uri" ,"sequence" ,"offer_id" ,"model_id" ,"ts" , 
    "isp_len"  ,"isp_unit"  ,"update_ts"  )
     VALUES (:forecast_id, :forecast_uri,:sequence, :offer_id, :model_id, :ts ,
      :isp_len , :isp_unit , extract(epoch from now()) * 1000) """


class DTForecastQueries(QueryObject):
    __PROJECTION__ = """ "forecast_id", "isp_start" ,"range_id" ,"cost_mwh" ,"ts" ,"isp_len" """
    __TABLE_NAME__ = "market_offer_forecast"
    LIST = """SELECT ${projection}  FROM "${table_prefix}${table_name}" """
    GET_BY_URI = """SELECT ${projection}  FROM "${table_prefix}${table_name}" WHERE 
    dt_uri = :dt_uri and (( market_id is NULL and :market_id is NULL) or market_id=:market_id )"""

    INSERT = """INSERT INTO "${table_prefix}${table_name}"
     ( "dt_uri","market_id","job_id","ext" ,"update_ts"  )
     VALUES (:dt_uri, :market_id,:job_id, :ext,extract(epoch from now()) * 1000) """
    pass


class DTForecastAPImpl(DTForecastAPI):
    q_dt_info: DTForecastInfoQueries
    q_dt_offer: DTForecastQueries

    def __init__(self, table_prefix: str):
        super().__init__()
        self.q_dt_info: DTForecastInfoQueries = DTForecastInfoQueries.build(table_prefix=table_prefix)
        self.q_dt_offer: DTForecastQueries = DTForecastQueries.build(table_prefix=table_prefix)

    @abstractmethod
    def save(self, forecast_info: DTForecastInfoDAO) -> DTForecastInfoDAO:
        with ConnectionWrapper() as conn:
            inserted_id = conn.insert(q=self.q_dt_info.INSERT, args=vars(forecast_info),
                                      return_id_col="dt_id")
            if inserted_id is None:
                raise ValueError(f"ForecastInfo not saved: {forecast_info.__dict__}")
            forecast_info.forecast_uri = inserted_id
            return forecast_info

    @abstractmethod
    def list_forecasts(self, ts: Optional[TimeSpan], dt_id: Optional[int]) -> List[DTForecastInfoDAO]:
        with ConnectionWrapper() as conn:
            if ts is None:

            conn.get(q=self.)
            return conn.select(q=self.queries.LIST, args={}, obj_type=DigitalTwinDAO)
        pass

    @abstractmethod
    def find_forecasts(self, ts: Optional[TimeSpan], dt_id: Optional[int], model_id: Optional[int], ) \
            -> List[DTForecastInfoDAO]:
        pass

    @abstractmethod
    def get(self, forecast_id: int) -> Optional[DTForecastInfoDAO]:
        pass

    def get_by_uri(self, forecast_uri: str) -> Optional[DTForecastInfoDAO]:
        pass

    @abstractmethod
    def get_offer(self, forecast_id: int) -> List[DTForecastOfferDAO]:
        pass

    @abstractmethod
    def get_offers(self, forecast_id: List[int]) -> List[DTForecastOfferDAO]:
        pass
