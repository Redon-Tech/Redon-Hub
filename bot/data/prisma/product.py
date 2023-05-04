from prisma import Prisma
from .. import config, database as db
from typing import Optional
import json


class Product:
    def __init__(self, dbResponse) -> None:
        self.id = dbResponse.id
        self.createdAt = dbResponse.createdAt
        self.name = dbResponse.name
        self.description = dbResponse.description
        self.imageId = dbResponse.imageId
        self.price = dbResponse.price
        self.productId = dbResponse.productId
        self.stock = dbResponse.stock
        self._attachments = dbResponse.attachments
        self._tags = dbResponse.tags
        self.purchases = dbResponse.purchases
        self.owners = dbResponse.owners

    def __repr__(self) -> str:
        return f"<Product id={self.id} name={self.name}>"

    def dict(self) -> dict:
        return {
            "id": self.id,
            "createdAt": self.createdAt,
            "name": self.name,
            "description": self.description,
            "imageId": self.imageId,
            "price": self.price,
            "productId": self.productId,
            "stock": self.stock,
            "attachments": self.attachments,
            "tags": self.tags,
            "purchases": self.purchases,
            "owners": self.owners,
        }

    @property
    def attachments(self) -> list:
        if type(self._attachments) == list:
            return self._attachments

        return json.loads(self._attachments)

    @attachments.setter
    def attachments(self, value: list) -> None:
        if config.Data.Database == "mysql":
            self._attachments = json.dumps(value)
        else:
            self._attachments = value

    @property
    def tags(self) -> list:
        if type(self._tags) == list:
            return self._tags

        return json.loads(self._tags)

    @tags.setter
    def tags(self, value: list) -> None:
        if config.Data.Database == "mysql":
            self._tags = json.dumps(value)
        else:
            self._tags = value

    async def push(self) -> None:
        if config.Data.Database == "mysql":
            self._attachments = json.dumps(self.attachments)
            self._tags = json.dumps(self.tags)

        await db.product.update(
            where={"id": self.id},
            data={
                "name": self.name,
                "description": self.description,
                "imageId": self.imageId,
                "price": self.price,
                "productId": self.productId,
                "stock": self.stock,
                "attachments": self._attachments,
                "tags": self._tags,
                "purchases": self.purchases,
                "owners": self.owners,
            },
        )


async def get_product(id: int) -> Product:
    product = await db.product.find_unique(
        where={"id": id},
    )
    return Product(product)


async def get_product_by_name(name: str) -> Product:
    product = await db.product.find_unique(
        where={"name": name},
    )
    return Product(product)


async def get_products() -> list:
    products = await db.product.find_many()
    return [Product(product) for product in products]


async def create_product(
    name: str,
    description: Optional[str],
    imageId: Optional[str],
    price: int,
    productId: int,
    attachments: Optional[list],
    tags: Optional[list],
) -> Product:
    if config.Data.Database == "mysql":
        attachments = json.dumps(attachments)
        tags = json.dumps(tags)

    prod = await db.product.create(
        data={
            "name": name,
            "description": description or "",
            "imageId": imageId or "",
            "price": price,
            "productId": productId,
            "attachments": attachments,
            "tags": tags,
        },
    )
    product = Product(prod)

    return product


async def delete_product(id: int) -> None:
    await db.product.delete(
        where={"id": id},
    )
