
import asyncio
import itertools
import json
import os
import platform
import sys

from discord.ext import commands
from discord.ext.commands import Bot, Context
import discord

from .constants import *
from .utils import get_logger

def main():

    logger = get_logger()

    if not os.path.exists(DIR_PATH):
        os.mkdir(DIR_PATH)

    if not os.path.isfile(DIR_PATH + '/config.json'):
        with open(DIR_PATH + '/config.json', 'w+') as file:
            json.dump(DEFAULT_CONFIG, file, indent = 4, sort_keys = False)
        sys.exit(f'config.json not found. A default one has been created under the following path:\n{DIR_PATH}/config.json\nPlease fill out the config.json file before running the bot')

    else:
        with open(DIR_PATH + '/config.json') as file:
            config = json.load(file)

    def get_prefix(bot, message):
        total = []
        a = map(''.join, itertools.product(*((c.upper(), c.lower()) for c in config['prefix'])))
        for x in list(a): total.append(x)
        prefixes = list(total)

        return commands.when_mentioned_or(*prefixes)(bot, message)

    intents = discord.Intents.default()
    intents.message_content = True
    bot = Bot(
        case_insensitive = True,
        command_prefix = get_prefix,
        description = 'MyAnimeList in Discord Now!',
        intents = intents,
        help_command = None)

    @bot.event
    async def on_ready() -> None:
        logger.info(f'Logged in as {bot.user.name} - {bot.user.id}')
        logger.info(f'Discord API version: {discord.__version__}')
        logger.info(f'Python version: {platform.python_version()}')
        logger.info(f'Running on: {platform.system()} {platform.release()} ({os.name})')
        logger.info(f'Prefix: {config["prefix"]} (case insensitive and acceptable with maximum 1 space after prefix), mentionable')
        logger.info(f'Loaded {len(bot.cogs)} cogs with a total of {len(bot.commands)} commands')

    @bot.event
    async def on_message(message: discord.Message) -> None:
        if message.author == bot.user or message.author.bot:
            return
        if message.content.lower().startswith(f'{config["prefix"].lower()} '):
            message.content = config["prefix"] + message.content[len(config["prefix"]) + 1:]

        await bot.process_commands(message)

    @bot.event
    async def on_command_completion(context: Context) -> None:
        full_command_name = context.command.qualified_name
        split = full_command_name.split(' ')
        executed_command = str(split[0])
        if context.guild is not None:
            logger.info(
                f'Executed {executed_command} command in {context.guild.name} (ID: {context.guild.id}) by {context.author} (ID: {context.author.id})')
        else:
            logger.info(
                f'Executed {executed_command} command by {context.author} (ID: {context.author.id}) in DMs')

    @bot.event
    async def on_command_error(context: Context, error) -> None:
        if isinstance(error, commands.CommandNotFound):
            return

        else:
            full_command_name = context.command.qualified_name
            split = full_command_name.split(' ')
            executed_command = str(split[0])
            if context.guild is not None:
                logger.error(
                    f'Failed to execute {executed_command} command in {context.guild.name} (ID: {context.guild.id}) by {context.author} (ID: {context.author.id})\n{error}\n')
            else:
                logger.error(
                    f'Failed to execute {executed_command} command by {context.author} (ID: {context.author.id}) in DMs\n{error}\n')

            return await context.send(f'**{context.author.mention}** {error}')

    @bot.command()
    async def ping(context: Context):
        await context.send(f'Pong! {round(bot.latency * 1000)}ms')

    @bot.command()
    async def reload(context: Context):
        await load_cogs(
            context = context,
            bot_command = True)

    async def load_cogs(
        context: Context = None,
        bot_command: bool = False
        ) -> None:
        for file in os.listdir(os.path.dirname(os.path.realpath(__file__))):
            if not file.endswith('.py'):
                continue

            extension = file[:-3]
            try:
                await bot.load_extension(f'maldisc.{extension}')
                logger.info(f'Loaded extension: {extension}')
                if bot_command == True:
                    await context.send(f'✅ Loaded extension: {extension}')

            except commands.ExtensionAlreadyLoaded:
                await bot.reload_extension(f'maldisc.{extension}')
                logger.info(f'Reloaded extension: {extension}')
                if bot_command == True:
                    await context.send(f'⚠️ Reloaded extension: {extension}')

            except Exception as e:
                exception = f'{type(e).__name__}: {e}'
                logger.error(f'Failed to load extension: {extension}\n{exception}\n')
                if bot_command == True:
                    await context.send(f'❌ Failed to load extension: {extension}\n{exception}')


    asyncio.run(load_cogs())
    bot.run(
        config['token'],
        reconnect = True)
