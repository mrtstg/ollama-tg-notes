import logging

from beanie import PydanticObjectId
from ..models import Note
from aiogram import F, Router, types
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    Message,
    ReplyKeyboardRemove,
)
from ..acl import TG_ACL
from ..filters import ACLFilter
from ..date_mapper import *
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import Match

router = Router(name=__name__)


@router.callback_query(F.data.regexp("^delete_(.*)$").as_("match"))
async def delete_note_callback(query: CallbackQuery, match: Match[str]):
    note_id = match.group(1)
    note = await Note.find_one(Note.id == PydanticObjectId(note_id))
    if note is None:
        await query.answer("Заметка не найдена!")
        return

    if note.uid != query.from_user.id:
        await query.answer("Это не ваша заметка!")
        return

    await note.delete()
    await query.answer("Заметка удалена!")
