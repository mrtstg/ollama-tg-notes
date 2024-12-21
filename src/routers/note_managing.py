import logging

from beanie import PydanticObjectId
from ..models import Note
from aiogram import F, Router
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from ..acl import TG_ACL
from ..filters import ACLFilter
import datetime
from typing import Match, Callable, Coroutine
from ..utils import *

router = Router(name=__name__)


def generate_note_payload(note: Note, back_command: str) -> dict:
    back_payload = back_command + "_page1"
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        types.InlineKeyboardButton(
            text="Отметить завершенность",
            callback_data="finish_" + str(note.id) + "_" + back_command,
        )
    )
    keyboard.row(
        types.InlineKeyboardButton(
            text="Удалить заметку", callback_data="delete_" + str(note.id)
        )
    )
    keyboard.row(
        types.InlineKeyboardButton(text="Назад к заметкам", callback_data=back_payload)
    )
    payload = {
        "text": (
            "Заметка: "
            + note.note
            + "\nСостояние: "
            + ("завершена" if note.finished else "не завершена")
        ),
        "reply_markup": keyboard.as_markup(),
    }
    return payload


@router.callback_query(
    ACLFilter(TG_ACL), F.data.regexp(r"^finish_([^_]+)_(.+)").as_("match")
)
async def finish_note(query: CallbackQuery, match: Match[str]):
    note_id = match.group(1)
    back_command = match.group(2)

    note = await Note.find_one(
        Note.id == PydanticObjectId(note_id), Note.uid == query.from_user.id
    )
    if note is None:
        await query.answer("Заметка не найдена!")
        return

    note.finished = not note.finished
    await note.save()

    payload = generate_note_payload(note, back_command)
    try:
        assert query.message is not None
        await query.message.edit_text(**payload)  # type: ignore
    except Exception as e:
        try:
            await query.message.answer(**payload)  # type: ignore
        except:
            await query.answer("Внутренняя ошибка!")


@router.callback_query(
    ACLFilter(TG_ACL), F.data.regexp(r"^note_(.*)_(.*)").as_("match")
)
async def examine_note(query: CallbackQuery, match: Match[str]):
    note_id = match.group(1)
    back_command = match.group(2)
    back_payload = back_command + "_page1"
    note = await Note.find_one(
        Note.id == PydanticObjectId(note_id), Note.uid == query.from_user.id
    )
    if note is None:
        await query.answer("Заметка не найдена!")
        return

    payload = generate_note_payload(note, back_payload)
    try:
        assert query.message is not None
        await query.message.edit_text(**payload)  # type: ignore
    except:
        try:
            await query.message.answer(**payload)  # type: ignore
        except:
            await query.answer("Внутренняя ошибка!")
