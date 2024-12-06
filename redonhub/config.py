"""
    File: /bot/config.py
    Usage: Used to load the config file and make it accessible to other files.
    Credit: 
        - Inspired by https://github.com/python-discord/bot/tree/main/bot/constants.py
"""

from pathlib import Path
from logging import getLogger
import json
import os

_log = getLogger(__name__)
parent = os.path.dirname(os.path.abspath(__file__)).replace("redonhub", "")

# with open("example.config.json", encoding="UTF-8") as f:
#     _CONFIG = json.load(f)
with open(parent + "example.config.json", encoding="UTF-8") as f:
    _CONFIG = json.load(f)


def _recursive_update(d, u):
    for k, v in u.items():
        if isinstance(v, dict):
            d[k] = _recursive_update(d.get(k, {}), v)
        else:
            d[k] = v
    return d


if Path("config.json").exists():
    _log.info("Config: Loading user config")
    with open("config.json", encoding="UTF-8") as f:
        USER_CONFIG = json.load(f)
    _CONFIG = _recursive_update(_CONFIG, USER_CONFIG)


class JSONGetter(type):
    def __getattr__(cls, name):
        try:
            if cls.subsection is not None:
                return _CONFIG[cls.section][cls.subsection][name]
            return _CONFIG[cls.section][name]
        except KeyError as e:
            dotted_path = ".".join(
                (cls.section, cls.subsection, name)
                if cls.subsection is not None
                else (cls.section, name)
            )
            _log.error(f"Tried to access non-existent config key: {dotted_path}")
            raise AttributeError(repr(name)) from e


class Bot(metaclass=JSONGetter):
    section = "Bot"
    subsection = None

    Prefix: str
    Guilds: list
    Owners: list


class Activity(metaclass=JSONGetter):
    section = "Bot"
    subsection = "Activity"

    Presence: str
    Status: str


class Logging(metaclass=JSONGetter):
    section = "Logging"
    subsection = None

    PurchasesChannel: int
    GlobalCustomerRole: int


class Data(metaclass=JSONGetter):
    section = "Data"
    subsection = None

    Database: str


class API(metaclass=JSONGetter):
    section = "API"
    subsection = None

    IP: str
    Port: int
    Key: str
