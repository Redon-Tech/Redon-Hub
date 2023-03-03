from prisma import Prisma
from .. import config, database as db
import json


class User:
    def __init__(self, dbResponse) -> None:
        self.id = dbResponse.id
        self.createdAt = dbResponse.createdAt
        self.discordId = dbResponse.discordId
        self.verifiedAt = dbResponse.verifiedAt
        self._purchases = dbResponse.purchases

    def __repr__(self) -> str:
        return f"<User id={self.id} discordId={self.discordId}>"

    def dict(self) -> dict:
        return {
            "id": self.id,
            "createdAt": self.createdAt,
            "discordId": self.discordId,
            "verifiedAt": self.verifiedAt,
            "purchases": self.purchases,
        }

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

        await db.user.update(
            where={"id": self.id},
            data={
                "discordId": self.discordId,
                "verifiedAt": self.verifiedAt,
                "purchases": self._purchases,
            },
        )


async def get_user(id: int) -> User:
    user = await db.user.find_unique(
        where={"id": id},
    )
    return User(user)


async def get_user_by_discord_id(discord_id: int) -> User:
    user = await db.user.find_first(
        where={"discordId": discord_id},
    )
    return User(user)


async def get_users() -> list:
    users = await db.user.find_many()
    return [User(user) for user in users]


async def create_user(id: int) -> User:
    user = await db.user.create(
        data={
            "id": id,
            "purchases": json.dumps([]),
        },
    )
    return User(user)
