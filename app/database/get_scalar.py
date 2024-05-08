from app.database.models import *
from sqlalchemy import select
from app.database.requests import  *
async def get_spec(specialization_id):
    async with assync_session() as session:
        res = await session.scalar(select(Specialization.name).where(Specialization.id==specialization_id))
        return res

async def get_employee(employee_id):
    async with assync_session() as session:
        res = await session.scalar(select(Employee.name).where(Employee.id==employee_id))
        return res
    
async def get_branch(branch_id):
    async with assync_session() as session:
        res = await session.scalar(select(Branch.name).where(Branch.id==branch_id))
        return res
    
async def get_full_branch(branch_id):
    async with assync_session() as session:
        res = await session.scalar(select(Branch).where(Branch.id==branch_id))
        return res
    
async def get_service(service_id):
    async with assync_session() as session:
        res = await session.scalar(select(Services.name).where(Services.id==service_id))
        return res
    
async def get_time(time):
    async with assync_session() as session:
        res = await session.scalar(select(Timeslots.time).where(Timeslots.id==time))
        return res

async def get_price(service_id):
    async with assync_session() as session:
        price = await session.scalar(select(Services.price).where(Services.id==service_id))
        return price

async def get_record(rec_id):
    async with assync_session() as session:
        res = await session.scalar(select(Record).where(Record.id==rec_id))
        return res
    
async def get_close(close_id):
    async with assync_session() as session:
        res = await session.scalar(select(ClosedTime).where(ClosedTime.id==close_id))
        return res
    
async def get_similar_record(user_id, employee_id, service_id, branch_id):
    async with assync_session() as session:
        res = await session.scalar(select(Record).where(Record.user_id!=user_id).where(Record.employee_id==employee_id, Record.service_id==service_id, Record.branch_id==branch_id))
        return res