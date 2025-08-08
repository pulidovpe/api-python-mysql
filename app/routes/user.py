from flask import Blueprint, request, jsonify
from app.models.user import User
from passlib.apps import custom_app_context as pwd_context
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.exceptions import BadRequest, NotFound

user_bp = Blueprint('user', __name__)

@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    user_email = get_jwt_identity()
    user = User.query.filter_by(email=user_email).first()
    if not user:
        raise NotFound('User not found')

    return jsonify({
        'message': 'Profile retrieved successfully',
        'dataUser': {
            'id': user.id,
            'fullname': user.fullname,
            'email': user.email
        }
    }), 200

@user_bp.route('/getAllUsers', methods=['GET'])
@jwt_required()
def get_all_users():
    """Obtener lista de todos los usuarios (sin contraseñas)"""
    users = User.query.all()
    users_list = []
    
    for user in users:
        users_list.append({
            'id': user.id,
            'fullname': user.fullname,
            'email': user.email,
            'created_at': user.id  # Usando ID como referencia temporal
        })
    
    return jsonify({
        'message': 'Users retrieved successfully',
        'users': users_list,
        'total_users': len(users_list)
    }), 200

@user_bp.route('/update', methods=['PUT'])
@jwt_required()
def update_user():
    from app import db
    user_email = get_jwt_identity()
    user = User.query.filter_by(email=user_email).first()
    if not user:
        raise NotFound('User not found')

    data = request.get_json(silent=True)
    if not data:
        raise BadRequest('No data provided')
    if not any(key in data for key in ['fullname', 'email']):
        raise BadRequest('Fullname or email is required')

    if 'fullname' in data and data['fullname']:
        user.fullname = data['fullname']
    if 'email' in data and data['email']:
        if User.query.filter_by(email=data['email']).filter(User.id != user.id).first():
            raise BadRequest('Email already in use')
        user.email = data['email']

    db.session.commit()
    return jsonify({
        'message': 'User updated successfully',
        'dataUser': {'fullname': user.fullname, 'email': user.email}
    }), 200

@user_bp.route('/updatePassword', methods=['PUT'])
@jwt_required()
def update_password():
    from app import db
    user_email = get_jwt_identity()
    user = User.query.filter_by(email=user_email).first()
    if not user:
        raise NotFound('User not found')

    data = request.get_json(silent=True)
    if not data or not data.get('newPassword'):
        raise BadRequest('New password is required')

    user.password = pwd_context.hash(data['newPassword'])
    db.session.commit()
    return jsonify({'message': 'Password updated successfully'}), 200

@user_bp.route('/delete', methods=['DELETE'])
@jwt_required()
def delete_user():
    from app import db
    user_email = get_jwt_identity()
    user = User.query.filter_by(email=user_email).first()
    if not user:
        raise NotFound('User not found')

    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'}), 200

