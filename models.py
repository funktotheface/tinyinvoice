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
    password_hash = db.Column(db.String(128), nullable=True)
    google_sub = db.Column(db.String(255), unique=True, nullable=True)
    plan = db.Column(db.String(50), default='free')
    stripe_id = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    invoices = db.relationship("Invoice", back_populates="user", lazy="dynamic")
    stats = db.relationship("UserStats", back_populates="user", uselist=False)
    subscription = db.relationship("Subscription", back_populates="user", uselist=False)
    customers = db.relationship("Customer", back_populates="user", lazy="dynamic", cascade="all, delete-orphan")
    quotes = db.relationship("Quote", back_populates="user", lazy="dynamic", cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_pro(self):
        """Check if user has active Pro subscription."""
        if not self.subscription:
            return False
        return self.subscription.status == 'active' and self.subscription.current_period_end > datetime.utcnow()


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


class Subscription(db.Model):
    __tablename__ = 'subscriptions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    stripe_subscription_id = db.Column(db.String(255), unique=True)
    paypal_subscription_id = db.Column(db.String(255), unique=True)
    status = db.Column(db.String(50), default='active')  # active, paused, cancelled, past_due
    payment_method = db.Column(db.String(50))  # 'stripe' or 'paypal'
    stripe_payment_method_id = db.Column(db.String(255))  # Stripe payment method token
    paypal_email = db.Column(db.String(255))  # PayPal email for reference
    current_period_start = db.Column(db.DateTime)
    current_period_end = db.Column(db.DateTime)  # Subscription expires on this date
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    cancelled_at = db.Column(db.DateTime, nullable=True)

    user = db.relationship("User", back_populates="subscription")

    def __repr__(self):
        return f"<Subscription user_id={self.user_id} status={self.status}>"


class Customer(db.Model):
    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    customer_number = db.Column(db.Integer, nullable=False)  # Auto-increment per user
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.Text, nullable=True)
    user_field = db.Column(db.String(255), nullable=True)  # User-definable field (e.g., tax ID, company reg)
    tags = db.Column(db.String(500), nullable=True)  # Comma-separated tags for organization
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship("User", back_populates="customers")

    __table_args__ = (
        db.UniqueConstraint('user_id', 'customer_number', name='uq_user_customer_number'),
    )

    def __repr__(self):
        return f"<Customer id={self.id} name={self.name} user_id={self.user_id}>"


class Quote(db.Model):
    __tablename__ = 'quotes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=True)
    quote_number = db.Column(db.String(50), nullable=False)  # User-definable format, e.g. Q-2025-001
    client_name = db.Column(db.String(255), nullable=False)
    client_email = db.Column(db.String(255), nullable=True)
    business_name = db.Column(db.String(255), nullable=False)
    business_address = db.Column(db.Text, nullable=True)
    invoice_date = db.Column(db.DateTime, nullable=False)
    expiry_date = db.Column(db.DateTime, nullable=True)  # Quote expiration date
    total = db.Column(db.Numeric(12, 2), default=Decimal('0.00'))
    items_data = db.Column(db.Text, nullable=True)  # JSON-serialized items (descriptions, quantities, prices, etc.)
    status = db.Column(db.String(50), default='draft')  # draft, sent, accepted, converted, declined
    converted_invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship("User", back_populates="quotes")

    def __repr__(self):
        return f"<Quote id={self.id} quote_number={self.quote_number} user_id={self.user_id}>"
