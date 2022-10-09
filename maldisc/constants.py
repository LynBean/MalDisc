
from platformdirs import PlatformDirs

DEFAULT_CONFIG = {
    "prefix": "YOUR_BOT_PREFIX_HERE, e.g. !",
    "token": "YOUR_BOT_TOKEN_HERE",
    "mal_config": {
        "__comment_": "If mal_config get set to enable, the search API will be changed to MAL API instead of JIKAN API",
        "__comment__": "You can get your client_id and client_secret from https://myanimelist.net/apiconfig",
        "enabled": False,
        "client_id": "YOUR_MAL_CLIENT_ID_HERE",
        "client_secret": "YOUR_MAL_CLIENT_SECRET_HERE"
    }
    }

DIR_PATH = PlatformDirs('MalDisc', 'Kim').user_data_dir

