
import asyncio
import aiohttp
import base64
import hashlib
import secrets
import json
import os

from uuid import uuid4

from .constants import *
from .exceptions import *

with open(DIR_PATH + '/config.json') as file:
    config = json.load(file)

async def to_json(response):
    if response.status in (200, 304):
        return await response.json()

    elif response.status == 429:
        raise TooManyRequests()

    else:
        raise Exception(f'**Status Code {response.status}**: {response.reason}')

async def JikanRequests(url: str, max_retry: int = 5) -> dict:

    for _ in range(max_retry):
        async with aiohttp.ClientSession() as session:

            try:
                async with session.get(

                    f'https://api.jikan.moe/v4/{url.replace(" ", "%20")}',

                    headers = {
                        'Content-Type': 'application/json',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'
                        },

                    timeout = 2

                    ) as response:

                    return await to_json(response)

            except (TooManyRequests, asyncio.TimeoutError):
                await asyncio.sleep(1)
                continue

    raise Exception('Max retry exceeded')

async def MalRequests(url: str, max_retry: int = 5) -> dict:

    for _ in range(max_retry):
        async with aiohttp.ClientSession() as session:

            try:
                async with session.get(

                    f'https://api.myanimelist.net/v2/{url.replace(" ", "+")}',

                    headers = {
                        'X-MAL-CLIENT-ID': config['mal_config']['client_id'],
                        'Content-Type': 'application/json',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'
                        },

                    timeout = 2

                    ) as response:

                    return await to_json(response)

            except (TooManyRequests, asyncio.TimeoutError):
                await asyncio.sleep(1)
                continue


class JikanAnime:

    async def Full(id) -> dict:
        return await JikanRequests(f'anime/{id}/full')

    async def Anime(id) -> dict:
        return await JikanRequests(f'anime/{id}')

    async def Characters(id) -> dict:
        return await JikanRequests(f'anime/{id}/characters')

    async def Staff(id) -> dict:
        return await JikanRequests(f'anime/{id}/staff')

    async def Episodes(id, page: int = None) -> dict:
        return await JikanRequests(f'anime/{id}/episodes{f"?page={page}" if page != None else ""}')

    async def EpisodesByID(id, episode_id) -> dict:
        return await JikanRequests(f'anime/{id}/episodes/{episode_id}')

    async def News(id, page: int = None) -> dict:
        return await JikanRequests(f'anime/{id}/news{f"?page={page}" if page != None else ""}')

    async def Forum(id, filter: str = None) -> dict:
        return await JikanRequests(f'anime/{id}/forum{f"?filter={filter}" if filter != None else ""}')

    async def Videos(id) -> dict:
        return await JikanRequests(f'anime/{id}/videos')

    async def VideosEpisodes(id, page: int = None) -> dict:
        return await JikanRequests(f'anime/{id}/videos/episodes{f"?page={page}" if page != None else ""}')

    async def Pictures(id) -> dict:
        return await JikanRequests(f'anime/{id}/pictures')

    async def Statistics(id) -> dict:
        return await JikanRequests(f'anime/{id}/statistics')

    async def MoreInfo(id) -> dict:
        return await JikanRequests(f'anime/{id}/moreinfo')

    async def Recommendations(id) -> dict:
        return await JikanRequests(f'anime/{id}/recommendations')

    async def UserUpdates(id, page: int = None) -> dict:
        return await JikanRequests(f'anime/{id}/userupdates{f"?page={page}" if page != None else ""}')

    async def Reviews(id, page: int = None) -> dict:
        return await JikanRequests(f'anime/{id}/reviews{f"?page={page}" if page != None else ""}')

    async def Relations(id) -> dict:
        return await JikanRequests(f'anime/{id}/relations')

    async def Themes(id) -> dict:
        return await JikanRequests(f'anime/{id}/themes')

    async def External(id) -> dict:
        return await JikanRequests(f'anime/{id}/external')

    async def Streaming(id) -> dict:
        return await JikanRequests(f'anime/{id}/streaming')

    async def Search(
        page: int = None, limit: int = None, query: str = None,
        type: str = None, score: float = None, min_score: float = None,
        max_score: float = None, status: str = None, rating: str = None,
        sfw: bool = None, genres: str = None, genres_exclude: str = None,
        order_by: str = None, sort: str = None, letter: str = None,
        producers:str = None, start_date: str = None, end_date: str = None,
        **kwargs
        ) -> dict:

        return await JikanRequests(f'anime?{f"&page={page}" if page != None else ""}{f"&limit={limit}" if limit != None else ""}{f"&q={query}" if query != None else ""}{f"&type={type}" if type != None else ""}{f"&score={score}" if score != None else ""}{f"&min_score={min_score}" if min_score != None else ""}{f"&max_score={max_score}" if max_score != None else ""}{f"&status={status}" if status != None else ""}{f"&rating={rating}" if rating != None else ""}{f"&sfw={sfw}" if sfw != None else ""}{f"&genres={genres}" if genres != None else ""}{f"&genres_exclude={genres_exclude}" if genres_exclude != None else ""}{f"&order_by={order_by}" if order_by != None else ""}{f"&sort={sort}" if sort != None else ""}{f"&letter={letter}" if letter != None else ""}{f"&producers={producers}" if producers != None else ""}{f"&start_date={start_date}" if start_date != None else ""}{f"&end_date={end_date}" if end_date != None else ""}')

class MalAnime:

    async def Search(
        query: str = None, limit: int = None, offset: int = None,
        fields: str = None, nsfw: bool = None,
        **kwargs
    ) -> dict:

        return await MalRequests(f'anime?{f"&q={query}" if query != None else ""}{f"&limit={limit}" if limit != None else ""}{f"&offset={offset}" if offset != None else ""}{f"&fields={fields}" if fields != None else ""}{f"&nsfw={nsfw}" if nsfw != None else ""}')

    async def Anime(id, fields: str = None) -> dict:
        return await MalRequests(f'anime/{id}{f"?fields={fields}" if fields != None else ""}')

    async def Ranking(
        ranking_type: str, limit = None, offset = None,
        fields: str = None
        ) -> dict:

        return await MalRequests(f'anime/ranking/?ranking_type={ranking_type}{f"&limit={limit}" if limit != None else ""}{"&offset={offset}" if offset != None else ""}{"&fields={fields}" if fields != None else ""}')

    async def Seasonal(
        year: int, season: str, sort:str = None,
        limit: int = None, offset: int = None, fields: str = None
        ) -> dict:

        return await MalRequests(f'anime/season/{year}/{season}?{f"&sort={sort}" if sort != None else ""}{f"&limit={limit}" if limit != None else ""}{"&offset={offset}" if offset != None else ""}{"&fields={fields}" if fields != None else ""}')


class JikanManga:

    async def Full(id) -> dict:
        return await JikanRequests(f'manga/{id}/full')

    async def Manga(id) -> dict:
        return await JikanRequests(f'manga/{id}')

    async def Characters(id) -> dict:
        return await JikanRequests(f'manga/{id}/characters')

    async def News(id, page: int = None) -> dict:
        return await JikanRequests(f'manga/{id}/news{f"?page={page}" if page != None else ""}')

    async def Topics(id, filter: str = None) -> dict:
        return await JikanRequests(f'manga/{id}/forum{f"?filter={filter}" if filter != None else ""}')

    async def Pictures(id) -> dict:
        return await JikanRequests(f'manga/{id}/pictures')

    async def Statistics(id) -> dict:
        return await JikanRequests(f'manga/{id}/statistics')

    async def MoreInfo(id) -> dict:
        return await JikanRequests(f'manga/{id}/moreinfo')

    async def Recommendations(id) -> dict:
        return await JikanRequests(f'manga/{id}/recommendations')

    async def UserUpdates(id, page: int = None) -> dict:
        return await JikanRequests(f'manga/{id}/userupdates{f"?page={page}" if page != None else ""}')

    async def Reviews(id, page: int = None) -> dict:
        return await JikanRequests(f'manga/{id}/reviews{f"?page={page}" if page != None else ""}')

    async def Relations(id) -> dict:
        return await JikanRequests(f'manga/{id}/relations')

    async def External(id) -> dict:
        return await JikanRequests(f'manga/{id}/external')

    async def Search(
        page: int = None, limit: int = None, query: str = None,
        type: str = None, score: float = None, min_score: float = None,
        max_score: float = None, status: str = None, sfw: bool = None,
        genres: str = None, genres_exclude: str = None, order_by: str = None,
        sort: str = None, letter: str = None, magazines: str = None,
        start_date: str = None, end_date: str = None,
        **kwargs
    ) -> dict:

        return await JikanRequests(f'manga?{f"&page={page}&" if page is not None else ""}{f"&limit={limit}&" if limit is not None else ""}{f"&q={query}&" if query is not None else ""}{f"&type={type}&" if type is not None else ""}{f"&score={score}&" if score is not None else ""}{f"&min_score={min_score}&" if min_score is not None else ""}{f"&max_score={max_score}&" if max_score is not None else ""}{f"&status={status}&" if status is not None else ""}{f"&sfw={sfw}&" if sfw is not None else ""}{f"&genres={genres}&" if genres is not None else ""}{f"&genres_exclude={genres_exclude}&" if genres_exclude is not None else ""}{f"&order_by={order_by}&" if order_by is not None else ""}{f"&sort={sort}&" if sort is not None else ""}{f"&letter={letter}&" if letter is not None else ""}{f"&magazines={magazines}&" if magazines is not None else ""}{f"&start_date={start_date}&" if start_date is not None else ""}{f"&end_date={end_date}&" if end_date is not None else ""}')

class JikanCharacters:

    async def Full(id) -> dict:
        return await JikanRequests(f'character/{id}/full')

    async def Character(id) -> dict:
        return await JikanRequests(f'character/{id}')

    async def Anime(id) -> dict:
        return await JikanRequests(f'character/{id}/anime')

    async def Manga(id) -> dict:
        return await JikanRequests(f'character/{id}/manga')

    async def VoiceActors(id) -> dict:
        return await JikanRequests(f'character/{id}/voices')

    async def Pictures(id) -> dict:
        return await JikanRequests(f'character/{id}/pictures')

    async def Search(
        page: int = None, limit: int = None, query: str = None,
        order_by: str = None, sort: str = None, letter: str = None,
        **kwargs
    ) -> dict:

        return await JikanRequests(f'characters?{f"&page={page}" if page is not None else ""}{f"&limit={limit}" if limit is not None else ""}{f"&q={query}" if query is not None else ""}{f"&order_by={order_by}" if order_by is not None else ""}{f"&sort={sort}" if sort is not None else ""}{f"&letter={letter}" if letter is not None else ""}')

