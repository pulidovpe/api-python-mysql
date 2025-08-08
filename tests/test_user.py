import pytest
from app.models.user import User
from faker import Faker

fake = Faker()

@pytest.fixture
def auth_client(client, app):
    test_email = fake.email()
    test_password = 'password123'
    test_fullname = fake.name()

    # Registro
    client.post('/register', json={
        'fullname': test_fullname,
        'email': test_email,
        'password': test_password
    })

    # Login y token
    login_response = client.post('/login', json={
        'email': test_email,
        'password': test_password
    })
    access_token = login_response.json['access_token']

    # Diccionario de autorización listo
    auth_header = {'Authorization': f'Bearer {access_token}'}

    return client, auth_header, test_email


def test_get_all_users(auth_client, app):
    client, auth_header, test_email = auth_client
    
    # Crear algunos usuarios adicionales para la prueba
    with app.app_context():
        # Crear usuarios adicionales directamente en la BD
        user1 = User(fullname=fake.name(), email=fake.email(), password='hashed_password_1')
        user2 = User(fullname=fake.name(), email=fake.email(), password='hashed_password_2')
        from app import db
        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()

    response = client.get('/getAllUsers', headers=auth_header)

    assert response.status_code == 200
    assert response.json['message'] == 'Users retrieved successfully'
    assert 'users' in response.json
    assert 'total_users' in response.json
    assert response.json['total_users'] >= 3  # Al menos 3 usuarios (el original + 2 adicionales)
    
    # Verificar que los usuarios no incluyen contraseñas
    for user in response.json['users']:
        assert 'id' in user
        assert 'fullname' in user
        assert 'email' in user
        assert 'password' not in user  # No debe incluir contraseñas


def test_update_user(auth_client):
    client, auth_header, test_email = auth_client
    new_email = fake.email()

    response = client.put('/update', json={
        'fullname': 'Updated User',
        'email': new_email
    }, headers=auth_header)

    assert response.status_code == 200
    assert response.json['message'] == 'User updated successfully'
    assert response.json['dataUser']['fullname'] == 'Updated User'
    assert response.json['dataUser']['email'] == new_email


def test_update_password(auth_client, app):
    client, auth_header, test_email = auth_client
    new_password = 'newpassword123_updated'

    response = client.put('/updatePassword', json={
        'newPassword': new_password
    }, headers=auth_header)

    assert response.status_code == 200
    assert response.json['message'] == 'Password updated successfully'
    
    with app.app_context():
        user = User.query.filter_by(email=test_email).first()
        assert user.verify_password(new_password)


def test_delete_user(auth_client, app):
    client, auth_header, test_email = auth_client

    response = client.delete('/delete', headers=auth_header)

    assert response.status_code == 200
    assert response.json['message'] == 'User deleted successfully'
    
    with app.app_context():
        user = User.query.filter_by(email=test_email).first()
        assert user is None
