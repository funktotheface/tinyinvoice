from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from sqlalchemy import func
import json

from models import db, Customer
from .decorators import pro_required

customers_bp = Blueprint('customers', __name__, url_prefix='/customers')


@customers_bp.route('/', methods=['GET'])
@login_required
@pro_required
def list_customers():
    """
    Display list of saved customers with search and tag filtering.
    """
    search_query = request.args.get('q', '').strip()
    tag_filter = request.args.get('tag', '').strip()
    
    query = current_user.customers
    
    # Search by name or email
    if search_query:
        query = query.filter(
            (Customer.name.ilike(f'%{search_query}%')) |
            (Customer.email.ilike(f'%{search_query}%'))
        )
    
    # Filter by tag (case-insensitive, comma-separated)
    if tag_filter:
        query = query.filter(Customer.tags.ilike(f'%{tag_filter}%'))
    
    customers = query.order_by(Customer.customer_number).all()
    
    # Extract all unique tags for filter dropdown
    all_tags = set()
    for cust in current_user.customers.all():
        if cust.tags:
            all_tags.update([t.strip() for t in cust.tags.split(',')])
    
    return render_template(
        'customers/list.html',
        customers=customers,
        search_query=search_query,
        tag_filter=tag_filter,
        all_tags=sorted(all_tags)
    )


@customers_bp.route('/create', methods=['GET', 'POST'])
@login_required
@pro_required
def create_customer():
    """
    Create a new saved customer.
    """
    if request.method == 'POST':
        try:
            # Get the next customer number for this user
            last_customer = current_user.customers.order_by(Customer.customer_number.desc()).first()
            next_number = (last_customer.customer_number + 1) if last_customer else 1
            
            customer = Customer(
                user_id=current_user.id,
                customer_number=next_number,
                name=request.form.get('name', '').strip(),
                email=request.form.get('email', '').strip(),
                phone=request.form.get('phone', '').strip(),
                address=request.form.get('address', '').strip(),
                user_field=request.form.get('user_field', '').strip(),
                tags=request.form.get('tags', '').strip()
            )
            
            if not customer.name:
                flash("Customer name is required.", "error")
                return redirect(url_for('customers.create_customer'))
            
            db.session.add(customer)
            db.session.commit()
            
            flash(f"Customer '{customer.name}' created successfully!", "success")
            return redirect(url_for('customers.list_customers'))
        
        except Exception as e:
            current_app.logger.error(f"Failed to create customer: {str(e)}")
            flash("Failed to create customer. Please try again.", "error")
    
    return render_template('customers/create.html', user_field_label='Custom Field')


@customers_bp.route('/<int:customer_id>/edit', methods=['GET', 'POST'])
@login_required
@pro_required
def edit_customer(customer_id):
    """
    Edit an existing customer.
    """
    customer = Customer.query.filter_by(id=customer_id, user_id=current_user.id).first_or_404()
    
    if request.method == 'POST':
        try:
            customer.name = request.form.get('name', '').strip()
            customer.email = request.form.get('email', '').strip()
            customer.phone = request.form.get('phone', '').strip()
            customer.address = request.form.get('address', '').strip()
            customer.user_field = request.form.get('user_field', '').strip()
            customer.tags = request.form.get('tags', '').strip()
            
            if not customer.name:
                flash("Customer name is required.", "error")
                return redirect(url_for('customers.edit_customer', customer_id=customer_id))
            
            db.session.commit()
            
            flash(f"Customer '{customer.name}' updated successfully!", "success")
            return redirect(url_for('customers.list_customers'))
        
        except Exception as e:
            current_app.logger.error(f"Failed to update customer: {str(e)}")
            flash("Failed to update customer. Please try again.", "error")
    
    return render_template('customers/edit.html', customer=customer, user_field_label='Custom Field')


@customers_bp.route('/<int:customer_id>/delete', methods=['POST'])
@login_required
@pro_required
def delete_customer(customer_id):
    """
    Delete a customer.
    """
    customer = Customer.query.filter_by(id=customer_id, user_id=current_user.id).first_or_404()
    customer_name = customer.name
    
    try:
        db.session.delete(customer)
        db.session.commit()
        
        flash(f"Customer '{customer_name}' deleted successfully!", "success")
    except Exception as e:
        current_app.logger.error(f"Failed to delete customer: {str(e)}")
        flash("Failed to delete customer. Please try again.", "error")
    
    return redirect(url_for('customers.list_customers'))
