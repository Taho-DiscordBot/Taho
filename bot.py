"""
The MIT License (MIT)

Copyright (c) 2022-present Taho-DiscordBot

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""
from __future__ import annotations
import asyncio
import discord
from tortoise import Tortoise, run_async
import config
from taho.babel import Babel, _
from taho.bot import Bot
from typing import TYPE_CHECKING

import logging
fmt = logging.Formatter(
    fmt="%(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
sh = logging.FileHandler(filename='logs/tortoise.log', encoding='utf-8', mode='w')
sh.setLevel(logging.DEBUG)
sh.setFormatter(fmt)

logger_tortoise = logging.getLogger("tortoise")
logger_tortoise.setLevel(logging.DEBUG)
logger_tortoise.addHandler(sh)

if TYPE_CHECKING:
    from sshtunnel import SSHTunnelForwarder


if __name__ == "__main__":
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    bot = Bot(intents=intents, config=config)

    babel = Babel(bot)
    babel.load()

    try:
        bot.run(config.token)
    except Exception as e:
        raise e
    finally:
        asyncio.set_event_loop(asyncio.new_event_loop())
        run_async(Tortoise.close_connections())
        bot.stop_ssh_server()
        asyncio.get_event_loop().close()
        print("finish")

