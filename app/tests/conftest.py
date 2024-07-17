import os
# from dotenv import load_dotenv
import pytest
from sqlalchemy.orm import sessionmaker, declarative_base
import sqlalchemy as db
from app.models import Customers
import app.utils as utils


def db_prep():
    utils.init_creds()
    # Base = declarative_base()
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    # DB_NAME = os.getenv('DB_NAME')
    DB_NAME = f"{os.getenv('DB_NAME')}_test"
    DB_HOST = os.getenv('DB_HOST')

    SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

    engine = db.create_engine(SQLALCHEMY_DATABASE_URL)
    # Base.metadata.create_all(engine, tables=[Customers.__table__])

    return engine


@pytest.fixture(scope="session", autouse=True)
def fake_db():
    engine = db_prep()
    Base = declarative_base()
    Base.metadata.create_all(engine, tables=[Customers.__table__])
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()
        # Base = declarative_base()
        Base.metadata.drop_all(engine, tables=[Customers.__table__])
