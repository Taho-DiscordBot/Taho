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
from typing import TYPE_CHECKING
import discord
import taho
import config
import argparse
import os
import sys
import platform
import logging
import logging.handlers

if TYPE_CHECKING:
    from typing import Tuple

# Tortoise logger
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

# Discord.py logger
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
logging.getLogger('discord.http').setLevel(logging.INFO)

handler = logging.handlers.RotatingFileHandler(
    filename='logs/discord.log',
    encoding='utf-8',
    maxBytes=32 * 1024 * 1024,  # 32 MiB
    backupCount=5,  # Rotate through 5 files
)
dt_fmt = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')
handler.setFormatter(formatter)
logger.addHandler(handler)


def show_version() -> None:
    entries = []

    entries.append('- Python v{0.major}.{0.minor}.{0.micro}-{0.releaselevel}'.format(sys.version_info))
    version_info = taho.version_info
    entries.append('- Taho v{0.major}.{0.minor}.{0.micro}-{0.releaselevel}'.format(version_info))

    discord_version = discord.version_info
    entries.append('- discord.py v{0.major}.{0.minor}.{0.micro}-{0.releaselevel}'.format(discord_version))

    uname = platform.uname()
    entries.append('- system info: {0.system} {0.release} {0.version}'.format(uname))


def core(parser: argparse.ArgumentParser, args: argparse.Namespace) -> None:
    if args.version:
        show_version()
    else:
        parser.print_help()

def update_babel(parser: argparse.ArgumentParser=None, args: argparse.Namespace=None) -> None:
    keywords = (
        "gettext",
        "ngettext",
        "pgettext",
        "npgettext",
        "lazy_gettext",
        "lazy_ngettext",
        "lazy_pgettext",
        "_d",

    )
    command = "pybabel extract -o translations/messages.pot . "
    for keyword in keywords:
        command += f"-k {keyword} "
    try:
        os.system(command)
        os.system("pybabel update -i translations/messages.pot -d translations")
    except Exception as e:
        print("==============================")
        print(e)
        print("Failed to update translations")
        print("Make sure you have babel installed, and you activated the virtual environment")
    else:
        print("==============================")
        print("Updated translations")

def compile_babel(parser: argparse.ArgumentParser=None, args: argparse.Namespace=None) -> None:
    try:
        os.system("pybabel compile -d translations")
    except Exception as e:
        print("==============================")
        print(e)
        print("Failed to compile translations")
        print("Make sure you have babel installed, and you activated the virtual environment")
    else:
        print("==============================")
        print("Compiled translations")
    

def start(parser: argparse.ArgumentParser=None, args: argparse.Namespace=None) -> None:
    print("Starting bot...")

    compile_babel()

    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True

    bot = taho.Bot(intents=intents, config=config, sync_tree=args.sync_tree)

    try:
        bot.run(config.token, log_handler=None)
    except KeyboardInterrupt:
        pass
    finally:
        print("Bot closed")

def add_update_babel_args(subparser: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparser.add_parser('update_babel', help='Extracts messages from source code and updates messages.pot')
    parser.set_defaults(func=update_babel)

def add_compile_babel_args(subparser: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparser.add_parser('compile_babel', help='Compiles translations to .mo files')
    parser.set_defaults(func=update_babel)

def add_start_args(subparser: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparser.add_parser('start', help='Start the bot')
    parser.set_defaults(func=start)

    parser.add_argument(
        '--sync_tree', 
        help='whether to sync the CommandTree on bot start, use it when you change a command, or a translation', 
        action='store_true',
        dest='sync_tree',
        )


def parse_args() -> Tuple[argparse.ArgumentParser, argparse.Namespace]:
    parser = argparse.ArgumentParser(prog='taho', description='Tools for Taho (translations, update and start)')
    parser.add_argument('-v', '--version', action='store_true', help='shows the bot version')
    parser.set_defaults(func=core)

    subparser = parser.add_subparsers(dest='subcommand', title='subcommands')
    add_update_babel_args(subparser)
    add_compile_babel_args(subparser)
    add_start_args(subparser)
    return parser, parser.parse_args()

def main() -> None:
    parser, args = parse_args()
    args.func(parser, args)


if __name__ == '__main__':
    main()