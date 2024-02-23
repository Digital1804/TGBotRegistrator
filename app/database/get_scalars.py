from app.database.models import *
from sqlalchemy import select

from app.database.requests import  *

day_name = {
    0: "Понедельник",
    1: "Вторник",
    2: "Среда",
    3: "Четверг",
    4: "Пятница",
    5: "Суббота",
    6: "Воскресенье"
}
async def get_specializations():
    async with assync_session() as session:
        res = await session.scalars(select(Specialization))
        return res
    
async def get_services(spec_id):
    async with assync_session() as session:
        res = await session.scalars(select(Services).where(Services.specialization_id==spec_id))
        return res
     
async def get_branchs(serv_id):
    async with assync_session() as session:
        res = await session.scalars(select(Branch).where(Branch.id.in_(select(BranchToService.branch_id).where(BranchToService.service_id==serv_id))))
        return res
    
async def get_all_branchs():
    async with assync_session() as session:
        res = await session.scalars(select(Branch))
        return res
    
async def get_employees(branch_id, serv_id):
    async with assync_session() as session:
        res = await session.scalars(select(Employee).where(Employee.id.in_(select(EmployeeToService.employee_id).where(BranchToService.service_id==serv_id))).where(Employee.branch_id==branch_id))
        return res
    
async def get_employee_workdays(employee_id):
    async with assync_session() as session:
        res = await session.scalars(select(Shedule.weekday).where(Shedule.employee_id==employee_id))
        return res

async def get_dates(employee_id):
    async with assync_session() as session:
        res = await session.scalars(select(Shedule).where(Shedule.employee_id==employee_id))
        return res
    
async def get_times(employee_id, data):
    async with assync_session() as session:
        date = datetime.strptime(data, '%d.%m.%Y').date()
        day = date.weekday()
        beg = await session.scalar(select(Shedule.from_time).where(Shedule.employee_id==employee_id).where(Shedule.weekday == day_name[day]))
        fin = await session.scalar(select(Shedule.till_time).where(Shedule.employee_id==employee_id).where(Shedule.weekday == day_name[day]))
        launch = await session.scalar(select(Shedule.launch_time).where(Shedule.employee_id==employee_id))
        closed_times = await session.scalars(select(ClosedTime.time).where(ClosedTime.employee_id==employee_id).where(ClosedTime.day==date))
        res = await session.scalars(select(Timeslots).where(Timeslots.time >= beg).where(Timeslots.time <= fin).where(Timeslots.time != launch).where(Timeslots.time.not_in(closed_times)))
        return res    
 
async def get_records(user_id):
    async with assync_session() as session:
        res = await session.scalars(select(Record).where(Record.user_id==user_id))
        return res.all()
    
    