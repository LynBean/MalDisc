
import asyncio
import itertools
import os
import platform
import random
import textwrap

from discord import Intents, Message
from discord.ext.commands import Bot, CommandNotFound, Context, ExtensionAlreadyLoaded
from discord.ui import Button, View
import discord

from .constants import *
from .exceptions import *
from .utils import *

def main():
    config = MalDiscConfigParser()
    log_utils = MalDiscLogging()
    logger = log_utils.get_logger()

    def get_prefix():
        total = []

        for prefix in config.read(list, 'BOT', 'prefixes'):
            a = map(''.join, itertools.product(
                *((c.upper(), c.lower()
                 ) for c in prefix)))

            for x in list(a):
                total.append(x)

        return tuple(dict.fromkeys(total))

    prefixes = get_prefix()
    intents = Intents().all()
    bot = Bot(
        case_insensitive = True,
        command_prefix = '',
        description = 'MyAnimeList in Discord Now!',
        intents = intents,
        help_command = None)

    bot.config = config

    @bot.event
    async def on_ready():
        logger.info(f'Logged in as {bot.user.name} - {bot.user.id}')
        logger.info(f'MalDisc version: {get_version()}')
        logger.info(f'Discord API version: {discord.__version__}')
        logger.info(f'Python version: {platform.python_version()}')
        logger.info(f'Running on: {platform.system()} {platform.release()} ({os.name})')
        logger.info(f'Prefix (case insensitive): {", ".join(config.read(list, "BOT", "prefixes"))}')
        logger.info(f'Loaded {len(bot.cogs)} cogs with a total of {len(bot.commands)} commands')
        return

    @bot.event
    async def on_message(message: Message):
        if message.author == bot.user or message.author.bot:
            return

        if 'https://myanimelist.net/' in message.content.lower() and config.read(bool, 'FEATURES', 'enableurldetection') == True:
            splitted = message.content.split('https://myanimelist.net/')[1].split('/')
            type = splitted[0]
            id = splitted[1]

            if type != 'anime' and type != 'manga':
                return

            message.content = f"{'animeid' if type == 'anime' else 'mangaid' if type == 'manga' else None} {id}"
            await bot.process_commands(message)
            return

        for prefix in prefixes:
            if not message.content.lower().startswith(prefix):
                continue

            message.content = message.content[len(prefix):].lstrip()
            await bot.process_commands(message)
            return

    @bot.event
    async def on_command_completion(context: Context):
        full_command_name = context.command.qualified_name
        split = full_command_name.split(' ')
        executed_command = str(split[0])
        logger.info(f'Executed {executed_command} command '\
            f'{f"in {context.guild.name} (ID: {context.guild.id}) by {context.author} (ID: {context.author.id})" if context.guild is not None else f"by {context.author} (ID: {context.author.id}) in DMs"}')

        return

    @bot.event
    async def on_command_error(context: Context, error):
        if isinstance(error, CommandNotFound):
            await context.send(f'Command not found. Use '\
                f'`{config.read(list, "BOT", "prefixes")[0]} help` '\
                    'to see all available commands')

        else:
            full_command_name = context.command.qualified_name
            split = full_command_name.split(' ')
            executed_command = str(split[0])
            logger.error(f'Failed to execute {executed_command} command '\
                f'{f"in {context.guild.name} (ID: {context.guild.id}) by {context.author} (ID: {context.author.id})" if context.guild is not None else f"by {context.author} (ID: {context.author.id}) in DMs"} '\
                    f'{error}\n')

            await context.send(f'**{context.author.mention}** {error}')

        return

    @bot.command()
    async def ping(context: Context):
        await context.send(f'Pong! {round(bot.latency * 1000)}ms')
        return

    @bot.command()
    async def reload(context: Context):
        await load_cogs(
            context = context,
            bot_command = True)

        return

    async def load_cogs(
        context: Context = None,
        bot_command: bool = False):
        for file in os.listdir(os.path.dirname(os.path.realpath(__file__))):
            if not file.endswith('.py'):
                continue

            enabled = ['anime', 'manga', 'random', 'top', 'help', 'eval']
            if file[:-3] not in enabled:
                continue

            extension = file[:-3]
            try:
                await bot.load_extension(f'maldisc.{extension}')
                logger.info(f'Loaded extension: {extension}')
                if bot_command == True:
                    await context.send(f'✅ Loaded extension: {extension}')

            except ExtensionAlreadyLoaded:
                await bot.reload_extension(f'maldisc.{extension}')
                logger.info(f'Reloaded extension: {extension}')
                if bot_command == True:
                    await context.send(f'⚠️ Reloaded extension: {extension}')

            except Exception as e:
                exception = f'{type(e).__name__}: {e}'
                logger.error(f'Failed to load extension: {extension}\n{exception}\n')
                if bot_command == True:
                    await context.send(f'❌ Failed to load extension: {extension}\n{exception}')

        return


    asyncio.run(load_cogs())
    bot.run(
        config.read(str, 'BOT', 'token'),
        reconnect = True)
