from effi_onto_tools.db.postgresql.init_db import DBMeta

from tm.core.db.postgresql.api_impl.db_updates import _run_ddl

_0_2_ddl = """

ALTER TABLE "${table_prefix}dt_info"
ADD "kb_id" character varying(250) NULL;
 
"""


def db_0_2_update(db_meta: DBMeta):
    from tm.core.db.postgresql import dao_manager

    _run_ddl(ddl_str=_0_2_ddl, db_version="0.2", table_prefix=db_meta.db_table_prefix)
