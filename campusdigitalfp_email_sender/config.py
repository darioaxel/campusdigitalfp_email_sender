import os
import configparser
from typing import Dict, Any

DEFAULT_CONFIG_FILE = "campusdigitalfp_email_sender.cfg"


def load_config(cfg_file: str = DEFAULT_CONFIG_FILE) -> Dict[str, Any]:
    """Devuelve dict con valores del .cfg o vacío si no existe."""
    cfg = configparser.ConfigParser()
    if os.path.isfile(cfg_file):
        cfg.read(cfg_file)
    return {
        "smtp_host": cfg.get("smtp", "host", fallback=None),
        "smtp_port": cfg.getint("smtp", "port", fallback=None),
        "smtp_user": cfg.get("smtp", "user", fallback=None),
        "smtp_password": cfg.get("smtp", "password", fallback=None),
        "from_name": cfg.get("defaults", "from_name", fallback=None),
    }