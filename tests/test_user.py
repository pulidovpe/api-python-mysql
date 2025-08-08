import pytest
from app import create_app, db
from app.models.user import User
from flask_jwt_extended import create_access_token

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"mysql+pymysql://{os.getenv('DB_USERNAME')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}/test_{os.getenv('DB_DATABASE')}"
    )
    with app.app_context():
        db.create_all()
    yield app
    with app.app_context():
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_update_user(client):
    # Registrar usuario
    client.post('/register', json={
        'fullname': 'Test User',
        'email': 'test@example.com',
        'password': 'password123'
    })
    # Login para obtener token
    login_response = client.post('/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    access_token = login_response.json['access_token']
    # Actualizar usuario
    response = client.put('/update', json={
        'fullname': 'Updated User',
        'email': 'updated@example.com'
    }, headers={'Authorization': f'Bearer {access_token}'})
    assert response.status_code == 200
    assert response.json['message'] == 'User updated successfully'
    assert response.json['dataUser']['fullname'] == 'Updated User'
    assert response.json['dataUser']['email'] == 'updated@example.com'

def test_update_password(client):
    # Registrar usuario
    client.post('/register', json={
        'fullname': 'Test User',
        'email': 'test@example.com',
        'password': 'password123'
    })
    # Login para obtener token
    login_response = client.post('/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    access_token = login_response.json['access_token']
    # Actualizar contraseña
    response = client.put('/updatePassword', json={
        'newPassword': 'newpassword123'
    }, headers={'Authorization': f'Bearer {access_token}'})
    assert response.status_code == 200
    assert response.json['message'] == 'Password updated successfully'
    # Verificar que la contraseña se haya actualizado
    user = User.query.filter_by(email='test@example.com').first()
    assert user.verify_password('newpassword123')

def test_delete_user(client):
    # Registrar usuario
    client.post('/register', json={
        'fullname': 'Test User',
        'email': 'test@example.com',
        'password': 'password123'
    })
    # Login para obtener token
    login_response = client.post('/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    access_token = login_response.json['access_token']
    # Eliminar usuario
    response = client.delete('/delete', headers={'Authorization': f'Bearer {access_token}'})
    assert response.status_code == 200
    assert response.json['message'] == 'User deleted successfully'
    # Verificar que el usuario haya sido eliminado
    user = User.query.filter_by(email='test@example.com').first()
    assert user is None