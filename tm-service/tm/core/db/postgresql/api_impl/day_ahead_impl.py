from datetime import tzinfo, timezone
from typing import List, Union, Optional, Dict, Any, Tuple

from effi_onto_tools.db import TimeSpan
from effi_onto_tools.db.postgresql.connection_wrapper import ConnectionWrapper
from ke_client.utils import time_utils 

from tm.core.db.api.day_ahead import DayAheadAPI


class DayAheadQueries:
    GET_DAY_OFFER = """SELECT "ts","update_ts","date_str","isp_start" ,"isp_len" ,"isp_unit",	"cost_mwh" 
    FROM "${table_prefix}day_ahead_offer" 
    WHERE "date_str" = :date_str AND COALESCE("isp_unit"=:isp_unit,TRUE)  ORDER BY isp_start asc """
    GET_DAY_OFFER_TS = """SELECT "ts","update_ts","date_str","isp_start" ,"isp_len" ,"isp_unit",	"cost_mwh" 
    FROM "${table_prefix}day_ahead_offer" 
    WHERE "ts" = :ts AND COALESCE("isp_unit"=:isp_unit,TRUE)  ORDER BY isp_start asc """

    LIST_DAY_OFFER = """SELECT  "ts","update_ts","date_str","isp_start" ,"isp_len" ,"isp_unit",	"cost_mwh" 
    FROM "${table_prefix}day_ahead_offer" 
        WHERE "ts" BETWEEN :ts_from and :ts_to and COALESCE("isp_unit"=:isp_unit,TRUE) 
     ORDER BY ts asc,isp_start asc """

    INSERT_OFFER = """INSERT INTO "${table_prefix}day_ahead_offer" 
     ( "ts","update_ts","date_str","isp_start" ,"isp_len" ,"isp_unit",	"cost_mwh" )
     VALUES (:ts,extract(epoch from now()) * 1000,:date_str,:isp_start, :isp_len, :isp_unit,:cost_mwh)
     ON CONFLICT ("ts", "isp_start","isp_unit") DO UPDATE
     SET update_ts = extract(epoch from now()) * 1000, date_str= EXCLUDED.date_str,
     isp_len= EXCLUDED.isp_len,  cost_mwh= EXCLUDED.cost_mwh 
        """

    SELECT_MAX_DATE = """SELECT MAX("ts") as ts FROM "${table_prefix}day_ahead_offer"  """
    COUNT_DAY_OFFER = """SELECT count(*) as "offer_count" , min("ts") as "first_ts", max("ts") as "last_ts" 
        FROM ( SELECT DISTINCT "ts" FROM "${table_prefix}day_ahead_offer"  
        WHERE "ts" BETWEEN :ts_from and :ts_to and COALESCE("isp_unit"=:isp_unit,TRUE) ) """

    LIST_DAY_OFFER_DATES_TS = """  SELECT DISTINCT "ts" FROM "${table_prefix}day_ahead_offer"  
        WHERE "ts" BETWEEN :ts_from and :ts_to and COALESCE("isp_unit"=:isp_unit,TRUE) order by "ts" desc  """


class DayAheadAPIImpl(DayAheadAPI):
    def __init__(self, table_prefix: str):
        super(DayAheadAPI, self).__init__(table_prefix=table_prefix)
        self.queries: DayAheadQueries = self.build_queries(DayAheadQueries)

    def log_day_offer(self, offer: List[Dict[str, Union[float, str, None]]]) -> List[Dict[str, Any]]:
        with ConnectionWrapper() as conn:
            inserted = conn.insert_batch(q=self.queries.INSERT_OFFER, arg_list=offer,
                                         return_id_col=["ts", "isp_start", "isp_len"], fail_safe=False)
            return [{k: v for k, v in zip(["ts", "isp_start", "isp_len"], r)} for r in inserted]

    def offers_last_date(self, ) -> Optional[str]:
        with ConnectionWrapper() as conn:
            res = conn.get(q=self.queries.SELECT_MAX_DATE, args={})
            # noinspection PyUnresolvedReferences
            if res is not None and res.ts is not None:
                # noinspection PyUnresolvedReferences
                return time_utils.from_timestamp(res.ts).strftime(time_utils.DATE_FORMAT)
            return None

    def get_offer_last_ts(self, ) -> Optional[int]:
        with ConnectionWrapper() as conn:
            res = conn.get(q=self.queries.SELECT_MAX_DATE, args={})
            # noinspection PyUnresolvedReferences
            if res is not None and res.ts is not None:
                # noinspection PyUnresolvedReferences
                return res.ts
            return None

    def get_day_offer(self, date_str: str, isp_unit: Optional[int] = None) -> List[dict]:
        with ConnectionWrapper() as conn:
            day_offer = conn.select(q=self.queries.GET_DAY_OFFER, args={"date_str": date_str, "isp_unit": isp_unit},
                                    obj_type=dict)
            return day_offer

    def get_day_offer_by_ts(self, ts: int, isp_unit: Optional[int] = None) -> List[dict]:
        with ConnectionWrapper() as conn:
            day_offer = conn.select(q=self.queries.GET_DAY_OFFER_TS, args={"ts": ts, "isp_unit": isp_unit},
                                    obj_type=dict)
            return day_offer

    def list_day_offer(self, ts: TimeSpan, isp_unit: Optional[int] = None) -> List[dict]:
        with ConnectionWrapper() as conn:
            args = {"ts_from": ts.ts_from, "ts_to": ts.ts_to, "isp_unit": isp_unit}
            day_offer = conn.select(q=self.queries.LIST_DAY_OFFER, args=args, obj_type=dict)
            return day_offer

    def count_day_offer(self, ts: TimeSpan, isp_unit: int) -> Tuple[int, int, int]:
        with ConnectionWrapper() as conn:
            args = {"ts_from": ts.ts_from, "ts_to": ts.ts_to, "isp_unit": isp_unit}
            row = conn.get(q=self.queries.COUNT_DAY_OFFER, args=args, obj_type=dict)
            return row["offer_count"], row["first_ts"], row["last_ts"]

    def list_day_offer_dates(self, ts: TimeSpan, isp_unit: int, tz: tzinfo = timezone.utc) -> List[str]:
        with ConnectionWrapper() as conn:
            args = {"ts_from": ts.ts_from, "ts_to": ts.ts_to, "isp_unit": isp_unit}
            rows = conn.select(q=self.queries.LIST_DAY_OFFER_DATES_TS, args=args, obj_type=dict)
            return [time_utils.datetime_to_str(time_utils.from_timestamp(r["ts"]), tz=tz)
                    for r in rows]
            # return row["offer_count"], row["first_ts"], row["last_ts"]
