from abc import abstractmethod
from typing import List, Optional, Dict

from effi_onto_tools.db.postgresql.connection_wrapper import ConnectionWrapper

from tm.core.db.api.dt_forecast import DTForecastAPI
from tm.core.db.postgresql.api_impl import QueryObject
from tm.core.db.postgresql.api_impl.dt_api_impl import DTAPIQueries
from tm.models.digital_twin import DTForecastInfoDAO, DTForecastOfferDAO
from tm.utils import TimeSpan


class DTForecastInfoQueries(QueryObject):
    # __PROJECTION__ = """ "forecast_id", "forecast_uri" ,"range_id" ,"job_id","sequence" ,"offer_id" ,"model_id" ,"ts" ,
    # "isp_len"  ,"isp_unit"  ,"update_ts" """
    __TABLE_NAME__ = "forecast_details"

    __PROJECTION__ = """ ${table_alias}."forecast_id",  ${table_alias}."forecast_uri" ,
        ${table_alias}."range_id" ,  ${table_alias}."sequence" ,  ${table_alias}."offer_id" ,
         ${table_alias}."model_id" , ${table_alias}."ts" ,  ${table_alias}."isp_len"  ,
        ${table_alias}."isp_unit"  ,${table_alias}."update_ts" """

    # LIST = """SELECT ${projection}  FROM "${table_prefix}${table_name}"
    #   WHERE  COALESCE( job_id = :job_id , TRUE ) AND COALESCE( model_id = :model_id , TRUE )
    #   AND   ("ts" BETWEEN :ts_from and :ts_to)  """
    LIST = """SELECT ${projection}  FROM "${table_prefix}${table_name}"  as ${table_alias}
        JOIN  "${table_prefix}""" + DTAPIQueries.__TABLE_NAME__ + """" as dt_info 
      WHERE COALESCE( dt_info.job_id = :job_id , TRUE ) AND
        COALESCE( model_id = :model_id , TRUE )  AND   ("ts" BETWEEN :ts_from and :ts_to)  """

    GET_BY_URI = """SELECT ${projection} FROM "${table_prefix}${table_name}" as ${table_alias} 
     WHERE   forecast_uri = :forecast_uri """
    # GET_MAX_TS = """SELECT max("ts") as "ts" from "${table_prefix}${table_name}"
    #     WHERE COALESCE( job_id = :job_id , TRUE ) AND COALESCE( model_id = :model_id , TRUE )  """
    GET_MAX_TS = """SELECT max("ts") as "ts" from "${table_prefix}${table_name}" 
        JOIN  "${table_prefix}""" + DTAPIQueries.__TABLE_NAME__ + """" as dt_info 
        WHERE  COALESCE( dt_info.job_id = :job_id , TRUE ) AND COALESCE( model_id = :model_id , TRUE )  """
    GET = """SELECT ${projection}  FROM "${table_prefix}${table_name}" as ${table_alias}
     WHERE  forecast_id = :forecast_id """

    INSERT = """INSERT INTO "${table_prefix}${table_name}"
     ( "forecast_id", "forecast_uri","range_id"  ,"sequence" ,"offer_id" ,"model_id" ,"ts" , 
    "isp_len"  ,"isp_unit"  ,"update_ts"  )
     VALUES (:forecast_id, :forecast_uri, :range_id, :sequence, :offer_id, :model_id, :ts ,
      :isp_len , :isp_unit , extract(epoch from now()) * 1000) """


class DTForecastQueries(QueryObject):
    __PROJECTION__ = """ "forecast_id", "isp_start" ,"cost_mwh" ,"ts" ,"isp_len" """
    __TABLE_NAME__ = "market_offer_forecast"

    LIST = """SELECT ${projection}  FROM "${table_prefix}${table_name}"  WHERE forecast_id in :forecast_ids """
    GET = """SELECT ${projection}  FROM "${table_prefix}${table_name}" WHERE forecast_id=:forecast_id"""

    INSERT_FORECAST_OFFER = """ INSERT INTO "${table_prefix}${table_name}"
        ("forecast_id", "isp_start",  "cost_mwh", "ts", "isp_len")
        VALUES (:forecast_id, :isp_start,   :cost_mwh, :ts, :isp_len)   """

    DELETE_FORECAST_OFFER = """ DELETE FROM "${table_prefix}${table_name}" WHERE forecast_id=:forecast_id  """


class DTForecastAPImpl(DTForecastAPI):
    q_dt_info: DTForecastInfoQueries
    q_dt_offer: DTForecastQueries

    def __init__(self, table_prefix: str):
        super().__init__()
        self.q_dt_info: DTForecastInfoQueries = DTForecastInfoQueries.build(table_prefix=table_prefix,
                                                                            table_alias="dtf_info")
        self.q_dt_offer: DTForecastQueries = DTForecastQueries.build(table_prefix=table_prefix)

    def save(self, forecast_info: DTForecastInfoDAO) -> DTForecastInfoDAO:
        with ConnectionWrapper() as conn:
            inserted_id = conn.insert(q=self.q_dt_info.INSERT, args=vars(forecast_info),
                                      return_id_col="forecast_id")
            if inserted_id is None:
                raise ValueError(f"ForecastInfo not saved: {forecast_info.__dict__}")
            forecast_info.forecast_id = inserted_id
            return forecast_info

    def list_forecasts(self, ts: Optional[TimeSpan], job_id: Optional[int]) -> List[DTForecastInfoDAO]:
        return self.find_forecasts(ts=ts, job_id=job_id, model_id=None)

    def find_forecasts(self, ts: Optional[TimeSpan], job_id: Optional[int], model_id: Optional[int], ) \
            -> List[DTForecastInfoDAO]:
        with ConnectionWrapper() as conn:
            if ts is None:
                t = conn.get(q=self.q_dt_info.GET_MAX_TS, args={"job_id": job_id, "model_id": model_id}, raw=True)
                if t is None:
                    return []
                args = {"ts_from": t[0], "ts_to": t[0], "job_id": job_id, "model_id": model_id}
            else:
                args = {"ts_from": ts.ts_from, "ts_to": ts.ts_to, "job_id": job_id, "model_id": model_id}
            return conn.select(q=self.q_dt_info.LIST, args=args, obj_type=DTForecastInfoDAO)

    def get(self, forecast_id: int) -> Optional[DTForecastInfoDAO]:
        with ConnectionWrapper() as conn:
            return conn.get(q=self.q_dt_info.GET, args={"forecast_id": forecast_id}, obj_type=DTForecastInfoDAO)

    def get_by_uri(self, forecast_uri: str) -> Optional[DTForecastInfoDAO]:
        with ConnectionWrapper() as conn:
            return conn.get(q=self.q_dt_info.GET_BY_URI, args={"forecast_uri": forecast_uri},
                            obj_type=DTForecastInfoDAO)

    def get_offer(self, forecast_id: int) -> List[DTForecastOfferDAO]:
        with ConnectionWrapper() as conn:
            return conn.select(q=self.q_dt_offer.GET, args={"forecast_id": forecast_id}, obj_type=DTForecastOfferDAO)

    def get_offers(self, forecast_ids: List[int]) -> List[DTForecastOfferDAO]:
        with ConnectionWrapper() as conn:
            return conn.select(q=self.q_dt_offer.LIST, args={"forecast_ids": forecast_ids}, obj_type=DTForecastOfferDAO)

    @abstractmethod
    def save_offer(self, forecast_offers: List[DTForecastOfferDAO]) -> List[Dict]:
        with ConnectionWrapper() as conn:
            inserted = conn.insert_batch(q=self.q_dt_offer.INSERT_FORECAST_OFFER,
                                         arg_list=[vars(fo) for fo in forecast_offers],
                                         return_id_col=["offer_id", "isp_start", "cost_mwh", "isp_len"],
                                         fail_safe=False)

            return [{k: v for k, v in zip(["offer_id", "isp_start", "cost_mwh", "isp_len"], r)} for r in inserted]

    def clear_forecast_offer(self, forecast_id) -> int:
        with ConnectionWrapper() as conn:
            deleted = conn.update(q=self.q_dt_offer.DELETE_FORECAST_OFFER,
                                  args={"offer_id": forecast_id})

            return deleted
