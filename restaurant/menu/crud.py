from sqlalchemy import select, func, and_
from sqlalchemy.orm import Session

from restaurant.menu import models, schemas


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


def get_submenu_by_title(db: Session, title: str):
    return db.query(models.SubMenu).filter(models.SubMenu.title == title).first()


def create_submenu(db: Session, menu_id: int, submenu: schemas.SubMenuCreate):
    db_submenu = models.SubMenu(menu_id=menu_id, title=submenu.title, description=submenu.description)
    db.add(db_submenu)
    db.commit()
    db.refresh(db_submenu)
    return get_submenu_by_id(db=db, menu_id=menu_id, submenu_id=db_submenu.id)


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


def get_menu_by_title(db: Session, title: str):
    return db.query(models.Menu).filter(models.Menu.title == title).first()


def check_menu_by_id(db: Session, menu_id: int):
    return db.query(models.Menu).filter(models.Menu.id == menu_id).first()


def check_submenu_by_id(db: Session, submenu_id: int):
    return db.query(models.SubMenu).filter(models.SubMenu.id == submenu_id).first()


def create_menu(db: Session, menu: schemas.MenuCreate):
    db_menu = models.Menu(title=menu.title, description=menu.description)
    db.add(db_menu)
    db.commit()
    db.refresh(db_menu)
    return get_menu_by_id(db=db, menu_id=db_menu.id)


def get_dishes(db: Session, submenu_id: int, menu_id: int):
    dishes = (db.query(models.Dish).select_from(models.Dish).join(models.SubMenu).join(models.Menu).filter(
        and_(models.SubMenu.id == submenu_id, models.Menu.id == menu_id))
    )
    return dishes.all()


def get_dish_by_id(db: Session, submenu_id: int, menu_id: int, dish_id: int):
    dishes = (db.query(models.Dish).select_from(models.Dish).where(models.Dish.id == dish_id).join(models.SubMenu).join(
        models.Menu).filter(
        and_(models.SubMenu.id == submenu_id, models.Menu.id == menu_id))
    )
    return dishes.first()


def create_dish(db: Session, menu_id: int, submenu_id: int, dish: schemas.DishCreate):
    db_dish = models.Dish(submenu_id=submenu_id, title=dish.title, description=dish.description, price=dish.price)
    db.add(db_dish)
    db.commit()
    db.refresh(db_dish)
    return get_dish_by_id(db=db, menu_id=menu_id,submenu_id=submenu_id, dish_id=db_dish.id)


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
