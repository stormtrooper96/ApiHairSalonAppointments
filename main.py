from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from starlette.middleware.cors import CORSMiddleware

import crud
import models
import schemas
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/create-appointment/", response_model=schemas.Appointment)
def create_appointment(
    appointment: schemas.AppointmentCreate,
    db: Session = Depends(get_db)
):
    # Check if there's availability
    if not crud.check_availability(db,appointment.date,appointment.nameservice ,appointment.time):
        raise HTTPException(status_code=400, detail="No appointments available for the selected date")
    date_obj = datetime.strptime(appointment.date, "%Y-%m-%d").date()
        # Validate business hours based on day of week and time
    requested_weekday = date_obj.weekday() + 1  # Get weekday number (1-7)
    business_hours = crud.get_business_hours_by_weekday(db, requested_weekday)

    business_hoursAva = crud.validate_business_hours(db,date=date_obj,time=appointment.time)

    if not business_hoursAva:
        raise HTTPException(status_code=400, detail="Closed date")


    if not business_hours:
        raise HTTPException(status_code=400, detail="Invalid business hours for the selected day")

    if not crud.is_within_business_hours(appointment.time, business_hours.opens_at, business_hours.closes_at):
        raise HTTPException(status_code=400, detail="Appointment time is outside business hours")

    # Create appointment
    return crud.create_appointment(db=db, appointment=appointment)



@app.post("/create-non-business-hours/", response_model=schemas.NonBusinessHoursResponse)
def create_non_business_hours(
    non_business_hours: schemas.NonBusinessHoursCreate,
    db: Session = Depends(get_db)
):
    # Check if the non-business hours already exist
    date_obj = datetime.strptime(non_business_hours.dateClose, "%Y-%m-%d")
    if crud.get_non_business_hours_by_date(db, date_obj):
        raise HTTPException(status_code=400, detail="Non-business hours already exist for the selected date")

    # Create non-business hours
    return crud.create_non_business_hours(db=db, non_business_hours=non_business_hours,date=date_obj)


@app.post("/cancel-appointment/")
def cancel_appointment(
    appointment_id: int,
    db: Session = Depends(get_db)
):
    # Cancel appointment
    if not crud.cancel_appointment(db=db, appointment_id=appointment_id):
        raise HTTPException(status_code=404, detail="Appointment not found")
    return {"message": "Appointment cancelled successfully"}


@app.post("/create-service/", response_model=schemas.Service)
def create_service(
    service: schemas.ServiceCreate,
    db: Session = Depends(get_db)
):
    # Check if service already exists
    if crud.get_service_by_name(db, service.name):
        raise HTTPException(status_code=400, detail="Service already exists")

    if len(service.name)<5:
        raise HTTPException(status_code=400, detail="Service name is mandatory and must should up to 5 characters")
    if (service.duration<=0):
        raise HTTPException(status_code=400, detail="Service duration is mandatory and should up to 5")

    # Create service
    return crud.create_service(db=db, service=service)


@app.post("/create-company/", response_model=schemas.Company)
def create_company(
    company: schemas.CompanyCreate,
    db: Session = Depends(get_db)
):
    # Check if service already exists
    if crud.get_service_by_name(db, company.name):
        raise HTTPException(status_code=400, detail="Company already exists")

    # Create service
    return crud.create_company(db=db, company=company)
@app.get("/companies/", response_model=list[schemas.Company])
def getCompanies(
    db: Session = Depends(get_db)
):
    companies = crud.get_companies(db=db)
    return companies


@app.get("/appointments/", response_model=list[schemas.Appointment])
def get_appointments_by_date(
    date: str,
    db: Session = Depends(get_db)
):
    appointments = crud.get_appointments_by_date(db=db, date=date)
    return appointments

@app.get("/services/", response_model=list[schemas.Service])
def get_services(
    db: Session = Depends(get_db)
):
    services = crud.get_services(db=db)
    return services

@app.post("/business-hours/", response_model=schemas.BusinessHours)
def create_business_hours_route(
    business_hours: schemas.BusinessHoursCreate,
    db: Session = Depends(get_db)
):
    if crud.get_business_hours_by_weekday(db,business_hours.day_of_week):
        raise HTTPException(status_code=400, detail="day of week already exists")

    """Crea un nuevo registro de Business Hours a través de la API."""
    return crud.create_business_hours(db=db, business_hours=business_hours)