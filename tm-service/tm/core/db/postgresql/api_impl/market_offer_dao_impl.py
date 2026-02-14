from typing import List, Optional, Dict, Any

from effi_onto_tools.db import TimeSpan
from effi_onto_tools.db.postgresql.connection_wrapper import ConnectionWrapper

from tm.core.db.api.market_offer_dao import MarketOfferAPI
from tm.models.market_offer import EnergyMarketOfferInfo, RangeInfo, EnergyMarketOffer


class MarketOfferQueries:
    # TODO add override option for market offer , real offer > forecast offer
    LIST_OFFER_INFO = """SELECT "offer_id","market_id", "ts", "date_str",
     "offer_uri","sequence",  "isp_unit", "isp_len", "update_ts", "ext" 
      FROM "${table_prefix}offer_details" 
       WHERE  ("ts" BETWEEN :ts_from and :ts_to) and COALESCE("isp_unit"=:isp_unit,TRUE  )
       AND COALESCE(market_id = :market_id,TRUE)
        """
    SELECT_MARKET_OFFER_INFO_BY_URI = """SELECT "offer_id","market_id", "ts", "date_str",
     "offer_uri","sequence",  "isp_unit", "isp_len", "update_ts", "ext" 
      FROM "${table_prefix}offer_details"  WHERE offer_uri = :offer_uri   """

    INSERT_MARKET_OFFER_DETAILS = """  INSERT INTO "${table_prefix}offer_details" 
    ("market_id", "ts", "date_str", "offer_uri","sequence", "isp_unit", "isp_len", "update_ts", "ext")
    VALUES (:market_id, :ts, :date_str, :offer_uri,:sequence, :isp_unit, :isp_len,
     extract(epoch from now()) * 1000, NULL)   """
    # TODO: on conflixt
    # ON CONFLICT ("market_uri" ) DO UPDATE
    # SET update_ts = extract(epoch from now()) * 1000, date_str= EXCLUDED.date_str,
    # isp_len= EXCLUDED.isp_len,  cost_mwh= EXCLUDED.cost_mwh
    INSERT_RANGE = """INSERT INTO "${table_prefix}consumption_range" ("min_value", "max_value")
    VALUES (:min_value, :max_value) """
    # TODO: get range depraceted? look at select range
    GET_RANGE = """SELECT "range_id","min_value", "max_value"  FROM "${table_prefix}consumption_range" 
    WHERE ((:min_value is NULL and "min_value" is NULL) or (:min_value=min_value) )
     AND  ((:max_value is NULL and "max_value" is NULL) or (:max_value=max_value) )  """

    SELECT_RANGE = """SELECT "range_id","min_value", "max_value"  FROM "${table_prefix}consumption_range" 
    WHERE ( (:max_value is NULL) or  ( "min_value" is NULL or "min_value" < :max_value) )
     AND  ( (:min_value is NULL) or ( "max_value" is NULL or "max_value" > :min_value) )  """

    GET_MARKET_OFFER_BY_OFFER_ID = """SELECT "offer_id", "isp_start", "range_id", "cost_mwh", "ts", "isp_len"
      FROM "${table_prefix}market_offer"  WHERE offer_id = :offer_id
       """
    LIST_MARKET_OFFER = """SELECT offer."offer_id", offer."isp_start", offer."range_id", 
      offer."cost_mwh", offer."ts", offer."isp_len"
      FROM "${table_prefix}market_offer" offer  
      JOIN "${table_prefix}offer_details"  offer_info  on offer.offer_id = offer_info.offer_id 
      WHERE offer_info.market_id =:market_id AND
           (offer."ts" BETWEEN :ts_from and :ts_to) and COALESCE(offer_info."isp_unit"=:isp_unit,TRUE )  """

    INSERT_MARKET_OFFER = """ INSERT INTO "${table_prefix}market_offer" 
        ("offer_id", "isp_start", "range_id", "cost_mwh", "ts", "isp_len")
        VALUES (:offer_id, :isp_start, :range_id, :cost_mwh, :ts, :isp_len)   """

    DELETE_MARKET_OFFER = """ DELETE FROM "${table_prefix}market_offer"  WHERE offer_id=:offer_id  """


class MarketOfferAPIImpl(MarketOfferAPI):
    def __init__(self, table_prefix: str):
        super(MarketOfferAPI, self).__init__(table_prefix=table_prefix)
        self.queries: MarketOfferQueries = self.build_queries(MarketOfferQueries)

    def register_offer(self, market_offer: EnergyMarketOfferInfo) -> EnergyMarketOfferInfo:
        with ConnectionWrapper() as conn:
            inserted_id = conn.insert(q=self.queries.INSERT_MARKET_OFFER_DETAILS, args=vars(market_offer),
                                      return_id_col="offer_id")
            if inserted_id is None:
                raise ValueError(f"Market offer not saved: {market_offer.__dict__}")
            market_offer.offer_id = inserted_id
            return market_offer

    def list_offer_info(self, ts: Any, market_id: Optional[int] = None,
                        isp_unit: Optional[int] = None) -> List[EnergyMarketOfferInfo]:
        with ConnectionWrapper() as conn:
            args = {"ts_from": ts.ts_from, "ts_to": ts.ts_to, "isp_unit": isp_unit, "market_id": market_id}
            offers = conn.select(q=self.queries.LIST_OFFER_INFO, args=args, obj_type=EnergyMarketOfferInfo)
            return offers

    def get_offer_info(self, offer_uri: str) -> EnergyMarketOfferInfo:
        with ConnectionWrapper() as conn:
            args = {"offer_uri": offer_uri}
            offer = conn.get(q=self.queries.SELECT_MARKET_OFFER_INFO_BY_URI, args=args, obj_type=EnergyMarketOfferInfo)
            return offer

    def add_range(self, range_info: RangeInfo) -> RangeInfo:
        with ConnectionWrapper() as conn:
            inserted_id = conn.insert(q=self.queries.INSERT_RANGE, args=vars(range_info),
                                      return_id_col="range_id")
            if inserted_id is None:
                raise ValueError(f"Range not saved: {range_info.__dict__}")
            range_info.range_id = inserted_id
            return range_info

    def get_range(self, min_value: Optional[float] = None, max_value: Optional[float] = None) -> Optional[RangeInfo]:
        with ConnectionWrapper() as conn:
            args = {"min_value": min_value, "max_value": max_value}
            range_info = conn.get(q=self.queries.GET_RANGE, args=args, obj_type=RangeInfo)
            return range_info

    def list_range(self, min_value: Optional[float] = None, max_value: Optional[float] = None) -> List[RangeInfo]:
        with ConnectionWrapper() as conn:
            args = {"min_value": min_value, "max_value": max_value}
            range_info = conn.select(q=self.queries.SELECT_RANGE, args=args, obj_type=RangeInfo)
            return range_info

    def add_offer(self, market_offer_items: List[EnergyMarketOffer]) -> List[Dict]:
        with ConnectionWrapper() as conn:
            inserted = conn.insert_batch(q=self.queries.INSERT_MARKET_OFFER,
                                         arg_list=[vars(mo) for mo in market_offer_items],
                                         return_id_col=["offer_id", "isp_start","cost_mwh","isp_len"], fail_safe=False)

            return [{k: v for k, v in zip(["offer_id", "isp_start","cost_mwh","isp_len"], r)} for r in inserted]

    def clear_market_offer(self, offer_id) -> int:
        with ConnectionWrapper() as conn:
            deleted = conn.update(q=self.queries.DELETE_MARKET_OFFER,
                                  args={"offer_id": offer_id})

            return deleted

    def list_market_offer(self, ts: TimeSpan, market_id: Optional[int] = None,
                          isp_unit: Optional[int] = None) -> List[EnergyMarketOffer]:
        with ConnectionWrapper() as conn:
            args = {"ts_from": ts.ts_from, "ts_to": ts.ts_to, "isp_unit": isp_unit, "market_id": market_id}
            offers = conn.select(q=self.queries.LIST_MARKET_OFFER, args=args, obj_type=EnergyMarketOffer)

            return offers

    def get_market_offer(self, offer_id: int) -> List[EnergyMarketOffer]:
        with ConnectionWrapper() as conn:
            args = {"offer_id": offer_id}
            offer = conn.select(q=self.queries.GET_MARKET_OFFER_BY_OFFER_ID, args=args, obj_type=EnergyMarketOffer)
            return offer
