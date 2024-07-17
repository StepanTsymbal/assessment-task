import sys
import time
# from concurrent.futures import ThreadPoolExecutor

import pandas as pd

from . import schemas, crud
from .salesforce_connector import SalesforceConnector, get_auth_response

from datetime import datetime
import csv

import os
from dotenv import load_dotenv

CHUNK_SIZE = 10000


def init_creds():
    if not os.environ.get('DOCKER_ENV'):
        load_dotenv()


def create_customers_csv(customers=None):
    with open("customers_export_" + datetime.now().strftime("%d-%m-%Y_%H-%M-%S") + ".csv", "w", newline="") as f:
        # print('DEB:: f.name: ', f.name)
        # import os
        # print('DEB:: f.realpath: ', os.path.realpath(f.name))
        writer = csv.writer(f)
        writer.writerow(['customer_id', 'first_name', 'last_name', 'email', 'registration_date', 'total_spend',
                         'last_purchase_date'])
        for customer in customers:
            writer.writerow([customer.customer_id, customer.first_name, customer.last_name, customer.email,
                             customer.registration_date, customer.total_spend, customer.last_purchase_date])


def build_upsert_string(customers=None):
    data = """customer_id__c,firstName,lastName,email,registration_date__c,total_spend__c,last_purchase_date__c\n"""

    for customer in customers:
        row = (f"{customer.customer_id},"
               f"{get_empty_string_instead_none(customer.first_name)},"
               f"{get_empty_string_instead_none(customer.last_name)},"
               f"{get_empty_string_instead_none(customer.email)},"
               f"{get_empty_string_instead_none(customer.registration_date)},"
               f"{get_empty_string_instead_none(customer.total_spend)},"
               f"{get_empty_string_instead_none(customer.last_purchase_date)}\n")
        data += row

    return data


def get_empty_string_instead_none(value):
    return value if value is not None else ''


def get_final_result():
    print('WILL BE RUN UNTIL BULK JOB IS COMPLETE')


def sync_db_to_sf(session=None):
    CONSUMER_KEY = os.getenv('CONSUMER_KEY')
    CONSUMER_SECRET = os.getenv('CONSUMER_SECRET')
    USER_NAME = os.getenv('USER_NAME')
    TOKEN_URI = os.getenv('TOKEN_URI')

    # == PASSWORD + SECURITY_TOKEN
    PASSWORD = os.getenv('PASSWORD')
    API_VERSION = os.getenv('API_VERSION')
    EXTERNAL_ID_FIELD_NAME = os.getenv('EXTERNAL_ID_FIELD_NAME')
    OBJECT = os.getenv('OBJECT')

    customers = crud.get_customers(session)
    customers_string = build_upsert_string(customers)

    try:
        auth_response = get_auth_response(token_uri=TOKEN_URI, consumer_key=CONSUMER_KEY,
                                          consumer_secret=CONSUMER_SECRET, user_name=USER_NAME, password=PASSWORD)

        access_token = auth_response['access_token']
        instance_url = auth_response['instance_url']

        sf_connector = SalesforceConnector(api_version=API_VERSION, instance_url=instance_url,
                                           access_token=access_token)
        job_id = sf_connector.create_job(operation='upsert', external_id_field_name=EXTERNAL_ID_FIELD_NAME,
                                         obj=OBJECT)

        res = sf_connector.get_job_status(job_id=job_id, optype='ingest')
        content_url = res.json()['contentUrl']

        put_res = sf_connector.put_data(data=customers_string, content_url=content_url)
        patch_res = sf_connector.patch_state(job_id=job_id, state="UploadComplete")

        while res.json()['state'] not in ['JobComplete', 'Aborted', 'Failed']:
            print('DEB:: job state: ', res.json()['state'])
            time.sleep(0.5)
            res = sf_connector.get_job_status(job_id=job_id, optype='ingest')
        else:
            if res.json()['state'] == 'JobComplete' and res.json()['numberRecordsFailed'] == 0:
                print('DEB:: job state: ', res.json()['state'], ':: ALL GOOD')
            if res.json()['state'] == 'JobComplete' and res.json()['numberRecordsFailed'] != 0:
                print('DEB:: job state: ', res.json()['state'], ':: Complete with Errors: \n',
                      sf_connector.get_failure_status(job_id=job_id).content)
            if res.json()['state'] in ['Failed', 'Aborted']:
                print('DEB:: SMTH WENT WRONG')

        # with ThreadPoolExecutor(max_workers=4) as executor:
        #     a = executor.submit(get_job_status_async, job_id=job_id, sf_connector=sf_connector)
        #     b = executor.submit(get_final_result)

    except ConnectionError as error:
        print('Connection failed!', error)
        # return
    except:
        print("Unexpected error:", sys.exc_info()[0])


def get_customers_from_file(file=None, session=None):
    # file_bytes = file.file.read()
    # buffer = StringIO(file_bytes.decode('utf-8'))
    # csv_reader = csv.DictReader(buffer)
    # customers = [prep_customer(row) for row in csv_reader]
    #
    # return customers

    customers = []
    chunk_size = CHUNK_SIZE
    with pd.read_csv(file.file, chunksize=chunk_size) as reader:
        for chunk in reader:
            chunk = chunk.fillna('')
            customers = []
            for r in chunk.to_dict(orient='records'):
                customer = schemas.CustomerCreate(**r)
                customers.append(customer)

            crud.create_customers(session, customers)


def prep_customer(row):
    return schemas.CustomerCreate(**row)


def map_to_model(rows):
    customers = []
    for row in rows:
        customer = {'customer_id': row[0],
                    'first_name': row[1],
                    'last_name': row[2],
                    'total_spend': row[3],
                    }

        customers.append(customer)

    return customers

