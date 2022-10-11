
import asyncio

from discord.enums import ButtonStyle
from discord.ext import commands
from discord.ext.commands import Context
from discord.ui import Button, Select, View
import discord

from datetime import datetime, timezone

from .constants import *
from .requests_ import *

class Anime(commands.Cog, name = 'MyAnimeList in Discord Now!'):

    def __init__(self, bot):
        self.bot = bot

    class Overview:
        def __init__(self, mal_id):
            self.mal_id = mal_id
            self.response = None

        async def get(self):
            if self.response == None:
                self.response = (await JikanAnimeFull(mal_id = self.mal_id))['data']

        async def embeds(self) -> [discord.Embed]:
            await self.get()

            embed = discord.Embed(
                title = self.response['title'],
                url = self.response['url'],
                description = self.response['synopsis'],
                color = 0xf37a12
            )

            embed.set_thumbnail(url = self.response['images']['jpg']['large_image_url'])
            embed.add_field(name = 'Score',
                            value = f"{self.response['score'] if isinstance(self.response['score'], float) else 'N/A'} ⭐",
                            inline = True)

            embed.add_field(name = 'Rank',
                            value = f"No. {format(self.response['rank'], ',d') if isinstance(self.response['rank'], int) else 'N/A'} ⬆️",
                            inline = True)

            embed.add_field(name = 'Popularity',
                            value = f"No. {format(self.response['popularity'], ',d') if isinstance(self.response['popularity'], int) else 'N/A'} ⬆️",
                            inline = True)

            embed.add_field(name = 'Members',
                            value = f"{format(self.response['members'], ',d') if isinstance(self.response['members'], int) else 'N/A'} 👦🏽",
                            inline = True)

            embed.add_field(name = 'Favorites',
                            value = f"{format(self.response['favorites'], ',d') if isinstance(self.response['favorites'], int) else 'N/A'} ❤️",
                            inline = True)

            embed.add_field(name = 'Type',
                            value = f"{self.response['type'] if self.response['type'] != None else 'N/A'} 📺",
                            inline = True)

            embed.add_field(name = 'Status',
                            value = f"{self.response['status'] if self.response['status'] != None else 'N/A'} 🟩",
                            inline = True)

            embed.add_field(name = 'Episodes',
                            value = f"{format(self.response['episodes'], ',d') if isinstance(self.response['episodes'], int) else 'N/A'} 🟦",
                            inline = True)

            embed.add_field(name = 'Source',
                            value = f"{self.response['source'] if self.response['source'] != None else 'N/A'} 🟨",
                            inline = True)

            embed.add_field(name = 'Aired',
                            value = f"{self.response['aired']['string'] if self.response['aired']['string'] != None else 'N/A'} 🟪",
                            inline = True)

            embed.add_field(name = 'Season',
                            value = f"{self.response['season'] if self.response['season'] != None else 'N/A'} 🍂",
                            inline = True)

            if self.response['airing'] == True:
                embed.add_field(name = 'Broadcast', value = f"{self.response['broadcast']['string']} 🆕",
                inline = True)

            return [embed]

        async def json(self) -> dict:
            await self.get()
            return self.response


    class Characters:
        def __init__(self, mal_id):
            self.mal_id = mal_id
            self.response = None

        async def get(self):
            if self.response == None:
                self.response = (await JikanAnimeCharacters(mal_id = self.mal_id))['data']

        async def embeds(self) -> [discord.Embed]:
            await self.get()

            if len(self.response) == 0:
                embed = discord.Embed(
                    title = 'No characters found',
                    color = 0xf37a12)
                return [embed]

            embeds = []
            sc_embed = discord.Embed(
                title = f"**Supporting Characters**",
                color = 0xf37a12
            )

            # Splitting the main characters and the supporting characters into different embeds
            for dict in self.response:

                for voice_actor in dict['voice_actors']:
                    if voice_actor['language'] == 'Japanese':
                        voice_actor = voice_actor['person']['name']
                        break

                else: voice_actor = 'N/A'


                if dict['role'] == 'Main':
                    if len(embeds) < 9:
                        mc_embed = discord.Embed(
                            title = f"{dict['character']['name']}",
                            description = f"Liked: {format(dict['favorites'], ',d') if isinstance(dict['favorites'], int) else 'N/A'}\n{voice_actor}",
                            url = dict['character']['url'],
                            color = 0xf37a12
                        )

                        if dict['character']['images']['jpg']['image_url'] != None:
                            mc_embed.set_image(url = dict['character']['images']['jpg']['image_url'])

                        embeds.append(mc_embed)
                        continue

                    else:
                        sc_embed.add_field(
                        name = f"{dict['character']['name']} (Main)",
                        value = f"Liked: {format(dict['favorites'], ',d') if isinstance(dict['favorites'], int) else 'N/A'}\n{voice_actor}",
                        inline = True)

                        continue

                if dict['role'] == 'Supporting':
                    sc_embed.add_field(
                        name = f"{dict['character']['name']}",
                        value = f"Liked: {format(dict['favorites'], ',d') if isinstance(dict['favorites'], int) else 'N/A'}\n{voice_actor}",
                        inline = True)

                    continue

            if len(sc_embed.fields) != 0: embeds.append(sc_embed)
            return embeds

        async def json(self) -> dict:
            await self.get()
            return self.response


    class Relations:
        def __init__(self, mal_id):
            self.mal_id = mal_id
            self.response = None

        async def get(self):
            if self.response == None:
                self.response = (await JikanAnimeRelations(mal_id = self.mal_id))['data']

        async def embeds(self) -> [discord.Embed]:
            await self.get()

            if len(self.response) == 0:
                embed = discord.Embed(
                    title = 'No Relations found',
                    color = 0xf37a12)
                return [embed]

            embed = discord.Embed(
                title = 'Relations',
                color = 0xf37a12
            )

            for dict in self.response:

                for i in range(len(dict['entry'])):
                    embed.add_field(
                        name = f"**{dict['relation']} ({dict['entry'][i]['type']})**",
                        value = f"{dict['entry'][i]['name']}\n{dict['entry'][i]['url']}",
                        inline = True)

            return [embed]

        async def json(self) -> dict:
            await self.get()
            return self.response


    class Episodes:
        def __init__(self, mal_id):
            self.mal_id = mal_id
            self.response = None

        async def get(self):
            if self.response == None:
                self.response = (await JikanAnimeEpisodes(mal_id = self.mal_id))['data']

        async def embeds(self) -> [discord.Embed]:
            await self.get()

            if len(self.response) == 0:
                embed = discord.Embed(
                    title = 'No Episodes found',
                    color = 0xf37a12)
                return [embed]

            embed = discord.Embed(
                title = 'Episodes',
                color = 0xf37a12
            )

            for dict in self.response:
                embed.add_field(
                    name = f"**Episode {dict['mal_id']}: {dict['title']}**",
                    value = f"{dict['score']} ⭐\n{dict['forum_url']}",
                    inline = True)

            return [embed]

        async def json(self) -> dict:
            await self.get()
            return self.response


    class News:
        def __init__(self, mal_id):
            self.mal_id = mal_id
            self.response = None

        async def get(self):
            if self.response == None:
                self.response = (await JikanAnimeNews(mal_id = self.mal_id))['data']

        async def embeds(self) -> [discord.Embed]:
            await self.get()

            if len(self.response) == 0:
                embed = discord.Embed(
                    title = 'No News found',
                    color = 0xf37a12)
                return [embed]

            embeds = []
            # Maximum embeds in a message is 10, so only can show up to 10 news
            for i, dict in enumerate(self.response):
                if i == 10: break

                publish_date = datetime.fromisoformat(
                    dict['date']
                    ).astimezone(
                        timezone.utc
                        ).strftime(
                            '%Y-%m-%d %H:%M:%S')


                embed = discord.Embed(
                    title = f"**{dict['title']}**",
                    description = f"{dict['excerpt']}",
                    url = dict['url'],
                    color = 0xf37a12
                )
                embed.set_image(url = dict['images']['jpg']['image_url'])
                embed.set_footer(text = f"Published on {publish_date} (UTC)")
                embeds.append(embed)

            return embeds

        async def json(self) -> dict:
            await self.get()
            return self.response

    class Forum:
        def __init__(self, mal_id):
            self.mal_id = mal_id
            self.response = None

        async def get(self):
            if self.response == None:
                self.response = (await JikanAnimeForum(mal_id = self.mal_id))['data']

        async def embeds(self) -> [discord.Embed]:
            await self.get()

            if len(self.response) == 0:
                embed = discord.Embed(
                    title = 'No Forum found',
                    color = 0xf37a12)
                return [embed]

            embeds = []
            # Maximum embeds in a message is 10, so only can show up to 10 news
            for i, dict in enumerate(self.response):
                if i == 10: break

                publish_date = datetime.fromisoformat(
                    dict['date']
                    ).astimezone(
                        timezone.utc
                        ).strftime(
                            '%Y-%m-%d %H:%M:%S')

                embed = discord.Embed(
                    title = f"**{dict['title']}**",
                    description = f"Author: {dict['author_username']}\nComments: {format(dict['comments'], ',d') if isinstance(dict['comments'], int) else 'N/A'}",
                    url = dict['url'],
                    color = 0xf37a12
                )
                embed.set_footer(text = f"Published on {publish_date} (UTC)")
                embeds.append(embed)

            return embeds

        async def json(self) -> dict:
            await self.get()
            return self.response


    @commands.hybrid_command(
        name = 'ima',
        description = 'Search your favorite anime on MyAnimeList')
    async def ima(
        self,
        context: discord.ext.commands.context.Context,
        *,
        name: str
        ) -> None:
        """Search your favorite anime on MyAnimeList

        Args:
            context (discord.ext.commands.context.Context)
            name (str): Anime Title

        Returns:
            None: Send a discord embed into the channel
        """

        # Send a request to REST API to retrieve similar animes based on the anime name
        response = await AnimeSearch(query = name, limit = 25)

        # If the response is empty, then return
        if len(response['data']) == 0:
            await context.send(
                embed = discord.Embed(
                    title = 'No results found',
                    color = 0xf37a12))
            return

        # If the there are more than 1 results, then send a select menu
        elif len(response['data']) > 1:

            embed = discord.Embed(
                title = '**MyAnimeList**',
                description = f"{context.author.mention}\n**🎉 Hooray, we received several entries that were similar to your request**\n**👉🏽` {name} `👈🏽**\n\n**Please choose one of the anime listed below 😚\nSurely, the anime you're looking for is on the list uwu~ 😶‍🌫️**",
                url = f'https://myanimelist.net/search/all?q={name.replace(" ", "%20")}&cat=all')

            embed.set_thumbnail(url = 'https://upload.wikimedia.org/wikipedia/commons/7/7a/MyAnimeList_Logo.png')
            if response['data'][0]['images']['jpg']['small_image_url'] != None:
                embed.set_image(url = response['data'][0]['images']['jpg']['small_image_url'])

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
                    for index, dict in enumerate(response['data']):
                        select_options.append(
                            discord.SelectOption(
                                label = dict['title'],
                                value = str(index),
                                description = f"<{dict['type']} ({format(dict['episodes'], ',d') if isinstance(dict['episodes'], int) else 'N/A'} eps)> <Scored {dict['score'] if isinstance(dict['score'], float) else 'N/A'}> <{format(dict['members'], ',d') if isinstance(dict['members'], int) else 'N/A'} members>",
                                emoji = '📺' if dict['type'] == 'TV' else '🎞️' if dict['type'] == 'Movie' else '📼' if dict['type'] in ('OVA', 'ONA') else '🎵' if dict['type'] == 'Music' else '📺'))

                    select = discord.ui.Select(
                        placeholder = 'Select an anime',
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
            # Wait for the user to select an anime
            await view.wait()

            # If the user didn't select an anime, then return
            if view.choice == None:
                await message.delete()
                return

            # If the user selected an anime, then update the response
            await message.delete()
            mal_id = response['data'][view.choice]['mal_id']


        # If previously the response only has 1 result, then will skip the select menu, and directly go to the anime page
        elif len(response['data']) == 1:
            mal_id = response['data'][0]['mal_id']

        # Initialize Variables
        message = await context.send(
            embed = discord.Embed(
                title = 'Waiting for MyAnimeList response ...',
                color = 0xf37a12))

        overview = self.Overview(mal_id)
        overview.embeds = await overview.embeds()
        overview.json = await overview.json()
        external_links = (await JikanAnimeExternal(mal_id))['data']

        # Making Buttons and Selections for the embed
        class View(discord.ui.View):
            def __init__(
                self,
                *,
                timeout = 300,
                include_button: bool = True,
                include_select: bool = True):

                super().__init__(timeout = timeout)
                self.characters = None
                self.relations = None
                self.news = None
                self.forum = None

                # Making URL buttons redirecting to trailer and streaming sites
                if include_button == True:
                    anime = overview.json

                    # Trailer Button
                    if anime['trailer']['url'] != None:
                        self.add_item(
                            Button(
                                label = 'Watch Trailer',
                                style = ButtonStyle.link,
                                url = anime['trailer']['url']))

                    # Streaming Button
                    for index in range(len(anime['streaming'])):
                        self.add_item(
                            Button(
                                label = anime['streaming'][index]['name'],
                                style = ButtonStyle.link,
                                url = anime['streaming'][index]['url']))

                    # External Links Button
                    for dict in external_links:
                        self.add_item(
                            Button(
                                label = dict['name'] if dict['name'] not in ('', None) else 'Site',
                                style = ButtonStyle.link,
                                url = dict['url']))

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
                                description = 'Overview of Anime'
                                ),
                            discord.SelectOption(
                                label = 'Characters',
                                emoji = '👦🏽',
                                description = 'Characters in Anime'
                                ),
                            discord.SelectOption(
                                label = 'Relations',
                                emoji = '📺',
                                description = 'Relations of Anime'
                                ),
                            discord.SelectOption(
                                label = 'News',
                                emoji = '📰',
                                description = 'News of Anime'
                                ),
                            discord.SelectOption(
                                label = 'Forum',
                                emoji = '❓',
                                description = 'Forum of Anime'
                                ),
                            ]
                        )

                    # A callback function to catch user interactions with the selection menu
                    async def callback(interaction: discord.Interaction):
                        if interaction.data['values'][0] == 'Overview':
                            await interaction.response.defer()
                            await interaction.followup.edit_message(message_id = message.id, embeds = overview.embeds)

                        elif interaction.data['values'][0] == 'Characters':
                            if self.characters == None:
                                self.characters = Anime.Characters(mal_id)
                                self.characters.embeds = await self.characters.embeds()

                            await interaction.response.defer()
                            await interaction.followup.edit_message(message_id = message.id, embeds = self.characters.embeds)

                        elif interaction.data['values'][0] == 'Relations':
                            if self.relations == None:
                                self.relations = Anime.Relations(mal_id)
                                self.relations.embeds = await self.relations.embeds()

                            await interaction.response.defer()
                            await interaction.followup.edit_message(message_id = message.id, embeds = self.relations.embeds)

                        elif interaction.data['values'][0] == 'News':
                            if self.news == None:
                                self.news = Anime.News(mal_id)
                                self.news.embeds = await self.news.embeds()

                            await interaction.response.defer()
                            await interaction.followup.edit_message(message_id = message.id, embeds = self.news.embeds)

                        elif interaction.data['values'][0] == 'Forum':
                            if self.forum == None:
                                self.forum = Anime.Forum(mal_id)
                                self.forum.embeds = await self.forum.embeds()

                            await interaction.response.defer()
                            await interaction.followup.edit_message(message_id = message.id, embeds = self.forum.embeds)

                        else:
                            await interaction.response.defer()

                    select.callback = callback
                    self.add_item(select)


        # Finalize the embeds and send them
        view = View()
        await message.edit(embeds = overview.embeds, view = view)

        # Wait for user interactions for a timeout of 300 seconds
        await view.wait()
        # Delete the selection menu after the timeout, and keep the embed
        await message.edit(
            view = View(
                include_select = False))

        return



async def setup(bot):
    await bot.add_cog(
        Anime(bot))
