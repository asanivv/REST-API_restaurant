from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select, func, and_
from sqlalchemy.orm import Session

from restaurant.menu import models, schemas


def raise_if_not_exist(item: object, message: str):
    if not item:
        raise HTTPException(status_code=404, detail=message)


def get_submenus(db: Session, menu_id: UUID):
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


def get_submenu_by_id(db: Session, menu_id: UUID, submenu_id: UUID):
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


def create_submenu(db: Session, menu_id: UUID, submenu: schemas.SubMenuCreate):
    db_submenu = models.SubMenu(menu_id=menu_id, title=submenu.title, description=submenu.description)
    db.add(db_submenu)
    db.commit()
    db.refresh(db_submenu)
    db_submenu.dishes_count = 0
    return db_submenu


def get_menus(db: Session):
    menus = (db.query(
        models.Menu.id,
        models.Menu.title,
        models.Menu.description,
        func.count(models.SubMenu.id).label('submenus_count'),
        (
            select(func.coalesce(func.count(models.Dish.id), 0))
            .where(models.SubMenu.id == models.Dish.submenu_id)
            .scalar_subquery()
        ).label('dishes_count')
    ).join(models.SubMenu, isouter=True)
             .group_by(models.Menu.id, models.Menu.title, models.Menu.description, 'dishes_count'))

    return menus.all()


def get_menu_by_id(db: Session, menu_id: UUID):
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
             .group_by(models.Menu.id, models.Menu.title, models.Menu.description, 'dishes_count'))

    return menus.first()


def get_menu_by_title(db: Session, title: str):
    return db.query(models.Menu).filter(models.Menu.title == title).first()


def check_menu_by_id(db: Session, menu_id: UUID):
    return db.query(models.Menu).filter(models.Menu.id == menu_id).first()


def check_submenu_by_id(db: Session, submenu_id: UUID):
    return db.query(models.SubMenu).filter(models.SubMenu.id == submenu_id).first()


def create_menu(db: Session, menu: schemas.MenuCreate):
    db_menu = models.Menu(title=menu.title, description=menu.description)
    db.add(db_menu)
    db.commit()
    db.refresh(db_menu)
    db_menu.submenus_count = 0
    db_menu.dishes_count = 0
    return db_menu


def get_dishes(db: Session, submenu_id: UUID, menu_id: UUID):
    dishes = (db.query(models.Dish).select_from(models.Dish).join(models.SubMenu).join(models.Menu).filter(
        and_(models.SubMenu.id == submenu_id, models.Menu.id == menu_id))
    )
    return dishes.all()


def get_dish_by_id(db: Session, submenu_id: UUID, menu_id: UUID, dish_id: UUID):
    dishes = (db.query(models.Dish).select_from(models.Dish).where(models.Dish.id == dish_id).join(models.SubMenu).join(
        models.Menu).filter(
        and_(models.SubMenu.id == submenu_id, models.Menu.id == menu_id))
    )
    return dishes.first()


def create_dish(db: Session, menu_id: UUID, submenu_id: UUID, dish: schemas.DishCreate):
    db_dish = models.Dish(submenu_id=submenu_id, title=dish.title, description=dish.description, price=dish.price)
    db.add(db_dish)
    db.commit()
    db.refresh(db_dish)
    return get_dish_by_id(db=db, menu_id=menu_id, submenu_id=submenu_id, dish_id=db_dish.id)


def delete_menu_by_id(db: Session, menu_id: UUID):
    menu = db.get(models.Menu, menu_id)
    raise_if_not_exist(menu, "Menu not found")
    db.delete(menu)
    db.commit()
    return {"status": True, "message": "The menu has been deleted"}


def delete_submenu_by_id(db: Session, menu_id: UUID, submenu_id: UUID):
    menu = db.get(models.Menu, menu_id)
    raise_if_not_exist(menu, "Menu not found")
    submenu = db.get(models.SubMenu, submenu_id)
    db.delete(submenu)
    db.commit()
    return {"status": True, "message": "The submenu has been deleted"}


def delete_dish_by_id(db: Session, menu_id: UUID, submenu_id: UUID, dish_id: UUID):
    menu = db.get(models.Menu, menu_id)
    raise_if_not_exist(menu, "Menu not found")
    submenu = db.get(models.SubMenu, submenu_id)
    raise_if_not_exist(submenu, "Submenu not found")
    dish = db.get(models.Dish, dish_id)
    raise_if_not_exist(dish, "Dish not found")
    db.delete(dish)
    db.commit()
    return {"status": True, "message": "The dish has been deleted"}


def update_menu(db: Session, menu_id: UUID, menu: schemas.MenuBase):
    db_menu = db.get(models.Menu, menu_id)
    raise_if_not_exist(menu, "Menu not found")
    menu_data = menu.model_dump(exclude_unset=True)
    for key, value in menu_data.items():
        setattr(db_menu, key, value)
    db.add(db_menu)
    db.commit()
    db.refresh(db_menu)
    return get_menu_by_id(db, db_menu.id)


def update_submenu(db: Session, menu_id: UUID, submenu_id: UUID, submenu: schemas.MenuBase):
    db_menu = db.get(models.Menu, menu_id)
    raise_if_not_exist(db_menu, "Menu not found")
    db_submenu = db.get(models.SubMenu, submenu_id)
    raise_if_not_exist(db_submenu, "Submenu not found")
    submenu_data = submenu.model_dump(exclude_unset=True)
    for key, value in submenu_data.items():
        setattr(db_submenu, key, value)
    db.add(db_submenu)
    db.commit()
    db.refresh(db_submenu)
    return get_submenu_by_id(db=db, menu_id=menu_id, submenu_id=db_submenu.id)


def update_dish(db: Session, menu_id: UUID, submenu_id: UUID, dish_id: UUID, dish: schemas.DishUpdate):
    db_menu = db.get(models.Menu, menu_id)
    raise_if_not_exist(db_menu, "Menu not found")
    db_submenu = db.get(models.SubMenu, submenu_id)
    raise_if_not_exist(db_submenu, "Submenu not found")
    db_dish = db.get(models.Dish, dish_id)
    raise_if_not_exist(db_dish, "Submenu not found")
    dish_data = dish.model_dump(exclude_unset=True)
    for key, value in dish_data.items():
        setattr(db_dish, key, value)
    db.add(db_dish)
    db.commit()
    db.refresh(db_dish)
    return get_dish_by_id(db=db, menu_id=menu_id, submenu_id=submenu_id, dish_id=db_dish.id)
