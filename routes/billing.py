from flask import Blueprint

billing_bp = Blueprint('billing', __name__)

# Optional test route
@billing_bp.route('/billing-test')
def billing_test():
    return "<h1>Billing Blueprint ✅</h1>"
