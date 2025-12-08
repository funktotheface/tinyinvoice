from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from flask_login import login_user, logout_user, current_user
from models import db, User

YOUR_GOOGLE_CLIENT_ID = "492092696854-rhr0b7vfttgi1podj7ro35hr43p2af9e.apps.googleusercontent.com"

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

    return render_template('login.html', google_client_id=YOUR_GOOGLE_CLIENT_ID)

@auth_bp.route('/google_onetap', methods=['POST'])
def google_onetap():
    data = request.get_json()

    credential = data.get("credential")
    if not credential:
        return jsonify({"success": False, "error": "Missing credential"}), 400

    try:
        # Verify JWT from Google
        idinfo = id_token.verify_oauth2_token(
            credential,
            google_requests.Request(),
            YOUR_GOOGLE_CLIENT_ID
        )

        google_sub = idinfo["sub"]
        email = idinfo["email"]

        # 1️⃣ Look up user by Google account
        user = User.query.filter_by(google_sub=google_sub).first()

        if not user:
            # 2️⃣ If email already exists, link the Google account
            existing_email_user = User.query.filter_by(email=email).first()

            if existing_email_user:
                user = existing_email_user
                user.google_sub = google_sub
            else:
                # 3️⃣ Create a brand-new user
                user = User(
                    email=email,
                    google_sub=google_sub,
                    password_hash=None
                )
                db.session.add(user)

            db.session.commit()

        login_user(user)

        return jsonify({"success": True, "redirect": "/dashboard"})

    except Exception as e:
        print("Google verification error:", e)
        return jsonify({"success": False, "error": str(e)}), 400


@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

