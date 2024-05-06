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
    
@router.message(F.text.contains("Записаться на прием"))
async def spec(message: Message):
    user_id = message.chat.id
    user_state[user_id] = []
    await message.answer("Выберите направление", reply_markup=await kb.specializations())
    

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
        await callback.message.answer("Выберите врача", reply_markup=await kb.employees(branch_id, service_id, spec_id))
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
        await callback.message.answer("Выберите день", reply_markup=await kb.calendar(employee_id, branch_id, service_id, spec_id))
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
        await callback.message.answer("Выберите время", reply_markup= await kb.timeslots(data, employee_id, branch_id, service_id, spec_id))
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
        text = f"Вы записаны на <b>{se} {date} в {str(time)[:5]} </b> \n\n<b>Врач:</b> {em}\n<b>Отделение:</b> {br}"
        record = (await add_record(callback.from_user.id, date, time, service_id, branch_id, employee_id)).inserted_primary_key[0]
        close = (await close_time(employee_id, time, date, record)).inserted_primary_key[0]
        await callback.message.answer(text= text)
        await callback.answer('')
