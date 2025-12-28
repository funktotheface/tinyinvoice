from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user

def pro_required(f):
    """
    Decorator to restrict access to Pro-only features.
    Redirects free users to /pricing with a message.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Please log in to access this feature.", "info")
            return redirect(url_for('auth.login'))
        
        if not current_user.is_pro():
            flash("This feature is only available for Pro subscribers. Upgrade now!", "warning")
            return redirect(url_for('main.pricing'))
        
        return f(*args, **kwargs)
    
    return decorated_function
