
from ke_client.utils.enum_utils import BaseEnum


class KIVars(BaseEnum):
    ISP_UNIT = "ISP_UNIT"
    DAY_DURATION = "DAY_DURATION"




def setup_ke():
    from ke_client import configure_ke_client
    from tm import app_args
    configure_ke_client(app_args.config_path)

    from ke_client import ke_settings
    ki_vars = ke_settings.get_ki_vars()
    for k in KIVars.names():
        if k not in ki_vars:
            raise KeyError(f"{k} isn't defined in ki_vars")
        setattr(KIVars, k, ki_vars[k])
