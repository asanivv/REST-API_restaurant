from fastapi import FastAPI

from restaurant.menu import models
from restaurant.menu.database import engine
from restaurant.menu.routers import menu_router


models.Base.metadata.create_all(bind=engine)


app = FastAPI()

app.include_router(
    menu_router,
    prefix='/api/v1/menus'
)



