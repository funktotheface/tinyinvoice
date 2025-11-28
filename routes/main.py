from flask import Blueprint, render_template, request, send_file, current_app
from weasyprint  import HTML
from flask_login import login_required, current_user
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
    return f"<h1>Welcome, {current_user.email}!</h1>"

@main_bp.route('/pricing')
def pricing():
    return render_template('pricing.html')


@main_bp.route('/generate', methods=['POST'])
def generate_pdf():
    data = request.form.to_dict(flat=False)
    data = {k.rstrip('[]'): v for k, v in data.items()}
    logo_path = os.path.join(current_app.root_path, 'static', 'media', 'img', 'templateLogo.png')

    try:
        # 1. Create invoice
        invoice = Invoice(
            user_id=current_user.id,
            amount=float(data.get("total", 0))  # or however you get the invoice total
        )
        db.session.add(invoice)

        # 2. Update user stats (or create if first time)
        stats = UserStats.query.filter_by(user_id=current_user.id).first()
        if not stats:
            stats = UserStats(user_id=current_user.id)

        stats.total_invoices += 1
        stats.total_invoiced_amount += invoice.amount

        db.session.add(stats)
        db.session.commit()

    except Exception:
        db.session.rollback()

    html = render_template('invoice_template.html', data=data, branding=True, logo_path=logo_path)
    pdf = HTML(string=html).write_pdf()

    return send_file(
        io.BytesIO(pdf),
        mimetype='application/pdf',
        as_attachment=True,
        download_name='invoice.pdf'
    )


