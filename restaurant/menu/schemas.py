import decimal
from uuid import UUID

from pydantic import BaseModel, condecimal


class MenuBase(BaseModel):
    title: str
    description: str


class MenuCreate(MenuBase):
    submenus_count: int = 0
    dishes_count: int = 0


class Menu(MenuBase):
    id:  UUID
    submenus_count: int
    dishes_count: int

    class Config:
        from_attributes = True


class SubMenu(MenuBase):
    id: UUID
    dishes_count: int

    class Config:
        from_attributes = True


class SubMenuCreate(MenuBase):
    pass


class SubMenuUpdate(MenuBase):
    menu_id: UUID


class Dish(MenuBase):
    id: UUID
    price: condecimal(decimal_places=2)

    class Config:
        from_attributes = True


class DishCreate(MenuBase):
    price: decimal.Decimal


class DishUpdate(MenuBase):
    price: decimal.Decimal
