import os
import asyncio
from ollama import AsyncClient
import logging
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message
import logging
from .utils import *
from .utils import generate_notes_payload
from .acl import TG_ACL
from .filters import ACLFilter
import sys
from typing import Match
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from .models import *
from .routers.note_listing import router as listing_router
from .routers.note_creating import router as creating_router
from .routers.note_deleting import router as deleting_router
from .routers.note_managing import router as managing_router

logging.basicConfig(
    format="%(asctime)s - [%(levelname)s] - %(module)s:%(lineno)d - %(message)s",
    stream=sys.stdout,
    level=logging.INFO if os.environ.get("DEBUG", "0") != "1" else logging.DEBUG,
)

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

OLLAMA_MODEL = os.environ["OLLAMA_MODEL"]
OLLAMA_TIMEOUT = int(os.environ["OLLAMA_TIMEOUT"])
OLLAMA_HOST = os.environ["OLLAMA_HOST"]

ollama = AsyncClient(host=OLLAMA_HOST, timeout=OLLAMA_TIMEOUT)

main_router = Router(name=__name__)


@main_router.message(ACLFilter(TG_ACL), F.text.regexp(r"^/ask (.*)$").as_("match"))
async def any_message_handler(message: Message, match: Match[str]):
    assert message.from_user is not None
    notes = await get_week_notes(message.from_user.id)
    payload = generate_notes_payload(notes)
    now = datetime.datetime.now().strftime("%d.%m.%Y")
    data = [
        {
            "role": "system",
            "content": "Ты - персональный ассистент. Твоя задача - ответить максимально корректно по пользовательскому запросу. Используй контекст в виде задач на дни. Сегодня - "
            + now,
        },
        {
            "role": "user",
            "content": match.group(1) + "\n\n" + payload,
        },
    ]
    logging.debug(data)
    await message.answer("Запрос отправлен!")
    try:
        resp = await ollama.chat(model=OLLAMA_MODEL, messages=data)
    except Exception as e:
        await message.answer("Ошибка: " + str(e))
        return
    if resp.message.content is None:
        await message.answer("No reply from model!")
        return
    await message.answer(resp.message.content)


async def main():
    dp = Dispatcher()
    bot = Bot(os.environ["BOT_TOKEN"])

    client = AsyncIOMotorClient(
        f"mongodb://{os.environ['DB_USER']}:{os.environ['DB_PASS']}@{os.environ['DB_HOST']}:27017/"
    )
    await init_beanie(client.db, document_models=[Note])

    dp.include_routers(
        main_router, listing_router, deleting_router, creating_router, managing_router
    )

    logging.info("Бот начал работу!")
    while True:
        try:
            await dp.start_polling(
                bot,
                handle_signals=False,
            )
        except Exception as e:
            logging.error(str(e))
            await asyncio.sleep(10)
        except KeyboardInterrupt:
            break
        except SystemExit:
            break


if __name__ == "__main__":
    logging.info("Скрипт запущен!")
    loop.run_until_complete(main())
