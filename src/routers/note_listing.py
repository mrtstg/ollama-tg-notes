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
from ..utils import *

router = Router(name=__name__)


@router.message(Command("week"))
async def list_week_notes(message: Message):
    notes = await get_week_notes()
    await message.answer(generate_notes_payload(notes))


@router.message(Command("today"))
async def list_today_notes(message: Message):
    notes = await get_today_notes()
    text = "Заметки на сегодня:\n"
    for note in notes:
        text += " - " + note.note + "\n"
    await message.answer(text)


@router.message(Command("tomorrow"))
async def list_tomorrow_notes(message: Message):
    notes = await get_tomorrow_notes()
    text = "Заметки на завтра:\n"
    for note in notes:
        text += " - " + note.note + "\n"
    await message.answer(text)
