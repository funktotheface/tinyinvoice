from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from routes.main import main_bp
from routes.billing import billing_bp
from routes.auth import auth_bp
from livereload import Server

app = Flask(__name__)
app.config.from_object('config.Config')
app.debug = True
db = SQLAlchemy(app)

# Register blueprints
app.register_blueprint(main_bp)
app.register_blueprint(billing_bp)
app.register_blueprint(auth_bp)

# Temp root route
@app.route('/')
def home():
    return "<h1>TinyInvoice is running!</h1>"

if __name__ == '__main__':
    server = Server(app.wsgi_app)
    server.watch('templates/**/*.html')
    server.watch('static/css/**/*.css')
    server.watch('static/js/**/*.js')
    server.serve(debug=True, port=5000, open_url_delay=1)

