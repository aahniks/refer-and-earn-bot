import asyncio
import logging

from odmantic.engine import AIOEngine
from rich import traceback
from rich.logging import RichHandler
from telethon import TelegramClient, functions, types

traceback.install()
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[
        RichHandler(
            rich_tracebacks=True,
            markup=True,
        )
    ],
)


async def start_bot():
    from refer_bot import conf
    from refer_bot import storage as st
    from refer_bot.utils import get_id, handler_functions

    client = TelegramClient("bot", conf.API_ID, conf.API_HASH)
    await client.start(bot_token=conf.BOT_TOKEN)
    me = await client.get_me()
    conf.BOT_USERNAME = me.username
    logging.info(f"Logged in sucessfully as {conf.BOT_USERNAME}")

    engine = AIOEngine()
    logging.info("Created AsyncIO Engine for MongoDB")
    st.engine = engine

    conf.ADMINS = [await get_id(client, admin) for admin in conf.BOT_ADMINS.split(",")]
    logging.info(f"Usernames of bot admins {conf.BOT_ADMINS}")
    logging.info(f"Ids of admins {conf.ADMINS}")

    for handler in handler_functions():
        logging.info(f"Added event handler {handler.__name__}")
        client.add_event_handler(handler)

    await client(
        functions.bots.SetBotCommandsRequest(
            commands=[
                types.BotCommand(command=key, description=value)
                for key, value in conf.COMMANDS.items()
            ]
        )
    )
    logging.info(f"Set bot commands {conf.COMMANDS}")
    logging.info("Bot is up and running!")
    await client.run_until_disconnected()


def main():
    try:
        asyncio.run(start_bot())
    except KeyboardInterrupt:
        logging.critical("Aborted!")
