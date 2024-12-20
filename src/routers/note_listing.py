import logging
from ..models import Note
from aiogram import F, Router
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove
from ..acl import TG_ACL
from ..filters import ACLFilter
import datetime

router = Router(name=__name__)


@router.message(Command("today"))
async def list_today_notes(message: Message):
    now = datetime.datetime.now()
    start = datetime.datetime(now.year, now.month, now.day)
    end = datetime.datetime.fromtimestamp(start.timestamp() + 86400)
    notes = await Note.find(Note.date > start, Note.date < end).to_list()
    text = "Заметки на сегодня:\n"
    for note in notes:
        text += " - " + note.note + "\n"
    await message.answer(text)


@router.message(Command("tomorrow"))
async def list_tomorrow_notes(message: Message):
    now = datetime.datetime.now()
    start = datetime.datetime.fromtimestamp(
        datetime.datetime(now.year, now.month, now.day).timestamp() + 86400
    )
    end = datetime.datetime.fromtimestamp(start.timestamp() + 86400)
    notes = await Note.find(Note.date > start, Note.date < end).to_list()
    text = "Заметки на завтра:\n"
    for note in notes:
        text += " - " + note.note + "\n"
    await message.answer(text)
