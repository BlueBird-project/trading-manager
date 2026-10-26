from abc import abstractmethod
from typing import List, Optional

from effi_onto_tools.db.postgresql.connection_wrapper import ConnectionWrapper

from tm.core.db.api.capacity_notification import NotificationAPI
from tm.core.db.postgresql.api_impl import QueryObject
from tm.models.capacity_market import CapacityNotification
from tm.models.digital_twin import DigitalTwinDAO


class NotificationAPIQueries(QueryObject):
    __PROJECTION__ = """ "asset_manager_uri", "flex_instruction_uri", "flex_profile_uri", "power_limit_uri", "ts", 
     "max_consumption_uri", "max_consumption","update_ts" """
    __TABLE_NAME__ = "ke_capacity_notification"
    SELECT = """SELECT ${projection}  FROM "${table_prefix}${table_name}" WHERE 
    COALESCE(asset_manager_uri = :asset_manager_uri ,TRUE)  """
    GET_BY_URI = """SELECT ${projection}  FROM "${table_prefix}${table_name}" WHERE 
    asset_manager_uri = :asset_manager_uri  """
    GET_MAX_TS = """SELECT max(ts)  FROM "${table_prefix}${table_name}" WHERE 
    COALESCE(asset_manager_uri = :asset_manager_uri ,TRUE) """
    GET_BY_TS = """SELECT ${projection}  FROM "${table_prefix}${table_name}" WHERE 
    asset_manager_uri = :asset_manager_uri  AND "ts" = :max_ts"""

    INSERT = """INSERT INTO "${table_prefix}${table_name}"
     ("asset_manager_uri", "flex_instruction_uri", "flex_profile_uri", "power_limit_uri", 
     "ts", "max_consumption_uri", "max_consumption","update_ts")
     VALUES (:asset_manager_uri, :flex_instruction_uri, :flex_profile_uri,   :power_limit_uri,
     :ts, :max_consumption_uri, :max_consumption,  extract(epoch from now()) * 1000) """


class NotificationAPIImpl(NotificationAPI):
    queries: NotificationAPIQueries

    def __init__(self, table_prefix: str):
        super().__init__()
        self.queries: NotificationAPIQueries = NotificationAPIQueries.build(table_prefix=table_prefix)

    @abstractmethod
    def list(self, ) -> List[CapacityNotification]:
        with ConnectionWrapper() as conn:
            return conn.select(q=self.queries.SELECT, args={"asset_manager_uri": None}, obj_type=CapacityNotification)

    def save(self, notification: CapacityNotification) -> CapacityNotification:
        with ConnectionWrapper() as conn:
            update_ts = conn.insert(q=self.queries.INSERT, args=vars(notification),
                                    return_id_col="update_ts")
            if update_ts is None:
                raise ValueError(f"CapacityNotification not saved: {notification.__dict__}")
            notification.update_ts = update_ts
            return notification

    @abstractmethod
    def get_by_uri(self, asset_manager_uri: str) -> Optional[CapacityNotification]:
        with ConnectionWrapper() as conn:
            return conn.select(q=self.queries.SELECT, args={"asset_manager_uri": asset_manager_uri},
                               obj_type=CapacityNotification)

    @abstractmethod
    def get_recent(self, ) -> List[CapacityNotification]:
        with ConnectionWrapper() as conn:
            max_ts = conn.get(q=self.queries.GET_MAX_TS, args={"asset_manager_uri": None})
            if max_ts is None:
                return []
            return conn.select(q=self.queries.SELECT, args={"asset_manager_uri": None, "max_ts": max_ts},
                               obj_type=CapacityNotification)
