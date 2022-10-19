
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


class Top(Cog):

    def __init__(self, bot):
        self.bot = bot

    @hybrid_command(
        name = 'top',
        description = 'Get the top anime or manga')
    async def Top(
        self,
        context: Context,
        type: str,
        *,
        args: Optional[str]) -> None:

        ranking_type = 'all'
        offset = 0

        if args != None:
            for arg in args.split():
                if arg.startswith(('-offset', '--offset', '-o')):
                    offset = arg.split('=')[1]

                    if offset.isdigit():
                        offset = int(offset)
                        if offset < 0:
                            raise BadArgument('Offset must be a positive integer')

                    else:
                        raise BadArgument('Offset must be an integer')

                elif arg.startswith(('-ranking', '--ranking', '-r')):
                    ranking_type = arg.split('=')[1].lower()

                else:
                    raise BadArgument(f'Invalid argument: {arg}')

        # Validate type
        type = type.lower()
        if type not in ('anime', 'manga'):
            raise BadArgument('Type must be either anime or manga')

        if self.bot.config.read(bool, 'MAL_API', 'enabled') == True:
            if type == 'anime':
                module = MyAnimeList.Anime.Ranking
            elif type == 'manga':
                module = MyAnimeList.Manga.Ranking

        else:
            if type == 'anime':
                module = Jikan.Top.Anime
            elif type == 'manga':
                module = Jikan.Top.Manga

        # Validate ranking_type
        if module == MyAnimeList.Anime.Ranking:
            if ranking_type not in ('all', 'airing', 'upcoming', 'tv', 'ova', 'movie', 'special', 'bypopularity', 'favorite'):
                raise BadArgument('Ranking type must be either all, airing, upcoming, tv, ova, movie, special, bypopularity, or favorite')

        elif module == MyAnimeList.Manga.Ranking:
            if ranking_type not in ('all', 'manga', 'novels', 'oneshots', 'doujin', 'manhwa', 'manhua', 'bypopularity', 'favorite'):
                raise BadArgument('Ranking type must be either all, manga, novels, oneshots, doujin, manhwa, manhua, bypopularity, or favorite')

        elif module == Jikan.Top.Anime:
            if ranking_type not in ('all', 'airing', 'upcoming', 'bypopularity', 'favorite'):
                raise BadArgument('Ranking type must be either all, airing, upcoming, bypopularity, or favorite')

        elif module == Jikan.Top.Manga:
            if ranking_type not in ('all', 'publishing', 'upcoming', 'bypopularity', 'favorite'):
                raise BadArgument('Ranking type must be either all, publishing, upcoming, bypopularity, or favorite')

        message = await context.reply(
            mention_author = False,
            embed = Embed(
                title = 'Waiting for MyAnimeList response ...',
                color = Color.dark_gray()))

        results = await module(
            ranking_type = ranking_type,
            filter = ranking_type,
            limit = 500,
            page = offset,
            offset = offset * 500,
            fields = 'id,title,main_picture,mean,rank,media_type,num_episodes,num_volumes,num_list_users',
            sfw = False,
            nsfw = True)

        if len(results['data']) == 0:
            await message.edit(
                embed = Embed(
                    title = 'No results found',
                    color = Color.dark_red()))
            return

        page = []
        pages = []
        for index, result in enumerate(results['data']):
            if index % 25 == 0 and index != 0:
                pages.append(page)
                page = []

            if module == MyAnimeList.Anime.Ranking:
                try: picture = result['node']['main_picture']['medium']
                except KeyError: picture = None
                try: score = result['node']['mean']
                except KeyError: score = None
                try: rank = result['node']['rank']
                except KeyError: rank = None
                try: media_type = result['node']['media_type']
                except KeyError: media_type = None
                try: episodes = result['node']['num_episodes']
                except KeyError: episodes = None
                try: members = result['node']['num_list_users']
                except KeyError: members = None

                page.append({
                    'id': result['node']['id'], 'title': result['node']['title'], 'picture': picture,
                    'score': score, 'rank': rank, 'media_type': media_type,
                    'episodes': episodes, 'members': members})

            elif module == MyAnimeList.Manga.Ranking:
                try: picture = result['node']['main_picture']['medium']
                except KeyError: picture = None
                try: score = result['node']['mean']
                except KeyError: score = None
                try: rank = result['node']['rank']
                except KeyError: rank = None
                try: media_type = result['node']['media_type']
                except KeyError: media_type = None
                try: episodes = result['node']['num_volumes']
                except KeyError: episodes = None
                try: members = result['node']['num_list_users']
                except KeyError: members = None

                page.append({
                    'id': result['node']['id'], 'title': result['node']['title'], 'picture': picture,
                    'score': score, 'rank': rank, 'media_type': media_type,
                    'episodes': episodes, 'members': members})

            elif module == Jikan.Top.Anime:
                page.append({
                    'id': result['mal_id'], 'title': result['title'], 'picture': result['images']['jpg']['image_url'],
                    'score': result['score'], 'rank': result['rank'], 'media_type': result['type'],
                    'episodes': result['episodes'], 'members': result['members']})

            elif module == Jikan.Top.Manga:
                page.append({
                    'id': result['mal_id'], 'title': result['title'], 'picture': result['images']['jpg']['image_url'],
                    'score': result['score'], 'rank': result['rank'], 'media_type': result['type'],
                    'episodes': result['volumes'], 'members': result['members']})

            if index == len(results['data']) - 1:
                pages.append(page)

            continue

        def paging_view() -> Select:
            nonlocal page_index
            obj = Select(
                placeholder = f'You are in page {page_index + 1} among {len(pages)} pages',
                options = [SelectOption(
                    label = f'Page 👉🏽 {index + 1} 👈🏽',
                    value = int(index)
                    ) for index in range(len(pages))])

            obj.callback = paging_callback
            return obj

        def entries_view() -> Select:
            nonlocal page_index
            obj = Select(
                placeholder = f'Entries of rank between {pages[page_index][0]["rank"]} - {pages[page_index][-1]["rank"]}',
                options = [SelectOption(
                    label = (f"{entry['rank']}🔥 {entry['title']}")[:100],
                    value = int(index)
                    ) for index, entry in enumerate(pages[page_index])])

            obj.callback = entries_callback
            return obj

        def embed() -> Embed:
            nonlocal page_index, entry_index
            obj = Embed(
                title = pages[page_index][entry_index]['title'],
                url = 'https://myanimelist.net/anime/' + str(pages[page_index][entry_index]['id']),
                description = textwrap.dedent(f'''
                    {pages[page_index][entry_index]['media_type']} ({pages[page_index][entry_index]['episodes']} {'eps' if type == 'anime' else 'vols' if type == 'manga' else ''})
                    {f'Scored {pages[page_index][entry_index]["score"]}' if pages[page_index][entry_index]['score'] != None else 'Not scored yet'}
                    {f'{pages[page_index][entry_index]["members"]:,} of members' if pages[page_index][entry_index]['members'] != None else ''}'''),
                color = Color.dark_blue())

            obj.set_author(name = f'Rank {pages[page_index][entry_index]["rank"]}')
            obj.set_image(url = pages[page_index][entry_index]['picture'])
            return obj

        async def entries_callback(interaction: Interaction):
            await interaction.response.defer()
            nonlocal entry_index
            entry_index = int(interaction.data['values'][0])
            await message.edit(
                embed = embed())

        async def paging_callback(interaction: Interaction):
            await interaction.response.defer()
            nonlocal page_index
            page_index = int(interaction.data['values'][0])
            view.stop()

        async def about_callback(interaction: Interaction):
            await interaction.response.defer()
            nonlocal page_index, entry_index
            id = int(pages[page_index][entry_index]['id'])

            if type == 'anime':
                module = Anime
            elif type == 'manga':
                module = Manga

            await module(self.bot).SendContext(context, id)

        about_button = Button(
            style = ButtonStyle.blurple,
            label = 'Show me more about this entry')

        about_button.callback = about_callback
        page_index = 0

        while True:
            entry_index = 0
            view = View()
            view.timeout = self.bot.config.read(float, 'FEATURES', 'interactiontimeout')


            view.add_item(about_button)
            view.add_item(entries_view())
            if len(pages) != 1:
                view.add_item(paging_view())

            await message.edit(
                view = view,
                embed = embed())

            if await view.wait() == True:
                break

        await message.edit(view = None)
        return


async def setup(bot):
    await bot.add_cog(
        Top(bot))
