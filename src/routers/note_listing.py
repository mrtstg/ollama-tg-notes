import logging
from ..models import Note
from aiogram import F, Router
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from ..acl import TG_ACL
from ..filters import ACLFilter
import datetime
from typing import Match, Callable, Coroutine
from ..utils import *

router = Router(name=__name__)

filters_mapping: dict[str, Callable[[int], Coroutine[None, None, list[Note]]]] = {
    "week": get_week_notes,
    "today": get_today_notes,
    "tomorrow": get_tomorrow_notes,
    "pweek": get_prev_week_notes,
    "yesterday": get_yesterday_notes,
}


@router.callback_query(
    ACLFilter(TG_ACL), F.data.regexp("^([a-zA-Z]*)_page([0-9]*)").as_("match")
)
async def list_week_notes_buttons(query: CallbackQuery, match: Match[str]):
    filter_group = match.group(1)
    if filter_group not in filters_mapping:
        await query.answer("Неизвестный фильтр!")
        return
    page = int(match.group(2))
    notes = await filters_mapping[filter_group](query.from_user.id)
    payload = {
        "text": generate_notes_payload(notes, True),
        "reply_markup": build_notes_keyboard(
            filter_group, notes, page=page
        ).as_markup(),
    }
    try:
        assert query.message is not None
        await query.message.edit_text(**payload)  # type: ignore
    except:
        try:
            await query.message.answer(**payload)  # type: ignore
        except:
            await query.answer("Внутренняя ошибка!")


@router.message(ACLFilter(TG_ACL), Command("week"))
async def list_week_notes(message: Message):
    assert message.from_user is not None
    notes = await get_week_notes(message.from_user.id)
    await message.answer(
        generate_notes_payload(notes, True),
        reply_markup=build_notes_keyboard("week", notes).as_markup(),
    )


@router.message(ACLFilter(TG_ACL), Command("pweek"))
async def list_prev_week_notes(message: Message):
    assert message.from_user is not None
    notes = await get_prev_week_notes(message.from_user.id)
    await message.answer(
        generate_notes_payload(notes, True),
        reply_markup=build_notes_keyboard("pweek", notes).as_markup(),
    )


@router.message(ACLFilter(TG_ACL), Command("today"))
async def list_today_notes(message: Message):
    assert message.from_user is not None
    notes = await get_today_notes(message.from_user.id)
    text = "Заметки на сегодня:\n"
    for note in notes:
        text += (" - " if not note.finished else "✅") + note.note + "\n"
    await message.answer(
        text, reply_markup=build_notes_keyboard("today", notes).as_markup()
    )


@router.message(ACLFilter(TG_ACL), Command("yesterday"))
async def list_yesterday_notes(message: Message):
    assert message.from_user is not None
    notes = await get_yesterday_notes(message.from_user.id)
    text = "Заметки на вчера:\n"
    for note in notes:
        text += (" - " if not note.finished else "✅") + note.note + "\n"
    await message.answer(
        text, reply_markup=build_notes_keyboard("yesterday", notes).as_markup()
    )


@router.message(ACLFilter(TG_ACL), Command("tomorrow"))
async def list_tomorrow_notes(message: Message):
    assert message.from_user is not None
    notes = await get_tomorrow_notes(message.from_user.id)
    text = "Заметки на завтра:\n"
    for note in notes:
        text += (" - " if not note.finished else "✅") + note.note + "\n"
    await message.answer(
        text, reply_markup=build_notes_keyboard("tomorrow", notes).as_markup()
    )
