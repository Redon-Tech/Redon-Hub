from prisma import Prisma
from .. import config
import json


class Tag:
    def __init__(self, db: Prisma, dbResponse) -> None:
        self.db: Prisma = db
        self.id = dbResponse.id
        self.createdAt = dbResponse.createdAt
        self.name = dbResponse.name
        self._color = dbResponse.color
        self._textColor = dbResponse.textColor

    def __repr__(self) -> str:
        return f"<Tag id={self.id} name={self.name}>"

    @property
    def color(self) -> list:
        if type(self._color) == list:
            return self._color

        return json.loads(self._color)

    @color.setter
    def color(self, value: list) -> None:
        if config.Data.Database == "mysql":
            self._color = json.dumps(value)
        else:
            self._color = value

    @property
    def textColor(self) -> list:
        if type(self._textColor) == list:
            return self._textColor

        return json.loads(self._textColor)

    @textColor.setter
    def textColor(self, value: list) -> None:
        if config.Data.Database == "mysql":
            self._textColor = json.dumps(value)
        else:
            self._textColor = value


async def get_tag(db: Prisma, id: int) -> Tag:
    tag = await db.tag.find_unique(
        where={"id": id},
    )
    return Tag(db, tag)


async def get_tags(db: Prisma) -> list[Tag]:
    tags = await db.tag.find_many()
    return [Tag(db, tag) for tag in tags]


async def create_tag(db: Prisma, name: str, color: list, textColor: list) -> Tag:
    tag = await db.tag.create(
        data={
            "name": name,
            "color": color,
            "textColor": textColor,
        },
    )
    return Tag(db, tag)
