from fastapi import FastAPI

from menu.database import engine, Base
from menu.routers import menu_router

Base.metadata.create_all(bind=engine)


app = FastAPI()

app.include_router(
    menu_router,
    prefix='/api/v1/menus'
)



