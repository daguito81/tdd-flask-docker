import json
from project.api.models import User


class TestUsersPost:
    def test_add_user(self, test_app, test_database):
        client = test_app.test_client()
        resp = client.post(
            '/users',
            data=json.dumps({
                'username': 'daguito81',
                'email': 'dagoromer85@gmail.com',
            }),
            content_type='application/json',
        )
        data = json.loads(resp.data.decode())
        assert resp.status_code == 201
        assert 'dagoromer85@gmail.com was added!' in data['message']

    def test_add_user_invalid_json(self, test_app, test_database):
        client = test_app.test_client()
        resp = client.post(
            '/users',
            data=json.dumps({}),
            content_type='application/json',
        )
        data = json.loads(resp.data.decode())
        assert resp.status_code == 400
        assert 'Input payload validation failed' in data['message']

    def test_add_user_invalid_json_keys(self, test_app, test_database):
        client = test_app.test_client()
        resp = client.post(
            '/users',
            data=json.dumps({"email": "dago@gmail.com"}),
            content_type='application/json',
        )
        data = json.loads(resp.data.decode())
        assert resp.status_code == 400
        assert 'Input payload validation failed' in data['message']

    def test_add_user_duplicate_email(self, test_app, test_database):
        client = test_app.test_client()
        client.post(
            '/users',
            data=json.dumps({
                'username': 'dago',
                'email': 'dagovago@gmail.com',
            }),
            content_type='application/json',
        )
        resp = client.post(
            '/users',
            data=json.dumps({
                'username': 'dago',
                'email': 'dagovago@gmail.com',
            }),
            content_type='application/json',
        )
        data = json.loads(resp.data.decode())
        assert resp.status_code == 400
        assert 'Sorry. That email already exists.' in data['message']


class TestUsersGet:
    def test_single_user(self, test_app, test_database, add_user):
        # Given
        user = add_user(username='dago', email='dago@gmail.com')
        client = test_app.test_client()
        # When
        resp = client.get(f'/users/{user.id}')
        data = json.loads(resp.data.decode())
        # Then
        assert resp.status_code == 200
        assert 'dago' in data['username']
        assert 'dago@gmail.com' in data['email']

    def test_single_user_incorrect_id(self, test_app, test_database):
        # GIVEN
        client = test_app.test_client()
        # WHEN
        resp = client.get('/users/999')
        data = json.loads(resp.data.decode())
        # THEN
        assert resp.status_code == 404
        assert 'User 999 does not exist' in data['message']

    def test_all_users(self, test_app, test_database, add_user):
        # GIVEN
        test_database.session.query(User).delete()
        add_user("Dago", "dago@gmail.com")
        add_user("Cristy", "cristy@gmail.com")
        client = test_app.test_client()
        # WHEN
        resp = client.get('/users')
        data = json.loads(resp.data.decode())
        # THEN
        assert resp.status_code == 200
        assert len(data) == 2
        assert "Dago" in data[0]['username']
        assert "dago@gmail.com" in data[0]['email']
        assert "Cristy" in data[1]['username']
        assert "cristy@gmail.com" in data[1]['email']
