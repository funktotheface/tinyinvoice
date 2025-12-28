from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from decimal import Decimal
import stripe
import os

from models import db, Subscription, User
from .decorators import pro_required

billing_bp = Blueprint('billing', __name__, url_prefix='/billing')

# Initialize Stripe
stripe.api_key = current_app.config.get('STRIPE_SECRET_KEY') if current_app else os.getenv('STRIPE_SECRET_KEY')


@billing_bp.route('/upgrade', methods=['GET', 'POST'])
@login_required
def upgrade():
    """
    Display upgrade page with Stripe payment form and PayPal option.
    """
    if current_user.is_pro():
        flash("You already have an active Pro subscription!", "info")
        return redirect(url_for('main.dashboard'))
    
    stripe_public_key = current_app.config.get('STRIPE_PUBLIC_KEY')
    
    if request.method == 'POST':
        payment_method = request.form.get('payment_method')
        
        if payment_method == 'stripe':
            return redirect(url_for('billing.stripe_checkout'))
        elif payment_method == 'paypal':
            return redirect(url_for('billing.paypal_checkout'))
        
        flash("Invalid payment method.", "error")
    
    return render_template(
        'billing/upgrade.html',
        stripe_public_key=stripe_public_key,
        subscription_price=current_app.config.get('SUBSCRIPTION_PRICE_GBP', 4.99)
    )


@billing_bp.route('/stripe-checkout', methods=['GET', 'POST'])
@login_required
def stripe_checkout():
    """
    Initiate Stripe checkout for subscription.
    Uses Stripe Payment Element for card and PayPal payments.
    """
    try:
        # Create or retrieve Stripe customer
        if not current_user.stripe_id:
            customer = stripe.Customer.create(
                email=current_user.email,
                metadata={'user_id': current_user.id}
            )
            current_user.stripe_id = customer.id
            db.session.commit()
        
        # Create setup intent for payment method tokenization
        intent = stripe.SetupIntent.create(
            customer=current_user.stripe_id,
            payment_method_types=['card', 'paypal']
        )
        
        return render_template(
            'billing/stripe_checkout.html',
            client_secret=intent.client_secret,
            stripe_public_key=current_app.config.get('STRIPE_PUBLIC_KEY')
        )
    
    except Exception as e:
        current_app.logger.error(f"Stripe setup failed: {str(e)}")
        flash("Payment setup failed. Please try again.", "error")
        return redirect(url_for('billing.upgrade'))


@billing_bp.route('/stripe-checkout-complete', methods=['POST'])
@login_required
def stripe_checkout_complete():
    """
    Handle Stripe SetupIntent success and create subscription.
    """
    try:
        data = request.get_json()
        setup_intent_id = data.get('setup_intent_id')
        
        setup_intent = stripe.SetupIntent.retrieve(setup_intent_id)
        
        if setup_intent.status != 'succeeded':
            return jsonify({'error': 'Payment method setup failed'}), 400
        
        payment_method_id = setup_intent.payment_method
        
        # Create subscription
        subscription = stripe.Subscription.create(
            customer=current_user.stripe_id,
            items=[{
                'price_data': {
                    'currency': 'gbp',
                    'product_data': {
                        'name': 'TinyInvoice Pro',
                    },
                    'unit_amount': int(current_app.config.get('SUBSCRIPTION_PRICE_GBP', 4.99) * 100),
                    'recurring': {
                        'interval': 'month',
                        'interval_count': 4,  # 4-month billing cycle
                    }
                }
            }],
            default_payment_method=payment_method_id,
            off_session=True,
        )
        
        # Save subscription to DB
        sub = Subscription.query.filter_by(user_id=current_user.id).first()
        if not sub:
            sub = Subscription(user_id=current_user.id)
        
        sub.stripe_subscription_id = subscription.id
        sub.stripe_payment_method_id = payment_method_id
        sub.payment_method = 'stripe'
        sub.status = 'active'
        sub.current_period_start = datetime.fromtimestamp(subscription.current_period_start)
        sub.current_period_end = datetime.fromtimestamp(subscription.current_period_end)
        
        current_user.plan = 'pro'
        db.session.add(sub)
        db.session.commit()
        
        flash("Welcome to TinyInvoice Pro! Your subscription is active.", "success")
        return jsonify({'success': True, 'redirect': url_for('main.dashboard')})
    
    except Exception as e:
        current_app.logger.error(f"Stripe subscription creation failed: {str(e)}")
        return jsonify({'error': str(e)}), 400


@billing_bp.route('/paypal-checkout', methods=['GET', 'POST'])
@login_required
def paypal_checkout():
    """
    Initiate PayPal subscription setup.
    Placeholder for PayPal integration.
    """
    flash("PayPal integration coming soon!", "info")
    return redirect(url_for('billing.upgrade'))


@billing_bp.route('/manage', methods=['GET'])
@login_required
@pro_required
def manage_subscription():
    """
    Display subscription management page (view details, cancel, update payment method).
    """
    subscription = current_user.subscription
    
    if not subscription:
        flash("No active subscription found.", "warning")
        return redirect(url_for('main.dashboard'))
    
    return render_template(
        'billing/manage_subscription.html',
        subscription=subscription
    )


@billing_bp.route('/cancel', methods=['POST'])
@login_required
@pro_required
def cancel_subscription():
    """
    Cancel Pro subscription (user keeps access until period end).
    """
    subscription = current_user.subscription
    
    if not subscription:
        flash("No subscription to cancel.", "warning")
        return redirect(url_for('main.dashboard'))
    
    try:
        if subscription.payment_method == 'stripe':
            stripe.Subscription.delete(subscription.stripe_subscription_id)
        
        subscription.status = 'cancelled'
        subscription.cancelled_at = datetime.utcnow()
        db.session.commit()
        
        flash(f"Your Pro subscription has been cancelled. You'll have access until {subscription.current_period_end.strftime('%d %B %Y')}.", "info")
        return redirect(url_for('main.dashboard'))
    
    except Exception as e:
        current_app.logger.error(f"Subscription cancellation failed: {str(e)}")
        flash("Failed to cancel subscription. Please contact support.", "error")
        return redirect(url_for('billing.manage_subscription'))


@billing_bp.route('/webhook/stripe', methods=['POST'])
def stripe_webhook():
    """
    Handle Stripe webhook events (subscription updates, payment failures, etc).
    """
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    webhook_secret = current_app.config.get('STRIPE_WEBHOOK_SECRET')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError:
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError:
        return jsonify({'error': 'Invalid signature'}), 400
    
    # Handle subscription updates
    if event['type'] == 'customer.subscription.updated':
        subscription_data = event['data']['object']
        sub = Subscription.query.filter_by(stripe_subscription_id=subscription_data['id']).first()
        
        if sub:
            sub.current_period_end = datetime.fromtimestamp(subscription_data['current_period_end'])
            db.session.commit()
    
    elif event['type'] == 'customer.subscription.deleted':
        subscription_data = event['data']['object']
        sub = Subscription.query.filter_by(stripe_subscription_id=subscription_data['id']).first()
        
        if sub:
            sub.status = 'cancelled'
            sub.cancelled_at = datetime.utcnow()
            db.session.commit()
    
    return jsonify({'success': True}), 200

