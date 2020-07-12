import json

import pytest

from project.api.models import User


class TestUsersPost:
    def test_add_user(self, test_app, test_database):
        client = test_app.test_client()
        resp = client.post(
            "/users",
            data=json.dumps(
                {"username": "daguito81", "email": "dagoromer85@gmail.com"}
            ),
            content_type="application/json",
        )
        data = json.loads(resp.data.decode())
        assert resp.status_code == 201
        assert "dagoromer85@gmail.com was added!" in data["message"]

    def test_add_user_invalid_json(self, test_app, test_database):
        client = test_app.test_client()
        resp = client.post(
            "/users", data=json.dumps({}), content_type="application/json",
        )
        data = json.loads(resp.data.decode())
        assert resp.status_code == 400
        assert "Input payload validation failed" in data["message"]

    def test_add_user_invalid_json_keys(self, test_app, test_database):
        client = test_app.test_client()
        resp = client.post(
            "/users",
            data=json.dumps({"email": "dago@gmail.com"}),
            content_type="application/json",
        )
        data = json.loads(resp.data.decode())
        assert resp.status_code == 400
        assert "Input payload validation failed" in data["message"]

    def test_add_user_duplicate_email(self, test_app, test_database):
        client = test_app.test_client()
        client.post(
            "/users",
            data=json.dumps({"username": "dago", "email": "dagovago@gmail.com"}),
            content_type="application/json",
        )
        resp = client.post(
            "/users",
            data=json.dumps({"username": "dago", "email": "dagovago@gmail.com"}),
            content_type="application/json",
        )
        data = json.loads(resp.data.decode())
        assert resp.status_code == 400
        assert "Sorry. That email already exists." in data["message"]


class TestUsersGet:
    def test_single_user(self, test_app, test_database, add_user):
        # Given
        user = add_user(username="dago", email="dago@gmail.com")
        client = test_app.test_client()
        # When
        resp = client.get(f"/users/{user.id}")
        data = json.loads(resp.data.decode())
        # Then
        assert resp.status_code == 200
        assert "dago" in data["username"]
        assert "dago@gmail.com" in data["email"]

    def test_single_user_incorrect_id(self, test_app, test_database):
        # GIVEN
        client = test_app.test_client()
        # WHEN
        resp = client.get("/users/999")
        data = json.loads(resp.data.decode())
        # THEN
        assert resp.status_code == 404
        assert "User 999 does not exist" in data["message"]

    def test_all_users(self, test_app, test_database, add_user):
        # GIVEN
        test_database.session.query(User).delete()
        add_user("Dago", "dago@gmail.com")
        add_user("Cristy", "cristy@gmail.com")
        client = test_app.test_client()
        # WHEN
        resp = client.get("/users")
        data = json.loads(resp.data.decode())
        # THEN
        assert resp.status_code == 200
        assert len(data) == 2
        assert "Dago" in data[0]["username"]
        assert "dago@gmail.com" in data[0]["email"]
        assert "Cristy" in data[1]["username"]
        assert "cristy@gmail.com" in data[1]["email"]


class TestUsersDelete:
    def test_delete_user(self, test_app, test_database, add_user):
        # GIVEN
        test_database.session.query(User).delete()  # Make sure its empty
        user = add_user("user-to-be-deleted", "remove-me@mail.com")  # Add 1 user
        client = test_app.test_client()
        resp_one = client.get("/users")
        data = json.loads(resp_one.data.decode())
        assert resp_one.status_code == 200
        assert len(data) == 1
        # WHEN
        resp_two = client.delete(f"/users/{user.id}")
        data = json.loads(resp_two.data.decode())
        resp_three = client.get("/users")
        final_data = json.loads(resp_three.data.decode())
        # THEN
        assert resp_two.status_code == 200
        assert "remove-me@mail.com was removed!" in data["message"]
        assert resp_three.status_code == 200
        assert len(final_data) == 0

    def test_remove_user_incorrect_id(self, test_app, test_database, add_user):
        # GIVEN
        client = test_app.test_client()
        # WHEN
        resp = client.delete("/users/999")
        data = json.loads(resp.data.decode())
        # THEN
        assert resp.status_code == 404
        assert "User 999 does not exist" in data["message"]


class TestUsersPut:
    def test_update_user(self, test_app, test_database, add_user):
        # GIVEN
        test_database.session.query(User).delete()
        user = add_user("update-me", "update@mail.com")
        client = test_app.test_client()
        resp = client.get("/users")
        data = json.loads(resp.data.decode())
        assert resp.status_code == 200
        assert len(data) == 1
        assert "update-me" == data[0]["username"]
        # WHEN
        resp = client.put(
            f"/users/{user.id}",
            data=json.dumps({"username": "dago", "email": "dago@gmail.com"}),
            content_type="application/json",
        )
        data = json.loads(resp.data.decode())
        # THEN
        assert resp.status_code == 200
        assert f"User ID: {user.id} was updated!" in data["message"]
        resp = client.get(f"/users/{user.id}")
        data = json.loads(resp.data.decode())
        assert resp.status_code == 200
        assert "dago" in data["username"]
        assert "dago@gmail.com" in data["email"]

    @pytest.mark.parametrize(
        "user_id, payload, status_code, message",
        [
            [1, {}, 400, "Input payload validation failed"],
            [1, {"email": "mememe@mail.com"}, 400, "Input payload validation failed"],
            [
                999,
                {"username": "me", "email": "mememe@mail.com"},
                404,
                "User 999 does not exist",
            ],
        ],
    )
    def test_update_user_invalid_json(
        self, test_app, test_database, user_id, payload, status_code, message
    ):
        client = test_app.test_client()
        resp = client.put(
            f"/users/{user_id}",
            data=json.dumps(payload),
            content_type="application/json",
        )
        data = json.loads(resp.data.decode())
        assert resp.status_code == status_code
        assert message in data["message"]
