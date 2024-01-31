import decimal
import uuid

from sqlalchemy import delete
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.orm import Session

from restaurant.menu import models
from restaurant.menu.crud import is_valid_uuid
from restaurant.tests.Dependency import engine, client


class TestDishes:
    menu = {
        "title": "menu1",
        "description": "menu1",
        "id": "2e9b4f3a-b9d4-4168-8697-1f51de26dd1e",
    }

    submenu = {
        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "title": "submenu1",
        "description": "submenu1",
    }

    dish = {
        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "title": "dish",
        "description": "about dish",
        "price": "115.455"
    }

    def test_read_empty_dishes(self):
        # create menu
        response = client.post(
            "/",
            json=self.menu,
        )
        assert response.status_code == 201
        # create submenu
        response = client.post(
            f"/{self.menu['id']}/submenus/",
            json=self.submenu,
        )
        assert response.status_code == 201
        with Session(engine) as session:
            session.execute(delete(models.Dish))
            session.commit()
            assert session.get(models.Menu, self.menu['id']) is not None
            assert session.get(models.SubMenu, self.submenu['id']) is not None
            assert session.query(models.Dish).all() == []
        response = client.get(f"/{self.menu['id']}/submenus/{self.submenu['id']}/dishes/")
        assert response.status_code == 200
        assert response.json() == []
        # delete menu
        response = client.delete(f"/{self.menu['id']}/")
        assert response.status_code == 200
        with Session(engine) as session:
            assert session.get(models.Menu, self.menu['id']) is None
            assert session.get(models.SubMenu, self.submenu['id']) is None

    def test_create_dish(self):
        # create menu
        response = client.post(
            "/",
            json=self.menu,
        )
        assert response.status_code == 201
        # create submenu
        response = client.post(
            f"/{self.menu['id']}/submenus/",
            json=self.submenu,
        )
        assert response.status_code == 201
        response = client.post(
            f"/{self.menu['id']}/submenus/{self.submenu['id']}/dishes/",
            json={
                'id': self.dish['id'],
                "title": self.dish['title'],
                "description": self.dish['description'],
                "price": self.dish["price"],
            },
        )
        data = response.json()
        assert response.status_code == 201
        assert data["title"] == self.dish['title']
        assert data["description"] == self.dish['description']
        assert data["price"] == str(decimal.Decimal(self.dish["price"]).quantize(decimal.Decimal('0.00')))
        assert data["id"] is not None
        assert is_valid_uuid(data["id"]) is True
        with Session(engine) as session:
            assert session.get(models.Menu, self.menu['id']) is not None
            assert session.get(models.SubMenu, self.submenu['id']) is not None
            db_dish = session.get(models.Dish, self.dish['id'])
            assert db_dish is not None
            assert f'{db_dish.id}' == self.dish["id"]
            assert db_dish.title == self.dish["title"]
            assert db_dish.description == self.dish["description"]
            assert db_dish.price == decimal.Decimal(self.dish["price"]).quantize(decimal.Decimal('0.00'))
            session.execute(delete(models.Menu))
            session.commit()
            assert session.get(models.Menu, self.menu['id']) is None
            assert session.get(models.SubMenu, self.submenu['id']) is None

    def test_read_dishes(self):
        # create menu
        response = client.post(
            "/",
            json=self.menu,
        )
        assert response.status_code == 201
        # create submenu
        response = client.post(
            f"/{self.menu['id']}/submenus/",
            json=self.submenu,
        )
        # first dish
        response = client.post(
            f"/{self.menu['id']}/submenus/{self.submenu['id']}/dishes/",
            json=self.dish
        )
        assert response.status_code == 201
        # second dish
        dish2 = {
            'id': f"{uuid.uuid4()}",
            "title": "dish2",
            "description": "about dish2",
            "price": "12.57",
        }
        assert response.status_code == 201
        response = client.post(
            f"/{self.menu['id']}/submenus/{self.submenu['id']}/dishes/",
            json=dish2
        )
        assert response.status_code == 201
        response = client.get(f"/{self.menu['id']}/submenus/{self.submenu['id']}/dishes/")
        assert response.status_code == 200
        data = response.json()
        assert type(data) is list
        assert type(data[0]) is dict
        assert len(data) == 2
        for submenu in data:
            for key in submenu.keys():
                assert key in ('id', 'title', 'description', 'price')
        assert {
                   'id': self.dish['id'],
                   "title": self.dish['title'],
                   "description": self.dish['description'],
                   "price": str(decimal.Decimal(self.dish["price"]).quantize(decimal.Decimal('0.00'))),
               } in data
        assert dish2 in data
        with Session(engine) as session:
            assert session.get(models.Menu, self.menu['id']) is not None
            assert session.get(models.SubMenu, self.submenu['id']) is not None
            db_dish1 = session.get(models.Dish, self.dish['id'])
            assert f'{db_dish1.id}' == self.dish["id"]
            assert db_dish1.title == self.dish["title"]
            assert db_dish1.description == self.dish["description"]
            assert db_dish1.price == decimal.Decimal(self.dish["price"]).quantize(decimal.Decimal('0.00'))
            db_dish2 = session.get(models.Dish, dish2['id'])
            assert f'{db_dish2.id}' == dish2["id"]
            assert db_dish2.title == dish2["title"]
            assert db_dish2.description == dish2["description"]
            assert str(db_dish2.price) == dish2['price']
            session.execute(delete(models.Menu))
            session.commit()
            assert session.query(models.Menu).all() == []
            assert session.query(models.SubMenu).all() == []
            assert session.query(models.Dish).all() == []

    def test_read_dish_by_id(self):
        # create menu
        response = client.post(
            "/",
            json=self.menu,
        )
        assert response.status_code == 201
        # create submenu
        response = client.post(
            f"/{self.menu['id']}/submenus/",
            json=self.submenu,
        )
        # create dish
        response = client.post(
            f"/{self.menu['id']}/submenus/{self.submenu['id']}/dishes/",
            json=self.dish
        )
        assert response.status_code == 201
        # get dish
        response = client.get(f"/{self.menu['id']}/submenus/{self.submenu['id']}/dishes/{self.dish['id']}")
        assert response.status_code == 200
        data = response.json()
        assert type(data) is dict
        assert f"{data['id']}" == self.dish['id']
        assert data["title"] == self.dish['title']
        assert data["description"] == self.dish['description']
        assert data["price"] == str(decimal.Decimal(self.dish["price"]).quantize(decimal.Decimal('0.00')))
        with Session(engine) as session:
            db_dish = session.get(models.Dish, self.dish['id'])
            assert db_dish is not None
            assert f"{db_dish.id}" == self.dish['id']
            assert db_dish.title == self.dish['title']
            assert db_dish.description == self.dish['description']
            assert db_dish.price == decimal.Decimal(self.dish["price"]).quantize(decimal.Decimal('0.00'))
            session.execute(delete(models.Menu))
            session.commit()
            assert session.query(models.Menu).all() == []
            assert session.query(models.SubMenu).all() == []
            assert session.query(models.Dish).all() == []

    def test_create_dish_wrong_menu_id(self):
        menu_id = 11111
        response = client.post(
            f"/{menu_id}/submenus/{self.submenu['id']}/dishes/",
            json=self.dish
        )
        assert response.status_code == 422
        assert response.json() == {'detail': 'Wrong id type'}
        with Session(engine) as session:
            try:
                session.get(models.Menu, menu_id)
            except ProgrammingError as e:
                assert e.code == 'f405'

    def test_create_dish_wrong_submenu_id(self):
        # create menu
        response = client.post(
            "/",
            json=self.menu,
        )
        assert response.status_code == 201
        submenu_id = 11111
        response = client.post(
            f"/{self.menu['id']}/submenus/{submenu_id}/dishes/",
            json=self.dish
        )
        assert response.status_code == 422
        assert response.json() == {'detail': 'Wrong id type'}
        with Session(engine) as session:
            try:
                session.get(models.SubMenu, submenu_id)
            except ProgrammingError as e:
                assert e.code == 'f405'
        with Session(engine) as session:
            session.execute(delete(models.Menu).filter(models.Menu.id == self.menu['id']))
            session.commit()

    def test_dish_menu_id_is_not_registered(self):
        response = client.post(
            f"/{self.menu['id']}/submenus/{self.submenu}/dishes/",
            json=self.dish
        )
        assert response.status_code == 400
        assert response.json() == {"detail": "ID of Menu not registered"}
        with Session(engine) as session:
            assert session.get(models.Menu, self.menu['id']) is None

    def test_dish_submenu_id_is_not_registered(self):
        # create menu
        response = client.post(
            "/",
            json=self.menu,
        )
        assert response.status_code == 201
        response = client.post(
            f"/{self.menu['id']}/submenus/{self.submenu['id']}/dishes/",
            json=self.dish
        )
        assert response.status_code == 400
        assert response.json() == {"detail": "ID of Submenu not registered"}
        with Session(engine) as session:
            assert session.get(models.SubMenu, self.submenu['id']) is None
            session.execute(delete(models.Menu).filter(models.Menu.id == self.menu['id']))
            session.commit()

    def test_dish_title_is_already_registered(self):
        # create menu
        response = client.post(
            "/",
            json=self.menu,
        )
        assert response.status_code == 201
        # create submenu
        response = client.post(
            f"/{self.menu['id']}/submenus/",
            json=self.submenu,
        )
        assert response.status_code == 201
        # add dish
        response = client.post(
            f"/{self.menu['id']}/submenus/{self.submenu['id']}/dishes/",
            json=self.dish
        )
        assert response.status_code == 201
        # add dish with same title
        new_dish_id = uuid.uuid4()
        response = client.post(
            f"/{self.menu['id']}/submenus/{self.submenu['id']}/dishes/",
            json={
                'id': f'{new_dish_id}',
                "title": self.dish['title'],
                "description": "about new dish",
                "price": "12.57",
            }
        )
        assert response.status_code == 500
        assert response.json() == {"detail": "A duplicate record already exists"}
        with Session(engine) as session:
            db_dish = session.get(models.Dish, self.dish['id'])
            assert db_dish.title == self.dish['title']
            assert session.get(models.Dish, new_dish_id) is None
            session.execute(delete(models.Menu).filter(models.Menu.id == self.menu['id']))
            session.commit()

    def test_dish_id_not_found(self):
        # create menu
        response = client.post(
            "/",
            json=self.menu,
        )
        assert response.status_code == 201
        # create submenu
        response = client.post(
            f"/{self.menu['id']}/submenus/",
            json=self.submenu,
        )
        assert response.status_code == 201
        lookup_id = uuid.uuid4()
        response = client.get(f"/{self.menu['id']}/submenus/{self.submenu['id']}/dishes/{lookup_id}")
        assert response.status_code == 404
        assert response.json() == {"detail": "dish not found"}
        with Session(engine) as session:
            assert session.get(models.Dish, lookup_id) is None
            session.execute(delete(models.Menu).filter(models.Menu.id == self.menu['id']))
            session.commit()

    def test_delete_dish_by_wrong_id(self):
        # create menu
        response = client.post(
            "/",
            json=self.menu,
        )
        assert response.status_code == 201
        # create submenu
        response = client.post(
            f"/{self.menu['id']}/submenus/",
            json=self.submenu,
        )
        assert response.status_code == 201
        # try to delete dish
        wrong_id = 1111
        response = client.delete(f"/{self.menu['id']}/submenus/{self.submenu['id']}/dishes/{wrong_id}")
        assert response.status_code == 422
        assert response.json() == {"detail": "One or more wrong types id"}
        with Session(engine) as session:
            assert session.get(models.Menu, self.menu['id']) is not None
            assert session.get(models.SubMenu, self.submenu['id']) is not None
            try:
                session.get(models.Dish, wrong_id)
            except ProgrammingError as e:
                assert e.code == 'f405'
        with Session(engine) as session:
            session.execute(delete(models.Menu).filter(models.Menu.id == self.menu['id']))
            session.commit()

    def test_delete_dish_by_id(self):
        # create menu
        response = client.post(
            "/",
            json=self.menu,
        )
        assert response.status_code == 201
        # create submenu
        response = client.post(
            f"/{self.menu['id']}/submenus/",
            json=self.submenu,
        )
        assert response.status_code == 201
        # create dish
        response = client.post(
            f"/{self.menu['id']}/submenus/{self.submenu['id']}/dishes/",
            json=self.dish
        )
        assert response.status_code == 201
        with Session(engine) as session:
            assert session.get(models.Dish, self.dish['id']) is not None
        # delete dish
        response = client.delete(f"/{self.menu['id']}/submenus/{self.submenu['id']}/dishes/{self.dish['id']}/")
        assert response.status_code == 200
        assert response.json() == {"status": True, "message": "The dish has been deleted"}
        with Session(engine) as session:
            assert session.get(models.Menu, self.menu['id']) is not None
            assert session.get(models.SubMenu, self.submenu['id']) is not None
            assert session.get(models.Dish, self.dish['id']) is None

        # id not found
        new_dish_id = uuid.uuid4()
        response = client.delete(f"/{self.menu['id']}/submenus/{self.submenu['id']}/dishes/{new_dish_id}/")
        assert response.status_code == 404
        assert response.json() == {'detail': "Dish not found"}
        with Session(engine) as session:
            assert session.get(models.Dish, new_dish_id) is None
            session.execute(delete(models.Menu).filter(models.Menu.id == self.menu['id']))
            session.commit()

    def test_update_dish(self):
        # create menu
        response = client.post(
            "/",
            json=self.menu,
        )
        assert response.status_code == 201
        # create submenu
        response = client.post(
            f"/{self.menu['id']}/submenus/",
            json=self.submenu,
        )
        assert response.status_code == 201
        # create dish
        response = client.post(
            f"/{self.menu['id']}/submenus/{self.submenu['id']}/dishes/",
            json=self.dish
        )
        assert response.status_code == 201
        with Session(engine) as session:
            assert session.get(models.Menu, self.menu['id']) is not None
            assert session.get(models.Dish, self.submenu['id']) is not None
            assert session.get(models.Dish, self.dish['id']) is not None

        response = client.patch(
            f"/{self.menu['id']}/submenus/{self.submenu['id']}/dishes/{self.dish['id']}",
            json={

                'id': self.dish['id'],
                "title": self.dish['title'],
                "description": "this field has been changed",
                "price": '7.777',
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data['description'] == "this field has been changed"
        assert data['price'] == "7.78"
        with Session(engine) as session:
            db_dish = session.get(models.Dish, self.dish['id'])
            assert db_dish.description == "this field has been changed"
            assert db_dish.title == self.dish['title']
            assert str(db_dish.price) == '7.78'
            session.execute(delete(models.Menu).filter(models.Menu.id == self.menu['id']))
            session.commit()
