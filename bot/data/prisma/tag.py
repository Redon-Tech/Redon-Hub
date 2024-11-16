from prisma import Prisma
from prisma.models import Tag as TagModel
from .. import config, database as db
import json


class Tag:
    def __init__(self, dbResponse: TagModel) -> None:
        self.id = dbResponse.id
        self.createdAt = dbResponse.createdAt
        self.name = dbResponse.name
        self._color = dbResponse.color
        self._textColor = dbResponse.textColor

    def __repr__(self) -> str:
        return f"<Tag id={self.id} name={self.name}>"

    def dict(self) -> dict:
        return {
            "id": self.id,
            "createdAt": self.createdAt,
            "name": self.name,
            "color": self.color,
            "textColor": self.textColor,
        }

    @property
    def color(self) -> list:
        if isinstance(self._color, list):
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
        if isinstance(self._textColor, list):
            return self._textColor

        return json.loads(self._textColor)

    @textColor.setter
    def textColor(self, value: list) -> None:
        if config.Data.Database == "mysql":
            self._textColor = json.dumps(value)
        else:
            self._textColor = value

    async def push(self) -> None:
        if config.Data.Database == "mysql":
            self._color = json.dumps(self._color)
            self._textColor = json.dumps(self._textColor)

        await db.tag.update(
            where={"id": self.id},
            data={
                "name": self.name,
                "color": self._color,
                "textColor": self._textColor,
            },  # type: ignore
        )


async def get_tag(id: int) -> Tag:
    tag = await db.tag.find_unique_or_raise(
        where={"id": id},
    )
    return Tag(tag)


async def get_tag_by_name(name: str) -> Tag:
    tag = await db.tag.find_unique_or_raise(
        where={"name": name},
    )
    return Tag(tag)


async def get_tags() -> list[Tag]:
    tags = await db.tag.find_many()
    return [Tag(tag) for tag in tags]


async def create_tag(name: str, color: list, textColor: list) -> Tag:
    _color = None
    _textColor = None
    if config.Data.Database == "mysql":
        _color = json.dumps(color)
        _textColor = json.dumps(textColor)
    else:
        _color = color
        _textColor = textColor

    tag = await db.tag.create(
        data={
            "name": name,
            "color": _color,
            "textColor": _textColor,
        },  # type: ignore
    )
    return Tag(tag)


async def delete_tag(id: int) -> None:
    await db.tag.delete(
        where={"id": id},
    )
