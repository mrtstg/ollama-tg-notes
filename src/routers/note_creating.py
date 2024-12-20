import logging
from ..models import Note
from aiogram import F, Router, types
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import (
    InlineKeyboardButton,
    Message,
    ReplyKeyboardRemove,
    ReplyKeyboardMarkup,
)
from ..acl import TG_ACL
from ..filters import ACLFilter
from ..date_mapper import *
from aiogram.utils.keyboard import InlineKeyboardBuilder

available_date_mappers: dict[str, AbstractDateMapper] = {
    "Сегодня": TodayDateMapper(),
    "Завтра": TomorrowDateMapper(),
    "Ближайший ПН": ClosestWeekDayDateMapper(0),
    "Ближайший ВТ": ClosestWeekDayDateMapper(1),
    "Ближайшая СР": ClosestWeekDayDateMapper(2),
    "Ближайший ЧТ": ClosestWeekDayDateMapper(3),
    "Ближайший ПТ": ClosestWeekDayDateMapper(4),
    "Ближайшая СБ": ClosestWeekDayDateMapper(5),
    "Ближайшее ВС": ClosestWeekDayDateMapper(6),
}
available_date_mappers_keys: list[str] = list(available_date_mappers.keys())

router = Router(name=__name__)


class NoteCreatingStage(StatesGroup):
    TITLE, DATE = [State() for _ in range(2)]


@router.message(ACLFilter(TG_ACL), F.text.regexp("^/note$"))
async def create_note_start(message: Message, state: FSMContext):
    await message.answer("Введите заголовок заметки: ")
    await state.set_state(NoteCreatingStage.TITLE)


@router.message(NoteCreatingStage.TITLE, ACLFilter(TG_ACL), F.text.len() > 0)
async def create_note_title(message: Message, state: FSMContext):
    await state.set_state(NoteCreatingStage.DATE)
    await state.update_data(title=message.text)
    buttons = [[]]
    for b in available_date_mappers_keys:
        if len(buttons[-1]) >= 2:
            buttons.append([])

        buttons[-1].append(types.KeyboardButton(text=b))

    await message.answer(
        "Укажите дату или выберите из списка ниже: ",
        reply_markup=ReplyKeyboardMarkup(keyboard=buttons, one_time_keyboard=True),
    )


@router.message(
    ACLFilter(TG_ACL), NoteCreatingStage.DATE, F.text.in_(available_date_mappers_keys)
)
async def date_bindings_action(message: Message, state: FSMContext):
    assert message.text is not None
    assert message.from_user is not None
    date_mapper = available_date_mappers[message.text]
    await state.update_data(date=date_mapper.get_date())
    data = await state.get_data()
    new_note = Note(
        uid=message.from_user.id, note=data["title"], date=data["date"], finished=False
    )
    await new_note.create()
    await new_note.sync()
    await state.clear()

    keyboard = InlineKeyboardBuilder()
    logging.info(new_note.id)
    keyboard.row(
        types.InlineKeyboardButton(
            text="Удалить заметку", callback_data="delete_" + str(new_note.id)
        )
    )

    await message.answer("Заметка создана!", reply_markup=keyboard.as_markup())
