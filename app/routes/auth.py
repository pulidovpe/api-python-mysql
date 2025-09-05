from flask import Blueprint, request, jsonify, current_app
from passlib.apps import custom_app_context as pwd_context
from flask_jwt_extended import create_access_token
from app import db
from app.models import User
from werkzeug.exceptions import BadRequest, Unauthorized

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    if not data or not data.get('email') or not data.get('password'):
        raise BadRequest('Email and password are required')

    if User.query.filter_by(email=data['email']).first():
        raise BadRequest('Email already registered')

    hashed_password = pwd_context.hash(data['password'])
    new_user = User(fullname=data.get('fullname'), email=data['email'], password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    # 🔹 Agrega el counter después de registrar con éxito
    current_app.request_counter.add(1, {"method": request.method, "endpoint": request.path})

    # Usamos el email del usuario como identidad en el JWT
    access_token = create_access_token(identity=new_user.email)
    return jsonify({'message': 'User created successfully', 'access_token': access_token}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data or not data.get('email') or not data.get('password'):
        raise BadRequest('Email and password are required')

    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not user.verify_password(data['password']):
        raise Unauthorized('Invalid credentials')

    # 🔹 Agrega el counter después de validar las credenciales con éxito
    current_app.request_counter.add(1, {"method": request.method, "endpoint": request.path})

    # Usamos el email del usuario como identidad en el JWT
    access_token = create_access_token(identity=user.email)
    return jsonify({'message': 'Login successful', 'access_token': access_token}), 200
