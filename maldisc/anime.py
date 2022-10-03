
import asyncio

import discord
from discord import app_commands
from discord.enums import ButtonStyle
from discord.ext import commands
from discord.ext.commands import Context
from discord.ui import Button, View

from .constants import *
from .jikanrequests import JikanRequests


class Anime(commands.Cog, name = 'MyAnimeList in Discord Now!'):
    
    def __init__(self, bot):
        self.bot = bot
        
    @commands.hybrid_command(
        name = 'ima',
        description = 'Search your favorite anime on MyAnimeList')
    async def ima(self, context: Context, *, name):
        
        result = await JikanRequests(f'anime?q={name}&order_by=score&sort=desc')
        
        if len(result['data']) == 0:
            await context.send('No results found')
            return
        
        page = 0
        while len(result['data']) > 1:
            embed = discord.Embed(
                title = '**MyAnimeList**',
                description = f'{context.author.mention} Here are all similar animes based on your request:\n> **` {name} `**',
                url = f'https://myanimelist.net/search/all?q={name.replace(" ", "%20")}&cat=all')
            embed.set_thumbnail(url = 'https://upload.wikimedia.org/wikipedia/commons/7/7a/MyAnimeList_Logo.png')
            embed.set_footer(text = f'Page {page + 1} of {len(result["data"]) // 4 + 1}')
            
            try:
                for index, emoji in enumerate(['1️⃣', '2️⃣', '3️⃣', '4️⃣']):
                    j = result['data'][index + page * 4]
                    
                    embed.add_field(
                        name = f'{emoji} {j["title"]}',
                        value = f"*{j['type']} ({str(j['episodes'])} eps)*\n*Scored {str(j['score'])}*\n*{str(j['members'])} members*",
                        inline = False)
                    
            except IndexError:
                pass
                
            try:
                message = await message.edit(embed = embed)
            except UnboundLocalError:
                message = await context.send(embed = embed)
                for i in range(4 if len(result['data']) > 4 else len(result['data'])):
                    emoji = ['1️⃣', '2️⃣', '3️⃣', '4️⃣']
                    await message.add_reaction(emoji[i])
                if len(result['data']) > 4:
                    for emoji in ['◀️', '▶️']:
                        await message.add_reaction(emoji)
                        
                await message.add_reaction('❌')
            
            try:
                reaction, user = await self.bot.wait_for(
                    'reaction_add',
                    check = lambda reaction, user: reaction.message == message and str(reaction.emoji) in ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '◀️', '▶️', '❌'],
                    timeout = 60)
                
            except asyncio.TimeoutError:
                await message.delete()
                return
            
            if str(reaction.emoji) == '◀️':
                if page == 0:
                    page = len(result['data']) // 4
                else:
                    page -= 1
                    
            elif str(reaction.emoji) == '▶️':
                if page == len(result['data']) // 4:
                    page = 0
                else:
                    page += 1
                    
            elif str(reaction.emoji) == '❌':
                await message.delete()
                return
                    
            else:
                for index, emoji in enumerate(['1️⃣', '2️⃣', '3️⃣', '4️⃣']):
                    if str(reaction.emoji) != emoji:
                        continue
                    
                    mal_id = result['data'][index + page * 4]['mal_id']
                    await message.delete()
                    break
                break
            
        if len(result['data']) == 1:
            mal_id = result['data'][0]['mal_id']
            
        anime = await JikanRequests(f'anime/{mal_id}/full')
        anime = anime['data']
        
        embed = discord.Embed(
            title = anime['title'],
            url = anime['url'],
            description = anime['synopsis'],
            color = 0xf37a12
        )
        embed.set_thumbnail(url = anime['images']['jpg']['large_image_url'])
        embed.add_field(name = 'Score', value = f"{anime['score']} ⭐", inline = True)
        embed.add_field(name = 'Rank', value = f"No. {anime['rank']} 🔝", inline = True)
        embed.add_field(name = 'Popularity', value = f"No. {anime['popularity']} 🔝", inline = True)
        embed.add_field(name = 'Members', value = f"{anime['members']} 👦🏽", inline = True)
        embed.add_field(name = 'Favorites', value = f"{anime['favorites']} ❤️", inline = True)
        embed.add_field(name = 'Type', value = f"{anime['type']} 📺", inline = True)
        embed.add_field(name = 'Status', value = f"{anime['status']} 🟩", inline = True)
        embed.add_field(name = 'Episodes', value = f"{anime['episodes']} 🟦", inline = True)
        embed.add_field(name = 'Source', value = f"{anime['source']} 🟨", inline = True)
        embed.add_field(name = 'Aired', value = f"{anime['aired']['string']} 🟪", inline = True)
        embed.add_field(name = 'Season', value = f"{anime['season']} 🍂", inline = True)
        
        if anime['airing'] == True:
            embed.add_field(name = 'Broadcast', value = f"{anime['broadcast']['string']} 🆕", inline = True)
            
        view = View()
        if anime['trailer']['url'] != None:
            view.add_item(Button(
                style = ButtonStyle.link,
                label = 'Watch Trailer',
                url = anime['trailer']['url']))
            
        for index in range(len(anime['streaming'])):
            view.add_item(Button(
                style = ButtonStyle.link,
                label = anime['streaming'][index]['name'],
                url = anime['streaming'][index]['url']))
            
        message = await context.send(embed = embed, view = view)
        return
        
async def setup(bot):
    await bot.add_cog(Anime(bot))
