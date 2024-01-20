from typing import List

from fastapi import Depends, FastAPI
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


@app.get("/api/v1/menus", response_model=List[schemas.DishesCount])
def get_menus(db: Session = Depends(get_db)):
    crud.add_menu(db)
    # menus = crud.get_menu(db)
    # return [{'id': row[0], 'count': row[1]} for row in menus] #[{'id':0, 'count':1}]


@app.get("/api/v1/menus/{menu_id}", response_model=List[schemas.DishesCount])
def get_menus_by_id(db: Session = Depends(get_db)):
    pass


@app.get("/api/v1/menus/{menu_id}/submenus", response_model=List[schemas.DishesCount])
def get_submenus(db: Session = Depends(get_db)):
    pass


@app.get("/api/v1/menus/{menu_id}/submenus/{submenu_id}", response_model=List[schemas.DishesCount])
def get_submenus(db: Session = Depends(get_db)):
    pass


@app.get("/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes", response_model=List[schemas.DishesCount])
def get_submenus(db: Session = Depends(get_db)):
    pass


@app.get("/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}", response_model=List[schemas.DishesCount])
def get_submenus(db: Session = Depends(get_db)):
    pass


@app.post("/api/v1/menus", response_model=List[schemas.DishesCount])
def get_menus(db: Session = Depends(get_db)):
    crud.add_menu(db)
    # menus = crud.get_menu(db)
    # return [{'id': row[0], 'count': row[1]} for row in menus] #[{'id':0, 'count':1}]


@app.post("/api/v1/menus/{menu_id}/submenus", response_model=List[schemas.DishesCount])
def get_submenus(db: Session = Depends(get_db)):
    pass


@app.post("/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes", response_model=List[schemas.DishesCount])
def get_submenus(db: Session = Depends(get_db)):
    pass


@app.patch("/api/v1/menus/{menu_id}", response_model=List[schemas.DishesCount])
def get_menus_by_id(db: Session = Depends(get_db)):
    pass


@app.patch("/api/v1/menus/{menu_id}/submenus/{submenu_id}", response_model=List[schemas.DishesCount])
def get_submenus(db: Session = Depends(get_db)):
    pass


@app.patch("/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}", response_model=List[schemas.DishesCount])
def get_submenus(db: Session = Depends(get_db)):
    pass

@app.delete("/api/v1/menus/{menu_id}", response_model=List[schemas.DishesCount])
def get_menus_by_id(db: Session = Depends(get_db)):
    pass


@app.delete("/api/v1/menus/{menu_id}/submenus/{submenu_id}", response_model=List[schemas.DishesCount])
def get_submenus(db: Session = Depends(get_db)):
    pass


@app.delete("/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}", response_model=List[schemas.DishesCount])
def get_submenus(db: Session = Depends(get_db)):
    pass

# @app.get("/users/{user_id}", response_model=schemas.User)
# def read_user(user_id: int, db: Session = Depends(get_db)):
#     db_user = crud.get_user(db, user_id=user_id)
#     if db_user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     return db_user


# @app.post("/users/{user_id}/items/", response_model=schemas.Item)
# def create_item_for_user(
#     user_id: int, item: schemas.ItemCreate, db: Session = Depends(get_db)
# ):
#     return crud.create_user_item(db=db, item=item, user_id=user_id)
#
#
# @app.get("/items/", response_model=list[schemas.Item])
# def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     items = crud.get_items(db, skip=skip, limit=limit)
#     return items