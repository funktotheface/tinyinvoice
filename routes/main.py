from flask import Blueprint, render_template, request, send_file, current_app
from weasyprint  import HTML
import  io, os

# import DB model to record generated invoices
from models import db, Invoice


main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    return render_template('index.html')


@main_bp.route('/generate', methods=['POST'])
def generate_pdf():
    # Grab the form data
    data = request.form.to_dict(flat=False)  # flat=False keeps the item lists
    data  =  {k.rstrip('[]'): v for k, v in data.items()}
    logo_path = os.path.join(current_app.root_path, 'static', 'media', 'img', 'templateLogo.png')

    # Optionally persist a record that an invoice was created
    try:
        invoice = Invoice()
        db.session.add(invoice)
        db.session.commit()
    except Exception:
        # don't block PDF generation on DB errors
        db.session.rollback()

    # Render the HTML template for the invoice
    html = render_template('invoice_template.html', data=data, branding=True, logo_path=logo_path)


    # Generate the PDF
    pdf = HTML(string=html).write_pdf()


    # Send the PDF as a downloadable file
    return send_file(
        io.BytesIO(pdf),
        mimetype='application/pdf',
        as_attachment=True,
        download_name='invoice.pdf'
    )

