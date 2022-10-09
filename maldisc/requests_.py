
import asyncio
import aiohttp
import json
from authlib.integrations.requests_client import OAuth2Session

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


async def MalRequests(url: str) -> dict:
    '''
    Currently malfunctioning, I don't know how
    OAuth2Session is supposed to work
    '''

    client = OAuth2Session(
        client_id = config['mal_config']['client_id'],
        client_secret = config['mal_config']['client_secret'],
        redirect_uri = 'https://myanimelist.net')

    authorization_response, state = client.create_authorization_url(
        url = 'https://myanimelist.net/v1/oauth2/authorize')

    response = await aiohttp.ClientSession().get(authorization_response)

    token = client.fetch_token(
        authorization_response = authorization_response,
        grant_type = 'client_credentials')

    async with aiohttp.ClientSession() as session:

        access_token = await session.post(

            'https://myanimelist.net/v1/oauth2/authorize',

            data = {
                'client_id': config['mal_config']['client_id'],
                'client_secret': config['mal_config']['client_secret'],
                'grant_type': 'client_credentials'
                }

            )

        async with session.get(

            f'https://api.myanimelist.net/v2/{url.replace(" ", "%20")}',

            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'
                },

            timeout = 12

            ) as response:

            return await to_json(response)


async def JikanAnimeFull(mal_id) -> dict:
    return await JikanRequests(f'anime/{mal_id}/full')

async def JikanAnime(mal_id) -> dict:
    return await JikanRequests(f'anime/{mal_id}')

async def JikanAnimeCharacters(mal_id) -> dict:
    return await JikanRequests(f'anime/{mal_id}/characters')

async def JikanAnimeStaff(mal_id) -> dict:
    return await JikanRequests(f'anime/{mal_id}/staff')

async def JikanAnimeEpisodes(mal_id, page: int = None) -> dict:
    return await JikanRequests(f'anime/{mal_id}/episodes')

async def JikanAnimeEpisodesByID(mal_id, episode_id) -> dict:
    return await JikanRequests(f'anime/{mal_id}/episodes/{episode_id}')

async def JikanAnimeNews(mal_id, page: int = None) -> dict:
    return await JikanRequests(f'anime/{mal_id}/news')

async def JikanAnimeForum(mal_id, filter: str = None) -> dict:
    """
    Args:
        filter (str, optional): Enum: "all" "episode" "other" (Filter topics). Defaults to None.
    """
    return await JikanRequests(f'anime/{mal_id}/forum')

async def JikanAnimeVideos(mal_id) -> dict:
    return await JikanRequests(f'anime/{mal_id}/videos')

async def JikanAnimeVideosEpisodes(mal_id, page: int = None) -> dict:
    return await JikanRequests(f'anime/{mal_id}/videos/episodes')

async def JikanAnimePictures(mal_id) -> dict:
    return await JikanRequests(f'anime/{mal_id}/pictures')

async def JikanAnimeStatistics(mal_id) -> dict:
    return await JikanRequests(f'anime/{mal_id}/statistics')

async def JikanAnimeMoreInfo(mal_id) -> dict:
    return await JikanRequests(f'anime/{mal_id}/moreinfo')

async def JikanAnimeRecommendations(mal_id) -> dict:
    return await JikanRequests(f'anime/{mal_id}/recommendations')

async def JikanAnimeUserUpdates(mal_id, page: int = None) -> dict:
    return await JikanRequests(f'anime/{mal_id}/userupdates')

async def JikanAnimeReviews(mal_id, page: int = None) -> dict:
    return await JikanRequests(f'anime/{mal_id}/reviews')

async def JikanAnimeRelations(mal_id) -> dict:
    return await JikanRequests(f'anime/{mal_id}/relations')

async def JikanAnimeThemes(mal_id) -> dict:
    return await JikanRequests(f'anime/{mal_id}/themes')

async def JikanAnimeExternal(mal_id) -> dict:
    return await JikanRequests(f'anime/{mal_id}/external')

async def JikanAnimeStreaming(mal_id) -> dict:
    return await JikanRequests(f'anime/{mal_id}/streaming')

async def JikanAnimeSearch(
    page: int = None,
    limit: int = None,
    query: str = None,
    type: str = None,
    score: float = None,
    min_score: float = None,
    max_score: float = None,
    status: str = None,
    rating: str = None,
    sfw: bool = False,
    genres: str = None,
    genres_exclude: str = None,
    order_by: str = "score",
    sort: str = "desc",
    letter: str = None,
    producers:str = None,
    start_date: str = None,
    end_date: str = None
    ) -> dict:
    """QUERY PARAMETERS

    Args:
        page (int, optional): Defaults to None.
        limit (int, optional): Defaults to None.
        query (str, optional): Defaults to None.
        type (str, optional): Enum: "tv" "movie" "ova" "special" "ona" "music" (Available Anime types). Defaults to None.
        score (float, optional): Defaults to None.
        min_score (float, optional): Set a minimum score for results. Defaults to None.
        max_score (float, optional): Set a maximum score for results. Defaults to None.
        status (str, optional): Enum: "airing" "complete" "upcoming" (Available Anime statuses). Defaults to None.
        rating (str, optional): Enum: "g" "pg" "pg13" "r17" "r" "rx" (Available Anime audience ratings)

        Ratings
        -------
        G - All Ages
        PG - Children
        PG-13 - Teens 13 or older
        R - 17+ (violence & profanity)
        R+ - Mild Nudity
        Rx - Hentai. Defaults to None.

        sfw (bool, optional): Filter out Adult entries. Defaults to False.
        genres (str, optional): Filter by genre(s) IDs. Can pass multiple with a comma as a delimiter. e.g 1,2,3. Defaults to None.
        genres_exclude (str, optional): Exclude genre(s) IDs. Can pass multiple with a comma as a delimiter. e.g 1,2,3. Defaults to None.
        order_by (str, optional): Enum: "mal_id" "title" "type" "rating" "start_date" "end_date" "episodes" "score" "scored_by" "rank" "popularity" "members" "favorites" (Available Anime order_by properties). Defaults to "score".
        sort (str, optional): Enum: "desc" "asc" (Characters Search Query Sort). Defaults to "desc".
        letter (str, optional): Return entries starting with the given letter. Defaults to None.
        producers (str, optional): Filter by producer(s) IDs. Can pass multiple with a comma as a delimiter. e.g 1,2,3. Defaults to None.
        start_date (str, optional): Filter by starting date. Format: YYYY-MM-DD. e.g 2022, 2005-05, 2005-01-01. Defaults to None.
        end_date (str, optional): Filter by ending date. Format: YYYY-MM-DD. e.g 2022, 2005-05, 2005-01-01. Defaults to None.

    Returns:
        dict
    """
    QUERY_LINE = '?'

    if page is not None:
        QUERY_LINE += f'page={page}&'
    if limit is not None:
        QUERY_LINE += f'limit={limit}&'
    if query is not None:
        QUERY_LINE += f'q={query}&'
    if type is not None:
        QUERY_LINE += f'type={type}&'
    if score is not None:
        QUERY_LINE += f'score={score}&'
    if min_score is not None:
        QUERY_LINE += f'min_score={min_score}&'
    if max_score is not None:
        QUERY_LINE += f'max_score={max_score}&'
    if status is not None:
        QUERY_LINE += f'status={status}&'
    if rating is not None:
        QUERY_LINE += f'rating={rating}&'
    if sfw is not None:
        QUERY_LINE += f'sfw={sfw}&'
    if genres is not None:
        QUERY_LINE += f'genres={genres}&'
    if genres_exclude is not None:
        QUERY_LINE += f'genres_exclude={genres_exclude}&'
    if order_by is not None:
        QUERY_LINE += f'order_by={order_by}&'
    if sort is not None:
        QUERY_LINE += f'sort={sort}&'
    if letter is not None:
        QUERY_LINE += f'letter={letter}&'
    if producers is not None:
        QUERY_LINE += f'producers={producers}&'
    if start_date is not None:
        QUERY_LINE += f'start_date={start_date}&'
    if end_date is not None:
        QUERY_LINE += f'end_date={end_date}&'

    return await JikanRequests(f'anime{QUERY_LINE}')

async def MalAnimeSearch(
    query: str = None,
    limit: int = 100,
    offset: int = 0,
    fields: str = None
) -> dict:

    QUERY_LINE = '?'

    if query is not None:
        QUERY_LINE += f'query={query}&'
    if limit is not None:
        QUERY_LINE += f'limit={limit}&'
    if offset is not None:
        QUERY_LINE += f'offset={offset}&'
    if fields is not None:
        QUERY_LINE += f'fields={fields}&'

    return await MalRequests(f'anime{QUERY_LINE}')

async def AnimeSearch(
    page: int = None,
    limit: int = None,
    query: str = None,
    type: str = None,
    score: float = None,
    min_score: float = None,
    max_score: float = None,
    status: str = None,
    rating: str = None,
    sfw: bool = None,
    genres: str = None,
    genres_exclude: str = None,
    order_by: str = None,
    sort: str = None,
    letter: str = None,
    producers:str = None,
    start_date: str = None,
    end_date: str = None,
    offset: int = None,
    fields: str = None
    ) -> dict:
    if config['mal_config']['enabled'] == True:
        return await MalAnimeSearch(
            query = query,
            limit = limit,
            offset = offset,
            fields = fields)

    else:
        return await JikanAnimeSearch(
            page = page,
            limit = limit,
            query = query,
            type = type,
            score = score,
            min_score = min_score,
            max_score = max_score,
            status = status,
            rating = rating,
            sfw = sfw,
            genres = genres,
            genres_exclude = genres_exclude,
            order_by = order_by,
            sort = sort,
            letter = letter,
            producers = producers,
            start_date = start_date,
            end_date = end_date)
