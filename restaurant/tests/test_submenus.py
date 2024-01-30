import uuid

from sqlalchemy import delete
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.orm import Session

from restaurant.menu import models
from restaurant.menu.crud import is_valid_uuid
from restaurant.tests.Dependency import client, engine


class TestSubMenus:
    menu = {
        "id": f"{uuid.uuid4()}",
        "title": "menu1",
        "description": "about menu1",
    }
    submenu = {
        "id": f"{uuid.uuid4()}",
        "title": "submenu1",
        "description": "about submenu1",
    }

    def test_read_empty_submenu(self):
        with Session(engine) as session:
            session.execute(delete(models.SubMenu))
            session.commit()
        # create menu
        response = client.post(
            "/",
            json=self.menu,
        )
        assert response.status_code == 201
        assert response.json()['id'] == self.menu['id']
        response = client.get(f"/{self.menu['id']}/submenus/")
        assert response.status_code == 200
        assert response.json() == []
        # delete menu
        response = client.delete(f"/{self.menu['id']}/")
        assert response.status_code == 200

    def test_create_submenu(self):
        # create menu
        response = client.post(
            "/",
            json=self.menu,
        )
        assert response.status_code == 201
        assert response.json()['id'] == self.menu['id']
        # create submenu
        response = client.post(
            f"/{self.menu['id']}/submenus/",
            json={
                'id': self.submenu['id'],
                "title": self.submenu['title'],
                "description": self.submenu['description'],
            },
        )
        data = response.json()
        assert response.status_code == 201
        assert data['title'] == self.submenu['title']
        assert data['description'] == self.submenu['description']
        assert data['dishes_count'] == 0
        assert data['id'] is not None
        assert is_valid_uuid(data["id"]) is True
        # get submenu from db
        with Session(engine) as session:
            db_submenu = session.get(models.SubMenu, data['id'])
            assert f'{db_submenu.menu_id}' == self.menu['id']
            assert f'{db_submenu.id}' == data['id']
            assert db_submenu.title == data['title']
            assert db_submenu.description == data['description']
            session.delete(session.get(models.Menu, self.menu['id']))
            session.commit()
            assert session.get(models.SubMenu, data['id']) is None

    def test_read_submenus(self):
        # create menu
        response = client.post(
            "/",
            json=self.menu,
        )
        assert response.status_code == 201
        assert response.json()['id'] == self.menu['id']
        # create submenu
        response = client.post(
            f"/{self.menu['id']}/submenus/",
            json=self.submenu,
        )
        assert response.status_code == 201
        # get submenus
        response = client.get(f"/{self.menu['id']}/submenus/")
        assert response.status_code == 200
        data = response.json()
        assert type(data) is list
        assert type(data[0]) is dict
        for submenu in data:
            for key in submenu.keys():
                assert key in ('id', 'title', 'description', 'dishes_count')
        assert data[0]['id'] == self.submenu['id']
        assert data[0]['title'] == self.submenu['title']
        assert data[0]['description'] == self.submenu['description']
        with Session(engine) as session:
            db_submenu = session.get(models.SubMenu, data[0]['id'])
            assert f'{db_submenu.menu_id}' == self.menu['id']
            assert f'{db_submenu.id}' == data[0]['id']
            assert db_submenu.title == data[0]['title']
            assert db_submenu.description == data[0]['description']
            session.delete(session.get(models.Menu, self.menu['id']))
            session.commit()
            assert session.get(models.SubMenu, data[0]['id']) is None

    def test_read_submenu_by_id(self):
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
        # get submenu
        response = client.get(f"/{self.menu['id']}/submenus/{self.submenu['id']}/")
        assert response.status_code == 200
        data = response.json()
        assert type(data) is dict
        assert data['id'] == self.submenu['id']
        assert data['title'] == self.submenu['title']
        assert data['description'] == self.submenu['description']
        assert data['dishes_count'] == 0
        # delete menu
        with Session(engine) as session:
            db_submenu = session.get(models.SubMenu, data['id'])
            assert f'{db_submenu.menu_id}' == self.menu['id']
            assert f'{db_submenu.id}' == data['id']
            assert db_submenu.title == data['title']
            assert db_submenu.description == data['description']
            session.delete(session.get(models.Menu, self.menu['id']))
            session.commit()
            assert session.get(models.SubMenu, data['id']) is None

    def test_create_submenu_wrong_menu_id(self):
        wrong_id = 1111
        response = client.post(f"/{wrong_id}/submenus/",
                               json={
                                   'id': self.submenu['id'],
                                   "title": self.submenu['title'],
                                   "description": self.submenu['description'],
                               },
                               )
        assert response.status_code == 422
        assert response.json() == {'detail': "Wrong id type"}
        with Session(engine) as session:
            try:
                session.get(models.SubMenu, wrong_id)
            except ProgrammingError as e:
                assert e.code == 'f405'

    def test_submenu_menu_id_is_not_registered(self):
        lookup_id = uuid.uuid4()
        response = client.post(f"/{lookup_id}/submenus/",
                               json={
                                   'id': self.submenu['id'],
                                   "title": self.submenu['title'],
                                   "description": self.submenu['description'],
                               },
                               )
        assert response.status_code == 400
        assert response.json() == {'detail': 'ID of Menu not registered'}
        with Session(engine) as session:
            assert session.get(models.SubMenu, lookup_id) is None
            assert session.get(models.SubMenu, self.submenu['id']) is None

    def test_submenu_title_is_already_registered(self):
        # create menu
        response = client.post(
            "/",
            json=self.menu,
        )
        assert response.status_code == 201
        # add submenu
        response = client.post(f"/{self.menu['id']}/submenus/",
                               json={
                                   'id': self.submenu['id'],
                                   "title": self.submenu['title'],
                                   "description": self.submenu['description'],
                               },
                               )
        assert response.status_code == 201
        with Session(engine) as session:
            assert session.get(models.Menu, self.menu['id']) is not None
            assert session.get(models.SubMenu, self.submenu['id']) is not None
        new_submenu_id = uuid.uuid4()
        # try to add submenu again with same title
        response = client.post(f"/{self.menu['id']}/submenus/",
                               json={
                                   'id': f'{new_submenu_id}',
                                   "title": self.submenu['title'],
                                   "description": self.submenu['description'],
                               },
                               )
        assert response.status_code == 400
        assert response.json() == {'detail': 'Title of Submenu already registered'}
        with Session(engine) as session:
            assert session.get(models.SubMenu, new_submenu_id) is None
            session.execute(delete(models.Menu).filter(models.Menu.id == self.menu['id']))
            session.commit()
            assert session.get(models.SubMenu, self.submenu['id']) is None

    def test_submenu_id_not_found(self):
        # create menu
        response = client.post(
            "/",
            json=self.menu,
        )
        assert response.status_code == 201
        submenu_id = uuid.uuid4()
        response = client.get(f"/{self.menu['id']}/submenus/{submenu_id}")
        assert response.status_code == 404
        assert response.json() == {'detail': 'submenu not found'}
        with Session(engine) as session:
            assert session.get(models.SubMenu, submenu_id) is None
            session.execute(delete(models.Menu).filter(models.Menu.id == self.menu['id']))
            session.commit()
            assert session.get(models.Menu, self.menu['id']) is None

    def test_delete_wrong_submenu_by_id(self):
        # create menu
        response = client.post(
            "/",
            json=self.menu,
        )
        assert response.status_code == 201

        response = client.delete(f"/{self.menu['id']}/submenus/1")
        assert response.status_code == 422
        assert response.json() == {'detail': 'One or more wrong types id'}
        with Session(engine) as session:
            assert session.get(models.Menu, self.menu['id']) is not None
            session.execute(delete(models.Menu).filter(models.Menu.id == self.menu['id']))
            session.commit()
            assert session.get(models.Menu, self.menu['id']) is None

    def test_delete_submenu_by_id(self):
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
            assert session.get(models.Menu, self.menu['id']) is not None
            assert session.get(models.SubMenu, self.submenu['id']) is not None
        # delete submenu
        response = client.delete(f"/{self.menu['id']}/submenus/{self.submenu['id']}")
        assert response.status_code == 200
        assert response.json() == {"status": True, "message": "The submenu has been deleted"}
        with Session(engine) as session:
            assert session.get(models.Menu, self.menu['id']) is not None
            assert session.get(models.SubMenu, self.submenu['id']) is None
            session.execute(delete(models.Menu).filter(models.Menu.id == self.menu['id']))
            session.commit()
            assert session.get(models.Menu, self.menu['id']) is None

    def test_update_submenu(self):
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
