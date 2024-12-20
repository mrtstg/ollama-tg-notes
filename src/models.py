from beanie import Document, Indexed
import datetime


class Note(Document):

    class Settings:
        name = "notes"

    uid: Indexed(int)  # type: ignore
    note: str
    date: datetime.datetime
    finished: bool
