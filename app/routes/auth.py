from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from app import db
from app.models.user import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/', methods=['GET'])
def index():
    return jsonify({'response': 'Flask RESTful API'})

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    fullname = data.get('fullname')
    email = data.get('email')
    password = data.get('password')

    if not all([fullname, email, password]):
        return jsonify({'message': 'Missing fields'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'User already exists'}), 400

    new_user = User(fullname, email, password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User created successfully', 'dataUser': {'fullname': fullname, 'email': email}}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()
    if not user or not user.verify_password(password):
        return jsonify({'message': 'Invalid credentials'}), 401

    access_token = create_access_token(identity=user.id)
    return jsonify({
        'auth': True,
        'dataUser': {'fullname': user.fullname, 'email': user.email},
        'access_token': access_token
    }), 200