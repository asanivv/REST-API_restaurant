import decimal

from pydantic import BaseModel, condecimal


class MenuBase(BaseModel):
    title: str
    description: str | None = None


class MenuCreate(MenuBase):
    pass


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


class SubMenuCreate(MenuBase):
    pass
    # menu_id: int


class Dish(MenuBase):
    id: int
    price: condecimal(decimal_places=2)

    class Config:
        from_attributes = True


class DishCreate(MenuBase):
    price: decimal.Decimal
