from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app, send_file
from flask_login import login_required, current_user
from weasyprint import HTML
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
import json
import io
import os

from models import db, Quote, Customer, Invoice
from .decorators import pro_required

quotes_bp = Blueprint('quotes', __name__, url_prefix='/quotes')


@quotes_bp.route('/', methods=['GET'])
@login_required
@pro_required
def list_quotes():
    """
    Display list of quotes for the logged-in Pro user.
    """
    status_filter = request.args.get('status', '').strip()
    
    query = current_user.quotes
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    quotes = query.order_by(Quote.created_at.desc()).all()
    
    return render_template(
        'quotes/list.html',
        quotes=quotes,
        status_filter=status_filter
    )


@quotes_bp.route('/create', methods=['GET', 'POST'])
@login_required
@pro_required
def create_quote():
    """
    Create a new quote.
    """
    customers = current_user.customers.all()
    
    if request.method == 'POST':
        try:
            # Get form data
            quote_number = request.form.get('quote_number', '').strip()
            customer_id = request.form.get('customer_id', '')
            client_name = request.form.get('client_name', '').strip()
            client_email = request.form.get('client_email', '').strip()
            business_name = request.form.get('business_name', '').strip()
            business_address = request.form.get('business_address', '').strip()
            invoice_date = datetime.strptime(request.form.get('invoice_date', ''), '%Y-%m-%d')
            expiry_date_str = request.form.get('expiry_date', '').strip()
            expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d') if expiry_date_str else None
            
            # Validate required fields
            if not all([quote_number, client_name, business_name]):
                flash("Quote number, client name, and business name are required.", "error")
                return redirect(url_for('quotes.create_quote'))
            
            # Process items (same format as invoices)
            items_data = []
            item_descriptions = request.form.getlist('item_description[]')
            item_quantities = request.form.getlist('item_quantity[]')
            item_prices = request.form.getlist('item_price[]')
            
            total = Decimal('0.00')
            
            for desc, qty, price in zip(item_descriptions, item_quantities, item_prices):
                if desc and qty and price:
                    qty_val = Decimal(str(qty))
                    price_val = Decimal(str(price))
                    line_total = qty_val * price_val
                    total += line_total
                    
                    items_data.append({
                        'description': desc,
                        'quantity': str(qty_val),
                        'price': str(price_val),
                        'total': str(line_total)
                    })
            
            quote = Quote(
                user_id=current_user.id,
                customer_id=int(customer_id) if customer_id else None,
                quote_number=quote_number,
                client_name=client_name,
                client_email=client_email,
                business_name=business_name,
                business_address=business_address,
                invoice_date=invoice_date,
                expiry_date=expiry_date,
                total=total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
                items_data=json.dumps(items_data),
                status='draft'
            )
            
            db.session.add(quote)
            db.session.commit()
            
            flash(f"Quote '{quote_number}' created successfully!", "success")
            return redirect(url_for('quotes.list_quotes'))
        
        except Exception as e:
            current_app.logger.error(f"Failed to create quote: {str(e)}")
            flash("Failed to create quote. Please try again.", "error")
    
    return render_template('quotes/create.html', customers=customers)


@quotes_bp.route('/<int:quote_id>/edit', methods=['GET', 'POST'])
@login_required
@pro_required
def edit_quote(quote_id):
    """
    Edit an existing quote.
    """
    quote = Quote.query.filter_by(id=quote_id, user_id=current_user.id).first_or_404()
    customers = current_user.customers.all()
    items = json.loads(quote.items_data) if quote.items_data else []
    
    if request.method == 'POST':
        try:
            quote.quote_number = request.form.get('quote_number', '').strip()
            quote.client_name = request.form.get('client_name', '').strip()
            quote.client_email = request.form.get('client_email', '').strip()
            quote.business_name = request.form.get('business_name', '').strip()
            quote.business_address = request.form.get('business_address', '').strip()
            quote.invoice_date = datetime.strptime(request.form.get('invoice_date', ''), '%Y-%m-%d')
            
            expiry_date_str = request.form.get('expiry_date', '').strip()
            quote.expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d') if expiry_date_str else None
            
            # Reprocess items
            items_data = []
            item_descriptions = request.form.getlist('item_description[]')
            item_quantities = request.form.getlist('item_quantity[]')
            item_prices = request.form.getlist('item_price[]')
            
            total = Decimal('0.00')
            
            for desc, qty, price in zip(item_descriptions, item_quantities, item_prices):
                if desc and qty and price:
                    qty_val = Decimal(str(qty))
                    price_val = Decimal(str(price))
                    line_total = qty_val * price_val
                    total += line_total
                    
                    items_data.append({
                        'description': desc,
                        'quantity': str(qty_val),
                        'price': str(price_val),
                        'total': str(line_total)
                    })
            
            quote.items_data = json.dumps(items_data)
            quote.total = total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            
            db.session.commit()
            
            flash(f"Quote '{quote.quote_number}' updated successfully!", "success")
            return redirect(url_for('quotes.list_quotes'))
        
        except Exception as e:
            current_app.logger.error(f"Failed to update quote: {str(e)}")
            flash("Failed to update quote. Please try again.", "error")
    
    return render_template('quotes/edit.html', quote=quote, items=items, customers=customers)


@quotes_bp.route('/<int:quote_id>/preview', methods=['GET'])
@login_required
@pro_required
def preview_quote(quote_id):
    """
    Preview quote as PDF (does not convert to invoice).
    """
    quote = Quote.query.filter_by(id=quote_id, user_id=current_user.id).first_or_404()
    items = json.loads(quote.items_data) if quote.items_data else []
    
    return render_template(
        'quote_template.html',
        quote=quote,
        items=items,
        is_preview=True
    )


@quotes_bp.route('/<int:quote_id>/download', methods=['GET'])
@login_required
@pro_required
def download_quote_pdf(quote_id):
    """
    Download quote as PDF.
    """
    quote = Quote.query.filter_by(id=quote_id, user_id=current_user.id).first_or_404()
    items = json.loads(quote.items_data) if quote.items_data else []
    
    logo_path = os.path.join(current_app.root_path, 'static', 'media', 'img', 'templateLogo.png')
    
    html_content = render_template(
        'quote_template.html',
        quote=quote,
        items=items,
        logo_path=logo_path,
        is_download=True
    )
    
    pdf = HTML(string=html_content).write_pdf()
    
    return send_file(
        io.BytesIO(pdf),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f"quote_{quote.quote_number}.pdf"
    )


@quotes_bp.route('/<int:quote_id>/convert-to-invoice', methods=['POST'])
@login_required
@pro_required
def convert_to_invoice(quote_id):
    """
    Convert a quote to an invoice.
    """
    quote = Quote.query.filter_by(id=quote_id, user_id=current_user.id).first_or_404()
    
    try:
        # Create invoice from quote data
        invoice = Invoice(
            user_id=current_user.id,
            amount=quote.total
        )
        
        quote.status = 'converted'
        quote.converted_invoice_id = invoice.id
        
        db.session.add(invoice)
        db.session.commit()
        
        # Update user stats
        from models import UserStats
        stats = UserStats.query.filter_by(user_id=current_user.id).first()
        if stats:
            stats.total_invoices += 1
            stats.total_invoiced_amount += invoice.amount
            db.session.commit()
        
        flash(f"Quote '{quote.quote_number}' converted to Invoice #{invoice.id}!", "success")
        return redirect(url_for('quotes.list_quotes'))
    
    except Exception as e:
        current_app.logger.error(f"Failed to convert quote to invoice: {str(e)}")
        flash("Failed to convert quote. Please try again.", "error")
        return redirect(url_for('quotes.list_quotes'))


@quotes_bp.route('/<int:quote_id>/delete', methods=['POST'])
@login_required
@pro_required
def delete_quote(quote_id):
    """
    Delete a quote.
    """
    quote = Quote.query.filter_by(id=quote_id, user_id=current_user.id).first_or_404()
    quote_number = quote.quote_number
    
    try:
        db.session.delete(quote)
        db.session.commit()
        
        flash(f"Quote '{quote_number}' deleted successfully!", "success")
    except Exception as e:
        current_app.logger.error(f"Failed to delete quote: {str(e)}")
        flash("Failed to delete quote. Please try again.", "error")
    
    return redirect(url_for('quotes.list_quotes'))
