from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, condecimal
from sqlalchemy import Numeric


class MenuBase(BaseModel):
    title: str
    description: str | None = None


class Menu(MenuBase):
    id: int
    submenus_count: int
    dishes_count: int

    class Config:
        from_attributes = True


class SubMenu(MenuBase):
    id: int
    dishes_count: int

    class Config:
        from_attributes = True


class Dish(MenuBase):
    id: int
    price: condecimal(decimal_places=2)

    class Config:
        from_attributes = True

