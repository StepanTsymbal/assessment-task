import sqlalchemy as db
from sqlalchemy.orm import declarative_base

# from dotenv import load_dotenv
import os

from .models import Customers
from . import utils


utils.init_creds()

Base = declarative_base()

DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
DB_HOST = os.getenv('DB_HOST')

SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

engine = db.create_engine(SQLALCHEMY_DATABASE_URL)

Base.metadata.create_all(engine, tables=[Customers.__table__])