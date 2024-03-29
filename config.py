import os

# data files
SKIN_FILE_PATH = os.path.join("data", "skins.json")
SKIN_DATA_URL = "https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/skins.json"
CHAMPION_FILE_PATH = os.path.join("data", "champions.json")
CHAMPION_DATA_URL = "https://raw.communitydragon.org/pbe/plugins/rcp-be-lol-game-data/global/default/v1/champion-summary.json"
LOOT_DATA_FILE_PATH = os.path.join("data", "loot.json")
LOOT_DATA_URL = "https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-loot/global/default/trans.json"
LOOT_ITEMS_FILE_PATH = os.path.join("data", "lootItems.json")
LOOT_ITEMS_URL = "https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/loot.json"
# exporting
RAW_DATA_PATH = os.path.join("data", "raw")
EXPORT_PATH = "export"
TEMPLATE_PATH = "templates"
FAILED_ACCOUNT_PATH = "failedAccounts.txt" # in export folder
UNFINISHED_ACCOUNT_PATH = "uncheckedAccounts.txt"

# riot client
RIOT_CLIENT_LAUNCH_COOLDOWN = 15
RIOT_CLIENT_LOADING_RETRY_COUNT = 3
RIOT_CLIENT_LOADING_RETRY_COOLDOWN = 3

# league client
LEAGUE_CLIENT_LAUNCH_COOLDOWN = 15

# failure handling
LAUNCH_COOLDOWN_ON_INVALID_CREDENTIALS = 30
RATE_LIMITED_COOLDOWN = 300
MAX_RATE_LIMITED_ATTEMPTS = 5
MAX_FAILED_ATTEMPTS = 5

# lol store (refunds)
LOL_STORE_REQUEST_COOLDOWN = 30

# login captcha
LOGIN_URL = "https://authenticate.riotgames.com/api/v1/login"

# client watcher
CLIENT_WATCHER_CHECK_COOLDOWN = 1

# date format used for dates in export (banned until, last game time and so on)
DATE_FORMAT = "%Y-%m-%d %Hh%Mm%Ss"
