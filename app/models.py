import sqlalchemy as db
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Customers(Base):
    __tablename__ = 'customers'

    customer_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, server_default=None)
    last_name = db.Column(db.String)
    email = db.Column(db.String, unique=True)
    registration_date = db.Column(db.Date, server_default=db.func.now())
    total_spend = db.Column(db.Float, server_default='0.00')
    last_purchase_date = db.Column(db.Date, server_default=None, nullable=True)


