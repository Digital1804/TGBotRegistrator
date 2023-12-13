from aiogram import Bot, Dispatcher
import asyncio
import logging
import sys
from config import TOKEN
from app.handlers import router
from app.database.models import create_tables, create_data, drop_tables

async def main():
    #await drop_tables()
    await create_tables()
    #await create_data()
    bot = Bot(token=TOKEN, parse_mode='HTML')
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)
    
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('exit')