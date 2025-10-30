from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    return "<h1>TinyInvoice Main Blueprint ✅</h1>"
