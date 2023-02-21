from prisma import Prisma
from .. import config
from typing import Optional
import json


class Product:
    def __init__(self, db: Prisma, dbResponse) -> None:
        self.db: Prisma = db
        self.id = dbResponse.id
        self.createdAt = dbResponse.createdAt
        self.name = dbResponse.name
        self.description = dbResponse.description
        self.price = dbResponse.price
        self.productId = dbResponse.productId
        self._attachments = dbResponse.attachments
        self._tags = dbResponse.tags
        self.purchases = dbResponse.purchases
        self.owners = dbResponse.owners

    def __repr__(self) -> str:
        return f"<Product id={self.id} name={self.name}>"

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


async def get_product(db: Prisma, id: int) -> Product:
    product = await db.product.find_unique(
        where={"id": id},
    )
    return Product(db, product)


async def get_products(db: Prisma) -> list:
    products = await db.product.find_many()
    return [Product(db, product) for product in products]


async def create_product(
    db: Prisma,
    name: str,
    description: Optional[str],
    price: Optional[int],
    productId: Optional[int],
) -> Product:
    prod = await db.product.create(
        data={
            "name": name,
        },
    )
    product = Product(db, prod)

    if description:
        product.description = description
    if price:
        product.price = price
    if productId:
        product.productId = productId

    return product
