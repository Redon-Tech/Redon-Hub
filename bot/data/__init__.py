from .. import config

if config.Data.Database == "changelater":
    pass
else:
    from prisma import Prisma
    from .prisma import *

    database = Prisma()
