from datetime import datetime
from decimal import Decimal
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash 

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    plan = db.Column(db.String(50), default='free')
    stripe_id = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    invoices = db.relationship("Invoice", back_populates="user", lazy="dynamic")
    stats = db.relationship("UserStats", back_populates="user", uselist=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Invoice(db.Model):
    __tablename__ = 'invoices'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Optional: link invoice → user (allow anonymous invoices)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', name='fk_invoices_user_id'), nullable=True)

    # Optional: store invoice total as fixed-point numeric (monetary)
    amount = db.Column(db.Numeric(12, 2), default=Decimal('0.00'))

    # Relationship back to User
    user = db.relationship("User", back_populates="invoices")

    def __repr__(self):
        return f"<Invoice id={self.id} user_id={self.user_id} created_at={self.created_at}>"


class UserStats(db.Model):
    __tablename__ = 'user_stats'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    total_invoices = db.Column(db.Integer, default=0)
    total_invoiced_amount = db.Column(db.Numeric(14, 2), default=Decimal('0.00'))
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="stats")
