
import random
import textwrap

from discord import Color, Embed
from discord.enums import ButtonStyle
from discord.ext.commands import Cog, Context, hybrid_command
from discord.ui import Button, View
import discord

from .utils import *


class Help(Cog):
    def __init__(self, bot):
        self.bot = bot

    def Overview(self) -> Embed:
        embed = Embed(
            title = 'HELP!!!',
            description = textwrap.dedent(f'''
                **Available commands:**
                **Bot prefix:** {", ".join(self.bot.config.read(list, "BOT", "prefixes"))}

                **__anime__**
                **__manga__**
                **__animeid__**
                **__mangaid__**
                **__random__**
                **__top__**
                **__ping__**
                **__reload__**

                For more information on a specific command,
                type `{self.bot.config.read(list, "BOT", "prefixes")[0]} help <command>`


                **Developer: <@893868099797934090>**'''),
            color = Color.blurple(),
            url = 'https://github.com/LynBean/MalDisc')

        embed.set_image(url = f'https://opengraph.githubassets.com/{random.getrandbits(128):032x}/LynBean/MalDisc')
        return embed

    def Anime(self) -> Embed:
        return Embed(
            title = 'anime',
            description = textwrap.dedent(f'''
                **Description:**
                Search for an anime.

                **Usage:**
                `{self.bot.config.read(list, "BOT", "prefixes")[0]} anime <anime name>`

                **Example:**
                `{self.bot.config.read(list, "BOT", "prefixes")[0]} anime re zero`'''),
            color = Color.dark_blue())

    def Manga(self) -> Embed:
        return Embed(
            title = 'manga',
            description = textwrap.dedent(f'''
                **Description:**
                Search for a manga.

                **Usage:**
                `{self.bot.config.read(list, "BOT", "prefixes")[0]} manga <manga name>`

                **Example:**
                `{self.bot.config.read(list, "BOT", "prefixes")[0]} manga re zero`'''),
            color = Color.dark_blue())

    def Animeid(self) -> Embed:
        return Embed(
            title = 'animeid',
            description = textwrap.dedent(f'''
                **Description:**
                Search for an anime by its ID.

                **Usage:**
                `{self.bot.config.read(list, "BOT", "prefixes")[0]} animeid <anime id>`

                **Example:**
                `{self.bot.config.read(list, "BOT", "prefixes")[0]} animeid 50709`'''),
            color = Color.dark_blue())

    def Mangaid(self) -> Embed:
        return Embed(
            title = 'mangaid',
            description = textwrap.dedent(f'''
                **Description:**
                Search for a manga by its ID.

                **Usage:**
                `{self.bot.config.read(list, "BOT", "prefixes")[0]} mangaid <manga id>`

                **Example:**
                `{self.bot.config.read(list, "BOT", "prefixes")[0]} mangaid 98930`'''),
            color = Color.dark_blue())

    def Random(self) -> Embed:
        return Embed(
            title = 'random',
            description = textwrap.dedent(f'''
                **Description:**
                Get a random anime or manga.

                **Usage:**
                `{self.bot.config.read(list, "BOT", "prefixes")[0]} random <anime/manga>`

                **Available parameters:**
                `<integer>`: *How much entries to return in a single command. Default: 3*


                **Example:**
                `{self.bot.config.read(list, "BOT", "prefixes")[0]} random anime`
                `{self.bot.config.read(list, "BOT", "prefixes")[0]} random manga 25`'''),
            color = Color.dark_blue())

    def Top(self) -> Embed:
        return Embed(
            title = 'top',
            description = textwrap.dedent(f'''
                **Description:**
                Get the top anime or manga.

                **Usage:**
                `{self.bot.config.read(list, "BOT", "prefixes")[0]} top <anime/manga>`

                **Available flags:**
                `-r, --ranking`: *Show ranking based on either "all", "airing", or many other types. Default: "all"*

                `-o, --offset`: *How much entries to skip, every 1 offset skips 500 entries. Default: 0*

                **Example:**
                `{self.bot.config.read(list, "BOT", "prefixes")[0]} top anime`
                `{self.bot.config.read(list, "BOT", "prefixes")[0]} top anime -r=upcoming`
                `{self.bot.config.read(list, "BOT", "prefixes")[0]} top manga -o=30`
                `{self.bot.config.read(list, "BOT", "prefixes")[0]} top manga -r=all -o=30`'''),
            color = Color.dark_blue())

    def Ping(self) -> Embed:
        return Embed(
            title = 'ping',
            description = textwrap.dedent(f'''
                **Description:**
                Get the bot's latency.
                Pong! {round(self.bot.latency * 1000)}ms

                **Usage:**
                `{self.bot.config.read(list, "BOT", "prefixes")[0]} ping`'''),
            color = Color.dark_blue())

    def Reload(self) -> Embed:
        return Embed(
            title = 'reload',
            description = textwrap.dedent(f'''
                **Description:**
                Reload all cogs.

                **Usage:**
                `{self.bot.config.read(list, "BOT", "prefixes")[0]} reload`'''),
            color = Color.dark_blue())

    @hybrid_command(
        name = 'help',
        description = 'Shows this message')
    async def help(self, context: Context, *, command: str = 'overview'):

        def build_embed(command: str) -> Embed:
            try: embed = getattr(self, command.capitalize())()
            except AttributeError: embed = Embed(title = 'Command not found', color = Color.red())
            embed.set_thumbnail(url = self.bot.user.avatar.url)
            embed.set_author(name = f'{context.author.name} is asking for ...', icon_url = context.author.avatar.url)
            embed.set_footer(text = f'MalDisc version: {get_version()}')
            return embed

        await context.reply(
            mention_author = False,
            embed = build_embed(command),
            view = View().add_item(Button(
                style = ButtonStyle.link,
                label = 'Source Code',
                url = 'https://github.com/LynBean/MalDisc')))

        return


async def setup(bot):
    await bot.add_cog(
        Help(bot))
