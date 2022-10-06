
import asyncio

import discord
from discord.enums import ButtonStyle
from discord.ext import commands
from discord.ext.commands import Context
from discord.ui import Button, Select, View

from .constants import *
from .requests_ import *

class Anime(commands.Cog, name = 'MyAnimeList in Discord Now!'):

    def __init__(self, bot):
        self.bot = bot

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
        response = await JikanAnimeSearch(query = name)

        # If the response is empty, then return
        if len(response['data']) == 0:
            await context.send('No results found')
            return

        # If the there are more than 1 results, then send a select menu
        page = 0
        
        while len(response['data']) > 1:
            
            # Create pages
            embed = discord.Embed(
                title = '**MyAnimeList**',
                description = f'{context.author.mention} Here are all similar animes based on your request:\n> **` {name} `**',
                url = f'https://myanimelist.net/search/all?q={name.replace(" ", "%20")}&cat=all')
            
            embed.set_thumbnail(url = 'https://upload.wikimedia.org/wikipedia/commons/7/7a/MyAnimeList_Logo.png')
            embed.set_footer(text = f'Page {page + 1} of {len(response["data"]) // 4 + 1}')

            # 4 animes per page
            try:
                for index, emoji in enumerate(['1️⃣', '2️⃣', '3️⃣', '4️⃣']):
                    j = response['data'][index + page * 4]

                    embed.add_field(
                        name = f'{emoji} {j["title"]}',
                        value = f"*{j['type']} ({str(j['episodes'])} eps)*\n*Scored {str(j['score'])}*\n*{str(j['members'])} members*",
                        inline = False)

            except IndexError:
                pass
            
            # If the message is already sent, then edit it 
            try:
                message = await message.edit(embed = embed)
                
            # First time sending the message, with adding the reactions
            except UnboundLocalError:
                message = await context.send(embed = embed)
                
                for i in range(4 if len(response['data']) > 4 else len(response['data'])):
                    emoji = ['1️⃣', '2️⃣', '3️⃣', '4️⃣']
                    await message.add_reaction(emoji[i])
                    
                if len(response['data']) > 4:
                    for emoji in ['◀️', '▶️']:
                        await message.add_reaction(emoji)

                await message.add_reaction('❌')

            # Wait for a reaction
            try:
                reaction, user = await self.bot.wait_for(
                    'reaction_add',
                    check = lambda reaction, user: reaction.message == message and str(reaction.emoji) in ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '◀️', '▶️', '❌'],
                    timeout = 60)

            except asyncio.TimeoutError:
                await message.delete()
                return

            # Go to previous page, if first page, then go to last page
            if str(reaction.emoji) == '◀️':
                if page == 0:
                    page = len(response['data']) // 4
                else:
                    page -= 1

            # Go forward a page, if last page, then go to first page
            elif str(reaction.emoji) == '▶️':
                if page == len(response['data']) // 4:
                    page = 0
                else:
                    page += 1

            # Cancel the operation
            elif str(reaction.emoji) == '❌':
                await message.delete()
                return

            # Retrieve the anime id based on selected number
            else:
                for index, emoji in enumerate(['1️⃣', '2️⃣', '3️⃣', '4️⃣']):
                    if str(reaction.emoji) != emoji:
                        continue

                    mal_id = response['data'][index + page * 4]['mal_id']
                    await message.delete()
                    break
                
                break
        
        # If previously the response only has 1 result, then will skip the select menu, and directly go to the anime page
        if len(response['data']) == 1:
            mal_id = response['data'][0]['mal_id']
        
        
        # Making Overview Embed
        class Overview(object):
            def __init__(self, mal_id):
                self.mal_id = mal_id
                self.response = None
                
            async def get(self):
                if self.response == None:
                    self.response = (await JikanAnimeFull(mal_id = self.mal_id))['data']
                    
            async def embed(self) -> discord.Embed:
                await self.get()
                embed = discord.Embed(
                    title = self.response['title'],
                    url = self.response['url'],
                    description = self.response['synopsis'],
                    color = 0xf37a12
                )
                
                embed.set_thumbnail(url = self.response['images']['jpg']['large_image_url'])
                embed.add_field(name = 'Score',      value = f"{self.response['score']} ⭐", inline = True)
                embed.add_field(name = 'Rank',       value = f"No. {self.response['rank']} ⬆️", inline = True)
                embed.add_field(name = 'Popularity', value = f"No. {self.response['popularity']} ⬆️", inline = True)
                embed.add_field(name = 'Members',    value = f"{self.response['members']} 👦🏽", inline = True)
                embed.add_field(name = 'Favorites',  value = f"{self.response['favorites']} ❤️", inline = True)
                embed.add_field(name = 'Type',       value = f"{self.response['type']} 📺", inline = True)
                embed.add_field(name = 'Status',     value = f"{self.response['status']} 🟩", inline = True)
                embed.add_field(name = 'Episodes',   value = f"{self.response['episodes']} 🟦", inline = True)
                embed.add_field(name = 'Source',     value = f"{self.response['source']} 🟨", inline = True)
                embed.add_field(name = 'Aired',      value = f"{self.response['aired']['string']} 🟪", inline = True)
                embed.add_field(name = 'Season',     value = f"{self.response['season']} 🍂", inline = True)

                if self.response['airing'] == True:
                    embed.add_field(name = 'Broadcast', value = f"{self.response['broadcast']['string']} 🆕", inline = True)

                return embed
            
            async def json(self) -> dict:
                await self.get()
                return self.response
                
                
        # Making Characters Embed
        class Characters(object):
            def __init__(self, mal_id):
                self.mal_id = mal_id
                self.response = None
                
            async def get(self):
                if self.response == None:
                    self.response = (await JikanAnimeCharacters(mal_id = self.mal_id))['data']
                
            async def embed(self) -> discord.Embed:
                await self.get()
                embed = discord.Embed(
                    title = 'Characters',
                    color = 0xf37a12
                )
                
                for dict in self.response:
                    
                    for i in range(len(dict['voice_actors'])):
                        if dict['voice_actors'][i]['language'] != 'Japanese':
                            continue
                        
                        voice_actor = dict['voice_actors'][i]['person']['name']
                        break
                            
                    embed.add_field(
                        name = f"**{dict['character']['name']} ({dict['favorites']}❤️) ({dict['role']})**",
                        value = f"Voice Actor: {voice_actor}",
                        inline = False)
                    
                return embed
            
            async def json(self) -> dict:
                await self.get()
                return self.response
            
        # Initialize Embed Variables
        overview = Overview(mal_id)
        overview.embed = await overview.embed()
        overview.json = await overview.json()
        characters = Characters(mal_id)
        characters.embed = await characters.embed()
        characters.json = await characters.json()
        
        # Making Buttons and Selections for the embed
        class View(discord.ui.View):
            def __init__(
                self,
                *,
                timeout = 180,
                include_button: bool = True,
                include_select: bool = True):

                super().__init__(timeout = timeout)

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
                            ]
                        )

                    # A callback function to catch user interactions with the selection menu
                    async def callback(interaction: discord.Interaction):
                        if interaction.data['values'][0] == 'Overview':
                            await interaction.response.edit_message(embed = overview.embed)
                            
                        elif interaction.data['values'][0] == 'Characters':
                            await interaction.response.edit_message(embed = characters.embed)

                    select.callback = callback
                    self.add_item(select)


        # Finalize the embeds and send them
        view = View()
        message = await context.send(embed = overview.embed, view = view)
        
        # Wait for user interactions for a timeout of 60 seconds
        await view.wait()
        # Delete the selection menu after the timeout, and keep the embed
        await message.edit(
            view = View(include_select = False))
        
        return


async def setup(bot):
    await bot.add_cog(Anime(bot))
