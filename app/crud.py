from datetime import date

from sqlalchemy import func
from sqlalchemy.orm import Session
from . import models, schemas, utils
import sqlalchemy as db


def get_customers(session: Session):
    return session.query(models.Customers).all()


def create_customers(session: Session, customers: list[schemas.CustomerCreate]):
    db_customers = []
    for customer in customers:
        db_customer = models.Customers(first_name=customer.first_name,
                                       last_name=customer.last_name,
                                       email=customer.email,
                                       registration_date=customer.registration_date,
                                       total_spend=customer.total_spend,
                                       last_purchase_date=customer.last_purchase_date)

        db_customers.append(db_customer)
        session.add_all(db_customers)
        session.commit()
        session.refresh(db_customer)

    return db_customers


def get_analytics(session: Session, start_date: date, end_date: date):
    query_avg_total_spend = func.avg(models.Customers.total_spend)
    query_total_count = func.count(models.Customers.customer_id)
    query_active_count = func.count(models.Customers.last_purchase_date).filter(
        models.Customers.last_purchase_date >= start_date,
        models.Customers.last_purchase_date <= end_date
    )

    query_top_five_customers = db.select(
        models.Customers.customer_id,
        models.Customers.first_name,
        models.Customers.last_name,
        models.Customers.total_spend,
    ).limit(5).order_by(models.Customers.total_spend.desc())

    stats = session.query(query_avg_total_spend, query_total_count, query_active_count).all()

    customers = session.execute(query_top_five_customers).fetchall()
    top_customers = utils.map_to_model(customers)

    if stats[0][0] is None:
        average_total_spend = 0
    else:
        average_total_spend = round(stats[0][0], 2)

    if stats[0][1] == 0:
        active_customers_percentage = 0
    else:
        active_customers_percentage = round(stats[0][2] / stats[0][1] * 100, 1)

    data = {'average_total_spend': average_total_spend,
            'active_customers_percentage': active_customers_percentage,
            'top_customers': top_customers}

    return data
