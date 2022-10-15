
import asyncio

from discord.enums import ButtonStyle
from discord.ext import commands
from discord.ext.commands import Context
from discord.ui import Button, Select, View
import discord

from datetime import datetime, timezone

from .constants import *
from .requests import *

class Manga(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def Search(self, query: str) -> list:
        requester = Jikan.Manga.Search if self.bot.config['mal_config']['enabled'] != True else MyAnimeList.Manga.Search
        response = await requester(
            query = query,
            limit = 25,
            order_by = 'score',
            sort = 'desc',
            fields = 'id,title,main_picture,mean,rank,media_type,num_episodes,num_list_users',
            sfw = False,
            nsfw = True)

        result = []

        if requester == Jikan.Manga.Search:
            for dict in response['data']:
                result.append({
                    'id': dict['mal_id'],
                    'title': dict['title'],
                    'picture': dict['images']['jpg']['image_url'],
                    'score': dict['score'],
                    'rank': dict['rank'],
                    'media_type': dict['type'],
                    'volumes': dict['volumes'],
                    'members': dict['members']})

                continue

        elif requester == MyAnimeList.Manga.Search:
            for dict in response['data']:
                dict = dict['node']
                try: picture = dict['main_picture']['medium']
                except KeyError: picture = None
                try: score = dict['mean']
                except KeyError: score = None
                try: rank = dict['rank']
                except KeyError: rank = None
                try: media_type = dict['media_type']
                except KeyError: media_type = None
                try: volumes = dict['num_volumes']
                except KeyError: volumes = None
                try: members = dict['num_list_users']
                except KeyError: members = None

                result.append({
                    'id': dict['id'],
                    'title': dict['title'],
                    'picture': picture,
                    'score': score,
                    'rank': rank,
                    'media_type': media_type,
                    'volumes': volumes,
                    'members': members})

                continue

        return result

    class MangaDetails:
        def __init__(self, id: int):
            self.id = id
            self.full = None
            self.characters = None
            self.relations = None
            self.news = None
            self.topics = None

        async def getFull(self) -> None:
            if self.full != None: return
            self.full = await Jikan.Manga.Full(id = self.id)

        async def getCharacters(self) -> None:
            if self.characters != None: return
            self.characters = await Jikan.Manga.Characters(id = self.id)

        async def getRelations(self) -> None:
            if self.relations != None: return
            self.relations = (await self.arrangeFull())['relations']

        async def getNews(self) -> None:
            if self.news != None: return
            self.news = await Jikan.Manga.News(id = self.id)

        async def getTopics(self) -> None:
            if self.topics != None: return
            self.topics = await Jikan.Manga.Topics(id = self.id)

        async def arrangeFull(self) -> dict:
            await self.getFull()
            data = self.full['data']
            return {
                'id': data['mal_id'], 'url': data['url'], 'image': data['images']['jpg']['image_url'],
                'small_image': data['images']['jpg']['small_image_url'], 'title': data['title'],
                'title_english': data['title_english'], 'title_japanese': data['title_japanese'],
                'media_type': data['type'], 'chapters': data['chapters'], 'volumes': data['volumes'],
                'status': data['status'], 'publishing': data['publishing'], 'published': data['published']['string'],
                'score': data['score'], 'scored_by': data['scored_by'], 'rank': data['rank'],
                'popularity': data['popularity'], 'members': data['members'], 'favorites': data['favorites'],
                'synopsis': data['synopsis'], 'background': data['background'], 'authors': [author['name'] for author in data['authors']],
                'genres': [genre['name'] for genre in data['genres']], 'relations': data['relations'], 'external': data['external']
            }

        async def arrangeCharacters(self) -> tuple:
            await self.getCharacters()
            data = self.characters['data']
            if len(data) == 0: return None

            main = []
            supporting = []
            for character in data:
                group = main if character['role'] == 'Main' else supporting
                group.append({
                    'id': character['character']['mal_id'], 'url': character['character']['url'],
                    'image': character['character']['images']['jpg']['image_url'], 'name': character['character']['name']
                })

            return main, supporting

        async def arrangeNews(self) -> list:
            await self.getNews()
            data = self.news['data']
            if len(data) == 0: return None

            result = []
            for news in data:
                date = datetime.fromisoformat(
                    news['date']
                    ).astimezone(
                        timezone.utc
                        ).strftime(
                            '%Y-%m-%d %H:%M:%S')

                result.append({
                    'title': news['title'], 'url': news['url'], 'image': news['images']['jpg']['image_url'],
                    'date': date, 'author': news['author_username'], 'forum_url': news['forum_url'],
                    'comments': news['comments'], 'excerpt': news['excerpt']
                })

            return result

        async def arrangeTopics(self) -> list:
            await self.getTopics()
            data = self.topics['data']
            if len(data) == 0: return None

            result = []
            for thread in data:
                date = datetime.fromisoformat(
                    thread['date']
                    ).astimezone(
                        timezone.utc
                        ).strftime(
                            '%Y-%m-%d')

                result.append({
                    'title': thread['title'], 'url': thread['url'],
                    'date': date, 'author': thread['author_username'],
                    'comments': thread['comments']
                })

            return result

        async def buildOverview(self) -> None:
            data = await self.arrangeFull()
            embed = discord.Embed(
                title = data['title'],
                url = data['url'],
                description = data['synopsis'],
                color = discord.Color.random())
            embed.set_thumbnail(url = data['image'])
            embed.set_footer(text = data['background'])
            if isinstance(data['score'], float):
                embed.add_field(
                    name = 'Score',
                    value = f"{data['score']:,.2f} ⭐",
                    inline = True)
            if isinstance(data['rank'], int):
                embed.add_field(
                    name = 'Rank',
                    value = f"No. {data['rank']:,} ⬆️",
                    inline = True)
            if isinstance(data['popularity'], int):
                embed.add_field(
                    name = 'Popularity',
                    value = f"No. {data['popularity']:,} ⬆️",
                    inline = True)
            if isinstance(data['members'], int):
                embed.add_field(
                    name = 'Members',
                    value = f"{data['members']:,} 👥",
                    inline = True)
            if isinstance(data['favorites'], int):
                embed.add_field(
                    name = 'Favorites',
                    value = f"{data['favorites']:,} ⭐",
                    inline = True)
            if data['media_type'] != None:
                embed.add_field(
                    name = 'Type',
                    value = f"{data['media_type']} 📺",
                    inline = True)
            if len(data['genres']) > 0:
                embed.add_field(
                    name = 'Genres',
                    value = ', '.join(data['genres']),
                    inline = True)
            if data['status'] != None:
                embed.add_field(
                    name = 'Status',
                    value = f"{data['status']} 🟩",
                    inline = True)
            if isinstance(data['chapters'], int):
                embed.add_field(
                    name = 'Chapters',
                    value = f"{data['chapters']:,} 🟦",
                    inline = True)
            if isinstance(data['volumes'], int):
                embed.add_field(
                    name = 'Volumes',
                    value = f"{data['volumes']:,} 🟥",
                    inline = True)
            if len(data['authors']) > 0:
                embed.add_field(
                    name = 'Authors',
                    value = ', '.join(data['authors']),
                    inline = True)
            if data['published'] != None:
                embed.add_field(
                    name = 'Published',
                    value = f"{data['published']} 🟪",
                    inline = True)

            return [embed]

        async def buildCharacters(self) -> None:
            data = await self.arrangeCharacters()
            if data == None:
                return [discord.Embed(
                    title = 'No Characters Found',
                    color = discord.Color.red()
                )]

            embeds = []
            main, supporting = data

            supporting_embed = discord.Embed(
                title = 'Supporting Characters',
                url = f'https://myanimelist.net/manga/{self.id}/characters',
                color = discord.Color.dark_gray())

            for character in main:
                if len(embeds) < 9:
                    embed = discord.Embed(
                        title = character['name'],
                        url = character['url'],
                        color = discord.Color.dark_gold())
                    embed.set_thumbnail(url = character['image']) if character['image'] != None else None
                    embeds.append(embed)
                    continue

                else:
                    supporting_embed.add_field(
                        name = f"{character['name']} (Main)",
                        value = f'ID: {character["id"]}',
                        inline = True)
                    continue

            for character in supporting:
                supporting_embed.add_field(
                    name = f"{character['name']}",
                    value = f'ID: {character["id"]}',
                    inline = True)

            embeds.append(supporting_embed) if len(supporting_embed.fields) > 0 else None
            return embeds

        async def buildRelations(self) -> None:
            await self.getRelations()
            data = self.relations
            if len(data) == 0:
                return [discord.Embed(
                    title = 'No Relations Found',
                    color = discord.Color.red()
                )]

            embeds = []
            for relation in data:
                embed = discord.Embed(
                    title = relation['relation'],
                    color = discord.Color.dark_magenta())

                for entry in relation['entry']:
                    embed.add_field(
                        name = f"{entry['name']} ({entry['type']})",
                        value = entry['url'])

                embeds.append(embed)
                continue

            return embeds

        async def buildNews(self) -> None:
            data = await self.arrangeNews()
            if data == None:
                return [discord.Embed(
                    title = 'No News Found',
                    color = discord.Color.red()
                )]

            embeds = []
            for i, entry in enumerate(data):
                if i == 10: break

                embed = discord.Embed(
                    title = entry['title'],
                    url = entry['url'],
                    color = discord.Color.brand_green())
                embed.set_author(name = entry['author'])
                embed.set_thumbnail(url = entry['image'])
                embed.set_footer(text = f"Published on {entry['date']}")
                embeds.append(embed)

            return embeds

        async def buildTopics(self) -> None:
            data = await self.arrangeTopics()
            if data == None:
                return [discord.Embed(
                    title = 'No Forum Found',
                    color = discord.Color.red()
                )]

            embeds = []
            for i, thread in enumerate(data):
                if i == 10: break

                embed = discord.Embed(
                    title = thread['title'],
                    url = thread['url'],
                    color = discord.Color.blurple())
                embed.set_author(name = thread['author'])
                embed.set_footer(text = f"Published on {thread['date']}")
                embeds.append(embed)

            return embeds


    @commands.hybrid_command(
        name = 'imm',
        description = 'Search your favorite manga on MyAnimeList')
    async def All(
        self,
        context: Context,
        *,
        query: str
        ) -> None:

        result = await self.Search(query)

        # If the response is empty, then return
        if len(result) == 0:
            await context.send(
                embed = discord.Embed(
                    title = 'No results found',
                    color = 0xf37a12))
            return

        # If the there are more than 1 results, then send a select menu
        elif len(result) > 1:
            embed = discord.Embed(
                title = '**MyAnimeList**',
                description = f"{context.author.mention}\n**🎉 Hooray, we received several entries that were similar to your request**\n**👉🏽` {query} `👈🏽**\n\n**Please choose one of the manga listed below 😚\nSurely, the manga you're looking for is on the list uwu~ 😶‍🌫️**",
                url = f'https://myanimelist.net/search/all?q={query.replace(" ", "%20")}&cat=all')

            embed.set_thumbnail(url = 'https://upload.wikimedia.org/wikipedia/commons/7/7a/MyAnimeList_Logo.png')

            for data in result:
                if data['picture'] == None: continue
                embed.set_image(url = data['picture'])
                break

            embed.set_footer(icon_url = context.author.avatar.url, text = f'Have a nice day !! 😚')

            # Making Buttons and Selections
            class View(discord.ui.View):
                def __init__(
                    self,
                    timeout = 300
                    ):

                    super().__init__(timeout = timeout)
                    self.choice = None

                    select_options = []
                    for index, dict in enumerate(result):
                        select_options.append(
                            discord.SelectOption(
                                label = dict['title'],
                                value = str(index),
                                description = f"{dict['media_type']} ({format(dict['volumes'], ',d') if isinstance(dict['volumes'], int) else 'N/A'} vols) Scored {dict['score'] if isinstance(dict['score'], float) else 'N/A'} {format(dict['members'], ',d') if isinstance(dict['members'], int) else 'N/A'} members",
                                emoji = '🟩' if dict['media_type'].upper() == 'LIGHT_NOVEL' else '🟨' if dict['media_type'].upper() == 'MANGA' else '🟥' if dict['media_type'].upper() in ('MANHWA') else '1️⃣' if dict['media_type'].upper() == 'ONE_SHOT' else '⬛'))

                    select = discord.ui.Select(
                        placeholder = 'Select an manga',
                        options = select_options,
                        min_values = 1,
                        max_values = 1)

                    async def callback(interaction: discord.Interaction):
                        await interaction.response.defer()
                        self.choice = int(interaction.data['values'][0])
                        self.stop()

                    select.callback = callback
                    self.add_item(select)

            # Send the menu
            view = View()
            message = await context.send(embed = embed, view = view)
            # Wait for the user to select an entry
            await view.wait()

            # If the user didn't select an entry, then return
            if view.choice == None:
                await message.delete()
                return

            # If the user selected an entry, then update the response
            await message.delete()
            id = result[view.choice]['id']

        # If previously the response only has 1 result, then will skip the select menu, and directly go to the entry page
        elif len(result) == 1:
            id = result[0]['id']

        # Initialize Variables
        message = await context.send(
            embed = discord.Embed(
                title = 'Waiting for MyAnimeList response ...',
                color = discord.Color.dark_teal()))

        manga_details = self.MangaDetails(id = id)
        arranged_full = await manga_details.arrangeFull()
        built_overview = await manga_details.buildOverview()
        built_characters = None
        built_relations = None
        built_news = None
        built_topics = None

        # Making Buttons and Selections for the embed
        class View(discord.ui.View):
            def __init__(
                self,
                *,
                timeout: int = 300,
                include_button: bool = True,
                include_select: bool = True
                ) -> None:

                super().__init__(timeout = timeout)

                # Making URL buttons redirecting to trailer and streaming sites
                if include_button == True:

                    # External Links Button
                    for link in arranged_full['external']:
                        self.add_item(
                            Button(
                                label = link['name'] if link['name'] not in ('', None) else 'Site',
                                style = ButtonStyle.link,
                                url = link['url']))

                # Making Selection Menu for looking into different embeds
                if include_select == True:
                    select = Select(
                        placeholder = 'Categories',
                        min_values = 1,
                        max_values = 1,
                        options = [
                            discord.SelectOption(
                                label = 'Overview',
                                emoji = '📖',
                                description = 'Overview of Manga'),
                            discord.SelectOption(
                                label = 'Characters',
                                emoji = '👦🏽',
                                description = 'Characters in Manga'),
                            discord.SelectOption(
                                label = 'Relations',
                                emoji = '📺',
                                description = 'Relations of Manga'),
                            discord.SelectOption(
                                label = 'News',
                                emoji = '📰',
                                description = 'News of Manga'),
                            discord.SelectOption(
                                label = 'Topics',
                                emoji = '❓',
                                description = 'Topics of Manga')])

                    self.select = select
                    self.add_item(self.select)
                    return

        # A callback function to catch user interactions with the selection menu
        async def callback(interaction: discord.Interaction):
            if interaction.data['values'][0] == 'Overview':
                await interaction.response.defer()
                await interaction.followup.edit_message(message_id = message.id, embeds = built_overview)

            elif interaction.data['values'][0] == 'Characters':
                await interaction.response.defer()
                nonlocal built_characters
                if built_characters == None:
                    built_characters = await manga_details.buildCharacters()

                await interaction.followup.edit_message(message_id = message.id, embeds = built_characters)

            elif interaction.data['values'][0] == 'Relations':
                await interaction.response.defer()
                nonlocal built_relations
                if built_relations == None:
                    built_relations = await manga_details.buildRelations()

                await interaction.followup.edit_message(message_id = message.id, embeds = built_relations)

            elif interaction.data['values'][0] == 'News':
                await interaction.response.defer()
                nonlocal built_news
                if built_news == None:
                    built_news = await manga_details.buildNews()

                await interaction.followup.edit_message(message_id = message.id, embeds = built_news)

            elif interaction.data['values'][0] == 'Topics':
                await interaction.response.defer()
                nonlocal built_topics
                if built_topics == None:
                    built_topics = await manga_details.buildTopics()

                await interaction.followup.edit_message(message_id = message.id, embeds = built_topics)

            else:
                await interaction.response.defer()

        # Finalize the embeds and send them
        view = View()
        view.select.callback = callback
        await message.edit(embeds = built_overview, view = view)

        # Wait for user interactions for a timeout of 300 seconds
        await view.wait()
        # Delete the selection menu after the timeout, and keep the embed
        await message.edit(
            view = View(include_select = False))

        return



async def setup(bot):
    await bot.add_cog(
        Manga(bot))
