import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev")
    # Use an absolute path for the SQLite DB so sqlite can always locate it
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL") or f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'tinyinvoice.db')}"
    
    # Stripe Configuration
    STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
    STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY")
    STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
    
    # PayPal Configuration
    PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID")
    PAYPAL_CLIENT_SECRET = os.getenv("PAYPAL_CLIENT_SECRET")
    PAYPAL_MODE = os.getenv("PAYPAL_MODE", "sandbox")  # sandbox or live
    
    # Subscription Configuration
    SUBSCRIPTION_PRICE_GBP = 4.99  # £4.99 per month
    SUBSCRIPTION_BILLING_CYCLE_DAYS = 120  # 4 months = ~120 days

