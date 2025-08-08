from flask import Blueprint, request, jsonify
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

    # Usamos el email del usuario como identidad en el JWT
    access_token = create_access_token(identity=user.email)
    return jsonify({'access_token': access_token}), 200
