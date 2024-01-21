from fastapi import Depends, FastAPI
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session

from restaurant.menu import schemas, models, crud
from restaurant.menu.database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# @app.post("/menus/", response_model=schemas.Menu)
# def create_user(menu: schemas.MenuCreate, db: Session = Depends(get_db)):
#     db_menu = crud.get_menu_by_name(db, name=menu.name)
#     if db_menu:
#         raise HTTPException(status_code=400, detail="Email already registered")
#     return crud.create_menu(db=db, name=menu)


@app.get("/api/v1/menus/", response_model=list[schemas.Menu])
def get_menus(db: Session = Depends(get_db)):
    menus = crud.get_menus(db=db)
    if menus is None:
        raise HTTPException(status_code=404, detail="menus not found")
    else:
        return menus


@app.get("/api/v1/menus/{menu_id}/", response_model=schemas.Menu)
def get_menu_by_id(menu_id, db: Session = Depends(get_db)):
    menu = crud.get_menu_by_id(db=db, menu_id=menu_id)
    if menu is None:
        raise HTTPException(status_code=404, detail="menu not found")
    else:
        return menu


@app.get("/api/v1/menus/{menu_id}/submenus/", response_model=list[schemas.SubMenu])
def get_submenus(menu_id, db: Session = Depends(get_db)):
    submenus = crud.get_submenus(db=db, menu_id=menu_id)
    return submenus


@app.get("/api/v1/menus/{menu_id}/submenus/{submenu_id}/", response_model=schemas.SubMenu)
def get_submenu_by_id(menu_id, submenu_id, db: Session = Depends(get_db)):
    submenus = crud.get_submenu_by_id(db=db, menu_id=menu_id, submenu_id=submenu_id)
    if submenus is None:
        raise HTTPException(status_code=404, detail="submenu not found")
    else:
        return submenus


@app.get("/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/", response_model=list[schemas.Dish])
def get_dishes(menu_id: int, submenu_id: int, db: Session = Depends(get_db)):
    dishes = crud.get_dishes(db=db, menu_id=menu_id, submenu_id=submenu_id)
    return dishes


@app.get("/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}/", response_model=schemas.Dish)
def get_dish_by_id(menu_id, submenu_id, dish_id, db: Session = Depends(get_db)):
    dish = crud.get_dish_by_id(db=db, menu_id=menu_id, submenu_id=submenu_id, dish_id=dish_id)
    if dish is None:
        raise HTTPException(status_code=404, detail="dish not found")
    else:
        return dish

#
# @app.post("/api/v1/menus/", response_model=List[schemas.Menu])
# def get_menus(db: Session = Depends(get_db)):
#     crud.add_menu(db)
#     # menus = crud.get_menu(db)
#     # return [{'id': row[0], 'count': row[1]} for row in menus] #[{'id':0, 'count':1}]
#
#
# @app.post("/api/v1/menus/{menu_id}/submenus/", response_model=List[schemas.Menu])
# def get_submenus(db: Session = Depends(get_db)):
#     pass
#
#
# @app.post("/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/", response_model=List[schemas.Menu])
# def get_submenus(db: Session = Depends(get_db)):
#     pass
#
#
# @app.patch("/api/v1/menus/{menu_id}/", response_model=List[schemas.Menu])
# def get_menus_by_id(db: Session = Depends(get_db)):
#     pass
#
#
# @app.patch("/api/v1/menus/{menu_id}/submenus/{submenu_id}/", response_model=List[schemas.Menu])
# def get_submenus(db: Session = Depends(get_db)):
#     pass
#
#
# @app.patch("/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}/", response_model=List[schemas.Menu])
# def get_submenus(db: Session = Depends(get_db)):
#     pass
#
#
# @app.delete("/api/v1/menus/{menu_id}/", response_model=List[schemas.Menu])
# def get_menus_by_id(db: Session = Depends(get_db)):
#     pass
#
#
# @app.delete("/api/v1/menus/{menu_id}/submenus/{submenu_id}/", response_model=List[schemas.Menu])
# def get_submenus(db: Session = Depends(get_db)):
#     pass
#
#
# @app.delete("/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}/", response_model=List[schemas.Menu])
# def get_submenus(db: Session = Depends(get_db)):
#     pass
