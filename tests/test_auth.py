import pytest
from app import create_app, db
from config import TestingConfig
from faker import Faker

fake = Faker()

# 🔹 App compartida para toda la sesión de tests
@pytest.fixture(scope="session")
def app():
    app = create_app(TestingConfig)
    with app.app_context():
        db.create_all()
    yield app
    with app.app_context():
        db.drop_all()

@pytest.fixture(scope="session")
def client(app):
    return app.test_client()

def test_register(client):
    response = client.post('/register', json={
        'fullname': fake.name(),
        'email': fake.email(),
        'password': 'password123'
    })
    assert response.status_code == 201
    assert response.json['message'] == 'User created successfully'

def test_login(client):
    test_email = fake.email()
    test_password = 'password123'
    client.post('/register', json={
        'fullname': fake.name(),
        'email': test_email,
        'password': test_password
    })
    response = client.post('/login', json={
        'email': test_email,
        'password': test_password
    })
    assert response.status_code == 200
    assert 'access_token' in response.json
