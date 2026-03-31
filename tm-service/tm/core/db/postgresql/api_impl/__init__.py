__DB_VERSION__ = "0.1"
__DB_HASH__ = {

}
__SCHEMA_NAME__ = 'public'

from string import Template
from typing import Optional


# __TABLE_PREFIX__ = "tm_"


class QueryObject:
    __PROJECTION__: str = "*"
    __TABLE_NAME__: str

    @classmethod
    def _q(cls, q: str, table_prefix: str, table_alias: str, projection: str):
        ddl_template = Template(q)
        ddl_query_str = ddl_template.safe_substitute(table_prefix=table_prefix, projection=projection,
                                                     table_name=cls.__TABLE_NAME__, table_alias=table_alias)
        return ddl_query_str
        # return q.format(table_prefix=self.table_prefix)

    @classmethod
    def build(cls, table_prefix, table_alias: Optional[str] = None):
        q_obj = cls()
        table_alias = table_alias if table_alias is not None else table_prefix
        projection_template = Template(cls.__PROJECTION__)
        projection = projection_template.safe_substitute(table_alias=table_alias)
        for k, v in vars(cls).items():
            if type(v) is str and not v.startswith("__"):
                setattr(q_obj, k, cls._q(v, table_prefix, table_alias=table_alias, projection=projection))
        return q_obj
