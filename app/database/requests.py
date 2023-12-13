from app.database.models import *
from sqlalchemy import select, insert, delete, func

from datetime import datetime
   
    
async def close_time(employee_id, time, data, record_id):
    async with assync_session() as session:
        date = datetime.strptime(data, '%d.%m.%Y').date()
        res = await session.execute(insert(ClosedTime).values(employee_id=employee_id, time=time, day=date, record_id=record_id))
        await session.commit()
        return res 

        
async def delete_record(id):
    async with assync_session() as session:
        data = await session.scalar(select(Record.date).where(Record.id==id))
        time = await session.scalar(select(Record.start_time).where(Record.id==id))
        await session.execute(delete(ClosedTime).where(ClosedTime.day==data).where(ClosedTime.time==time))
        res = await session.execute(delete(Record).where(Record.id==id))
        await session.commit()
        return res