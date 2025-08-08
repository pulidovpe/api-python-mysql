from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User

user_bp = Blueprint('user', __name__)

@user_bp.route('/update', methods=['PUT'])
@jwt_required()
def update_user():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    fullname = data.get('fullname')
    email = data.get('email')

    user = User.query.get(current_user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    if fullname:
        user.fullname = fullname
    if email and email != user.email:
        if User.query.filter_by(email=email).first():
            return jsonify({'message': 'Email already in use'}), 400
        user.email = email

    db.session.commit()
    return jsonify({
        'message': 'User updated successfully',
        'dataUser': {'fullname': user.fullname, 'email': user.email},
        'auth': True
    }), 200

@user_bp.route('/updatePassword', methods=['PUT'])
@jwt_required()
def update_password():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    new_password = data.get('newPassword')

    if not new_password:
        return jsonify({'message': 'New password required'}), 400

    user = User.query.get(current_user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    user.password = sha256.hash(new_password)
    db.session.commit()
    return jsonify({'message': 'Password updated successfully', 'auth': True}), 200

@user_bp.route('/delete', methods=['DELETE'])
@jwt_required()
def delete_user():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'}), 200