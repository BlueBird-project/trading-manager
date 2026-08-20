import logging
from string import Template

from effi_onto_tools.db.postgresql.init_db import DBMeta, APP_CONFIG_TABLE_NAME
from sqlalchemy import text


def _run_ddl(ddl_str: str, table_prefix: str, db_version: str):
    from effi_onto_tools.db.postgresql.dbconnection import connection_manager
    logging.info(f"({table_prefix}) update db to {db_version}")
    with connection_manager.get_connection() as conn:
        ddl_template = Template(ddl_str)
        ddl_query_str = ddl_template.substitute(table_prefix=table_prefix)
        conn.execute(text(ddl_query_str))
        from tm.core.db.postgresql import dao_manager
        dao_manager.app_settings_dao.set('db_version', db_version)
        conn.commit()

        # conn.execute(text(f"""INSERT INTO "{table_prefix}{APP_CONFIG_TABLE_NAME}" ("key", "value","update_ts")
        #                     VALUES ('db_version', '{db_version}',EXTRACT(epoch FROM current_timestamp) *1000);"""))


def update_db(update_map, db_meta: DBMeta):
    from tm.core.db.postgresql import dao_manager
    cur_version = dao_manager.app_settings_dao.get("db_version")
    processed_versions = set()
    while cur_version not in processed_versions and cur_version != db_meta.db_version:
        update_stage = update_map[cur_version]
        logging.info(f"db update from: '{cur_version}'")
        update_stage(db_meta=db_meta)
        processed_versions.add(cur_version)
        cur_version = dao_manager.app_settings_dao.get("db_version")
        logging.info(f"db updated to: '{cur_version}'")
    #     TODO log stages
    logging.info("Finished update")
