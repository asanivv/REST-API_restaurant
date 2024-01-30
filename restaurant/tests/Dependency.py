import decimal
import uuid

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy import delete, URL
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database

from ..main import app
from ..menu import models
from ..menu.crud import is_valid_uuid
from ..menu.database import url_object, Base
from ..menu.routers import get_db, menu_router

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

menu_test = {
    "title": "menu1",
    "description": "menu1",
    "id": "2e9b4f3a-b9d4-4168-8697-1f51de26dd1e",
    "submenus_count": 0,
    "dishes_count": 0
}

submenu_test = {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "title": "submenu1",
    "description": "submenu1",
    "dishes_count": 0
}

dish_test = {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "title": "dish",
    "description": "about dish",
    "price": "115.455"
}

'''
 START MENU TESTS
'''



'''
 START SUBMENU TESTS
'''




'''
 START DISH TESTS
'''


def test_read_empty_dishes():
    with Session(engine) as session:
        session.execute(delete(models.Dish))
        session.commit()
    response = client.get(f"/{menu_test['id']}/submenus/{submenu_test['id']}/dishes/")
    assert response.status_code == 200
    assert response.json() == []


def test_create_dish():
    response = client.post(
        f"/{menu_test['id']}/submenus/{submenu_test['id']}/dishes/",
        json={
            'id': dish_test['id'],
            "title": dish_test['title'],
            "description": dish_test['description'],
            "price": dish_test["price"],
        },
    )
    data = response.json()
    assert response.status_code == 201
    assert data["title"] == dish_test['title']
    assert data["description"] == dish_test['description']
    assert data["price"] == str(decimal.Decimal(dish_test["price"]).quantize(decimal.Decimal('0.00')))
    assert data["id"] is not None
    assert is_valid_uuid(data["id"]) is True


def test_read_dishes():
    response = client.get(f"/{menu_test['id']}/submenus/{submenu_test['id']}/dishes/")
    assert response.status_code == 200
    data = response.json()
    assert type(data) is list
    assert type(data[0]) is dict
    for submenu in data:
        for key in submenu.keys():
            assert key in ('id', 'title', 'description', 'price')
    assert {
               'id': dish_test['id'],
               "title": dish_test['title'],
               "description": dish_test['description'],
               "price": str(decimal.Decimal(dish_test["price"]).quantize(decimal.Decimal('0.00'))),
           } in data


def test_read_dish_by_id():
    response = client.get(f"/{menu_test['id']}/submenus/{submenu_test['id']}/dishes/{dish_test['id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == dish_test['id']
    assert data["title"] == dish_test['title']
    assert data["description"] == dish_test['description']
    assert data["price"] == str(decimal.Decimal(dish_test["price"]).quantize(decimal.Decimal('0.00')))


def test_create_dish_wrong_menu_id():
    with pytest.raises(HTTPException) as err:
        client.post(f"/111/submenus/{submenu_test['id']}/dishes/",
                    json={
                        'id': dish_test['id'],
                        "title": dish_test['title'],
                        "description": dish_test['description'],
                        "price": dish_test["price"],
                    },
                    )
    assert err.value.status_code == 422
    assert err.value.detail == "Wrong id type"


def test_create_dish_wrong_submenu_id():
    with pytest.raises(HTTPException) as err:
        client.post(f"/{menu_test['id']}/submenus/1wwew231/dishes/",
                    json={
                        'id': dish_test['id'],
                        "title": dish_test['title'],
                        "description": dish_test['description'],
                        "price": dish_test["price"],
                    },
                    )
    assert err.value.status_code == 422
    assert err.value.detail == "Wrong id type"


def test_dish_menu_id_is_not_registered():
    with pytest.raises(HTTPException) as err:
        client.post(f"/{uuid.uuid4()}/submenus/{submenu_test['id']}/dishes/",
                    json={
                        'id': dish_test['id'],
                        "title": dish_test['title'],
                        "description": dish_test['description'],
                        "price": dish_test["price"],
                    },
                    )
    assert err.value.status_code == 400
    assert err.value.detail == "ID of Menu not registered"


def test_dish_submenu_id_is_not_registered():
    with pytest.raises(HTTPException) as err:
        client.post(f"/{menu_test['id']}/submenus/{uuid.uuid4()}/dishes/",
                    json={
                        'id': dish_test['id'],
                        "title": dish_test['title'],
                        "description": dish_test['description'],
                        "price": dish_test["price"],
                    },
                    )
    assert err.value.status_code == 400
    assert err.value.detail == "ID of Submenu not registered"


def test_dish_title_is_already_registered():
    with pytest.raises(HTTPException) as err:
        client.post(f"/{menu_test['id']}/submenus/{submenu_test['id']}/dishes/",
                    json={
                        'id': dish_test['id'],
                        "title": dish_test['title'],
                        "description": dish_test['description'],
                        "price": dish_test["price"],
                    },
                    )
    assert err.value.status_code == 500
    assert err.value.detail == "A duplicate record already exists"


def test_dish_id_not_found():
    with pytest.raises(HTTPException) as err:
        client.get(f"/{menu_test['id']}/submenus/{submenu_test['id']}/dishes/{uuid.uuid4()}")
    assert err.value.status_code == 404
    assert err.value.detail == "dish not found"


def test_delete_dish_by_wrong_id():
    with pytest.raises(HTTPException) as err:
        client.delete(f"/{menu_test['id']}/submenus/{submenu_test['id']}/dishes/1111")
    assert err.value.status_code == 422
    assert err.value.detail == "One or more wrong types id"


def test_update_dish():
    response = client.patch(f"/{menu_test['id']}/submenus/{submenu_test['id']}/dishes/{dish_test['id']}",
                            json={

                                'id': dish_test['id'],
                                "title": dish_test['title'],
                                "description": "this field has been changed",
                                "price": '7.777',
                            },
                            )
    assert response.status_code == 200
    data = response.json()
    assert data['description'] == "this field has been changed"
    assert data['price'] == "7.78"


def test_delete_dish_by_id():
    response = client.delete(f"/{menu_test['id']}/submenus/{submenu_test['id']}/dishes/{dish_test['id']}")
    assert response.status_code == 200
    assert response.json() == {"status": True, "message": "The dish has been deleted"}
    response = client.get(f"/{menu_test['id']}")
    assert response.status_code == 200
    response = client.get(f"/{menu_test['id']}/submenus/{submenu_test['id']}/")
    assert response.status_code == 200
    with pytest.raises(HTTPException) as err:
        client.get(f"/{menu_test['id']}/submenus/{submenu_test['id']}/dishes/{uuid.uuid4()}")
    assert err.value.status_code == 404
    assert err.value.detail == "dish not found"


def test_count_submenu_and_dish_of_menu():
    with Session(engine) as session:
        session.execute(delete(models.Menu))
        session.commit()

    # create menu
    menu = {
        "id": f"{uuid.uuid4()}",
        "title": "menu1",
        "description": "about menu1",
    }
    response = client.post("/", json=menu)
    assert response.status_code == 201
    assert response.json()['id'] == menu['id']
    response = client.get(f"/{menu['id']}")
    assert response.status_code == 200

    # create submenu
    submenu = {
        "id": f"{uuid.uuid4()}",
        "title": "submenu1",
        "description": "about submenu1",
    }
    response = client.post(f"/{menu['id']}/submenus/", json=submenu)
    assert response.status_code == 201
    assert response.json()['id'] == submenu['id']
    response = client.get(f"/{menu['id']}/submenus/{submenu['id']}/")
    assert response.status_code == 200

    # create dish1
    dish1 = {
        "id": f"{uuid.uuid4()}",
        "title": "dish1",
        "description": "about dish1",
        "price": "13.50"
    }
    response = client.post(f"/{menu['id']}/submenus/{submenu['id']}/dishes/", json=dish1)
    assert response.status_code == 201
    assert response.json()['id'] == dish1['id']
    response = client.get(f"/{menu['id']}/submenus/{submenu['id']}/dishes/{dish1['id']}")
    assert response.status_code == 200

    # create dish2
    dish2 = {
        "id": f"{uuid.uuid4()}",
        "title": "dish2",
        "description": "about dish2",
        "price": "12.50"
    }
    response = client.post(f"/{menu['id']}/submenus/{submenu['id']}/dishes/", json=dish2)
    assert response.status_code == 201
    assert response.json()['id'] == dish2['id']
    response = client.get(f"/{menu['id']}/submenus/{submenu['id']}/dishes/{dish2['id']}")
    assert response.status_code == 200

    # Views a specific menu
    response = client.get(f"/{menu['id']}/")
    assert response.status_code == 200
    assert response.json()['id'] == menu['id']
    assert response.json()['submenus_count'] == 1
    assert response.json()['dishes_count'] == 2

    # Views a specific submenu
    response = client.get(f"/{menu['id']}/submenus/{submenu['id']}/")
    assert response.status_code == 200
    assert response.json()['id'] == submenu['id']
    assert response.json()['dishes_count'] == 2

    # Delete submenu
    response = client.delete(f"/{menu['id']}/submenus/{submenu['id']}/")
    assert response.status_code == 200

    # Views a list of submenus
    response = client.get(f"/{menu['id']}/submenus/")
    assert response.status_code == 200
    assert response.json() == []

    # Views a list of dishes
    response = client.get(f"/{menu['id']}/submenus/{submenu['id']}/dishes/")
    assert response.status_code == 200
    assert response.json() == []

    # Views a specific menu
    response = client.get(f"/{menu['id']}/")
    assert response.status_code == 200
    assert response.json()['id'] == menu['id']
    assert response.json()['submenus_count'] == 0
    assert response.json()['dishes_count'] == 0

    # Delete menu
    response = client.delete(f"/{menu['id']}")
    assert response.status_code == 200

    # Views a list of menus
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == []
