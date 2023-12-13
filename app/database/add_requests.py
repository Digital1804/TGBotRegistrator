from app.database.models import *
from sqlalchemy import select, insert

from app.database.requests import  *
from app.database.get_scalar import *
from datetime import datetime

async def add_user(id, name):
    async with assync_session() as session:
        if await session.scalar(select(Customer).where(Customer.tg_id==id)) == None:
            res = await session.execute(insert(Customer).values(name=name, tg_id=id, join_date=datetime.now()))
            await session.commit()
            return res

async def add_record(user_id, data, time, service_id, branch_id, employee_id):
    async with assync_session() as session:
        date = datetime.strptime(data, '%d.%m.%Y').date()
        res = await session.execute(insert(Record).values(user_id=user_id, employee_id=employee_id, branch_id=branch_id, service_id=service_id, start_time=time, date=date, price=await get_price(service_id), confirm=False))
        await session.commit()
        return res