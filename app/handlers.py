from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from asyncio import sleep as asleep
import app.keyboards as kb
from datetime import timedelta
from app.database.requests import  *
from app.database.add_requests import  *
from app.database.get_scalar import *
from app.database.get_scalars import *

router = Router()
    
user_state = {}

@router.message(CommandStart())
async def process_start_command(message: Message):
    user_id = message.chat.id
    user_state[user_id] = []
    await add_user(message.from_user.id, message.from_user.username)
    await message.answer("Здравствуйте, чтобы вы хотели?", reply_markup=kb.main)
    
@router.message(F.text == "Мои записи")
async def my_records(message: Message):
    user_id = message.chat.id
    records = await get_records(user_id)
    if records != []:
        for record in records:
            date = record.date.strftime("%d.%m.%Y")
            time = str(record.start_time)[:5]
            await message.answer(f'{date} в {time}\nВрач: {await get_employee(record.employee_id)}\n')
    else:
        await message.answer("У вас нет записей")
    
    
@router.message(F.text == "Контакты")
async def contacts(message: Message):
    await message.answer("Наши контакты", reply_markup=await kb.contacts())
    
@router.callback_query(F.data.startswith('contbranch_'))
async def cont_callback(callback: CallbackQuery):
    branch = await get_full_branch(int(callback.data.split('_')[1]))
    await callback.message.answer(f"Адрес:{branch.address}\nТелефон регистратуры:{branch.phone}")
    
@router.message(F.text == "Записаться на прием")
async def spec(message: Message):
    user_id = message.chat.id
    user_state[user_id] = []
    await message.answer("Выберите специализацию", reply_markup=await kb.specializations())
    

@router.callback_query(F.data.startswith('specalization_'))
async def spec_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    button_id = 'specalization_'
    if button_id in user_state[user_id]:
        await callback.answer("Вы уже выбрали напраление")
    else:
        user_state[user_id].append(button_id)
        spec_id = int(callback.data.split('_')[1])
        await callback.message.answer("Выберите услугу", reply_markup=await kb.services(spec_id))
    

@router.callback_query(F.data.startswith('service_'))
async def service_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    button_id = 'service_'
    if button_id in user_state[user_id]:
        await callback.answer("Вы уже выбрали услугу")
    else:
        user_state[user_id].append(button_id)
        service_id, spec_id = map(int, callback.data.split('_')[1:])
        await callback.message.answer("Выберите отделение", reply_markup=await kb.branches(service_id, spec_id))
        await callback.answer('')
    

@router.callback_query(F.data.startswith('branch_'))
async def branch_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    button_id = 'branch_'
    if button_id in user_state[user_id]:
        await callback.answer("Вы уже выбрали филиал")
    else:
        user_state[user_id].append(button_id)
        branch_id, service_id, spec_id = map(int, callback.data.split('_')[1:])
        await callback.message.answer("Выберите сотрудника", reply_markup=await kb.employees(branch_id, service_id, spec_id))
        await callback.answer('')


@router.callback_query(F.data.startswith('employee_'))
async def send_calendar(callback: CallbackQuery):
    user_id = callback.from_user.id
    button_id = 'employee_'
    if button_id in user_state[user_id]:
        await callback.answer("Вы уже выбрали врача")
    else:
        user_state[user_id].append(button_id)
        employee_id, branch_id, service_id, spec_id = map(int, callback.data.split('_')[1:])
        await callback.message.answer("Выберите день:", reply_markup=await kb.calendar(employee_id, branch_id, service_id, spec_id))
        await callback.answer('')


@router.callback_query(F.data.startswith('calendar_'))
async def send_timeslots(callback: CallbackQuery):
    user_id = callback.from_user.id
    button_id = 'calendar_'
    if button_id in user_state[user_id]:
        await callback.answer("Вы уже выбрали дату")
    else:
        user_state[user_id].append(button_id)
        data, employee_id, branch_id, service_id, spec_id = callback.data.split('_')[1:]
        await callback.message.answer("Выберите время:", reply_markup= await kb.timeslots(data, employee_id, branch_id, service_id, spec_id))
        await callback.answer('')

@router.callback_query(F.data.startswith('time_'))
async def process_calendar_button(callback: CallbackQuery):
    user_id = callback.from_user.id
    button_id = 'time_'
    if button_id in user_state[user_id]:
        await callback.answer("Вы уже выбрали время")
    else:
        user_state[user_id].append(button_id)
        time_id, date, employee_id, branch_id, service_id, spec_id = callback.data.split('_')[1:]
        em = await get_employee(employee_id)
        br = await get_branch(branch_id)
        se = await get_service(service_id)
        time = await get_time(time_id)
        text = f"Ваша запись\nВрач: {em}\nОтделение: {br}\nУслуга: {se}\nДата: {date}\nВремя записи: {str(time)[:5]}"
        record = (await add_record(callback.from_user.id, date, time, service_id, branch_id, employee_id)).inserted_primary_key[0]
        close = (await close_time(employee_id, time, date, record)).inserted_primary_key[0]
        await callback.message.answer(text= text)
        await callback.answer('')
        await remind(callback, close, record)


async def remind(callback: CallbackQuery, close_id, record_id):
    record = await get_close_record(record_id)
    employee = await get_employee(record.employee_id)
    close = await get_close(close_id)
    res = close.day - timedelta(days=1)
    remind_time = res.strftime("%d.%m.%Y %H:%M:%S")
    await asleep(1)
    date = record.date.strftime("%d.%m.%Y")
    time = str(record.start_time)[:5]
    await callback.message.answer(f'Подтверждаете запись?\n{date} в {time}\nВрач: {employee}\n', reply_markup=await kb.yes_no(record_id, "mind"))
    await callback.answer('')
    # while True:
    #     if datetime.now().strftime("%Y-%m-%d %H:%M:%S") == remind_time:
    #         break

@router.message(F.text == "Отменить прием")
async def cancel(message: Message):
    await message.answer("Выберите запись для отмены", reply_markup=await kb.records(message.from_user.id))
    
@router.callback_query(F.data.startswith('record_'))
async def cancel_record(callback: CallbackQuery):
    user_id = callback.from_user.id
    button_id = 'record_'
    if button_id in user_state[user_id]:
        await callback.answer("Вы уже выбрали запись")
    else:
        user_state[user_id].append(button_id)
        record_id = int(callback.data.split('_')[1])
        await callback.message.answer("Вы уверены что хотите отменить прием?", reply_markup=await kb.yes_no(record_id, "delete"))
        await callback.answer('')

           
@router.callback_query(F.data.startswith('yes'))
async def yes(callback: CallbackQuery):
    user_id = callback.from_user.id
    user_state[user_id][-1]=''
    _, record_id, text = callback.data.split('_')
    await callback.message.delete()
    await callback.message.answer(text)
    await delete_record(int(record_id))
    
@router.callback_query(F.data.startswith('no'))
async def no(callback: CallbackQuery):
    user_id = callback.from_user.id
    user_state[user_id][-1]=''
    text = callback.data.split('_')[1]
    await callback.message.delete()
    await callback.message.answer(text)
    