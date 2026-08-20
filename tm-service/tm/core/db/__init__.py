from effi_onto_tools.db.dao_exception import DeprecatedSchemaException

from tm import app_args


def setup_db():
    from effi_onto_tools.db.postgresql import configure_pg
    configure_pg(app_args.config_path)
    from tm.core.db.postgresql import dao_manager

    def pg_check_db():
        from effi_onto_tools.db.postgresql.dbconnection import connection_manager
        try:
            connection_manager.check_db(db_meta=db_meta, assert_version=True)
        except DeprecatedSchemaException as ex:
            from tm.core.db.postgresql.api_impl.db_updates import update_db
            from tm.core.db.postgresql.api_impl import __DB_UPDATE_CHAIN__

            update_db(update_map=__DB_UPDATE_CHAIN__, db_meta=db_meta)

    db_meta = dao_manager.init()
    pg_check_db()

    from effi_onto_tools.db.postgresql.app_settings_dao_impl import AppSettingsImpl
    from tm.core.service import settings as service_settings
    AppSettingsImpl(table_prefix=db_meta.db_table_prefix, init_db=False).set("service_name", service_settings.name)
