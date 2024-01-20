from sqlalchemy import select, func
from sqlalchemy.orm import Session
from datetime import datetime
from restaurant.menu import models


# def get_menu(db: Session, menu_id: int):
#     return db.query(models.Menu).filter(models.Menu.id == menu_id).first()


# def get_menu_by_name(db: Session, name: str):
#     return db.query(models.Menu).filter(models.Menu.name == name).first()


def get_menu(db: Session):
    inner_stmt = db.query(models.Dish.sub_menu_id, func.count(models.Dish.id).label('count_dishes')).group_by(
        models.Dish.sub_menu_id)
                  #execute(select(models.Dish.sub_menu_id, func.count(models.Dish.id)).group_by(models.Dish.sub_menu_id)))


    dishes = select(models.Dish.sub_menu_id.label('sub_menu_id'), func.count(models.Dish.id).label('count_dishes')).group_by(
        models.Dish.sub_menu_id).alias('dishes')

    #.where(models.SubMenu..id < 7).order_by(User.id)
    query = (db.query(models.SubMenu.id,
                      models.SubMenu.name,
                      dishes.c.count_dishes)
             .join(dishes, dishes.c.sub_menu_id == models.SubMenu.id, isouter=True).order_by(models.SubMenu.id).all())
    print(query)

    # query = db.query(models.Menu).all()
    # for item in query:
    #     sub_menu = db.query(models.SubMenu).filter_by(menu_id=item.id).count()
    #     print(sub_menu)
    return inner_stmt


def add_menu(db: Session):
    menu = models.Menu()
    menu.name='menu' + str(datetime.now().timestamp())
    db.add(menu)
    db.commit()
    print(menu.id)



# def create_menu(db: Session, name: schemas.MenuCreate):
#     db_menu = models.Menu(name=name)
#     db.add(db_menu)
#     db.commit()
#     db.refresh(db_menu)
#     return db_menu
