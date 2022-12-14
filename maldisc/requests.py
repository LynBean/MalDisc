
import asyncio
import aiohttp

from .constants import *
from .exceptions import *
from .utils import *

config = MalDiscConfigParser()

async def validJson(response):
    if response.status in (200, 304):
        return await response.json()

    elif response.status == 429:
        raise TooManyRequests()

    else:
        raise RequestsError(f'**Status Code {response.status}**: {response.reason}')

class Jikan:

    async def Requests(url: str, max_retry: int = 5, timeout: float = 5.0) -> dict:

        for _ in range(max_retry):
            async with aiohttp.ClientSession() as session:

                try:
                    async with session.get(

                        f'https://api.jikan.moe/v4/{url.replace(" ", "%20")}',

                        headers = {
                            'Accept-Encoding': 'gzip',
                            'Cache-Control': 'no-store',
                            'Content-Type': 'application/json',
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'
                            },

                        timeout = timeout

                        ) as response:

                        result = await validJson(response)

                        return result

                except (TooManyRequests, asyncio.TimeoutError):
                    await asyncio.sleep(1)
                    continue

        raise RequestsError('Max retry exceeded')

    class Anime:
        async def Full(id) -> dict:
            return await Jikan.Requests(f'anime/{id}/full')
        async def Anime(id) -> dict:
            return await Jikan.Requests(f'anime/{id}')
        async def Characters(id) -> dict:
            return await Jikan.Requests(f'anime/{id}/characters')
        async def Staff(id) -> dict:
            return await Jikan.Requests(f'anime/{id}/staff')
        async def Episodes(id, page: int = None) -> dict:
            return await Jikan.Requests(f'anime/{id}/episodes{f"?page={page}" if page != None else ""}')
        async def EpisodesByID(id, episode_id) -> dict:
            return await Jikan.Requests(f'anime/{id}/episodes/{episode_id}')
        async def News(id, page: int = None) -> dict:
            return await Jikan.Requests(f'anime/{id}/news{f"?page={page}" if page != None else ""}')
        async def Forum(id, filter: str = None) -> dict:
            return await Jikan.Requests(f'anime/{id}/forum{f"?filter={filter}" if filter != None else ""}')
        async def Videos(id) -> dict:
            return await Jikan.Requests(f'anime/{id}/videos')
        async def VideosEpisodes(id, page: int = None) -> dict:
            return await Jikan.Requests(f'anime/{id}/videos/episodes{f"?page={page}" if page != None else ""}')
        async def Pictures(id) -> dict:
            return await Jikan.Requests(f'anime/{id}/pictures')
        async def Statistics(id) -> dict:
            return await Jikan.Requests(f'anime/{id}/statistics')
        async def MoreInfo(id) -> dict:
            return await Jikan.Requests(f'anime/{id}/moreinfo')
        async def Recommendations(id) -> dict:
            return await Jikan.Requests(f'anime/{id}/recommendations')
        async def UserUpdates(id, page: int = None) -> dict:
            return await Jikan.Requests(f'anime/{id}/userupdates{f"?page={page}" if page != None else ""}')
        async def Reviews(id, page: int = None) -> dict:
            return await Jikan.Requests(f'anime/{id}/reviews{f"?page={page}" if page != None else ""}')
        async def Relations(id) -> dict:
            return await Jikan.Requests(f'anime/{id}/relations')
        async def Themes(id) -> dict:
            return await Jikan.Requests(f'anime/{id}/themes')
        async def External(id) -> dict:
            return await Jikan.Requests(f'anime/{id}/external')
        async def Streaming(id) -> dict:
            return await Jikan.Requests(f'anime/{id}/streaming')
        async def Search(
            page: int = None, limit: int = None, query: str = None,
            type: str = None, score: float = None, min_score: float = None,
            max_score: float = None, status: str = None, rating: str = None,
            sfw: bool = None, genres: str = None, genres_exclude: str = None,
            order_by: str = None, sort: str = None, letter: str = None,
            producers:str = None, start_date: str = None, end_date: str = None,
            **kwargs) -> dict:
            return await Jikan.Requests(f'anime?{f"&page={page}" if page != None else ""}{f"&limit={limit}" if limit != None else ""}{f"&q={query}" if query != None else ""}{f"&type={type}" if type != None else ""}{f"&score={score}" if score != None else ""}{f"&min_score={min_score}" if min_score != None else ""}{f"&max_score={max_score}" if max_score != None else ""}{f"&status={status}" if status != None else ""}{f"&rating={rating}" if rating != None else ""}{f"&sfw={sfw}" if sfw != None else ""}{f"&genres={genres}" if genres != None else ""}{f"&genres_exclude={genres_exclude}" if genres_exclude != None else ""}{f"&order_by={order_by}" if order_by != None else ""}{f"&sort={sort}" if sort != None else ""}{f"&letter={letter}" if letter != None else ""}{f"&producers={producers}" if producers != None else ""}{f"&start_date={start_date}" if start_date != None else ""}{f"&end_date={end_date}" if end_date != None else ""}')

    class Manga:
        async def Full(id) -> dict:
            return await Jikan.Requests(f'manga/{id}/full')
        async def Manga(id) -> dict:
            return await Jikan.Requests(f'manga/{id}')
        async def Characters(id) -> dict:
            return await Jikan.Requests(f'manga/{id}/characters')
        async def News(id, page: int = None) -> dict:
            return await Jikan.Requests(f'manga/{id}/news{f"?page={page}" if page != None else ""}')
        async def Topics(id, filter: str = None) -> dict:
            return await Jikan.Requests(f'manga/{id}/forum{f"?filter={filter}" if filter != None else ""}')
        async def Pictures(id) -> dict:
            return await Jikan.Requests(f'manga/{id}/pictures')
        async def Statistics(id) -> dict:
            return await Jikan.Requests(f'manga/{id}/statistics')
        async def MoreInfo(id) -> dict:
            return await Jikan.Requests(f'manga/{id}/moreinfo')
        async def Recommendations(id) -> dict:
            return await Jikan.Requests(f'manga/{id}/recommendations')
        async def UserUpdates(id, page: int = None) -> dict:
            return await Jikan.Requests(f'manga/{id}/userupdates{f"?page={page}" if page != None else ""}')
        async def Reviews(id, page: int = None) -> dict:
            return await Jikan.Requests(f'manga/{id}/reviews{f"?page={page}" if page != None else ""}')
        async def Relations(id) -> dict:
            return await Jikan.Requests(f'manga/{id}/relations')
        async def External(id) -> dict:
            return await Jikan.Requests(f'manga/{id}/external')
        async def Search(
            page: int = None, limit: int = None, query: str = None,
            type: str = None, score: float = None, min_score: float = None,
            max_score: float = None, status: str = None, sfw: bool = None,
            genres: str = None, genres_exclude: str = None, order_by: str = None,
            sort: str = None, letter: str = None, magazines: str = None,
            start_date: str = None, end_date: str = None,
            **kwargs) -> dict:
            return await Jikan.Requests(f'manga?{f"&page={page}&" if page is not None else ""}{f"&limit={limit}&" if limit is not None else ""}{f"&q={query}&" if query is not None else ""}{f"&type={type}&" if type is not None else ""}{f"&score={score}&" if score is not None else ""}{f"&min_score={min_score}&" if min_score is not None else ""}{f"&max_score={max_score}&" if max_score is not None else ""}{f"&status={status}&" if status is not None else ""}{f"&sfw={sfw}&" if sfw is not None else ""}{f"&genres={genres}&" if genres is not None else ""}{f"&genres_exclude={genres_exclude}&" if genres_exclude is not None else ""}{f"&order_by={order_by}&" if order_by is not None else ""}{f"&sort={sort}&" if sort is not None else ""}{f"&letter={letter}&" if letter is not None else ""}{f"&magazines={magazines}&" if magazines is not None else ""}{f"&start_date={start_date}&" if start_date is not None else ""}{f"&end_date={end_date}&" if end_date is not None else ""}')

    class Characters:
        async def Full(id) -> dict:
            return await Jikan.Requests(f'character/{id}/full')
        async def Character(id) -> dict:
            return await Jikan.Requests(f'character/{id}')
        async def Anime(id) -> dict:
            return await Jikan.Requests(f'character/{id}/anime')
        async def Manga(id) -> dict:
            return await Jikan.Requests(f'character/{id}/manga')
        async def VoiceActors(id) -> dict:
            return await Jikan.Requests(f'character/{id}/voices')
        async def Pictures(id) -> dict:
            return await Jikan.Requests(f'character/{id}/pictures')
        async def Search(
            page: int = None, limit: int = None, query: str = None,
            order_by: str = None, sort: str = None, letter: str = None,
            **kwargs) -> dict:
            return await Jikan.Requests(f'characters?{f"&page={page}" if page is not None else ""}{f"&limit={limit}" if limit is not None else ""}{f"&q={query}" if query is not None else ""}{f"&order_by={order_by}" if order_by is not None else ""}{f"&sort={sort}" if sort is not None else ""}{f"&letter={letter}" if letter is not None else ""}')

    class Random:
        async def Anime() -> dict:
            return await Jikan.Requests('random/anime')
        async def Manga() -> dict:
            return await Jikan.Requests('random/manga')
        async def Characters() -> dict:
            return await Jikan.Requests('random/characters')
        async def People() -> dict:
            return await Jikan.Requests('random/people')
        async def Users() -> dict:
            return await Jikan.Requests('random/users', timeout = 10)

    class Top:
        async def Anime(type: str = None, filter: str = None, page: int = None, limit: int = None, **kwargs) -> dict:
            return await Jikan.Requests(f'top/anime?{f"&type={type}" if type is not None else ""}{f"&filter={filter}" if filter is not None else ""}{f"&page={page}" if page is not None else ""}{f"&limit={limit}" if limit is not None else ""}')
        async def Manga(type: str = None, filter: str = None, page: int = None, limit: int = None, **kwargs) -> dict:
            return await Jikan.Requests(f'top/manga?{f"&type={type}" if type is not None else ""}{f"&filter={filter}" if filter is not None else ""}{f"&page={page}" if page is not None else ""}{f"&limit={limit}" if limit is not None else ""}')
        async def People(page: int = None, limit: int = None, **kwargs) -> dict:
            return await Jikan.Requests(f'top/people?{f"&page={page}" if page is not None else ""}{f"&limit={limit}" if limit is not None else ""}')
        async def Characters(page: int = None, limit: int = None, **kwargs) -> dict:
            return await Jikan.Requests(f'top/characters?{f"&page={page}" if page is not None else ""}{f"&limit={limit}" if limit is not None else ""}')
        async def Reviews(page: int = None, **kwargs) -> dict:
            return await Jikan.Requests(f'top/reviews?{f"&page={page}" if page is not None else ""}')

class MyAnimeList:

    async def Requests(url: str, max_retry: int = 5, timeout: float = 5.0) -> dict:

        for _ in range(max_retry):
            async with aiohttp.ClientSession() as session:

                try:
                    async with session.get(

                        f'https://api.myanimelist.net/v2/{url.replace(" ", "+")}',

                        headers = {
                            'X-MAL-CLIENT-ID': config.read(str, 'MAL_API', 'clientid'),
                            'Content-Type': 'application/json',
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'
                            },

                        timeout = timeout

                        ) as response:

                        return await validJson(response)

                except (TooManyRequests, asyncio.TimeoutError):
                    await asyncio.sleep(1)
                    continue

    class Anime:
        async def Search(
            query: str = None, limit: int = None, offset: int = None,
            fields: str = None, nsfw: bool = None,
            **kwargs) -> dict:
            return await MyAnimeList.Requests(f'anime?{f"&q={query}" if query != None else ""}{f"&limit={limit}" if limit != None else ""}{f"&offset={offset}" if offset != None else ""}{f"&fields={fields}" if fields != None else ""}{f"&nsfw={nsfw}" if nsfw != None else ""}')
        async def Anime(id, fields: str = None) -> dict:
            return await MyAnimeList.Requests(f'anime/{id}{f"?fields={fields}" if fields != None else ""}')
        async def Ranking(
            ranking_type: str, limit: int = None, offset: int = None,
            fields: str = None, nsfw: bool = None,
            **kwargs) -> dict:
            return await MyAnimeList.Requests(f'anime/ranking?ranking_type={ranking_type}{f"&limit={limit}" if limit != None else ""}{f"&offset={offset}" if offset != None else ""}{f"&fields={fields}" if fields != None else ""}{f"&nsfw={nsfw}" if nsfw != None else ""}')
        async def Seasonal(
            year: int, season: str, sort:str = None,
            limit: int = None, offset: int = None,
            fields: str = None, nsfw: bool = None,
            **kwargs) -> dict:
            return await MyAnimeList.Requests(f'anime/season/{year}/{season}?{f"&sort={sort}" if sort != None else ""}{f"&limit={limit}" if limit != None else ""}{f"&offset={offset}" if offset != None else ""}{f"&fields={fields}" if fields != None else ""}{f"&nsfw={nsfw}" if nsfw != None else ""}')

    class Manga:
        async def Search(
            query: str = None, limit: int = None, offset: int = None,
            fields: str = None, nsfw: bool = None,
            **kwargs) -> dict:
            return await MyAnimeList.Requests(f'manga?{f"&q={query}" if query != None else ""}{f"&limit={limit}" if limit != None else ""}{f"&offset={offset}" if offset != None else ""}{f"&fields={fields}" if fields != None else ""}{f"&nsfw={nsfw}" if nsfw != None else ""}')
        async def Manga(id, fields: str = None) -> dict:
            return await MyAnimeList.Requests(f'manga/{id}{f"?fields={fields}" if fields != None else ""}')
        async def Ranking(
            ranking_type: str, limit: int = None, offset: int = None,
            fields: str = None, nsfw: bool = None,
            **kwargs) -> dict:
            return await MyAnimeList.Requests(f'manga/ranking?ranking_type={ranking_type}{f"&limit={limit}" if limit != None else ""}{f"&offset={offset}" if offset != None else ""}{f"&fields={fields}" if fields != None else ""}{f"&nsfw={nsfw}" if nsfw != None else ""}')
