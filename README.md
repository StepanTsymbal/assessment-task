# **FastAPI REST API**

## Main features:
1. Read data from DB
2. Insert data into DB
3. Get analytics from DB
4. Sync DB records with SF

Can be run directly or via **docker-composer.yaml** build. 

#### !! When run directly, then set all the creds, configs, etc. in the **_.env_** file. Otherwise - use **_docker-compose.yaml_** file !!
#### !! When runing directly, you have to download required libraries from the **_requirements.txt_** file

## Prerequisites:

### SF org with:
1. ConnectedApp created
2. customer_id__c (Number, External Id), registration_date__c (Date), total_spend__c (Number), last_purchase_date__c(Number) custom fields on the Contact object

### In case of running the app directly:
1. PostgreSQL DB

## Preconfigs:
1. Set **DB_USER**, **DB_PASSWORD**, **DB_NAME** for the PostgreSQL instance
2. Set **CONSUMER_KEY**, **CONSUMER_SECRET**, **USER_NAME**, **TOKEN_URI** and **PASSWORD** (_{password}{security_token}_ format) for the SF instance

## App Run:
1. To run directly: _**fastapi dev app/main.py**_
2. To run via docker: _**docker compose up**_

Additional feature of the **docker-compose.yaml** build:
pgAdmin client for easy DB manipulation (run on **_localhost:8888/browser_**, creds are in the **docker-compose.yaml** file)


