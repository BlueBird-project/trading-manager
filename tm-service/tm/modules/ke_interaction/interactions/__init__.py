import logging


def setup_ke():
    import ke_client
    ke_client.VERIFY_SERVER_CERT = False
    from ke_client import configure_ke_client
    from tm import app_args
    configure_ke_client(app_args.config_path)

    from ke_client import ke_settings
    ki_vars = ke_settings.get_ki_vars()
    from tm.modules.ke_interaction import KIVars
    for k in KIVars.names():
        if k not in ki_vars:
            raise KeyError(f"{k} isn't defined in ki_vars")
        setattr(KIVars, k, ki_vars[k])


setup_ke()

from tm.modules.ke_interaction.interactions.dam_interactions import ki
from tm.modules.ke_interaction.interactions.dt_interactions import ki as dt_ki
from tm.modules.ke_interaction.interactions.fm_interactions import ki as fm_ki
from tm.modules.ke_interaction.interactions.tou_interactions import ki as tou_ki
from ke_client import KEClient

ki_client: KEClient = KEClient.build(logger=logging.getLogger())
ki_client.include(ki_holder=ki)
ki_client.include(ki_holder=dt_ki)
ki_client.include(ki_holder=fm_ki)
ki_client.include(ki_holder=tou_ki)
