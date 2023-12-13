from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.database.requests import  *
from app.database.add_requests import  *
from app.database.get_scalar import *
from app.database.get_scalars import *
from datetime import datetime
from calendar import monthrange

day_name = {
    0: "Понедельник",
    1: "Вторник",
    2: "Среда",
    3: "Четверг",
    4: "Пятница",
    5: "Суббота",
    6: "Воскресенье"
}
day_num = {
    "Понедельник": 0,
    "Вторник": 1,
    "Среда": 2,
    "Четверг": 3,
    "Пятница": 4,
    "Суббота": 5,
    "Воскресенье": 6
}

main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Записаться на прием")],
    [KeyboardButton(text="Мои записи")],
    [KeyboardButton(text="Отменить прием")],
    [KeyboardButton(text="Контакты")]
], resize_keyboard=True, input_field_placeholder="Выберите действие")


async def specializations():
    spec_kb = InlineKeyboardBuilder()
    specializations = await get_specializations()
    for spec in specializations:
        spec_kb.add(InlineKeyboardButton(text=spec.name, callback_data=f'specalization_{spec.id}'))
    return spec_kb.adjust(2).as_markup()


async def services(specialization_id):
    services_kb = InlineKeyboardBuilder()
    services = await get_services(specialization_id)
    for service in services:
        services_kb.add(InlineKeyboardButton(text=service.name, callback_data=f'service_{service.id}_{specialization_id}'))
    return services_kb.adjust(2).as_markup()

async def branches(service_id, specialization_id):
    branches_kb = InlineKeyboardBuilder()
    branches = await get_branchs(service_id)
    for branch in branches:
        branches_kb.add(InlineKeyboardButton(text=branch.address, callback_data=f'branch_{branch.id}_{service_id}_{specialization_id}'))
    return branches_kb.as_markup()

async def employees(branch_id, service_id, specialization_id):
    employees_kb = InlineKeyboardBuilder()
    employees = await get_employees(branch_id, service_id)
    for employee in employees:
        employees_kb.add(InlineKeyboardButton(text=employee.name, callback_data=f'employee_{employee.id}_{branch_id}_{service_id}_{specialization_id}'))
    return employees_kb.adjust(2).as_markup()


async def calendar(employee_id, branch_id, service_id, specialization_id):
    calendar = InlineKeyboardBuilder()
    now = datetime.now().date()
    c_day, month, year = now.day, now.month, now.year
    work_days = await get_employee_workdays(employee_id)
    work_days = [day_num[day] for day in work_days]
    days = monthrange(year, month)[1]
    for day in range(1, days+1):
        data = f"{day}.{month}.{year}"
        date = datetime.strptime(data, '%d.%m.%Y').date()
        if (day > c_day) and (date.weekday() in work_days):
            callback_data_1 = f"calendar_{data}_{employee_id}_{branch_id}_{service_id}_{specialization_id}"
            calendar.add(InlineKeyboardButton(text=data, callback_data=callback_data_1))
            #calendar.add(InlineKeyboardButton(text=day_name[date.weekday()], callback_data=callback_data_1))
    # Добавляем кнопку "Назад"
    # callback_data_0 = f"calendar_back"
    # calendar.add(InlineKeyboardButton(text="Назад", callback_data=callback_data_0))
    return calendar.adjust(3).as_markup()
        

async def dates(employee_id, branch_id, service_id, specialization_id):
    dates_kb = InlineKeyboardBuilder()
    dates = await get_dates(employee_id)
    for date in dates:
        dates_kb.add(InlineKeyboardButton(text=date.weekday, callback_data=f'date_{date.id}_{employee_id}_{branch_id}_{service_id}_{specialization_id}'))
    return dates_kb.adjust(2).as_markup()


async def timeslots(date, employee_id, branch_id, service_id, specialization_id):
    time_kb = InlineKeyboardBuilder()
    time = await get_times(employee_id, date)
    for t in time:
        time_kb.add(InlineKeyboardButton(text=str(t.time), callback_data=f'time_{t.id}_{date}_{employee_id}_{branch_id}_{service_id}_{specialization_id}'))
    return time_kb.adjust(2).as_markup()

async def records(user_id):
    records_kb = InlineKeyboardBuilder()
    records = await get_records(user_id)
    for record in records:
        employee = await get_employee(record.employee_id)
        records_kb.add(InlineKeyboardButton(text=f"{record.date} в {record.start_time}\nВрач: {employee}", callback_data=f'record_{record.id}'))
    return records_kb.adjust(1).as_markup()

async def record(user_id):
    records_kb = InlineKeyboardBuilder()
    records = await get_records(user_id)
    for record in records:
        employee = await get_employee(record.employee_id)
        records_kb.add(InlineKeyboardButton(text=f"{record.date} в {record.start_time}\nВрач: {employee}", callback_data=f'record_{record.id}'))
    return records_kb.adjust(1).as_markup()

async def yes_no(record_id):
    yes_no_kb = InlineKeyboardBuilder()
    yes_no_kb.add(InlineKeyboardButton(text="Да", callback_data=f"yes_{record_id}"))
    yes_no_kb.add(InlineKeyboardButton(text="Нет", callback_data="no"))
    return yes_no_kb.adjust(2).as_markup()

async def contacts():
    contacts_kb = InlineKeyboardBuilder()
    contacts = await get_all_branchs()
    for contact in contacts:
        contacts_kb.add(InlineKeyboardButton(text=f"{contact.name}", callback_data=f"contbranch_{contact.id}"))
    return contacts_kb.as_markup()