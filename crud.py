from datetime import datetime, timedelta, time
from http.client import HTTPException
from typing import Optional

from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
import models
import schemas


# CRUD operations for Company
def get_company(db: Session, company_id: int):
    return db.query(models.Company).filter(models.Company.id == company_id).first()


def get_companies(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Company).offset(skip).limit(limit).all()


def create_company(db: Session, company: schemas.CompanyCreate):
    db_company = models.Company(**company.dict())
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company


# CRUD operations for BusinessHours

def get_business_hours(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.BusinessHours).offset(skip).limit(limit).all()

def create_business_hours(db: Session, business_hours: schemas.BusinessHoursCreate):
    """Crea un nuevo registro de Business Hours en la base de datos."""
    db_business_hours = models.BusinessHours(**business_hours.dict())
    db.add(db_business_hours)
    db.commit()
    db.refresh(db_business_hours)
    return db_business_hours


# CRUD operations for NonBusinessHours

def get_non_business_hours(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.NonBusinessHours).offset(skip).limit(limit).all()


def create_non_business_hours(db: Session, non_business_hours: schemas.NonBusinessHoursCreate, date):

    # Check for existing non-business hours with the same date

    try:
        db_non_business_hours = models.NonBusinessHours(
        **non_business_hours.dict(exclude={"dateClose"}),
        dateClose=date
        )
    except IntegrityError :
        db.rollback()
        db.refresh()
        raise ValueError('Value Exist')
    db.add(db_non_business_hours)
    db.commit()
    db.refresh(db_non_business_hours)
    return db_non_business_hours

# CRUD operations for Service
def get_service(db: Session, service_id: int):
    return db.query(models.Service).filter(models.Service.id == service_id).first()


def get_services(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Service).offset(skip).limit(limit).all()


def create_service(db: Session, service: schemas.ServiceCreate):
    db_service = models.Service(**service.dict())
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    return db_service


# CRUD operations for Appointment
def get_appointment(db: Session, appointment_id: int):
    return db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()


def get_appointments(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Appointment).offset(skip).limit(limit).all()


def create_appointment(db: Session, appointment: schemas.AppointmentCreate):
    # Obtenemos el servicio de la base de datos
    service = db.query(models.Service).filter(models.Service.name == appointment.nameservice).first()
    appointment_datetime_str = appointment.date + " " + appointment.time
    appointment_datetime = datetime.strptime(appointment_datetime_str, "%Y-%m-%d %H:%M:%S")
    # Verificamos si el servicio existe
    if not service:
        raise ValueError("Service not found")

    # Creamos la cita
    db_appointment = models.Appointment(
        **appointment.dict(exclude={"date", "time", "nameservice"}),
        service_id=service.id,
        date=appointment_datetime
    )
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment


def cancel_appointment(db: Session, appointment_id: int):
    appointment = db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()
    if appointment:
        db.delete(appointment)
        db.commit()
        return True
    return False


def get_appointments_by_date(db: Session, date: str):
    return db.query(models.Appointment).filter(models.Appointment.date == date).all()


# CRUD operations for Service

def get_service_by_name(db: Session, name: str):
    return db.query(models.Service).filter(models.Service.name == name).first()


def get_non_business_hours_by_date(db: Session, dateClose):
    return  db.query(models.NonBusinessHours).filter(models.NonBusinessHours.dateClose==dateClose)



def validate_business_hours(db: Session, date: str, time: str):
    # Convertir la fecha y la hora en un objeto datetime
    datetime_str = f"{date} {time}"

    appointment_datetime = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")

    # Verificar si la fecha está en las horas no laborables

    non_business_hours = db.query(models.NonBusinessHours).filter(
        models.NonBusinessHours.dateClose == appointment_datetime.date()).first()

    if non_business_hours:
        return False  # La fecha está en las horas no laborables, por lo tanto, no se pueden hacer citas

    # Obtener el objeto BusinessHours correspondiente a la fecha
    business_hours = db.query(models.BusinessHours).filter(models.BusinessHours.day_of_week == appointment_datetime.weekday()).first()

    if business_hours:
        # Validar si la hora de la cita está dentro del horario comercial
        if business_hours.opens_at <= appointment_datetime.time() <= business_hours.closes_at:
            return True
    return False


def check_availability(db: Session, date: str, nameservice: str, time: str):
    # Convert time to datetime object
    datetime_str = f"{date} {time}"  # Parse input format
    appointment_datetime = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
    service = db.query(models.Service).filter(models.Service.name == nameservice).first()
    if not service:
        return False

    # Calculate appointment end time
    duration = timedelta(minutes=service.duration)
    end_time_obj = (appointment_datetime + duration).time()
    # Check for existing appointments
    existing_appointments = db.query(models.Appointment).filter(
        models.Appointment.date == appointment_datetime.date(),
        models.Appointment.service_id == service.id
    ).all()

    for appointment in existing_appointments:
        start_datetime = appointment_datetime
        end_datetime = start_datetime + timedelta(minutes=service.duration)
        print(end_datetime)
        if start_datetime.time() < end_time_obj and end_datetime.time() > appointment.time():
            return False  # Overlap detected

    return True  # Available


def get_business_hours_by_weekday(db: Session, weekday: int) -> Optional[models.BusinessHours]:
    return db.query(models.BusinessHours).filter(models.BusinessHours.day_of_week == weekday).first()


def is_within_business_hours(time: time, opens_at: time, closes_at: time) -> bool:
    # Assuming time is a datetime.time object
    time_obj = datetime.strptime(time, "%H:%M:%S").time()
    return opens_at <= time_obj <= closes_at
