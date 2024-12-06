from .user import *
from .product import *
from .tag import *
from .. import database as db


def is_connected():
    return db.is_connected()
