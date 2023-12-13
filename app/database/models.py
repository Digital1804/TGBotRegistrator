from sqlalchemy import BigInteger, Boolean
from sqlalchemy.orm import relationship, mapped_column, Mapped, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.schema import ForeignKey
from config import DATABASE_URL
from sqlalchemy import String, DATE, DATETIME, TIME
from typing import List
from datetime import datetime
engine = create_async_engine(DATABASE_URL, echo=True)

assync_session = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase, AsyncAttrs):
    pass

class Branch(Base):
    __tablename__ = 'branches'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String)
    address: Mapped[str] = mapped_column(String)
    phone: Mapped[int] = mapped_column(BigInteger)
    
class Customer(Base):
    __tablename__ = 'custumers'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String)
    tg_id = mapped_column(BigInteger)
    join_date = mapped_column(DATETIME)
    phone = mapped_column(BigInteger)
    
class Employee(Base):
    __tablename__ = 'employees'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String)
    specialization_id: Mapped[int] = mapped_column(ForeignKey("specializations.id"))
    join_date = mapped_column(DATE)
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"))
    
class Specialization(Base):
    __tablename__ = 'specializations'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    
class Services(Base):
    __tablename__ = 'services'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String)
    price: Mapped[int] = mapped_column(BigInteger)
    specialization_id: Mapped[int] = mapped_column(ForeignKey("specializations.id"))
    
class BranchToService(Base):
    __tablename__ = 'branch_to_service'
    id: Mapped[int] = mapped_column(primary_key=True)
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"))
    service_id: Mapped[int] = mapped_column(ForeignKey("services.id"))

class EmployeeToService(Base):
    __tablename__ = 'employee_to_service'
    id: Mapped[int] = mapped_column(primary_key=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"))
    service_id: Mapped[int] = mapped_column(ForeignKey("services.id"))

class Shedule(Base):
    __tablename__ = 'shedule'
    id: Mapped[int] = mapped_column(primary_key=True)
    from_time = mapped_column(TIME)
    launch_time  = mapped_column(TIME)
    till_time = mapped_column(TIME)
    weekday: Mapped[str] = mapped_column(String)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"))

class Record(Base):
    __tablename__ = 'records'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id = mapped_column(ForeignKey("custumers.id"))
    date = mapped_column(DATE)
    start_time = mapped_column(TIME)
    service_id = mapped_column(ForeignKey("services.id"))
    branch_id = mapped_column(ForeignKey("branches.id"))
    employee_id = mapped_column(ForeignKey("employees.id"))
    discription = mapped_column(String)
    price = mapped_column(BigInteger)
    confirm = mapped_column(Boolean)
    
class ClosedTime(Base):
    __tablename__ = 'closed_time'
    id: Mapped[int] = mapped_column(primary_key=True)
    day = mapped_column(DATE)
    time = mapped_column(TIME)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"))
    record_id = mapped_column(ForeignKey("records.id"))
    
class Timeslots(Base):
    __tablename__ = 'time_slots'
    id: Mapped[int] = mapped_column(primary_key=True)
    time = mapped_column(TIME)

async def drop_tables():
    assync_session.configure(bind=engine)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    
async def create_tables(): 
    assync_session.configure(bind=engine)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def create_data():
    assync_session.configure(bind=engine)
    async with assync_session() as session:
        session.add_all([
            Branch(name="Барабанная", address="г. Новосибирск, ул. Барабанная, д. 1", phone= 83838815090),
            Branch(name="Садовая", address="г. Новосибирск, ул. Садовая, д. 2", phone= 83838834568),
            Specialization(name="Кардиология"),
            Specialization(name="Травматология"),
            Services(name="Кардиологический осмотр", price=100, specialization_id=1),
            Services(name="Вывих", price=100, specialization_id=2),
            Services(name="Вправление", price=100, specialization_id=2),
            Employee(name="Иван Петоров", specialization_id=2, join_date=datetime.strptime("01-01-2022", '%m-%d-%Y').date(), branch_id=2),
            Employee(name="Петр Иванов", specialization_id=2, join_date=datetime.strptime("01-01-2022", '%m-%d-%Y').date(), branch_id=2),
            Employee(name="Иван Сидоров", specialization_id=1, join_date=datetime.strptime("01-01-2022", '%m-%d-%Y').date(), branch_id=1),
            EmployeeToService(employee_id=1, service_id=2),
            EmployeeToService(employee_id=1, service_id=3),
            EmployeeToService(employee_id=2, service_id=2),
            EmployeeToService(employee_id=2, service_id=3),
            EmployeeToService(employee_id=3, service_id=1),
            BranchToService(branch_id=1, service_id=1),
            BranchToService(branch_id=2, service_id=2),
            BranchToService(branch_id=2, service_id=3),
            Shedule(from_time=datetime.strptime("08:00:00", '%H:%M:%S').time(), launch_time=datetime.strptime("12:00:00", '%H:%M:%S').time(), till_time=datetime.strptime("20:00:00", '%H:%M:%S').time(), weekday="Понедельник", employee_id=3),
            Shedule(from_time=datetime.strptime("08:00:00", '%H:%M:%S').time(), launch_time=datetime.strptime("12:00:00", '%H:%M:%S').time(),till_time=datetime.strptime("20:00:00", '%H:%M:%S').time(), weekday="Понедельник", employee_id=1),
            Shedule(from_time=datetime.strptime("08:00:00", '%H:%M:%S').time(), launch_time=datetime.strptime("12:00:00", '%H:%M:%S').time(),till_time=datetime.strptime("20:00:00", '%H:%M:%S').time(), weekday="Вторник", employee_id=1),
            Shedule(from_time=datetime.strptime("08:00:00", '%H:%M:%S').time(), launch_time=datetime.strptime("12:00:00", '%H:%M:%S').time(),till_time=datetime.strptime("16:00:00", '%H:%M:%S').time(), weekday="Среда", employee_id=2),
            Shedule(from_time=datetime.strptime("08:00:00", '%H:%M:%S').time(), launch_time=datetime.strptime("12:00:00", '%H:%M:%S').time(),till_time=datetime.strptime("17:00:00", '%H:%M:%S').time(), weekday="Четверг", employee_id=2),
            Timeslots(time=datetime.strptime("08:00:00", '%H:%M:%S').time()),
            Timeslots(time=datetime.strptime("09:00:00", '%H:%M:%S').time()),
            Timeslots(time=datetime.strptime("10:00:00", '%H:%M:%S').time()),
            Timeslots(time=datetime.strptime("11:00:00", '%H:%M:%S').time()),
            Timeslots(time=datetime.strptime("12:00:00", '%H:%M:%S').time()),
            Timeslots(time=datetime.strptime("13:00:00", '%H:%M:%S').time()),
            Timeslots(time=datetime.strptime("14:00:00", '%H:%M:%S').time()),
            Timeslots(time=datetime.strptime("15:00:00", '%H:%M:%S').time()),
            Timeslots(time=datetime.strptime("16:00:00", '%H:%M:%S').time()),
            Timeslots(time=datetime.strptime("17:00:00", '%H:%M:%S').time()),
            Timeslots(time=datetime.strptime("18:00:00", '%H:%M:%S').time()),
            Timeslots(time=datetime.strptime("19:00:00", '%H:%M:%S').time()),
            Timeslots(time=datetime.strptime("20:00:00", '%H:%M:%S').time())
            #Record(user_id=732791195, date=datetime.strptime("01-01-2022", '%m-%d-%Y').date(), start_time=datetime.strptime("08:00:00", '%H:%M:%S').time(), service_id=1, branch_id=1, employee_id=1, price=100)
        ])
        await session.commit()
            
            