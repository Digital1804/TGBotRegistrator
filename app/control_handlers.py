from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from asyncio import sleep as asleep
from datetime import timedelta
import app.keyboards as kb
from app.database.requests import  *
from app.database.add_requests import  *
from app.database.get_scalar import *
from app.database.get_scalars import *
from app.bot import bot
router = Router()

async def remind():
    while True:
        records = await get_close_records()
        for record in records:
            date = record.date.strftime("%d.%m.%Y")
            employee = await get_employee(record.employee_id)
            time = str(record.start_time)[:5]
            await bot.send_message(chat_id=record.user_id, text=f'Подтверждаете запись?\n{date} в {time}\nВрач: {employee}\n', reply_markup=await kb.yes_no_mind(record.id))
        await asleep(60*60*12)
#a function for offering other clients to sign up for a special time  
@router.channel_post()
async def offer_time(record):
    custumer = await get_similar_record(record.user_id, record.employee_id, record.service_id, record.branch_id)
    employee = await get_employee(custumer.employee_id)
    time = str(record.start_time)[:5]
    await bot.send_message(chat_id=custumer.user_id, text=f'На вашу услугу сободна запись \n{date} в {time}\nВрач: {employee}\nНе хотите прийти в это время?', reply_markup=await kb.yes_no_offer(record.id))

@router.message(F.text.contains("Мои записи"))
async def my_records(message: Message):
    records = await get_records(message.chat.id)
    if records != []:
        for record in records:
            date = record.date.strftime("%d.%m.%Y")
            time = str(record.start_time)[:5]
            await message.answer(f'{date} в {time}\nВрач: {await get_employee(record.employee_id)}\n')
    else:
        await message.answer("У вас нет записей")
    
    
@router.message(F.text.contains("Контакты"))
async def contacts(message: Message):
    await message.answer("Наши контакты", reply_markup=await kb.contacts())
    
@router.callback_query(F.data.startswith('contbranch_'))
async def cont_callback(callback: CallbackQuery):
    branch = await get_full_branch(int(callback.data.split('_')[1]))
    await callback.message.answer(f"<b>Адрес: </b>{branch.address}\n\n<b>Телефон регистратуры: </b><code>{branch.phone}</code>")

@router.message(F.text.contains("Отменить прием"))
async def cancel(message: Message):
    await message.answer("Выберите запись для отмены", reply_markup=await kb.records(message.from_user.id))
    
@router.callback_query(F.data.startswith('record_'))
async def cancel_record(callback: CallbackQuery):
    button_id = 'record_'
    record_id = int(callback.data.split('_')[1])
    await callback.message.answer("Вы уверены что хотите отменить прием?", reply_markup=await kb.yes_no_delete(record_id))
    await callback.answer('')

           
@router.callback_query(F.data.startswith('no'))
async def no(callback: CallbackQuery):
    text = callback.data.split('_')[2]
    await callback.message.delete()
    await callback.message.answer(text)
    
@router.callback_query(F.data.startswith('yes'))
async def yes(callback: CallbackQuery):
    _, record_id, text = callback.data.split('_')
    await callback.message.delete()
    await callback.message.answer(text)
    await offer_time(get_record(int(record_id)))
    await delete_record(int(record_id))
    await delete_closed_time(int(record_id))
