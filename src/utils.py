from .models import Note
import datetime


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
