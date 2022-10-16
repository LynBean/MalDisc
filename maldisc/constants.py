
from platformdirs import PlatformDirs

DEFAULT_CONFIG = {
    "prefix": "YOUR_BOT_PREFIX_HERE",
    "token": "YOUR_BOT_TOKEN_HERE",
    "enable_url_detection": True,
    "mal_config": {
        "enabled": False,
        "client_id": "YOUR_MAL_CLIENT_ID_HERE"
    }
    }

DIR_PATH = PlatformDirs('MalDisc', 'Kim').user_data_dir

