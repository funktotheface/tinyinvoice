from flask import Blueprint

auth_bp = Blueprint('auth', __name__)

# Optional test route
@auth_bp.route('/auth-test')
def auth_test():
    return "<h1>Auth Blueprint ✅</h1>"
