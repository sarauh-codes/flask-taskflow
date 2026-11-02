import pytest

from website import create_app, db


@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
    })
    yield app
    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def signup(client, email='ada@example.com', password='secret123'):
    return client.post('/signup', data={
        'email': email,
        'firstName': 'Ada',
        'password1': password,
        'password2': password,
    })


def logout(client):
    return client.get('/logout')
