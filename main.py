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


@app.post("/api/v1/menus/", response_model=schemas.Menu)
def create_menu(menu: schemas.MenuCreate, db: Session = Depends(get_db)):
    db_menu = crud.get_menu_by_title(db=db, title=menu.title)
    if db_menu:
        raise HTTPException(status_code=400, detail="Menu already registered")
    return crud.create_menu(db=db, menu=menu)


@app.post("/api/v1/menus/{menu_id}/submenus/", response_model=schemas.SubMenu)
def create_submenu(menu_id: int, submenu: schemas.SubMenuCreate, db: Session = Depends(get_db)):
    db_menu = crud.check_menu_by_id(db=db, menu_id=menu_id)
    if not db_menu:
        raise HTTPException(status_code=400, detail="Menu ID not registered")
    db_submenu = crud.get_submenu_by_title(db=db, title=submenu.title)
    if db_submenu:
        raise HTTPException(status_code=400, detail="Submenu already registered")
    return crud.create_submenu(db=db, menu_id=menu_id, submenu=submenu)


@app.post("/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/", response_model=schemas.Dish)
def create_dish(menu_id: int, submenu_id:int, dish: schemas.DishCreate, db: Session = Depends(get_db)):
    db_menu = crud.check_menu_by_id(db=db, menu_id=menu_id)
    if not db_menu:
        raise HTTPException(status_code=400, detail="Menu ID not registered")
    db_submenu = crud.check_submenu_by_id(db=db, submenu_id=submenu_id)
    if not db_submenu:
        raise HTTPException(status_code=400, detail="Submenu ID not registered")
    return crud.create_dish(db=db, menu_id=menu_id, submenu_id=submenu_id, dish=dish)

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
