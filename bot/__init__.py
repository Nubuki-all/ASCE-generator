import argparse
import asyncio
import logging
import os
import re
import shlex
import sys
import time
import traceback
from logging import DEBUG, INFO, basicConfig, getLogger, warning
from logging.handlers import RotatingFileHandler
from pathlib import Path
from urllib.parse import urlparse

from pyrogram import Client
from pyrogram import errors as pyro_errors
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from .config import *

uptime = time.time()
PASSWD = PASSWD.split()
if os.path.exists("logs.txt"):
    with open("logs.txt", "r+") as f_d:
        f_d.truncate(0)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[
        RotatingFileHandler("logs.txt", maxBytes=2097152000, backupCount=10),
        logging.StreamHandler(),
    ],
)
logging.getLogger("urllib3").setLevel(logging.INFO)
logging.getLogger("telethon").setLevel(logging.INFO)
LOGS = logging.getLogger(__name__)


def get_readable_time(seconds: int) -> str:
    result = ""
    (days, remainder) = divmod(seconds, 86400)
    days = int(days)
    if days != 0:
        result += f"{days}d "
    (hours, remainder) = divmod(remainder, 3600)
    hours = int(hours)
    if hours != 0:
        result += f"{hours}h "
    (minutes, seconds) = divmod(remainder, 60)
    minutes = int(minutes)
    if minutes != 0:
        result += f"{minutes}m "
    seconds = int(seconds)
    result += f"{seconds}s"
    return result


def is_url(string):
    parsed = urlparse(string)
    return all([parsed.scheme, parsed.netloc])


def reformat_spaces(url):
    space_pattern = re.compile(r"\s+")
    new_url = re.sub(space_pattern, "%20", url)
    return new_url


try:
    bot = Client(
        "ASCE",
        api_id=APP_ID,
        api_hash=API_HASH,
        bot_token=BOT_TOKEN,
        workers=3,
    )
except Exception:
    LOGS.critical(traceback.format_exc())
    LOGS.info("quiting…")
    exit()


async def startup():
    try:
        for i in SUDO.split():
            try:
                await bot.send_message(int(i), f"**I'm Online**")
            except Exception:
                pass
    except BaseException:
        pass
    LOGS.info("Bot has started.")
