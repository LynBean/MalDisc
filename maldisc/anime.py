
import asyncio

from discord.enums import ButtonStyle
from discord.ext import commands
from discord.ext.commands import Context
from discord.ui import Button, Select, View
import discord

from datetime import datetime, timezone

from .constants import *
from .requests import *

class Anime(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.overview = None
        self.characters = None
        self.characters_id = None
        self.relations = None
        self.relations_id = None
        self.news = None
        self.news_id = None
        self.forum = None
        self.forum_id = None

    async def Search(self, query: str) -> list:
        Api = JikanAnime.Search if self.bot.config['mal_config']['enabled'] != True else MalAnime.Search

        response = await Api(
            query = query,
            limit = 25,
            fields = 'id,title,main_picture,mean,rank,media_type,num_episodes,num_list_users',
            nsfw = True)

        response = response['data']

        result = []

        if Api == JikanAnime.Search:
            for dict in response:
                id = dict['id']
                title = dict['title']
                try: picture = dict['images']['jpg']['image_url']
                except KeyError: picture = None
                try: score = dict['score']
                except KeyError: score = None
                try: rank = dict['rank']
                except KeyError: rank = None
                try: media_type = dict['type']
                except KeyError: media_type = None
                try: num_episodes = dict['episodes']
                except KeyError: num_episodes = None
                try: num_list_users = dict['members']
                except KeyError: num_list_users = None

                result.append(
                    {
                        'id': id,
                        'title': title,
                        'picture': picture,
                        'score': score,
                        'rank': rank,
                        'media_type': media_type,
                        'num_episodes': num_episodes,
                        'num_list_users': num_list_users})

        elif Api == MalAnime.Search:
            for dict in response:
                dict = dict['node']
                id = dict['id']
                title = dict['title']
                try: picture = dict['main_picture']['medium']
                except KeyError: picture = None
                try: score = dict['mean']
                except KeyError: score = None
                try: rank = dict['rank']
                except KeyError: rank = None
                try: media_type = dict['media_type']
                except KeyError: media_type = None
                try: num_episodes = dict['num_episodes']
                except KeyError: num_episodes = None
                try: num_list_users = dict['num_list_users']
                except KeyError: num_list_users = None

                result.append(
                    {
                        'id': id,
                        'title': title,
                        'picture': picture,
                        'score': score,
                        'rank': rank,
                        'media_type': media_type,
                        'num_episodes': num_episodes,
                        'num_list_users': num_list_users})

                continue

        return result


    @commands.hybrid_command(
        name = 'ima',
        description = 'Search your favorite anime on MyAnimeList')
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
                description = f"{context.author.mention}\n**🎉 Hooray, we received several entries that were similar to your request**\n**👉🏽` {query} `👈🏽**\n\n**Please choose one of the anime listed below 😚\nSurely, the anime you're looking for is on the list uwu~ 😶‍🌫️**",
                url = f'https://myanimelist.net/search/all?q={query.replace(" ", "%20")}&cat=all')

            embed.set_thumbnail(url = 'https://upload.wikimedia.org/wikipedia/commons/7/7a/MyAnimeList_Logo.png')

            for i in range(len(result)):
                if result[i]['picture'] == None: continue
                embed.set_image(url = result[i]['picture'])
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
                                description = f"{dict['media_type']} ({format(dict['num_episodes'], ',d') if isinstance(dict['num_episodes'], int) else 'N/A'} eps) Scored {dict['score'] if isinstance(dict['score'], float) else 'N/A'} {format(dict['num_list_users'], ',d') if isinstance(dict['num_list_users'], int) else 'N/A'} members",
                                emoji = '📺' if dict['media_type'].upper() == 'TV' else '🎞️' if dict['media_type'].upper() == 'MOVIE' else '📼' if dict['media_type'].upper() in ('OVA', 'ONA', 'SPECIAL') else '🎵' if dict['media_type'].upper() == 'Music' else '📺'))

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
            id = result[view.choice]['id']

        # If previously the response only has 1 result, then will skip the select menu, and directly go to the anime page
        elif len(result) == 1:
            id = result[0]['id']

        # Initialize Variables
        async def overview_embeds(response: dict) -> [discord.Embed]:
            embed = discord.Embed(
                title = response['title'],
                url = response['url'],
                description = response['synopsis'],
                color = 0xf37a12
            )

            embed.set_thumbnail(url = response['images']['jpg']['large_image_url'])
            embed.add_field(name = 'Score',
                            value = f"{response['score'] if isinstance(response['score'], float) else 'N/A'} ⭐",
                            inline = True)

            embed.add_field(name = 'Rank',
                            value = f"No. {format(response['rank'], ',d') if isinstance(response['rank'], int) else 'N/A'} ⬆️",
                            inline = True)

            embed.add_field(name = 'Popularity',
                            value = f"No. {format(response['popularity'], ',d') if isinstance(response['popularity'], int) else 'N/A'} ⬆️",
                            inline = True)

            embed.add_field(name = 'Members',
                            value = f"{format(response['members'], ',d') if isinstance(response['members'], int) else 'N/A'} 👦🏽",
                            inline = True)

            embed.add_field(name = 'Favorites',
                            value = f"{format(response['favorites'], ',d') if isinstance(response['favorites'], int) else 'N/A'} ❤️",
                            inline = True)

            embed.add_field(name = 'Type',
                            value = f"{response['type'] if response['type'] != None else 'N/A'} 📺",
                            inline = True)

            embed.add_field(name = 'Status',
                            value = f"{response['status'] if response['status'] != None else 'N/A'} 🟩",
                            inline = True)

            embed.add_field(name = 'Episodes',
                            value = f"{format(response['episodes'], ',d') if isinstance(response['episodes'], int) else 'N/A'} 🟦",
                            inline = True)

            embed.add_field(name = 'Source',
                            value = f"{response['source'] if response['source'] != None else 'N/A'} 🟨",
                            inline = True)

            embed.add_field(name = 'Aired',
                            value = f"{response['aired']['string'] if response['aired']['string'] != None else 'N/A'} 🟪",
                            inline = True)

            embed.add_field(name = 'Season',
                            value = f"{response['season'] if response['season'] != None else 'N/A'} 🍂",
                            inline = True)

            if response['airing'] == True:
                embed.add_field(name = 'Broadcast', value = f"{response['broadcast']['string']} 🆕",
                inline = True)

            return [embed]

        async def characters_embeds(response: dict) -> [discord.Embed]:
            if len(response) == 0:
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
            for dict in response:

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

        async def relations_embeds(response: dict) -> [discord.Embed]:
            if len(response) == 0:
                embed = discord.Embed(
                    title = 'No Relations found',
                    color = 0xf37a12)
                return [embed]

            embed = discord.Embed(
                title = 'Relations',
                color = 0xf37a12
            )

            for dict in response:

                for i in range(len(dict['entry'])):
                    embed.add_field(
                        name = f"**{dict['relation']} ({dict['entry'][i]['type']})**",
                        value = f"{dict['entry'][i]['name']}\n{dict['entry'][i]['url']}",
                        inline = True)

            return [embed]

        async def news_embeds(response: dict) -> [discord.Embed]:
            if len(response) == 0:
                embed = discord.Embed(
                    title = 'No News found',
                    color = 0xf37a12)
                return [embed]

            embeds = []
            # Maximum embeds in a message is 10, so only can show up to 10 news
            for i, dict in enumerate(response):
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

        async def forum_embeds(response: dict) -> [discord.Embed]:
            if len(response) == 0:
                embed = discord.Embed(
                    title = 'No Forum found',
                    color = 0xf37a12)
                return [embed]

            embeds = []
            # Maximum embeds in a message is 10, so only can show up to 10 news
            for i, dict in enumerate(response):
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

        message = await context.send(
            embed = discord.Embed(
                title = 'Waiting for MyAnimeList response ...',
                color = 0xf37a12))

        self.overview = (await JikanAnime.Full(id = id))['data']
        self.overview_embeds = await overview_embeds(self.overview)
        external_links = (await JikanAnime.External(id = id))['data']

        # Making Buttons and Selections for the embed
        class View(discord.ui.View):
            def __init__(
                self,
                *,
                overview: dict,
                timeout: int = 300,
                include_button: bool = True,
                include_select: bool = True
                ) -> None:

                super().__init__(timeout = timeout)

                # Making URL buttons redirecting to trailer and streaming sites
                if include_button == True:

                    # Trailer Button
                    if overview['trailer']['url'] != None:
                        self.add_item(
                            Button(
                                label = 'Watch Trailer',
                                style = ButtonStyle.link,
                                url = overview['trailer']['url']))

                    # Streaming Button
                    for index in range(len(overview['streaming'])):
                        self.add_item(
                            Button(
                                label = overview['streaming'][index]['name'],
                                style = ButtonStyle.link,
                                url = overview['streaming'][index]['url']))

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

                    self.select = select
                    self.add_item(self.select)
                    return

        # A callback function to catch user interactions with the selection menu
        async def callback(interaction: discord.Interaction):
            if interaction.data['values'][0] == 'Overview':
                await interaction.response.defer()
                await interaction.followup.edit_message(message_id = message.id, embeds = self.overview_embeds)

            elif interaction.data['values'][0] == 'Characters':
                if self.characters == None or self.characters_id != id:
                    self.characters_id = id
                    self.characters = (await JikanAnime.Characters(id = id))['data']
                    self.characters_embeds = await characters_embeds(self.characters)

                await interaction.response.defer()
                await interaction.followup.edit_message(message_id = message.id, embeds = self.characters_embeds)

            elif interaction.data['values'][0] == 'Relations':
                if self.relations == None or self.relations_id != id:
                    self.relations_id = id
                    self.relations = (await JikanAnime.Relations(id = id))['data']
                    self.relations_embeds = await relations_embeds(self.relations)

                await interaction.response.defer()
                await interaction.followup.edit_message(message_id = message.id, embeds = self.relations_embeds)

            elif interaction.data['values'][0] == 'News':
                if self.news == None or self.news_id != id:
                    self.news_id = id
                    self.news = (await JikanAnime.News(id = id))['data']
                    self.news_embeds = await news_embeds(self.news)

                await interaction.response.defer()
                await interaction.followup.edit_message(message_id = message.id, embeds = self.news_embeds)

            elif interaction.data['values'][0] == 'Forum':
                if self.forum == None or self.forum_id != id:
                    self.forum_id = id
                    self.forum = (await JikanAnime.Forum(id = id))['data']
                    self.forum_embeds = await forum_embeds(self.forum)

                await interaction.response.defer()
                await interaction.followup.edit_message(message_id = message.id, embeds = self.forum_embeds)

            else:
                await interaction.response.defer()

        # Finalize the embeds and send them
        view = View(overview = self.overview)
        view.select.callback = callback
        await message.edit(embeds = self.overview_embeds, view = view)

        # Wait for user interactions for a timeout of 300 seconds
        await view.wait()
        # Delete the selection menu after the timeout, and keep the embed
        await message.edit(
            view = View(
                overview = self.overview,
                include_select = False))

        return



async def setup(bot):
    await bot.add_cog(
        Anime(bot))
