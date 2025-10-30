from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from routes.main import main_bp
from routes.billing import billing_bp
from routes.auth import auth_bp



#initialize flask

app = Flask(__name__)
app.config.from_object('config.Config')

#initialize extensions

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'

#import and register blueprints

from routes.main import main_bp
from routes.billing import billing_bp
from routes.auth import auth_bp

app.register_blueprint(main_bp)
app.register_blueprint(billing_bp)
app.register_blueprint(auth_bp)

#temp root route for testing
@app.route('/')
def home():
    return "<h1>TinyInvoice is runnning!</h1>"

if __name__ == '__main__':
    app.run(debug=True)
