from flask import Blueprint, render_template, request, send_file, current_app
from weasyprint  import HTML
from flask_login import login_required, current_user
from decimal import Decimal, ROUND_HALF_UP
import  io, os

# import DB model to record generated invoices
from models import db, Invoice, User, UserStats

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    return render_template('index.html')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    stats = UserStats.query.filter_by(user_id=current_user.id).first()
    invoices = (
        Invoice.query.filter_by(user_id=current_user.id)
        .order_by(Invoice.created_at.desc())
        .limit(5)
        .all()
    )
    return render_template('dashboard.html', stats=stats, invoices=invoices)

@main_bp.route('/pricing')
def pricing():
    return render_template('pricing.html')


@main_bp.route('/generate', methods=['POST'])
def generate_pdf():
    data = request.form.to_dict(flat=False)
    data = {k.rstrip('[]'): v for k, v in data.items()}
    logo_path = os.path.join(current_app.root_path, 'static', 'media', 'img', 'templateLogo.png')

    try:
        # Parse total safely (form fields come through as lists because flat=False)
        raw_total = data.get('total', [0])
        try:
            # Convert to Decimal via string to avoid binary float issues
            amount = Decimal(str(raw_total[0])) if isinstance(raw_total, list) else Decimal(str(raw_total))
            # Quantize to 2 decimal places using bankers/half-up rounding
            amount = amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        except Exception:
            amount = Decimal('0.00')

        # 1. Create invoice (allow anonymous if user not logged in)
        uid = current_user.id if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated else None
        invoice = Invoice(
            user_id=uid,
            amount=amount
        )
        db.session.add(invoice)

        # 2. Update user stats only for authenticated users
        if uid is not None:
            stats = UserStats.query.filter_by(user_id=uid).first()
            if stats:
                stats.total_invoices = (stats.total_invoices or 0) + 1
                prev = stats.total_invoiced_amount or Decimal('0.00')
                stats.total_invoiced_amount = prev + invoice.amount
                db.session.add(stats)
        db.session.commit()

    except Exception as e:
        # Log the exception so the real error is visible during debugging
        current_app.logger.exception('Error creating invoice or updating stats')
        db.session.rollback()

    html = render_template('invoice_template.html', data=data, branding=True, logo_path=logo_path)
    pdf = HTML(string=html).write_pdf()

    return send_file(
        io.BytesIO(pdf),
        mimetype='application/pdf',
        as_attachment=True,
        download_name='invoice.pdf'
    )


