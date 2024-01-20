from pydantic import BaseModel


class MenuBase(BaseModel):
    name: str


class Menu(MenuBase):
    id: int

    class Config:
        from_attributes = True


class MenuCreate(MenuBase):
    name: str


class SubMenuBase(BaseModel):
    name: str


class SubMenu(SubMenuBase):
    id: int
    menu_id: int

    class Config:
        from_attributes = True

class DishesCount(BaseModel):
    id: int
    count: int
