from abc import ABC, abstractmethod
from datetime import tzinfo, timezone
from typing import List, Union, Optional, Dict, Any, Tuple

from effi_onto_tools.db import Pagination, TimeSpan
from effi_onto_tools.db.postgresql.connection_wrapper import ConnectionWrapper
from effi_onto_tools.utils import time_utils

from tm.core.db.api.day_ahead import DayAheadAPI
from tm.core.db.api.market import MarketAPI
from tm.models.market import EnergyMarket


class MarketQueries:
    # TODO: list columns instead of *
    LIST_MARKET = """SELECT "market_id","market_uri", "market_name", "market_type", 
    "market_description", "market_location", "isp_unit", "isp_len","subscribe", "update_ts", "ext"
    FROM "${table_prefix}market_details"    """
    LIST_SUBSCRIBED_MARKET = """SELECT "market_id","market_uri", "market_name", "market_type", 
    "market_description", "market_location", "isp_unit", "isp_len","subscribe", "update_ts", "ext"
    FROM "${table_prefix}market_details"  WHERE "subscribe"   """
    SELECT_MARKET_BY_URI = """SELECT "market_id","market_uri", "market_name", "market_type", 
    "market_description", "market_location", "isp_unit", "isp_len","subscribe", "update_ts", "ext"
    FROM "${table_prefix}market_details" WHERE market_uri = :market_uri   """

    INSERT_MARKET = """INSERT INTO "${table_prefix}market_details" 
    ("market_uri", "market_name", "market_type", "market_description", "market_location",
     "isp_unit", "isp_len", "update_ts", "ext") 
     VALUES (:market_uri,:market_name,:market_type, :market_description, :market_location,
     :isp_unit,:isp_len,extract(epoch from now()) * 1000,:ext)
   
        """
    # ON CONFLICT ("market_uri" ) DO UPDATE
    # SET update_ts = extract(epoch from now()) * 1000, date_str= EXCLUDED.date_str,
    # isp_len= EXCLUDED.isp_len,  cost_mwh= EXCLUDED.cost_mwh


class MarketAPIImpl(MarketAPI):
    def __init__(self, table_prefix: str):
        super(MarketAPI, self).__init__(table_prefix=table_prefix)
        self.queries: MarketQueries = self.build_queries(MarketQueries)

    def save_market(self, market: EnergyMarket) -> EnergyMarket:
        with ConnectionWrapper() as conn:
            inserted_id = conn.insert(q=self.queries.INSERT_MARKET, args=vars(market),
                                      return_id_col="market_id")
            if inserted_id is None:
                raise ValueError(f"Market not saved: {market.__dict__}")
            market.market_id = inserted_id
            return market

    def list_market(self) -> List[EnergyMarket]:
        with ConnectionWrapper() as conn:
            args = {}
            markets = conn.select(q=self.queries.LIST_MARKET, args=args, obj_type=EnergyMarket)
            return markets

    def list_subscribed_market(self) -> List[EnergyMarket]:
        with ConnectionWrapper() as conn:
            args = {}
            markets = conn.select(q=self.queries.LIST_SUBSCRIBED_MARKET, args=args, obj_type=EnergyMarket)
            return markets

    def get_market(self, market_uri: str) -> EnergyMarket:
        with ConnectionWrapper() as conn:
            args = {"market_uri": market_uri}
            market = conn.get(q=self.queries.SELECT_MARKET_BY_URI, args=args, obj_type=EnergyMarket)
            return market
