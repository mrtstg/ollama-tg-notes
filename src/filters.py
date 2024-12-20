from aiogram.types import Message
from aiogram.filters import BaseFilter
import logging


class ACLFilter(BaseFilter):
    allowed_ids: list[int]

    def __init__(self, allowed_ids: list[int]):
        self.allowed_ids = allowed_ids

    async def __call__(self, message: Message) -> bool:
        if message.from_user is None:
            return False

        if message.from_user.id not in self.allowed_ids:
            logging.error("Forbid user %s" % message.from_user.id)
            return False

        return True
