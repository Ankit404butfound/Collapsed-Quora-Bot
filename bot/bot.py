import logging
from decouple import config
from telethon.sync import TelegramClient, events
from quora import User
from quora.exceptions import ProfileNotFoundError

from watcher import Watcher

from .utils import (
    extract_quora_username,
    get_answer_count,
)
from bot import database_api as api


TOKEN = config("TOKEN")
API_ID = config("APP_ID")
API_HASH = config("API_HASH")


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(message)s",
    level=logging.INFO,
)


class Client(TelegramClient):
    def __init__(self, name, API_ID, API_HASH):
        super().__init__(name, API_ID, API_HASH)
        self.watcher = Watcher()
        self.dispatcher = self.watcher.dispatcher


bot = Client("CollapsedQuoraBot", API_ID, API_HASH)


@bot.on(events.NewMessage(pattern=r"/notify (.*)"))
async def register(event):
    text = event.text.replace("/notify", "")
    print(text)
    username = extract_quora_username(text.strip())
    if username is None:
        await event.reply("Please send Quora username or profile link in valid format")
        return
    if api.does_exist(username):
        await event.reply("This Quora profile is already registered.")
        return
    try:
        answer = await get_answer_count(username)
        await event.reply(
            f"Account registered, you have written {answer} answer/s\nYou will be notified when any of your answers collapses."
        )
        api.add_account(username, event.sender_id, event.sender.username, answer)
    except ProfileNotFoundError:
        await event.reply(f"No profile found with username {username}")
    except Exception as e:
        await event.reply("Some unknown error occurred.")
        print(e)


def main():
    bot.start(bot_token=TOKEN)
    bot.run_until_disconnected()
