### Configuration Parameters

| Name                | Type   | Default (app default)                                        | Description                                                           |
|---------------------|--------|--------------------------------------------------------------|-----------------------------------------------------------------------|
| `APP_USE_SCHEDULER` | *bool* | `true`(`false`)                                              | Enable background tasks                                               |
| `APP_USE_REST_API`  | *bool* | `true`(`true`)                                               | Enable REST API                                                       |
| `APP_USE_KE_API`    | *bool* | `false`(`false`)                                             | Enable KE client                                                      |
| `DB_USER`           | *str*  | `postgres`(`postgres`)                                       | db usename                                                            |
| `DB_PASS`           | *str*  | `postgres`(`postgres`)                                       |                                                                       |
| `DB_NAME`           | *str*  | `postgres`(`postgres`)                                       |                                                                       |
| `DB_HOST`           | *str*  | `tge-postgres`(`tge-postgres`)                               |                                                                       |
| `db_init`           | *bool* | `false`(`false`)                                             | enable schema init on start from `/app/resources/db/pg_init.sql` file |
| `DB_TABLE_PREFIX`   | *str*  | `tge_`(`tge`)                                                |                                                                       |
| `KE_REST_ENDPOINT`  | *str*  | `http://localhost:8280/rest/`(`http://localhost:8280/rest/`) |                                                                       |

### Graph patterns location:

`/app/resources/ke_config.yml` - app config file

 