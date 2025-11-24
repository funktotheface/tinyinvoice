from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

# central SQLAlchemy object; will be initialized from app
db = SQLAlchemy()


class Invoice(db.Model):
	__tablename__ = 'invoices'
	id = db.Column(db.Integer, primary_key=True)
	created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

	def __repr__(self):
		return f"<Invoice id={self.id} created_at={self.created_at}>"
