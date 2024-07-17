import datetime
from datetime import date
from app.models import Customers
from app.crud import get_analytics, create_customers


# class TestModels:
def test_analytics(fake_db):
    customer1 = Customers(
        customer_id=1,
        email='test1@test.test',
        last_name='l_name1',
        total_spend=1000,
        last_purchase_date=date.today(),
        registration_date=date.today() + datetime.timedelta(days=10)
    )
    customer2 = Customers(
        customer_id=2,
        email='test2@test.test',
        last_name='l_name2',
        total_spend=2000,
        last_purchase_date=date.today(),
        registration_date=date.today() + datetime.timedelta(days=-10)
    )
    create_customers(fake_db, [customer2, customer1])
    analytics = get_analytics(fake_db, date.today(), date.today())

    assert analytics.get('average_total_spend') == (customer1.total_spend + customer2.total_spend)/2
    assert analytics.get('active_customers_percentage') == 100
    assert analytics.get('top_customers')[1].get('total_spend') == customer1.total_spend
