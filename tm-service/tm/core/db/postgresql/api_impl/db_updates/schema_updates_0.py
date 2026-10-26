from effi_onto_tools.db.postgresql.init_db import DBMeta

from tm.core.db.postgresql.api_impl.db_updates import _run_ddl

_0_2_ddl = """

ALTER TABLE "${table_prefix}dt_info"
ADD "kb_id" character varying(250) NULL;
 
"""
_0_3_ddl = """

CREATE TABLE "${table_prefix}ke_capacity_notification" (
  "asset_manager_uri" character varying(250) NOT NULL,
  "flex_instruction_uri" character varying(250) NOT NULL,
  "flex_profile_uri" character varying(250) NOT NULL,
  "power_limit_uri" character varying(250) NOT NULL,
  "ts" bigint NOT NULL,
  "max_consumption_uri" character varying(250) NOT NULL,
  "max_consumption" double precision NOT NULL,
  "update_ts" bigint NOT NULL
);

ALTER TABLE "${table_prefix}ke_capacity_notification"
ADD CONSTRAINT "${table_prefix}ke_capacity_notification_asset_manager_uri_ts" PRIMARY KEY ("asset_manager_uri", "ts");
CREATE INDEX "${table_prefix}ke_capacity_notification_ts" ON "${table_prefix}ke_capacity_notification" ("ts");

 
"""


def db_0_2_update(db_meta: DBMeta):
    _run_ddl(ddl_str=_0_2_ddl, db_version="0.2", table_prefix=db_meta.db_table_prefix)


def db_0_3_update(db_meta: DBMeta):
    _run_ddl(ddl_str=_0_3_ddl, db_version="0.3", table_prefix=db_meta.db_table_prefix)
