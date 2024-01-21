from sqlalchemy import select, func, and_
from sqlalchemy.orm import Session

from restaurant.menu import models


def get_submenus(db: Session, menu_id):
    # menu_id: UUID):
    submenus = db.query(models.SubMenu.id,
                        models.SubMenu.title,
                        models.SubMenu.description,
                        (
                            select(func.count(models.Dish.id))
                            .where(models.SubMenu.id == models.Dish.submenu_id)
                            .scalar_subquery().label('dishes_count')
                        )
                        ).filter(models.SubMenu.menu_id == menu_id)
    return submenus.all()


def get_submenu_by_id(db: Session, menu_id, submenu_id):
    # menu_id: UUID):
    submenus = db.query(models.SubMenu.id,
                        models.SubMenu.title,
                        models.SubMenu.description,
                        (
                            select(func.count(models.Dish.id))
                            .where(models.SubMenu.id == models.Dish.submenu_id)
                            .scalar_subquery().label('dishes_count')
                        )
                        ).filter(and_(models.SubMenu.menu_id == menu_id, models.SubMenu.id == submenu_id))
    return submenus.first()


def get_menus(db: Session):
    menus = (db.query(
        models.Menu.id,
        models.Menu.title,
        models.Menu.description,
        func.count(models.SubMenu.id).label('submenus_count'),
        (
            select(func.count(models.Dish.id))
            .where(models.SubMenu.id == models.Dish.submenu_id)
            .scalar_subquery()
        ).label('dishes_count')
    ).join(models.SubMenu, isouter=True)
             .group_by(models.Menu.id, models.Menu.title, models.Menu.description, ))

    return menus.all()


def get_menu_by_id(db: Session, menu_id):
    menus = (db.query(
        models.Menu.id,
        models.Menu.title,
        models.Menu.description,
        func.count(models.SubMenu.id).label('submenus_count'),
        (
            select(func.count(models.Dish.id))
            .where(models.SubMenu.id == models.Dish.submenu_id)
            .scalar_subquery()
        ).label('dishes_count')
    ).filter(models.Menu.id == menu_id)
             .join(models.SubMenu, isouter=True)
             .group_by(models.Menu.id, models.Menu.title, models.Menu.description, ))

    return menus.first()


def get_dishes(db: Session, submenu_id: int, menu_id: int):
    dishes = (db.query(models.Dish).select_from(models.Dish).join(models.SubMenu).join(models.Menu).filter(
        and_(models.SubMenu.id == submenu_id, models.Menu.id == menu_id))
    )
    return dishes.all()


def get_dish_by_id(db: Session, submenu_id: int, menu_id: int, dish_id: int):
    dishes = (db.query(models.Dish).select_from(models.Dish).where(models.Dish.id == dish_id).join(models.SubMenu).join(models.Menu).filter(
        and_(models.SubMenu.id == submenu_id, models.Menu.id == menu_id))
    )
    return dishes.first()

# def add_menu(db: Session):
#     menu = models.Menu()
#     menu.name='menu' + str(datetime.now().timestamp())
#     db.add(menu)
#     db.commit()
#     print(menu.id)


# def create_menu(db: Session, name: schemas.MenuCreate):
#     db_menu = models.Menu(name=name)
#     db.add(db_menu)
#     db.commit()
#     db.refresh(db_menu)
#     return db_menu
