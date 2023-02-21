from prisma import Prisma
from .. import config
import json


class User:
    def __init__(self, db: Prisma, dbResponse) -> None:
        self.db: Prisma = db
        self.id = dbResponse.id
        self.createdAt = dbResponse.createdAt
        self.discordId = dbResponse.discordId
        self.verifiedAt = dbResponse.verifiedAt
        self._purchases = dbResponse.purchases

    def __repr__(self) -> str:
        return f"<User id={self.id} discordId={self.discordId}>"

    @property
    def purchases(self) -> list:
        if type(self._purchases) == list:
            return self._purchases

        return json.loads(self._purchases)

    @purchases.setter
    def purchases(self, value: list) -> None:
        if config.Data.Database == "mysql":
            self._purchases = json.dumps(value)
        else:
            self._purchases = value

    async def push(self) -> None:
        if config.Data.Database == "mysql":
            self._purchases = json.dumps(self.purchases)

        await self.db.user.update(
            where={"id": self.id},
            data={
                "discordId": self.discordId,
                "verifiedAt": self.verifiedAt,
                "purchases": self._purchases,
            },
        )


async def get_user(db: Prisma, id: int) -> User:
    user = await db.user.find_unique(
        where={"id": id},
    )
    return User(db, user)


async def get_user_by_discord_id(db: Prisma, discord_id: int) -> User:
    user = await db.user.find_first(
        where={"discordId": discord_id},
    )
    return User(db, user)


async def get_users(db: Prisma) -> list:
    users = await db.user.find_many()
    return [User(db, user) for user in users]


async def create_user(db: Prisma, id: int) -> User:
    user = await db.user.create(
        data={
            "id": id,
            "purchases": json.dumps([]),
        },
    )
    return User(db, user)
