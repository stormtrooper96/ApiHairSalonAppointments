from datetime import datetime, time

from pydantic import BaseModel
from typing import Optional


class CompanyBase(BaseModel):
    name: str
    address: str
    phone: str
    url: str


class CompanyCreate(CompanyBase):
    pass


class Company(CompanyBase):
    id: int

    class Config:
        orm_mode = True


class BusinessHoursBase(BaseModel):
    company_id: int

    day_of_week: int  # 1 for Monday, 2 for Tuesday, etc.
    opens_at: time
    closes_at: time


class BusinessHoursCreate(BaseModel):
    company_id: int
    day_of_week: int  # 1 for Monday, 2 for Tuesday, etc.
    opens_at: time
    closes_at: time



class BusinessHours(BusinessHoursBase):
    id: int

    class Config:
        orm_mode = True


class NonBusinessHoursBase(BaseModel):
    dateClose: str  # For specific dates like holidays
    company_id: int
    reason: Optional[str]  # Optional explanation for closure


class NonBusinessHoursCreate(NonBusinessHoursBase):
    dateClose: str
    company_id: int

    reason: Optional[str]  # Optional explanation for closure
class NonBusinessHoursResponse(NonBusinessHoursBase):
    dateClose: datetime
    company_id: int

    reason: Optional[str]  # Optional explanation for closure



class NonBusinessHours(NonBusinessHoursBase):
    id: int

    class Config:
        orm_mode = True


class ServiceBase(BaseModel):
    name: str
    duration: int
    price: float
    company_id: int



class ServiceCreate(ServiceBase):
    pass


class Service(ServiceBase):
    id: int

    class Config:
        orm_mode = True


class AppointmentBase(BaseModel):
    date: datetime
    customerName: str
    customerPhone: str
    status: str
    serviceDescrip: Optional[str]
    company_id: int



class AppointmentCreate(AppointmentBase):
    date: str
    time: str
    nameservice: str
    company_id: int
    customerName: str
    customerPhone: str
    status: str
    serviceDescrip: Optional[str]


class Appointment(AppointmentBase):
    id: int

    class Config:
        orm_mode = True
