from .models import Note
import datetime


async def get_week_notes() -> list[Note]:
    return await get_notes_from_range(get_date_range_from_today(86400 * 7))


async def get_today_notes() -> list[Note]:
    return await get_notes_from_range(get_date_range_from_today(86400))


async def get_tomorrow_notes() -> list[Note]:
    return await get_notes_from_range(get_date_range_from_today(86400, 86400))


async def get_notes_from_range(
    date_range: tuple[datetime.datetime, datetime.datetime]
) -> list[Note]:
    (start, end) = date_range
    return await Note.find(Note.date >= start, Note.date <= end).to_list()


def get_date_range_from_today(
    end_from_start_offset: int = 0, start_offset: int = 0
) -> tuple[datetime.datetime, datetime.datetime]:
    now = datetime.datetime.now()
    start_date = datetime.datetime.fromtimestamp(
        datetime.datetime(now.year, now.month, now.day).timestamp() + start_offset
    )
    end_date = datetime.datetime.fromtimestamp(
        start_date.timestamp() + end_from_start_offset
    )
    return (start_date, end_date)


# crops text for callback button if its longer that 50 symbols
def process_note_title(title: str) -> str:
    if len(title) > 50:
        return title[:0] + "..."
    return title


def generate_notes_payload(notes: list[Note], include_finished: bool = False) -> str:
    text = ""
    all_dates: list[datetime.datetime] = sorted(
        [note.date for note in notes], reverse=True
    )
    all_dates_str_set: list[str] = []
    for date in reversed(all_dates):
        s = date.strftime("%d.%m.%Y")
        if s in all_dates:
            continue
        all_dates_str_set.append(s)
    notes_dict: dict[str, list[Note]] = {d: [] for d in all_dates_str_set}
    for note in notes:
        notes_dict[note.date.strftime("%d.%m.%Y")].append(note)

    for date in all_dates_str_set:
        text += "Задачи на " + date + ":\n"
        for note in notes_dict[date]:
            if note.finished and include_finished:
                text += " - " + note.note + " [ЗАКОНЧЕНА]\n"
            elif not note.finished:
                text += " - " + note.note + "\n"
    return text
