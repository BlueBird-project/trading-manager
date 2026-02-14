__DB_VERSION__ = "0.1"
__DB_HASH__ = {

}
__SCHEMA_NAME__ = 'public'

from string import Template


# __TABLE_PREFIX__ = "tm_"


class QueryObject:
    __PROJECTION__: str = "*"
    __TABLE_NAME__: str

    @classmethod
    def _q(cls, q: str, table_prefix: str):
        ddl_template = Template(q)
        ddl_query_str = ddl_template.safe_substitute(table_prefix=table_prefix, projection=cls.__PROJECTION__,
                                                     table_name=cls.__TABLE_NAME__)
        return ddl_query_str
        # return q.format(table_prefix=self.table_prefix)

    @classmethod
    def build(cls, table_prefix):
        q_obj = cls()
        for k, v in vars(cls).items():
            if type(v) is str and not v.startswith("__"):
                setattr(q_obj, k, cls._q(v, table_prefix))
        return q_obj
