import logging
import time

from effi_onto_tools.utils.enum_utils import EnumUtils


class KIVars(EnumUtils):
    ISP_UNIT = "ISP_UNIT"
    DAY_DURATION = "DAY_DURATION"


def _set_ke_client(bg_mode=False):
    from tm.modules.ke_interaction.interactions import setup_ke
    from tm.modules.ke_interaction.interactions.client import ki_client as ke_ki_client
    import ke_client
    ke_client.VERIFY_SERVER_CERT = False
    setup_ke()

    # ke_client.KE_CONFIG_PATH = ke_config_path
    MAX_ATTEMPTS = 20

    def try_register():
        cur_attempt = 0
        wait_time = 30
        is_registered = False
        while not is_registered:
            try:
                ke_ki_client.register()
                timeout_attempt = 0
                # TODO: register should return TRUE on success
                while not is_registered:
                    time.sleep(1)
                    is_registered = ke_ki_client.is_registered
                    if is_registered:
                        logging.info("KE client registered")
                    else:
                        logging.warning(f"KE client is not registered, wait for all KI to be registered.")
                        time.sleep(10)
                    if timeout_attempt > 10:
                        raise TimeoutError("Registration timeout")
                    else:
                        timeout_attempt += 1

            except Exception as ex:
                logging.error(f"Register on start failed: {ex}, another attempt in {wait_time}s.")
                time.sleep(wait_time)
                wait_time = min(wait_time * 2, 600)
                if cur_attempt > MAX_ATTEMPTS:
                    raise ConnectionError("Can't register to knowledge engine.")
                cur_attempt += 1

    def try_bg_register():
        try_register()
        ke_ki_client.start()

    if bg_mode:
        # background start

        import threading
        t = threading.Thread(target=try_bg_register)
        t.start()

    else:
        try_register()
        # ki.ke_client.register()
        ke_ki_client.start_sync()
    return ke_ki_client


def set_bg_ke_client():
    ki_client = _set_ke_client(bg_mode=True)
    while not ki_client.is_registered:
        # TODO: stop service id can't register
        logging.info(f"KE client is not registered, wait for all KI to be registered.")
        time.sleep(3)
    time.sleep(2)
    return ki_client


def set_sync_ke_client():
    _set_ke_client(bg_mode=False)
