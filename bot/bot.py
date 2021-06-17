import logging
import asyncio
import time
from decouple import config
from telethon.sync import TelegramClient, events
from quora import User
from quora.exceptions import ProfileNotFoundError
from watcher import Watcher
from watcher.events.quora import (
    AnswerCountChange,
    FollowerCountChange,
)
from .utils import (
    extract_quora_username,
    get_answer_count,
)
from bot import database_api as api


TOKEN = config("TOKEN")
API_ID = config("APP_ID")
API_HASH = config("API_HASH")
LOGGING_LEVEL = int(config("LOGGING_LEVEL", 20))


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(message)s",
    level=LOGGING_LEVEL,
)


def stateCustomizer(answerCount):
    def wrapper(obj):
        obj.answerCount = answerCount
        return obj

    return wrapper


class Client(TelegramClient):
    def __init__(self, name, API_ID, API_HASH):
        super().__init__(name, API_ID, API_HASH)
        self.watcher = Watcher()
        for username, answerCount in api.get_all_data():
            self.watcher.add_quora(
                username,
                stateInitializer=stateCustomizer(answerCount),
                update_interval=300,
                )
            time.sleep(5)
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
        event.client.watcher.add_quora(username)
    except ProfileNotFoundError:
        await event.reply(f"No profile found with username {username}")
    except Exception as e:
        await event.reply("Some unknown error occurred.")
        print(e)


@bot.dispatcher.on(AnswerCountChange)
async def dispatch_event(event):
    username = event.profile.username
    try:
        tg_id = api.get_tg_id(username)
        api.update_count(username, event.countChange)
        if event.countChange < 0:
            await bot.send_message(
                int(tg_id),
                f"{abs(event.countChange)} answer(s) not visible in your account.\nIn case you haven't deleted any answer then, it might have collapsed.\nCurrent answer count: {event.profile.answerCount}",
            )
        else:
            await bot.send_message(
                int(tg_id),
                f"Congratulations for writing {event.countChange} new answer(s).\nIn case you have restored any previous answer, ignore this message.\nCurrent answer count: {event.profile.answerCount}",
            )
    except Exception as e:
        print(e)


@bot.dispatcher.on(FollowerCountChange)
async def dispatch_follower_event(event):
    username = event.profile.username
    try:
        tg_id = api.get_tg_id(username)
        if event.countChange < 0:
            await bot.send_message(
                int(tg_id),
                f"{abs(event.countChange)} person unfollowed you.\nCurent followers: {event.profile.followerCount}",
            )
        else:
            await bot.send_message(
                int(tg_id),
                f"Congratulations for gaining {event.countChange} new follower(s).\nCurrent Followers: {event.profile.followerCount}",
            )
    except Exception as e:
        print(e)


def main():
    tasks = []
    bot.start(bot_token=TOKEN)
    loop = asyncio.get_event_loop()
    loop.create_task(bot.watcher.start())
    bot.run_until_disconnected()
