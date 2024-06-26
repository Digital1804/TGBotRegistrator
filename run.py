import asyncio
import logging
import sys
from app import record_handlers
from app import control_handlers
from app.bot import *
from app.database.models import create_tables, create_data, drop_tables


async def main():
    #await drop_tables()
    await create_tables()
    #await create_data()
    dp.include_routers(record_handlers.router, control_handlers.router)
    loop = asyncio.get_event_loop()
    loop.create_task(control_handlers.remind())
    await dp.start_polling(bot)
    
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('exit')