import pytest
from app import create_app, db
from config import TestingConfig

# 🔹 App única para toda la sesión de tests
@pytest.fixture(scope="session")
def app():
    app = create_app(TestingConfig)
    with app.app_context():
        db.create_all()
    yield app
    with app.app_context():
        db.drop_all()

# 🔹 Cliente único para toda la sesión
@pytest.fixture(scope="session")
def client(app):
    return app.test_client()
