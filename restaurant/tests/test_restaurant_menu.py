from .test_dishes import TestDishes
from .test_menus import TestMenus
from .test_submenus import TestSubMenus


class TestRestaurantMenu(TestDishes, TestSubMenus, TestMenus):
    pass