from ke_client import KEClient

from tm.modules.ke_interaction.interactions import setup_ke, init_client

setup_ke()
ki_client: KEClient = init_client()
