from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, Time, Date, DateTime

from database import Base


class Company(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)
    address = Column(String)
    phone = Column(String)
    url = Column(String)


class BusinessHours(Base):
    __tablename__ = "business_hours"

    id = Column(Integer, primary_key=True)
    day_of_week = Column(Integer)  # Monday, Tuesday, etc.
    opens_at = Column(Time)
    closes_at = Column(Time)
    company_id = Column(Integer, ForeignKey("companies.id"),nullable=False)


class NonBusinessHours(Base):
    __tablename__ = "non_business_hours"

    id = Column(Integer, primary_key=True)
    dateClose = Column(Date, unique=True)  # For specific dates like holidays
    reason = Column(String)  # Optional explanation for closure
    company_id = Column(Integer, ForeignKey("companies.id"),nullable=False)


class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    duration = Column(Integer)
    price = Column(Float)
    company_id = Column(Integer, ForeignKey("companies.id"),nullable=False )


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True)
    date = Column(DateTime)
    service_id = Column(Integer, ForeignKey("services.id"))
    customerName = Column(String)
    customerPhone = Column(String)
    status = Column(String)
    serviceDescrip=Column(String)
    company_id = Column(Integer, ForeignKey("companies.id"),nullable=False)
