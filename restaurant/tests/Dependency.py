from fastapi.testclient import TestClient
from sqlalchemy import URL
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database

from main import app
from menu.database import url_object, Base
from menu.routers import get_db, menu_router

test_url = URL.create(
    "postgresql",
    username=url_object.username,
    password=url_object.password,
    host=url_object.host,
    database='tests',
    port=url_object.port,
)

engine = create_engine(test_url)

if not database_exists(engine.url):
    create_database(engine.url)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.include_router(menu_router)
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)



