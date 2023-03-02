from .. import config

if config.Data.Database == "changelater":
    pass
else:
    from prisma import Prisma

    database = Prisma()

    from .prisma import *
