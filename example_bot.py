import logging
import asyncio
import sys
from datetime import datetime

from aiogram_calendar import Calendar, CalendarCallback, get_user_locale
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, CallbackQuery
from aiogram.utils.markdown import hbold
from aiogram.client.default import DefaultBotProperties

from config import API_TOKEN

# All handlers should be attached to the Router (or Dispatcher)
dp = Dispatcher()

# Initialising keyboard
kb = [
    [
        KeyboardButton(text='Open Calendar'),
    ],
]
start_kb = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.reply(f"Hello, {hbold(message.from_user.full_name)}! Select a date", reply_markup=start_kb)

@dp.message(F.text.lower() == 'open calendar')
async def dialog_cal_handler(message: Message):
    await message.answer(
        "Please select a date: ",
        reply_markup=await Calendar(
            locale=await get_user_locale(message.from_user)
        ).start_calendar()
    )

@dp.callback_query(CalendarCallback.filter())
async def process_dialog_calendar(callback_query: CallbackQuery, callback_data: CallbackData):
    selected, date = await Calendar(
        locale=await get_user_locale(callback_query.from_user)
    ).process_selection(callback_query, callback_data)
    if selected:
        await callback_query.message.answer(
            f'You selected {date.strftime("%d/%m/%Y")}',
            reply_markup=start_kb
        )

async def main() -> None:
    # ParseMode.HTML ensures that all messages and inline keyboards sent by the bot will parse HTML tags, including <s>
    bot = Bot(API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
