import pytest

from server.dao.models.main import User

class TestUserDAO:
    def test_create_user(self, factory, sample_user):
        # create user test
        with factory.user_dao() as dao:
            dao.create(sample_user)

            retrieved = dao.get_one(sample_user.id)
            assert retrieved is not None
            assert retrieved.username == sample_user.username
            assert retrieved.password == sample_user.password

    @pytest.mark.xfail
    def test_create_duplicate_user(self, factory):
        user1 = User(id=1, username="duplicate", password="pass1")
        user2 = User(id=2, username="duplicate", password="pass2")

        with factory.user_dao() as dao:
            dao.create(user1)

        with factory.user_dao() as dao:
            dao.create(user2)

    def test_get_one_existing(self, factory, sample_user):
        # test get one
        with factory.user_dao() as dao:
            dao.create(sample_user)
            user = dao.get_one(sample_user.id)

            assert user is not None
            assert user.id == sample_user.id
            assert user.username == sample_user.username

    def test_get_one_non_existing(self, factory):
        # test get one non existing user
        with factory.user_dao() as dao:
            user = dao.get_one(999)
            assert user is None

    def test_get_all(self, factory):
        """Тест получения всех пользователей."""
        users = [
            User(id=1, username="user1", password="pass1"),
            User(id=2, username="user2", password="pass2"),
            User(id=3, username="user3", password="pass3"),
        ]

        with factory.user_dao() as dao:
            for user in users:
                dao.create(user)

            all_users = dao.get_all()
            assert len(all_users) == 3
            usernames = [u.username for u in all_users]
            assert "user1" in usernames
            assert "user2" in usernames
            assert "user3" in usernames

    def test_get_by_username_existing(self, factory, sample_user):
        # test get_user_by_username
        with factory.user_dao() as dao:
            dao.create(sample_user)
            user = dao.get_by_username("testuser")

            assert user is not None
            assert user.id == sample_user.id

    def test_get_by_username_non_existing(self, factory):
        # test get by non existing username
        with factory.user_dao() as dao:
            user = dao.get_by_username("nonexistent")
            assert user is None

    def test_update_partial(self, factory, sample_user):
        # test update partial
        with factory.user_dao() as dao:
            dao.create(sample_user)

            update_data = {
                "id": sample_user.id,
                "username": "updated_username"
            }
            dao.update(update_data)

            updated = dao.get_one(sample_user.id)
            assert updated.username == "updated_username"
            assert updated.password == sample_user.password
            assert updated.admin == sample_user.admin

    def test_update_full(self, factory, sample_user):
        with factory.user_dao() as dao:
            dao.create(sample_user)

            update_data = {
                "id": sample_user.id,
                "username": "new_username",
                "password": "new_password",
                "admin": True,
                "authorized": False
            }
            dao.update(update_data)

            updated = dao.get_one(sample_user.id)
            assert updated.username == "new_username"
            assert updated.password == "new_password"
            assert updated.admin == True
            assert updated.authorized == False

    @pytest.mark.xfail
    def test_update_non_existing(self, factory):
        # test update non existing user
        with factory.user_dao() as dao:
            update_data = {"id": 999, "username": "new_name"}
            dao.update(update_data)

    def test_activate_user(self, factory, sample_user):
        # test activate user
        with factory.user_dao() as dao:
            dao.create(sample_user)

            # deactivate
            dao.activate(sample_user.id, activate=False)
            user = dao.get_one(sample_user.id)
            assert user.authorized == 0  # int(False) = 0

            # activate
            dao.activate(sample_user.id, activate=True)
            user = dao.get_one(sample_user.id)
            assert user.authorized == 1  # int(True) = 1

            # Даем права админа
            dao.grant_admin(sample_user.id, grant=True)
            user = dao.get_one(sample_user.id)
            assert user.admin == 1

            # Забираем права
            dao.grant_admin(sample_user.id, grant=False)
            user = dao.get_one(sample_user.id)
            assert user.admin == 0

    def test_delete_user(self, factory, sample_user):
        # test delete user
        with factory.user_dao() as dao:
            dao.create(sample_user)

            assert dao.get_one(sample_user.id) is not None

            dao.delete(sample_user.id)

            assert dao.get_one(sample_user.id) is None

    @pytest.mark.xfail
    def test_delete_non_existing(self, factory):
        # test delete non existing user
        with factory.user_dao() as dao:
            dao.delete(999)

    @pytest.mark.parametrize("field,value", [
        ("username", "test"),
        ("password", "hash"),
        ("admin", True),
        ("authorized", False),
    ])
    def test_user_fields(self, factory, field, value):
        user_data = {
            "id": 1,
            "username": "testuser",
            "password": "hashed",
            "admin": False,
            "authorized": True
        }
        user_data[field] = value

        user = User(**user_data)

        with factory.user_dao() as dao:
            dao.create(user)
            retrieved = dao.get_one(1)
            assert getattr(retrieved, field) == value