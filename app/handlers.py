from aiogram import Router, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
import app.keyboards as kb
from app.database.requests import  *
from app.database.add_requests import  *
from app.database.get_scalar import *
from app.database.get_scalars import *
from typing import Any, Dict

router = Router()

class Recording(StatesGroup):
    reg = State()
    spec = State()
    service = State()
    branch = State()
    employee = State()
    date = State()
    time = State()
    confirm = State()
    
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
            await message.answer(f'{record.date} в {record.start_time}\nВрач: {await get_employee(record.employee_id)}\n')
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
async def spec(message: Message, state: FSMContext):
    user_id = message.chat.id
    user_state[user_id] = []
    await message.answer("Выберите специализацию", reply_markup=await kb.specializations())
    await state.set_state(Recording.spec)
    

@router.callback_query(F.data.startswith('specalization_'))
async def spec_callback(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    button_id = 'specalization_'
    if button_id in user_state[user_id]:
        await callback.answer("Вы уже выбрали напраление")
    else:
        user_state[user_id].append(button_id)
        spec_id = int(callback.data.split('_')[1])
        await callback.message.answer("Выберите услугу", reply_markup=await kb.services(spec_id))
        await state.update_data(spec=spec_id)
        await state.set_state(Recording.service)
    

@router.callback_query(F.data.startswith('service_'))
async def service_callback(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    button_id = 'service_'
    if button_id in user_state[user_id]:
        await callback.answer("Вы уже выбрали услугу")
    else:
        user_state[user_id].append(button_id)
        service_id, spec_id = map(int, callback.data.split('_')[1:])
        await callback.message.answer("Выберите отделение", reply_markup=await kb.branches(service_id, spec_id))
        await callback.answer('')
        await state.update_data(service=service_id)
        await state.set_state(Recording.branch)
    

@router.callback_query(F.data.startswith('branch_'))
async def branch_callback(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    button_id = 'branch_'
    if button_id in user_state[user_id]:
        await callback.answer("Вы уже выбрали филиал")
    else:
        user_state[user_id].append(button_id)
        branch_id, service_id, spec_id = map(int, callback.data.split('_')[1:])
        await callback.message.answer("Выберите сотрудника", reply_markup=await kb.employees(branch_id, service_id, spec_id))
        await callback.answer('') 
        await state.update_data(branch=branch_id)
        await state.set_state(Recording.employee)


@router.callback_query(F.data.startswith('employee_'))
async def send_calendar(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    button_id = 'employee_'
    if button_id in user_state[user_id]:
        await callback.answer("Вы уже выбрали врача")
    else:
        user_state[user_id].append(button_id)
        employee_id, branch_id, service_id, spec_id = map(int, callback.data.split('_')[1:])
        await callback.message.answer("Выберите день:", reply_markup=await kb.calendar(employee_id, branch_id, service_id, spec_id))
        await callback.answer('')
        await state.update_data(employee=employee_id)
        await state.set_state(Recording.date)


@router.callback_query(F.data.startswith('calendar_'))
async def send_timeslots(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    button_id = 'calendar_'
    if button_id in user_state[user_id]:
        await callback.answer("Вы уже выбрали дату")
    else:
        user_state[user_id].append(button_id)
        data, employee_id, branch_id, service_id, spec_id = callback.data.split('_')[1:]
        await callback.message.answer("Выберите время:", reply_markup= await kb.timeslots(data, employee_id, branch_id, service_id, spec_id))
        await callback.answer('')
        await state.update_data(date=data)
        await state.set_state(Recording.time)

@router.callback_query(F.data.startswith('time_'))
async def process_calendar_button(callback: CallbackQuery, state: FSMContext):
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
        text = f"Ваша запись\nВрач: {em}\nОтделение: {br}\nУслуга: {se}\nДата: {date}\nВремя записи: {time}"
        await add_record(callback.from_user.id, date, time, service_id, branch_id, employee_id)
        await close_time(employee_id, time, date)
        await callback.message.answer(text= text)
        await callback.answer('')
        data = await state.update_data(time=time)
        await state.set_state(Recording.confirm)
        await show_summary(callback=callback, data=data)
        
        
    
async def show_summary(callback: CallbackQuery, data: Dict[str, Any], positive: bool = True) -> None:
    name = data["spec"]
    await callback.message.answer(text=name)

        
        
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
        await callback.message.answer("Вы уверены что хотите отменить прием?", reply_markup=await kb.yes_no(record_id))
        await callback.answer('')
        
@router.callback_query(F.data.startswith('yes'))
async def yes(callback: CallbackQuery):
    user_id = callback.from_user.id
    user_state[user_id][-1]=''
    record_id = int(callback.data.split('_')[1])
    await callback.message.answer("Ваша запись отменена")
    await callback.answer('')
    await delete_record(record_id)
    
@router.callback_query(F.data.startswith('no'))
async def no(callback: CallbackQuery):
    user_id = callback.from_user.id
    user_state[user_id][-1]=''
    await callback.message.answer("Вы не стали отменять запись")
    await callback.answer('')
    