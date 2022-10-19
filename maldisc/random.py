
from typing import Optional
import textwrap

from discord import Color, Embed, Interaction, SelectOption
from discord.enums import ButtonStyle
from discord.ext.commands import BadArgument, Cog, Context, hybrid_command
from discord.ui import Button, Select, View
import discord

from .anime import Anime
from .constants import *
from .manga import Manga
from .requests import *

class Random(Cog):
    def __init__(self, bot):
        self.bot = bot

    @hybrid_command(
        name = 'random',
        description = 'Get a random entry from MyAnimeList')
    async def random(
        self,
        context: Context,
        type: str,
        entries: Optional[int] = 3) -> None:

        if entries > 25: raise commands.BadArgument('You can only get 25 entries at a time.')
        if entries < 1: raise commands.BadArgument('You must get at least 1 entry.')

        type = str(type)
        if type.lower() == 'anime': api = Jikan.Random.Anime
        elif type.lower() == 'manga': api = Jikan.Random.Manga
        elif type.lower() in ('characters', 'character'): api = Jikan.Random.Characters
        elif type.lower() == 'people': api = Jikan.Random.People
        elif type.lower() in ('users', 'user'): api = Jikan.Random.Users
        else: raise commands.BadArgument('Type must be either anime, manga, characters, person, or users')

        if api == Jikan.Random.Users: estimated_time = -(entries // -3) * 10
        else: estimated_time = -(entries // -3)

        message = await context.reply(
            mention_author = False,
            embed = Embed(
                title = 'Waiting for MyAnimeList response ...',
                description = textwrap.dedent(f'''
                    Entries requested: {entries}
                    Estimated time: {estimated_time} seconds'''),
                color = Color.dark_gray()
                ).set_footer(text = 'Due to prevent DDOS, MyAnimeList only allows 3 requests per second, 60 requests per minute'))

        results = [await api() for _ in range(entries)]

        if api == Jikan.Random.Anime:
            embeds = []
            for result in results:
                result = result['data']

                embed = Embed(
                    title = result['title'],
                    url = result['url'],
                    description = textwrap.dedent(f'''
                        {result['type']} ({result['episodes']} eps)
                        {f'Scored {result["score"]} by {result["scored_by"]} users' if result['score'] != None else 'Not scored yet'}
                        {f'{result["members"]:,} of members' if result['members'] != None else ''}'''),
                    color = Color.dark_blue())

                embed.set_image(url = result['images']['jpg']['image_url'])
                embeds.append(embed)
                continue

            selection = Select(
                placeholder = f'Here you go, {entries} random anime',
                options = [SelectOption(
                    label = (f"{result['data']['title']}")[:100], value = int(index))
                           for index, result in enumerate(results)])

        elif api == Jikan.Random.Manga:
            embeds = []
            for result in results:
                result = result['data']

                embed = Embed(
                    title = result['title'],
                    url = result['url'],
                    description = textwrap.dedent(f'''
                        {result['type']} ({result['volumes']} vols)
                        {f'Scored {result["score"]} by {result["scored_by"]} users' if result['score'] != None else 'Not scored yet'}
                        {f'{result["members"]:,} of members' if result['members'] != None else ''}'''))

                embed.set_image(url = result['images']['jpg']['image_url'])
                embeds.append(embed)
                continue

            selection = Select(
                placeholder = f'Here you go, {entries} random manga',
                options = [SelectOption(
                    label = (f"{result['data']['title']}")[:100], value = int(index))
                           for index, result in enumerate(results)])

        elif api == Jikan.Random.Characters:
            results = [result['data']['name'] for result in results]
            return await message.edit(
                embed = Embed(
                    title = 'This feature is not yet implemented',
                    description = f'Results : {", ".join(results)}',
                    color = Color.red()))

        elif api == Jikan.Random.People:
            results = [result['data']['name'] for result in results]
            return await message.edit(
                embed = Embed(
                    title = 'This feature is not yet implemented',
                    description = f'Results : {", ".join(results)}',
                    color = Color.red()))

        elif api == Jikan.Random.Users:
            results = [result['data']['username'] for result in results]
            return await message.edit(
                embed = Embed(
                    title = 'This feature is not yet implemented',
                    description = f'Results : {", ".join(results)}',
                    color = Color.red()))


        view = View()
        view.timeout = self.bot.config.read(float, 'FEATURES', 'interactiontimeout')
        entry_button = Button(
            style = ButtonStyle.blurple,
            label = 'Show me more about this entry')

        async def selection_callback(interaction: Interaction):
            await interaction.response.defer()
            nonlocal current_index
            current_index = int(interaction.data['values'][0])
            await interaction.followup.edit_message(
                message_id = message.id,
                embed = embeds[current_index])

        async def entry_callback(interaction: Interaction):
            await interaction.response.defer()
            id = int(results[current_index]['data']['mal_id'])

            if api == Jikan.Random.Anime: module = Anime
            elif api == Jikan.Random.Manga: module = Manga

            await module(self.bot).SendContext(context, id)

        entry_button.callback = entry_callback
        view.add_item(entry_button)
        selection.callback = selection_callback
        if entries > 1: view.add_item(selection)

        await message.edit(
            embed = embed,
            view = view)

        current_index = -1
        await view.wait()
        await message.edit(view = None)

        return


async def setup(bot):
    await bot.add_cog(
        Random(bot))
