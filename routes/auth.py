from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, current_user
from models import db, User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))  # or home page

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # check if email already exists
        if User.query.filter_by(email=email).first():
            flash("Email already registered.", "error")
            return redirect(url_for('auth.signup'))

        user = User(email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        login_user(user)
        return redirect(url_for('main.dashboard'))

    return render_template('signup.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            flash("Invalid email or password.", "error")
            return redirect(url_for('auth.login'))

        login_user(user)
        return redirect(url_for('main.dashboard'))

    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))
