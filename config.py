import os

# data files
SKIN_FILE_PATH = os.path.join("data", "skins.json")
SKIN_DATA_URL = "https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/skins.json"
CHAMPION_FILE_PATH = os.path.join("data", "champions.json")
CHAMPION_DATA_URL = "https://raw.communitydragon.org/pbe/plugins/rcp-be-lol-game-data/global/default/v1/champion-summary.json"

# exporting
RAW_DATA_PATH = os.path.join("data", "raw")
EXPORT_PATH = "export"
TEMPLATE_PATH = "templates"
FAILED_ACCOUNT_PATH = "failedAccounts.txt" # in export folder
UNFINISHED_ACCOUNT_PATH = "uncheckedAccounts.txt"

# riot client
RIOT_CLIENT_LAUNCH_COOLDOWN = 5
RIOT_CLIENT_LOADING_RETRY_COUNT = 4
RIOT_CLIENT_LOADING_RETRY_COOLDOWN = 3

# league client
LEAGUE_CLIENT_LAUNCH_COOLDOWN = 5

# failure handling
LAUNCH_COOLDOWN_ON_INVALID_CREDENTIALS = 30
RATE_LIMITED_COOLDOWN = 300
MAX_RATE_LIMITED_ATTEMPTS = 5
MAX_FAILED_ATTEMPTS = 5

# lol store (refunds)
LOL_STORE_REQUEST_COOLDOWN = 30