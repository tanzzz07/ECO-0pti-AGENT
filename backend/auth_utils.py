from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from models import User


def admin_required(fn):

    @wraps(fn)
    def wrapper(*args, **kwargs):

        user_id = int(get_jwt_identity())

        user = User.query.get(user_id)

        if not user:
            return jsonify({
                "error": "User not found"
            }), 404

        if user.role != "admin":
            return jsonify({
                "error": "Admin access required"
            }), 403

        return fn(*args, **kwargs)

    return wrapper