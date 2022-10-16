
import asyncio
import itertools
import json
import os
import platform
import sys
import textwrap

from discord.ext import commands
from discord.ext.commands import Bot, Context
from discord.ui import Button, View
import discord

from .constants import *
from .exceptions import *
from .utils import get_logger, get_version

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

    def get_prefix():
        total = []
        a = map(''.join, itertools.product(*((c.upper(), c.lower()) for c in config['prefix'])))
        for x in list(a): total.append(x)

        return tuple(total)

    intents = discord.Intents.default()
    intents.message_content = True
    bot = Bot(
        case_insensitive = True,
        command_prefix = '',
        description = 'MyAnimeList in Discord Now!',
        intents = intents,
        help_command = None)
    bot.config = config

    @bot.event
    async def on_ready() -> None:
        logger.info(f'Logged in as {bot.user.name} - {bot.user.id}')
        logger.info(f'MalDisc version: {get_version()}')
        logger.info(f'Discord API version: {discord.__version__}')
        logger.info(f'Python version: {platform.python_version()}')
        logger.info(f'Running on: {platform.system()} {platform.release()} ({os.name})')
        logger.info(f'Prefix: {config["prefix"]} (case insensitive)')
        logger.info(f'Loaded {len(bot.cogs)} cogs with a total of {len(bot.commands)} commands')

    @bot.event
    async def on_message(message: discord.Message) -> None:
        if message.author == bot.user or message.author.bot:
            return

        if message.content.lower().startswith(get_prefix()):
            message.content = message.content[len(config["prefix"]):].lstrip()
            await bot.process_commands(message)

        if 'https://myanimelist.net/' in message.content.lower() and config['enable_url_detection'] == True:
            splitted = message.content.split('https://myanimelist.net/')[1].split('/')
            type = splitted[0]
            id = splitted[1]

            message.content = f"{'animeid' if type == 'anime' else 'mangaid' if type == 'manga' else None} {id}"
            await bot.process_commands(message)

        return

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
            return await context.send(f'Command not found. Use `{config["prefix"]} help` to see all available commands')

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
    async def help(context: Context):
        description = textwrap.dedent(
            f'''
            **MyAnimeList in Discord Now!**
            
            **{config["prefix"]} __anime__ <title>**: Search for an anime
            **{config["prefix"]} __manga__ <title>**: Search for a manga
            **{config["prefix"]} __mangaid__ <id>**: Search for a manga by its ID
            **{config["prefix"]} __animeid__ <id>**: Search for an anime by its ID
            **{config["prefix"]} __ping__**: Pong! {round(bot.latency * 1000)}ms
            **{config["prefix"]} __reload__**: Reload the bot
            
            
            **Developer: <@893868099797934090>**
            ''')
        
        embed = discord.Embed(
            title = 'HELP!!!',
            description = description,
            color = discord.Color.blurple(),
            url = 'https://github.com/LynBean/maldisc')
        embed.set_thumbnail(url = bot.user.avatar.url)
        embed.set_author(name = f'{context.author.name} is asking for ...', icon_url = context.author.avatar.url)
        embed.set_footer(text = f'MalDisc version: {get_version()}')
        await context.reply(
            mention_author = False,
            embed = embed,
            view = View().add_item(Button(
                style = discord.ButtonStyle.link,
                label = 'Source Code',
                url = 'https://github.com/LynBean/maldisc')))

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

            enabled = ['anime', 'manga']
            if file[:-3] not in enabled:
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
