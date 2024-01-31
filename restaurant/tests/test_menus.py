import uuid

from sqlalchemy import delete, func
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.orm import Session

from menu import models
from menu.crud import is_valid_uuid
from tests.Dependency import client, engine


class TestMenus:
    menu = {
        "id": f"{uuid.uuid4()}",
        "title": "menu1",
        "description": "about menu1",
    }

    def test_read_empty_menu(self):
        with Session(engine) as session:
            session.execute(delete(models.Menu))
            session.commit()
            assert session.query(models.Menu).all() == []
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == []

    def test_create_menu(self):
        # create menu
        response = client.post(
            "/",
            json=self.menu,
        )
        data = response.json()
        assert response.status_code == 201
        assert data["title"] == self.menu['title']
        assert data["description"] == self.menu['description']
        assert data["submenus_count"] == 0
        assert data["dishes_count"] == 0
        assert data["id"] is not None
        assert is_valid_uuid(data["id"]) is True
        # get menu from db
        with Session(engine) as session:
            db_menu = session.get(models.Menu, data['id'])
            assert f'{db_menu.id}' == data['id']
            assert db_menu.title == data['title']
            assert db_menu.description == data['description']
        # delete menu
        response = client.delete(f"/{self.menu['id']}/")
        assert response.status_code == 200

    def test_create_menu_wrong_menu_id(self):
        wrong_id = 1111
        response = client.post("/",
                               json={
                                   'id': f'{wrong_id}',
                                   "title": self.menu['title'],
                                   "description": self.menu['description'],
                               },
                               )
        assert response.status_code == 422
        assert response.is_error == True
        with Session(engine) as session:
            try:
                session.get(models.Menu, wrong_id)
            except ProgrammingError as e:
                assert e.code == 'f405'

    def test_delete_wrong_menu_by_id(self):
        menu_id = 11111
        response = client.delete(f"/{menu_id}/")
        assert response.status_code == 422
        assert response.json() == {'detail': 'Wrong id type'}
        with Session(engine) as session:
            try:
                session.get(models.Menu, menu_id)
            except ProgrammingError as e:
                assert e.code == 'f405'

    def test_delete_menu_by_id(self):
        # create menu
        response = client.post(
            "/",
            json=self.menu,
        )
        assert response.status_code == 201

        response = client.delete(f"/{self.menu['id']}/")
        assert response.status_code == 200
        assert response.json() == {"status": True, "message": "The menu has been deleted"}
        response = client.get(f"/{self.menu['id']}")
        assert response.status_code == 404
        assert response.json() == {'detail': 'menu not found'}

    def test_menu_id_not_found(self):
        response = client.get(f"/{self.menu['id']}")
        assert response.status_code == 404
        assert response.json() == {'detail': 'menu not found'}
        with Session(engine) as session:
            assert session.get(models.Menu, self.menu['id']) is None

    def test_menu_is_already_registered(self):
        # create menu
        response = client.post(
            "/",
            json=self.menu,
        )
        assert response.status_code == 201
        # create menu again
        response = client.post(
            "/",
            json=self.menu,
        )
        assert response.status_code == 400
        assert response.json() == {'detail': 'Title of Menu already registered'}
        with Session(engine) as session:
            assert session.query(models.Menu).filter(models.Menu.title == self.menu['title']).first() is not None
        # duplicate record: id
        response = client.post(
            "/",
            json={
                'id': f"{self.menu['id']}",
                "title": "menu2",
                "description": "about menu2",
            },
        )
        assert response.status_code == 500
        assert response.json() == {"detail": "A duplicate record already exists"}
        with Session(engine) as session:
            assert session.get(models.Menu, self.menu['id']) is not None
        response = client.delete(f"/{self.menu['id']}/")
        assert response.status_code == 200

    def test_read_menus(self):
        # create menu
        response = client.post(
            "/",
            json=self.menu,
        )
        assert response.status_code == 201
        # get all menus
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert type(data) is list
        assert type(data[0]) is dict
        for menu in data:
            for key in menu.keys():
                assert key in ('id', 'title', 'description', 'submenus_count', 'dishes_count')
        assert data[0]['id'] == self.menu['id']
        assert data[0]['title'] == self.menu['title']
        assert data[0]['description'] == self.menu['description']
        # delete menu
        response = client.delete(f"/{self.menu['id']}/")
        assert response.status_code == 200
        # get all menu
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == []

    def test_read_menu_by_id(self):
        # create menu
        response = client.post(
            "/",
            json=self.menu,
        )
        assert response.status_code == 201
        # get menu by id
        response = client.get(f"/{self.menu['id']}")
        assert response.status_code == 200
        data = response.json()
        assert type(data) is dict
        assert data['id'] == self.menu['id']
        assert data['title'] == self.menu['title']
        assert data['description'] == self.menu['description']
        assert data["submenus_count"] == 0
        assert data["dishes_count"] == 0
        # delete menu
        response = client.delete(f"/{self.menu['id']}/")
        assert response.status_code == 200
        with Session(engine) as session:
            assert session.get(models.Menu, data['id']) is None

    def test_update_menu(self):
        # create menu
        response = client.post(
            "/",
            json=self.menu,
        )
        assert response.status_code == 201
        # update menu
        response = client.patch(f"/{self.menu['id']}/",
                                json={
                                    "id": self.menu['id'],
                                    "title": self.menu['title'],
                                    "description": "this field has been changed",
                                },
                                )
        assert response.status_code == 200
        data = response.json()
        assert data['description'] == "this field has been changed"
        assert data['id'] == self.menu['id']
        assert data['title'] == self.menu['title']
        # delete menu
        response = client.delete(f"/{self.menu['id']}/")
        assert response.status_code == 200

    def test_count_submenu_and_dish_of_menu(self):
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
        with Session(engine) as session:
            assert session.get(models.Menu, menu['id']) is not None

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
        with Session(engine) as session:
            assert session.get(models.SubMenu, submenu['id']) is not None

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
        with Session(engine) as session:
            assert session.get(models.Dish, dish1['id']) is not None

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
        with Session(engine) as session:
            assert session.get(models.Dish, dish2['id']) is not None

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

        with Session(engine) as session:
            assert session.query(func.count(models.SubMenu.id)).filter(
                models.SubMenu.menu_id == menu['id']).first()[0] == 1
            assert session.query(func.count(models.Dish.id)).filter(
                models.Dish.submenu_id == submenu['id']).first()[0] == 2

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

        with Session(engine) as session:
            assert session.query(models.SubMenu).all() == []
            assert session.query(models.Dish).all() == []

        # Views a specific menu
        response = client.get(f"/{menu['id']}/")
        assert response.status_code == 200
        assert response.json()['id'] == menu['id']
        assert response.json()['submenus_count'] == 0
        assert response.json()['dishes_count'] == 0

        with Session(engine) as session:
            assert session.get(models.Menu, menu['id']) is not None
            assert session.query(func.count(models.SubMenu.id)).filter(
                models.SubMenu.menu_id == menu['id']).first()[0] == 0
            assert session.query(func.count(models.Dish.id)).filter(
                models.Dish.submenu_id == submenu['id']).first()[0] == 0

        # Delete menu
        response = client.delete(f"/{menu['id']}")
        assert response.status_code == 200

        # Views a list of menus
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == []
        with Session(engine) as session:
            assert session.get(models.Menu, menu['id']) is None
