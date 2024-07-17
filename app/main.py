from datetime import datetime
from typing import Annotated

from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session

from . import crud, schemas, utils

from .database import engine

from fastapi import Depends, FastAPI, UploadFile, BackgroundTasks, Query

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    utils.init_creds()


def get_session():
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()


@app.get("/customers/", response_model=list[schemas.Customer])
def read_customers(session: Session = Depends(get_session)):
    customers = crud.get_customers(session)

    return customers


@app.get("/customers/csv", response_model=list[schemas.Customer])
def read_customers(session: Session = Depends(get_session)):
    try:
        customers = crud.get_customers(session)
        utils.create_customers_csv(customers=customers)
    except Exception as error:
        return f"Smth went wrong:\n{error}"

    return customers


@app.post("/customers")
def add_customers(file: UploadFile, session: Session = Depends(get_session)):
    try:
        customers = utils.get_customers_from_file(file=file, session=session)
        # crud.create_customers(session, customers)

    except Exception as error:
        return f"Smth went wrong:\n{error}"

    return f'{file.filename} uploaded successfully'


@app.get("/analytics")
def get_analytics(start_date: Annotated[str, Query(regex='\d{4}-\d{2}-\d{2}')],
                  end_date: Annotated[str, Query(regex='\d{4}-\d{2}-\d{2}')],
                  session: Session = Depends(get_session)):
    try:
        start_date_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date_date = datetime.strptime(end_date, '%Y-%m-%d').date()

        return crud.get_analytics(session, start_date_date, end_date_date)
    except Exception as error:
        return f"Smth went wrong: {error}"


@app.post("/sync")
async def sync(background_tasks: BackgroundTasks, session: Session = Depends(get_session)):
    try:
        background_tasks.add_task(utils.sync_db_to_sf, session=session)
    except Exception as error:
        return f"Smth went wrong:\n{error}"

    return "Sync in Progress"
