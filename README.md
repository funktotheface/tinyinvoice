# TinyInvoice.me

**TinyInvoice** is a lightweight Flask web application for generating and managing invoices.
Designed to be flexible, fast and user firnedly, it allows users to create useable PDF invoices in seconds.
No signup is required to use the free or basic package, with the pro package offering extra benefits such as 
client management and invoice templates.

Users can pay for one off invoices or subscribe for unlimited use via stripe. 

##Table of Contents


- [Project Overview](#project-overview)
- [Project Structure](#project-structure)
- [Setup & Installation](#setup--installation)
- [Running the App](#running-the-app)
- [Blueprints & Templates](#blueprints--templates)
- [Common Issues & Fixes](#common-issues--fixes)

  ## Project Overview

  TinyInvoice uses Flask, a lightweight web framework as the application backbone.

  **Key Concepts**

  - **Flask app (`app.py`)** – Core engine, receives web requests and delegates them to Blueprints.
- **Blueprints** – Modular components that organize app functionality:
  - `main_bp` → homepage, invoice creation
  - `billing_bp` → payments and subscriptions
  - `auth_bp` → user authentication
- **Templates (`base.html`, `index.html`)** – HTML layouts with reusable headers and footers.
- **Virtual environment (`venv`)** – Isolates project dependencies.
- **Database (`tinyinvoice.db`)** – SQLite database for local development.
- **Extensions** – Tools to extend functionality:
  - SQLAlchemy (database)
  - Flask-Login (authentication)
  - WeasyPrint (PDF generation)
 
    ## Project Structure
 
    Initial project file structure should look like this

```text
tinyinvoice/
├── app.py # Core Flask app (engine room)
├── config.py # Configuration and environment variables
├── models.py # Database models
├── routes/ # Blueprints (modular route handling)
│ ├── init.py
│ ├── main.py
│ ├── billing.py
│ └── auth.py
├── templates/ # HTML templates
│ ├── base.html
│ ├── index.html
│ ├── invoice_template.html
│ ├── dashboard.html
│ └── login.html
├── static/ # CSS/JS assets
│ ├── css/
│ └── js/
├── instance/
│ └── tinyinvoice.db # SQLite database
├── .env # Environment variables (not committed)
├── requirements.txt # Python dependencies
├── README.md
└── venv/ # Virtual environment
```

## Setup & Installation

clone the repo:
```bash
cd /your/project/path
git clone https://github.com/funktotheface/tinyinvoice.git
cd tinyinvoice
```

Create & activate the virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate     # Linux/Mac
# venv\Scripts\activate      #Windows
```

Install dependencies:
```bash
pip intsall falsk weasyprint stripe gunicorn flask_sqlalchemy flask_login python python-dotenv
pip freeze > requirements.txt
```

## Running the App:
```bash
python app.py
````
Visit http://127.0.0.1:5000 in your browser.

You should see a confirmation page "TinyInvoice Main Blueprint"

## Blueprints & Templates
- Blueprints(main_bp, billing_bp, auth_bp) allow modular organization of routes.
- -Templates use Jinja2:
  ```jinja
  {% extends "base.html" %}     # inherit skeleton with header/footer
  {% block content %}     # page-specific content
  {% include "partial.html %}    # small reusable components like navigation menus
  ```

  **note:** Child templates call the parent (base.html), not the other way around. This keeps layouts consistent across pages.

  ## Common Issues & Fixes

  | Issue | Fix |
  |-------|-----|
  |VS Code shows flask could not be resolved|Ensure VS Code uses the venv interpreter: Ctrl+Shift+P → Python: Select Interpreter → pick venv/bin/python|
  |Blueprint import errors|Make sure each routes/*.py file defines a Blueprint, e.g.: main_bp = Blueprint('main', __name__)|
  |Terminal can’t activate venv|Check you created it in the project folder: python3 -m venv venv|
  |Permission denied when creating repo on external drive|Change folder ownership: sudo chown -R $USER:$USER /path/to/folder|
  



