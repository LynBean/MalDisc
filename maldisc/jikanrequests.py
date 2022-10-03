
import aiohttp

from .constants import *
from .exceptions import *

async def JikanRequests(url):
        
    async with aiohttp.ClientSession() as session:
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'})
        
        async with session.get(f'https://api.jikan.moe/v4/{url.replace(" ", "%20")}', timeout = 5) as response:
            
            if response.status in (200, 304):
                return await response.json()
            elif response.status == 304:
                raise JikanRequestsBadReqeusts(response.message)
            elif response.status == 404:
                raise JikanRequestsNotFound(response.message)
            elif response.status == 429:
                raise JikanRequestsTooManyRequests(response.message)
            elif response.status == 500:
                raise JikanRequestsInternalServerError(response.message)
            elif response.status == 503:
                raise JikanRequestsServiceUnavailable(response.message)
            else:
                raise