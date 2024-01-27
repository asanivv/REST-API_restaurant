import decimal
import uuid

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import delete
from sqlalchemy.orm import Session

from restaurant.menu import models
from restaurant.menu.crud import is_valid_uuid
from restaurant.menu.database import engine
from restaurant.menu.routers import menu_router

client = TestClient(menu_router)

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


def get_menu_by_id(menu_id: str):
    with Session(engine) as session:
        return session.get(models.Menu, menu_id)


def get_submenu_by_id(submenu_id: str):
    with Session(engine) as session:
        return session.get(models.SubMenu, submenu_id)


def get_dish_by_id(dish_id):
    with Session(engine) as session:
        return session.get(models.Dish, dish_id)


'''
 START MENU TESTS
'''


def test_read_empty_menu():
    with Session(engine) as session:
        session.execute(delete(models.Menu))
        session.commit()
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == []


def test_create_menu():
    response = client.post(
        "/",
        json={
            'id': menu_test['id'],
            "title": menu_test['title'],
            "description": menu_test['description'],
        },
    )
    data = response.json()
    assert response.status_code == 201
    assert data["title"] == menu_test['title']
    assert data["description"] == menu_test['description']
    assert data["submenus_count"] == menu_test['submenus_count']
    assert data["dishes_count"] == menu_test['dishes_count']
    assert data["id"] is not None
    assert is_valid_uuid(data["id"]) is True


def test_delete_wrong_menu_by_id():
    with pytest.raises(HTTPException) as err:
        client.delete("/11111/")
    assert err.value.status_code == 422
    assert err.value.detail == "Wrong id type"


def test_delete_menu_by_id():
    response = client.delete(f"/{menu_test['id']}")
    assert response.status_code == 200
    assert response.json() == {"status": True, "message": "The menu has been deleted"}
    assert get_menu_by_id(menu_test['id']) is None


def test_menu_id_not_found():
    with pytest.raises(HTTPException) as err:
        client.get(f"/{menu_test['id']}")
    assert err.value.status_code == 404
    assert err.value.detail == "menu not found"


def test_menu_is_already_registered():
    client.post("/",
                json={
                    'id': menu_test['id'],
                    "title": menu_test['title'],
                    "description": menu_test['description'],
                },
                )
    with pytest.raises(HTTPException) as err:
        client.post("/",
                    json={
                        'id': menu_test['id'],
                        "title": menu_test['title'],
                        "description": menu_test['description'],
                    },
                    )
    assert err.value.status_code == 400
    assert err.value.detail == "Title of Menu already registered"


def test_read_menu():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert type(data) is list
    assert type(data[0]) is dict
    for menu in data:
        for key in menu.keys():
            assert key in ('id', 'title', 'description', 'submenus_count', 'dishes_count')
    assert menu_test in data


def test_read_menu_by_id():
    response = client.get(f"/{menu_test['id']}")
    assert response.status_code == 200
    assert response.json() == menu_test


def test_update_menu():
    response = client.patch(f"/{menu_test['id']}/",
                            json={
                                "id": menu_test['id'],
                                "title": menu_test['title'],
                                "description": "this field has been changed",
                            },
                            )
    assert response.status_code == 200
    data = response.json()
    assert data['description'] == "this field has been changed"


'''
 START SUBMENU TESTS
'''


def test_read_empty_submenu():
    with Session(engine) as session:
        session.execute(delete(models.SubMenu))
        session.commit()
    response = client.get(f"/{menu_test['id']}/submenus/")
    assert response.status_code == 200
    assert response.json() == []


def test_create_submenu():
    response = client.post(
        f"/{menu_test['id']}/submenus/",
        json={
            'id': submenu_test['id'],
            "title": submenu_test['title'],
            "description": submenu_test['description'],
        },
    )
    data = response.json()
    assert response.status_code == 201
    assert data["title"] == submenu_test['title']
    assert data["description"] == submenu_test['description']
    assert data["dishes_count"] == submenu_test['dishes_count']
    assert data["id"] is not None
    assert is_valid_uuid(data["id"]) is True


def test_read_submenu():
    response = client.get(f"/{menu_test['id']}/submenus/")
    assert response.status_code == 200
    data = response.json()
    assert type(data) is list
    assert type(data[0]) is dict
    for submenu in data:
        for key in submenu.keys():
            assert key in ('id', 'title', 'description', 'dishes_count')
    assert submenu_test in data


def test_create_submenu_wrong_menu_id():
    with pytest.raises(HTTPException) as err:
        client.post("/1111/submenus/",
                    json={
                        'id': submenu_test['id'],
                        "title": submenu_test['title'],
                        "description": submenu_test['description'],
                    },
                    )
    assert err.value.status_code == 422
    assert err.value.detail == "Wrong id type"


def test_submenu_menu_id_is_not_registered():
    with pytest.raises(HTTPException) as err:
        client.post(f"/{uuid.uuid4()}/submenus/",
                    json={
                        'id': submenu_test['id'],
                        "title": submenu_test['title'],
                        "description": submenu_test['description'],
                    },
                    )
    assert err.value.status_code == 400
    assert err.value.detail == "ID of Menu not registered"


def test_submenu_title_is_already_registered():
    with pytest.raises(HTTPException) as err:
        client.post(f"/{menu_test['id']}/submenus/",
                    json={
                        'id': submenu_test['id'],
                        "title": submenu_test['title'],
                        "description": submenu_test['description'],
                    },
                    )
    assert err.value.status_code == 400
    assert err.value.detail == "Title of Submenu already registered"


def test_submenu_id_not_found():
    with pytest.raises(HTTPException) as err:
        client.get(f"/{menu_test['id']}/submenus/{uuid.uuid4()}")
    assert err.value.status_code == 404
    assert err.value.detail == "submenu not found"


def test_delete_wrong_submenu_by_id():
    with pytest.raises(HTTPException) as err:
        client.delete(f"/{menu_test['id']}/submenus/1")
    assert err.value.status_code == 422
    assert err.value.detail == "One or more wrong types id"


def test_delete_submenu_by_id():
    response = client.delete(f"/{menu_test['id']}/submenus/{submenu_test['id']}")
    assert response.status_code == 200
    assert response.json() == {"status": True, "message": "The submenu has been deleted"}
    assert get_menu_by_id(menu_test['id']) is not None
    assert get_submenu_by_id(submenu_test['id']) is None


def test_submenu_is_already_registered():
    client.post(f"/{menu_test['id']}/submenus/",
                json={
                    'id': submenu_test['id'],
                    "title": submenu_test['title'],
                    "description": submenu_test['description'],
                },
                )
    with pytest.raises(HTTPException) as err:
        client.post(f"/{menu_test['id']}/submenus/",
                    json={
                        'id': submenu_test['id'],
                        "title": submenu_test['title'],
                        "description": submenu_test['description'],
                    },
                    )
    assert err.value.status_code == 400
    assert err.value.detail == "Title of Submenu already registered"


def test_update_submenu():
    response = client.patch(f"/{menu_test['id']}/submenus/{submenu_test['id']}/",
                            json={

                                "id": submenu_test['id'],
                                "title": submenu_test['title'],
                                "description": "this field has been changed",
                            },
                            )
    assert response.status_code == 200
    data = response.json()
    assert data['description'] == "this field has been changed"


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
    assert get_menu_by_id(menu_test['id']) is not None
    assert get_submenu_by_id(submenu_test['id']) is not None
    assert get_dish_by_id(submenu_test['id']) is None


